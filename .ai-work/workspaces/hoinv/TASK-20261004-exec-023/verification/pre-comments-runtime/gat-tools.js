import z from "@deepseek-ai/schemastery";
import { ReasoningEffortId } from "@deepseek-ai/dsh-llm";
import { parentAgentOptionsForDelegation } from "@deepseek-ai/dsh-subagent";
import { TeamMissionId, TeamTaskId, scopesOverlap } from "@vuhoi/gat-core";
import { defineTool } from "@deepseek-ai/dsh-tools";
import { lstat, readFile } from "node:fs/promises";
import { join } from "node:path";
import { parse } from "yaml";
//#region lib/types/team-config.js
/** Workspace Team roster loading and built-in fallback definitions. */
const MEMBER_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/u;
const DOCUMENT_KEYS = new Set(["version", "members"]);
const MEMBER_KEYS = new Set([
	"name",
	"description",
	"prompt",
	"context",
	"provider",
	"model",
	"reasoning_effort"
]);
function record(value, label, keys) {
	if (typeof value !== "object" || value === null || Array.isArray(value)) throw new Error(`${label} must be a mapping`);
	const result = value;
	const unknown = Object.keys(result).find((key) => !keys.has(key));
	if (unknown !== void 0) throw new Error(`${label} contains unknown field ${JSON.stringify(unknown)}`);
	return result;
}
function text(value, label, max) {
	if (typeof value !== "string" || value.trim().length === 0 || value !== value.trim()) throw new Error(`${label} must be a trimmed non-empty string`);
	if (value.length > max) throw new Error(`${label} exceeds ${max} characters`);
	return value;
}
function normalizeMember(value, index) {
	const label = `members[${index}]`;
	const member = record(value, label, MEMBER_KEYS);
	const name = text(member.name, `${label}.name`, 64);
	if (!MEMBER_NAME.test(name)) throw new Error(`${label}.name must be lower-kebab-case`);
	const context = member.context ?? "fresh";
	if (context !== "fresh" && context !== "fork") throw new Error(`${label}.context must be fresh or fork`);
	const reasoningEffort = member.reasoning_effort === void 0 ? void 0 : text(member.reasoning_effort, `${label}.reasoning_effort`, 80);
	return {
		name,
		description: text(member.description, `${label}.description`, 200),
		prompt: text(member.prompt, `${label}.prompt`, 16384),
		context,
		provider: text(member.provider, `${label}.provider`, 200),
		model: text(member.model, `${label}.model`, 200),
		...reasoningEffort === void 0 ? {} : { reasoningEffort }
	};
}
function normalizeDocument(value, maxMembers) {
	const document = record(value, "team_members.yaml", DOCUMENT_KEYS);
	if (document.version !== 1) throw new Error("team_members.yaml version must be 1");
	if (!Array.isArray(document.members) || document.members.length === 0) throw new Error("team_members.yaml members must be a non-empty array");
	if (document.members.length > maxMembers) throw new Error(`team_members.yaml defines ${document.members.length} members; maximum is ${maxMembers}`);
	const members = document.members.map(normalizeMember);
	if (new Set(members.map((member) => member.name)).size !== members.length) throw new Error("team_members.yaml member names must be unique");
	return members;
}
/** Build the four-member starter Team on the Lead's current LLM provider. */
function builtInTeamMembers(provider) {
	return [
		{
			name: "advisor",
			description: "Advises the Lead when requested.",
			prompt: "Act as the Team advisor. Give evidence-based options, risks, and a concise recommendation when the Lead asks. Do not edit files unless explicitly assigned.",
			context: "fresh",
			provider,
			model: "gpt-5.6-sol"
		},
		{
			name: "senior-dev",
			description: "Handles complex implementation and rigorous reviews.",
			prompt: "Handle complex implementation and careful code or design review. Verify assumptions, coordinate write scopes, and report concrete evidence.",
			context: "fresh",
			provider,
			model: "gpt-5.6-sol"
		},
		{
			name: "dev",
			description: "Handles normal implementation tasks.",
			prompt: "Implement assigned normal-complexity tasks, coordinate through the Team board, and report verification evidence.",
			context: "fresh",
			provider,
			model: "gpt-5.6-terra"
		},
		{
			name: "junior-dev",
			description: "Handles simple tasks with a clear design.",
			prompt: "Implement only clearly specified simple tasks. Escalate ambiguity or missing design to the Lead before editing.",
			context: "fresh",
			provider,
			model: "gpt-5.6-luna"
		}
	];
}
/** Load a bounded literal workspace file, falling back to the built-in starter Team on any config error. */
async function loadTeamMembers(cwd, fallbackProvider, maxMembers, maxBytes) {
	try {
		if (cwd === void 0) throw new Error("the Session has no workspace");
		const path = join(cwd, "team_members.yaml");
		const entry = await lstat(path);
		if (!entry.isFile() || entry.isSymbolicLink()) throw new Error("team_members.yaml must be a regular file");
		if (entry.size > maxBytes) throw new Error(`team_members.yaml exceeds ${maxBytes} bytes`);
		const source = await readFile(path, "utf8");
		if (Buffer.byteLength(source, "utf8") > maxBytes) throw new Error(`team_members.yaml exceeds ${maxBytes} bytes`);
		return {
			source: "workspace",
			diagnostics: [],
			members: normalizeDocument(parse(source), maxMembers)
		};
	} catch (error) {
		const detail = error instanceof Error ? error.message : String(error);
		return {
			source: "built-in-default",
			diagnostics: [`Workspace Team config unavailable or invalid; used built-in defaults: ${cwd === void 0 ? detail : detail.replaceAll(cwd, "<workspace>")}`],
			members: builtInTeamMembers(fallbackProvider).slice(0, maxMembers)
		};
	}
}
//#endregion
//#region lib/types/index.js
/** Scoped model-facing tools for the opt-in Agent Teams runtime. */
/** Cordis plugin name. */
const name = "tool-agent-team";
/** Services required by the Team tool plugin. */
const inject = [
	"agents",
	"agentTeams",
	"llm",
	"subagents",
	"tools",
	"systemPrompt"
];
/** Loader schema for the opt-in Team tool plugin. */
const Config = z.object({
	freshProvider: z.string().default("spawn"),
	forkProvider: z.string().default("fork"),
	externalRestrictedTools: z.array(z.string().min(1)).default([]),
	minExecutionMembers: z.natural().min(1).max(Number.MAX_SAFE_INTEGER).default(2),
	maxExecutionMembers: z.natural().min(1).max(Number.MAX_SAFE_INTEGER).default(4),
	simpleMode: z.boolean().default(true),
	teamMembersMaxBytes: z.natural().min(1).max(Number.MAX_SAFE_INTEGER).default(65536)
});
/** Model-facing collaboration guidance shared by Lead and teammates. */
const POLICY = `Agent Teams is available in this session, but create teammates only when the user explicitly asks to use Agent Teams or teammates.

Once Agent Team is enabled, do not use subagent, subagent_fork, workflow, Ralph, or any other external sub-agent delegation path. Delegate only to members of the current Team. If the Team lacks a required skill or capability, ask the HUMAN to approve adding a suitable member; after approval, create that member with spawn_teammate, then assign the task to that member.

Each effect requires an exact current HUMAN-authorized mission lease bound by the host to this Agent; model tool arguments cannot grant it. Structural task edits invalidate mission approval. Messages may remain queued until the target has an exact lease.

The Team Lead and all teammates share the same working directory and filesystem. Edits are immediately visible to every member. Split write work into disjoint scopes, record expected write scopes on shared tasks, and use task dependencies when work must be ordered. Write-scope overlap is advisory, not a lock.

Prefer read/edit/write for file changes. If a file operation returns FS_STALE_VERSION, read the current file, rebase your intended change onto the new content, and retry. Bash, formatters, code generators, and scripts are not fully protected by the filesystem version guard; coordinate them explicitly and have the Lead review the final diff and run tests.

send_message steers an exactly authorized live target at its nearest step boundary or starts its idle turn. An inactive or unauthorized target stays queued until trusted host recovery and exact execution authorization. A delivered peer item starts with its stable message id and sender name. A successful send is already durable even when its result says queued; do not resend it. Shared-task workflow is list, get, claim with the current revision, perform the work, then complete. Task readiness never starts an owner. Before wait_agent, use list_agents and make sure another required member is running or provisioning; ask the HUMAN for trusted host recovery and exact authorization when the required member is inactive; a queued message never supplies wake authority. wait_agent observes only changes after that call starts, never wakes a member, and returns noProgress immediately when no other member can produce a change. Re-list after wakeup or timeout. The Lead must wait for required teammates before giving the final answer.`;
const ACTIVE_WAIT_STATUSES = new Set(["running", "provisioning"]);
const OWN_RESTRICTED_TOOLS = new Set([
	"list_agents",
	"wait_agent",
	"send_message",
	"interrupt_agent",
	"team_task_create",
	"team_task_list",
	"team_task_get"
]);
const RESTRICTED_REPORT_STATES = new Set(["blocked", "review_required"]);
const STRUCTURAL_TASK_ACTIONS = new Set([
	"edit",
	"set_dependencies",
	"delete"
]);
const EXTERNAL_SUBAGENT_TOOLS = new Set([
	"subagent",
	"subagent_fork",
	"workflow",
	"ralph"
]);
const NO_ACTIVE_PEER_MESSAGE = "No other Team member is running or provisioning. wait_agent cannot make progress or wake inactive teammates. Re-list with list_agents and team_task_list, then ask the HUMAN for trusted host recovery and exact authorization of each required inactive teammate before waiting again. Queued messages never supply wake authority.";
/** Count durable teammate rows without treating runtime idleness as removal. */
function durableActiveTeammates(view) {
	return view.members.filter((member) => member.role === "teammate" && member.status !== "provisioning" && member.status !== "failed" && (member.bindings === void 0 || member.bindings.every((binding) => binding.readiness === "ready"))).length;
}
/** Validate and preflight one optional child route before durable provisioning starts. */
async function childAgentOptions(ctx, parent, selection, signal) {
	const { provider, model, reasoning_effort: effort } = selection;
	for (const [name, value] of [
		["provider", provider],
		["model", model],
		["reasoning_effort", effort]
	]) if (value !== void 0 && (value.length === 0 || value.trim() !== value)) throw new Error(`child LLM ${name} must be a trimmed non-empty string`);
	if (provider === void 0 !== (model === void 0)) throw new Error("child LLM provider and model must be supplied together");
	if (provider === void 0 && effort === void 0) return void 0;
	const parentOptions = parentAgentOptionsForDelegation(parent);
	const effectiveProvider = provider ?? parentOptions.provider;
	const effectiveModel = model ?? parentOptions.model;
	if (effectiveProvider === void 0 || effectiveModel === void 0) throw new Error("cannot select a teammate LLM without an effective provider and model");
	const reasoningEffort = effort === void 0 ? void 0 : ReasoningEffortId(effort);
	await ctx.llm.resolveCallConfig({
		provider: effectiveProvider,
		model: effectiveModel,
		...reasoningEffort === void 0 ? {} : { reasoningEffort }
	}, signal);
	return {
		...provider === void 0 ? {} : {
			provider,
			model
		},
		...reasoningEffort === void 0 ? {} : { reasoningEffort }
	};
}
/** Return the legacy governed-mode approval failure, if any. */
function approvalFailure(view) {
	if (view.planApproval === void 0) return `current Team plan revision ${view.planRevision} is not HUMAN-approved`;
	if (view.planPhase !== "approved" || view.planApproval.approvedRevision !== view.planRevision) return `approved revision ${view.planApproval.approvedRevision} is stale for current revision ${view.planRevision}`;
}
/** Describe the active readiness contract without hiding the legacy approval gate. */
function executionRequirement(config) {
	const members = `at least ${config.minExecutionMembers} durable active teammates`;
	return config.simpleMode ? `an exact current HUMAN-authorized mission lease and ${members}` : `an exact current Team plan approved by HUMAN and ${members}`;
}
/** Read the canonical Team view and convert projection failures into one stable denial. */
function guardedTeamView(ctx, agent) {
	try {
		return ctx.agentTeams.remoteView(agent);
	} catch {
		return "canonical Team projection is unavailable; execution is fail-closed until it can be resolved";
	}
}
/** Admit only the exact built-in repair operation, including status arguments. */
function restrictedOwnToolAdmission(name, args) {
	if (OWN_RESTRICTED_TOOLS.has(name)) return true;
	if (name !== "report_team_status") return false;
	const state = typeof args === "object" && args !== null && "state" in args ? args.state : void 0;
	if (typeof state === "string" && RESTRICTED_REPORT_STATES.has(state)) return true;
	return `Team status reporting is restricted to blocked or review_required while Team execution is restricted; received state ${typeof state === "string" ? JSON.stringify(state) : `<${typeof state}>`}`;
}
/** Canonical capability and complete-WBS predicate shared by approval, preflight, and dispatch. */
function completeEnvelopeDiagnostics(current, agent, ctx, config) {
	const envelopeDiagnostics = [];
	for (const provider of [...new Set([config.freshProvider, config.forkProvider])].sort()) if (ctx.subagents.getProvider(provider) === void 0) envelopeDiagnostics.push(`spawn provider "${provider}" is unavailable`);
	const visibleTools = new Set(ctx.tools.schemas(agent).map((schema) => schema.name));
	for (const toolName of [...new Set(config.externalRestrictedTools)].sort()) if (!visibleTools.has(toolName)) envelopeDiagnostics.push(`configured restricted tool "${toolName}" is unavailable`);
	const tasks = [...current.tasks].sort((left, right) => String(left.id).localeCompare(String(right.id)));
	for (const [index, task] of tasks.entries()) for (const other of tasks.slice(index + 1)) {
		const overlap = [...task.writeScopes].sort().flatMap((left) => [...other.writeScopes].sort().flatMap((right) => scopesOverlap(left, right) ? [[left, right]] : []))[0];
		if (overlap !== void 0) envelopeDiagnostics.push(`task write-scope overlap (${task.id}, ${other.id}): ${JSON.stringify(overlap[0])} overlaps ${JSON.stringify(overlap[1])}`);
	}
	return envelopeDiagnostics;
}
/** Canonical complete-envelope evaluation shared by preflight and dispatch enforcement. */
function readiness(current, agent, ctx, config) {
	const approvalDiagnostic = config.simpleMode ? void 0 : approvalFailure(current);
	const authorityDiagnostic = ctx.agentTeams.executionDiagnostic(agent);
	const durableCount = durableActiveTeammates(current);
	const memberDiagnostic = durableCount < config.minExecutionMembers ? `only ${durableCount} durable active teammate(s); ${config.minExecutionMembers} required` : void 0;
	const envelopeDiagnostics = completeEnvelopeDiagnostics(current, agent, ctx, config);
	return {
		durableCount,
		mandatoryDiagnostics: [...envelopeDiagnostics, ...approvalDiagnostic === void 0 ? [] : [approvalDiagnostic]],
		diagnostics: [
			...authorityDiagnostic === void 0 ? [] : [authorityDiagnostic],
			...approvalDiagnostic === void 0 ? [] : [approvalDiagnostic],
			...memberDiagnostic === void 0 ? [] : [memberDiagnostic],
			...envelopeDiagnostics
		]
	};
}
/** Build fresh additive readiness metadata from canonical and live registries. */
function preflight(agent, ctx, config) {
	const current = guardedTeamView(ctx, agent);
	if (typeof current === "string") throw new Error(current);
	const { durableCount, diagnostics } = readiness(current, agent, ctx, config);
	return {
		planRevision: current.planRevision,
		planPhase: current.planPhase,
		...current.planApproval === void 0 ? {} : { approvedRevision: current.planApproval.approvedRevision },
		durableActiveTeammates: durableCount,
		requiredActiveTeammates: config.minExecutionMembers,
		executionReady: diagnostics.length === 0,
		diagnostics
	};
}
/**
* One roster row, matching `TeamMemberView`. The Lead pseudo-row omits the
* teammate-only provisioning fields, so only identity, role, status, and
* diagnostics are required.
*/
const MEMBER_VIEW_SCHEMA = {
	type: "object",
	additionalProperties: false,
	properties: {
		id: {
			type: "string",
			required: true
		},
		name: {
			type: "string",
			required: true
		},
		role: {
			type: "string",
			required: true,
			enum: ["lead", "teammate"]
		},
		status: {
			type: "string",
			required: true,
			enum: [
				"running",
				"idle",
				"inactive",
				"provisioning",
				"failed"
			]
		},
		description: { type: "string" },
		provider: { type: "string" },
		context: {
			type: "string",
			enum: ["fresh", "fork"]
		},
		model: { type: "string" },
		diagnostics: {
			type: "array",
			required: true,
			items: { type: "string" }
		},
		bindings: {
			type: "array",
			items: {
				type: "object",
				additionalProperties: false,
				properties: {
					binderId: {
						type: "string",
						required: true
					},
					protocolVersion: {
						type: "integer",
						required: true
					},
					readiness: {
						type: "string",
						required: true,
						enum: [
							"ready",
							"unavailable",
							"failed"
						]
					}
				}
			}
		}
	}
};
/** One shared task, matching the public `TeamTaskView`. */
const TASK_VIEW_SCHEMA = {
	type: "object",
	additionalProperties: false,
	properties: {
		id: {
			type: "string",
			required: true
		},
		missionId: { type: "string" },
		revision: {
			type: "integer",
			required: true
		},
		subject: {
			type: "string",
			required: true
		},
		description: {
			type: "string",
			required: true
		},
		status: {
			type: "string",
			required: true,
			enum: [
				"pending",
				"in_progress",
				"completed",
				"deleted"
			]
		},
		ownerName: { type: "string" },
		blockedBy: {
			type: "array",
			required: true,
			items: { type: "string" }
		},
		writeScopes: {
			type: "array",
			required: true,
			items: { type: "string" }
		},
		ready: {
			type: "boolean",
			required: true
		},
		writeScopeWarnings: {
			type: "array",
			required: true,
			items: { type: "string" }
		}
	}
};
const SPAWN_VALUE_SCHEMA = {
	type: "object",
	additionalProperties: false,
	properties: { member: {
		...MEMBER_VIEW_SCHEMA,
		required: true
	} }
};
const MEMBER_LIST_VALUE_SCHEMA = {
	type: "array",
	items: MEMBER_VIEW_SCHEMA
};
/** One committed member-work row, matching the complete `TeamWorkView`. */
const WORK_VIEW_SCHEMA = {
	type: "object",
	additionalProperties: false,
	properties: {
		memberId: {
			type: "string",
			required: true
		},
		state: {
			type: "string",
			required: true,
			enum: [
				"working",
				"blocked",
				"review_required",
				"done"
			]
		},
		summary: {
			type: "string",
			required: true
		},
		reason: { type: "string" },
		taskId: { type: "string" },
		files: {
			type: "array",
			required: true,
			items: { type: "string" }
		},
		updatedAt: {
			type: "integer",
			required: true
		}
	}
};
const SEND_VALUE_SCHEMA = {
	type: "object",
	additionalProperties: false,
	properties: {
		messageId: {
			type: "string",
			required: true
		},
		status: {
			type: "string",
			required: true,
			enum: ["accepted", "queued"]
		}
	}
};
/** `noProgress` is present only on the model-only shortcut that skips the wait. */
const WAIT_VALUE_SCHEMA = {
	type: "object",
	additionalProperties: false,
	properties: {
		timedOut: {
			type: "boolean",
			required: true
		},
		noProgress: {
			type: "object",
			additionalProperties: false,
			properties: {
				reason: {
					type: "string",
					required: true,
					const: "no-active-peer"
				},
				message: {
					type: "string",
					required: true
				}
			}
		}
	}
};
const INTERRUPT_VALUE_SCHEMA = {
	type: "object",
	additionalProperties: false,
	properties: { previousStatus: {
		type: "string",
		required: true,
		enum: [
			"running",
			"idle",
			"inactive"
		]
	} }
};
const TASK_LIST_VALUE_SCHEMA = {
	type: "object",
	additionalProperties: false,
	properties: {
		tasks: {
			type: "array",
			required: true,
			items: TASK_VIEW_SCHEMA
		},
		nextCursor: { type: "integer" },
		preflight: {
			type: "object",
			required: true,
			additionalProperties: false,
			properties: {
				planRevision: {
					type: "integer",
					required: true
				},
				planPhase: {
					type: "string",
					required: true,
					enum: ["draft", "approved"]
				},
				approvedRevision: { type: "integer" },
				durableActiveTeammates: {
					type: "integer",
					required: true
				},
				requiredActiveTeammates: {
					type: "integer",
					required: true
				},
				executionReady: {
					type: "boolean",
					required: true
				},
				diagnostics: {
					type: "array",
					required: true,
					items: { type: "string" }
				}
			}
		}
	}
};
/**
* Declare one canonical output schema with compact model-facing JSON. Every
* Team result is a fixed record, so the declared schema is what makes the
* compiler check `execute` against the value the model is promised.
* @param schema - canonical value schema for one tool.
* @returns the `output` declaration accepted by {@link defineTool}.
*/
function jsonOutput(schema) {
	return {
		schema,
		render: (_args, value) => [{
			type: "text",
			text: JSON.stringify(value)
		}]
	};
}
/** Recover the exact caller guaranteed by Agent-scoped tool discovery. */
function callingAgent(agent, toolName) {
	/* v8 ignore next 2 -- Team tools are registered only in an exact Agent scope, so discovery supplies this carrier. */
	if (agent === void 0) throw new Error(`${toolName} requires a calling Agent`);
	return agent;
}
/** Register the complete Team tool set in one exact Agent scope. */
function install(agent, ctx, config) {
	const scoped = agent.ctx;
	const { role, name: memberName, id: teamId } = ctx.agentTeams.membership(agent);
	const disposers = [];
	const register = (disposer) => {
		disposers.push(disposer);
	};
	try {
		register(scoped.tools.guard((exec) => {
			const current = guardedTeamView(ctx, agent);
			if (typeof current === "string") return `Team execution denied: ${current}`;
			if ((EXTERNAL_SUBAGENT_TOOLS.has(exec.name) || exec.capabilities.includes("external-delegation")) && current.enabled) return `External sub-agent delegation denied for tool "${exec.name}": Agent Team is enabled for this session. Use an existing Team member. If the required skill or capability is missing, ask the HUMAN to approve adding a member, create it with spawn_teammate, then assign the task to that member.`;
			const evaluation = readiness(current, agent, ctx, config);
			const active = evaluation.durableCount;
			if (exec.name === "spawn_teammate") {
				if ((!exec.capabilities.length || !exec.capabilities.every((key) => ["team-bootstrap", "nested-dispatch"].includes(key))) && ctx.agentTeams.executionDiagnostic(agent) !== void 0) return "Team spawn denied: nested capability union requires an exact execution lease";
				const failure = completeEnvelopeDiagnostics(current, agent, ctx, config)[0];
				if (failure !== void 0) return `Team spawn denied: ${failure}`;
				if (active >= config.maxExecutionMembers) return `Team spawn denied: durable teammate cap of ${config.maxExecutionMembers} reached; found ${active}`;
				return;
			}
			if (evaluation.diagnostics.length === 0) return void 0;
			const controlKeys = new Set([
				"team-inspection",
				"human-question",
				"team-structure",
				"team-coordination",
				"team-safety",
				"team-report-restricted",
				"nested-dispatch"
			]);
			const controlOnly = exec.capabilities.length > 0 && exec.capabilities.every((key) => controlKeys.has(key));
			if (exec.capabilities.length === 1 && exec.capabilities[0] === "nested-dispatch") return void 0;
			if (exec.name === "team_task_update") {
				const args = exec.arguments;
				const action = typeof args === "object" && args !== null && "action" in args ? args.action : void 0;
				if (controlOnly && typeof action === "string" && STRUCTURAL_TASK_ACTIONS.has(action)) return void 0;
				return `Team task action ${JSON.stringify(action)} is unavailable while Team execution is restricted; use edit, set_dependencies, or delete`;
			}
			const ownAdmission = restrictedOwnToolAdmission(exec.name, exec.arguments);
			if (controlOnly && (ownAdmission === true || exec.capabilities.every((key) => [
				"team-inspection",
				"human-question",
				"nested-dispatch"
			].includes(key)))) return void 0;
			if (typeof ownAdmission === "string") return ownAdmission;
			const condition = evaluation.mandatoryDiagnostics[0] ?? `Team execution requires ${executionRequirement(config)}; found ${active}`;
			return `Team execution denied for tool "${exec.name}": ${condition}`;
		}));
		register(scoped.systemPrompt.section({
			name: "team:policy",
			order: scoped.systemPrompt.getSectionOrder("TEAM_POLICY"),
			text: `${POLICY}\n\nExecution requires ${executionRequirement(config)}, and the durable teammate cap is ${config.maxExecutionMembers}.\n\nYour Team role is ${role}; your Team name is ${memberName}; Team id is ${teamId}.`
		}));
		register(scoped.tools.register(defineTool({
			name: "spawn_teammate",
			capabilities: ["team-bootstrap"],
			description: "Create one named, durable teammate. Only the Team Lead may call this tool. For a missing skill or capability, obtain explicit HUMAN approval before adding the member, then assign work to that member.",
			parameters: {
				name: {
					type: "string",
					required: true,
					description: "Unique lower-kebab-case teammate name."
				},
				description: {
					type: "string",
					required: true,
					description: "Short description of the delegated responsibility."
				},
				prompt: {
					type: "string",
					required: true,
					description: "Complete initial task for the teammate."
				},
				context: {
					type: "string",
					enum: ["fresh", "fork"],
					description: "fresh starts without Lead history; fork inherits completed Lead turns. Defaults to fresh."
				},
				provider: {
					type: "string",
					description: "LLM provider route for this teammate. Supply together with model."
				},
				model: {
					type: "string",
					description: "Model id interpreted by provider. Supply together with provider."
				},
				reasoning_effort: {
					type: "string",
					description: "Optional adapter-owned reasoning effort for the teammate route."
				}
			},
			output: jsonOutput(SPAWN_VALUE_SCHEMA),
			async execute(args, exec) {
				const agent = callingAgent(exec.agent, "spawn_teammate");
				const context = args.context ?? "fresh";
				const agentOptions = await childAgentOptions(ctx, agent, args, exec.signal);
				return await ctx.agentTeams.spawnTeammate(agent, {
					name: args.name,
					description: args.description,
					prompt: [{
						type: "text",
						text: args.prompt
					}],
					context,
					provider: context === "fork" ? config.forkProvider : config.freshProvider,
					...agentOptions === void 0 ? {} : { agentOptions },
					signal: exec.signal
				});
			}
		})));
		register(scoped.tools.register(defineTool({
			name: "report_team_status",
			capabilities: ["team-report-restricted"],
			description: "Commit your current durable Team work state and return the complete authoritative work view.",
			parameters: {
				state: {
					type: "string",
					required: true,
					enum: [
						"working",
						"blocked",
						"review_required",
						"done"
					]
				},
				summary: {
					type: "string",
					required: true
				},
				reason: { type: "string" },
				task_id: { type: "string" },
				files: {
					type: "array",
					items: { type: "string" }
				}
			},
			output: jsonOutput(WORK_VIEW_SCHEMA),
			async execute(args, exec) {
				const work = await ctx.agentTeams.reportWork(callingAgent(exec.agent, "report_team_status"), {
					state: args.state,
					summary: args.summary,
					...args.reason === void 0 ? {} : { reason: args.reason },
					...args.task_id === void 0 ? {} : { taskId: TeamTaskId(args.task_id) },
					files: args.files ?? []
				});
				return {
					...work,
					files: [...work.files]
				};
			}
		})));
		register(scoped.tools.register(defineTool({
			name: "send_message",
			capabilities: ["team-coordination"],
			description: "Send one durable message to another Team member. An exactly authorized live target receives it at the nearest step boundary or starts a turn. Other targets remain queued until trusted host recovery and exact authorization.",
			parameters: {
				target: {
					type: "string",
					required: true,
					description: "Team member name, or lead."
				},
				message: {
					type: "string",
					required: true,
					description: "Self-contained message for the target."
				}
			},
			output: jsonOutput(SEND_VALUE_SCHEMA),
			execute(args, exec) {
				return ctx.agentTeams.sendMessage(callingAgent(exec.agent, "send_message"), {
					target: args.target,
					content: [{
						type: "text",
						text: args.message
					}],
					signal: exec.signal
				});
			}
		})));
		register(scoped.tools.register(defineTool({
			name: "list_agents",
			capabilities: ["team-inspection"],
			description: "List the Lead and every durable teammate with current runtime status.",
			parameters: {},
			output: jsonOutput(MEMBER_LIST_VALUE_SCHEMA),
			async execute(_args, exec) {
				return Promise.resolve(ctx.agentTeams.listMembers(callingAgent(exec.agent, "list_agents")));
			}
		})));
		register(scoped.tools.register(defineTool({
			name: "wait_agent",
			capabilities: ["team-coordination"],
			description: "Wait for the next teammate status, mailbox, or shared-task change after this call starts. This never wakes inactive members and returns noProgress immediately when no other member is running or provisioning. Re-list after wakeup or timeout instead of polling.",
			parameters: { timeout_ms: {
				type: "integer",
				description: "Wait duration in milliseconds, from 10000 through 3600000. Defaults to 30000."
			} },
			output: jsonOutput(WAIT_VALUE_SCHEMA),
			async execute(args, exec) {
				const caller = callingAgent(exec.agent, "wait_agent");
				const timeoutMs = args.timeout_ms ?? 3e4;
				if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1e4 || timeoutMs > 36e5) return await ctx.agentTeams.waitForChange(caller, timeoutMs, exec.signal);
				if (!ctx.agentTeams.listMembers(caller).some((member) => member.id !== caller.id && ACTIVE_WAIT_STATUSES.has(member.status))) return {
					timedOut: false,
					noProgress: {
						reason: "no-active-peer",
						message: NO_ACTIVE_PEER_MESSAGE
					}
				};
				return await ctx.agentTeams.waitForChange(caller, timeoutMs, exec.signal);
			}
		})));
		register(scoped.tools.register(defineTool({
			name: "interrupt_agent",
			capabilities: ["team-safety"],
			description: "Interrupt one teammate's current turn while preserving its pending inbox. Team Lead only.",
			parameters: { target: {
				type: "string",
				required: true,
				description: "Teammate name."
			} },
			output: jsonOutput(INTERRUPT_VALUE_SCHEMA),
			async execute(args, exec) {
				return Promise.resolve(ctx.agentTeams.interrupt(callingAgent(exec.agent, "interrupt_agent"), args.target));
			}
		})));
		register(scoped.tools.register(defineTool({
			name: "team_task_create",
			capabilities: ["team-structure"],
			description: "Create one unowned pending task on the shared Team task board.",
			parameters: {
				mission_id: {
					type: "string",
					required: true,
					description: "Explicit canonical mission identity; list order never grants authority."
				},
				subject: {
					type: "string",
					required: true,
					description: "Concise task title."
				},
				description: {
					type: "string",
					required: true,
					description: "Complete task details and acceptance criteria."
				},
				blocked_by: {
					type: "array",
					items: { type: "string" },
					description: "Task ids that must complete first."
				},
				write_scopes: {
					type: "array",
					items: { type: "string" },
					description: "Advisory workspace-relative file or directory prefixes this task expects to modify."
				}
			},
			output: jsonOutput(TASK_VIEW_SCHEMA),
			async execute(args, exec) {
				return await ctx.agentTeams.createTask(callingAgent(exec.agent, "team_task_create"), {
					missionId: TeamMissionId(args.mission_id),
					subject: args.subject,
					description: args.description,
					...args.blocked_by === void 0 ? {} : { blockedBy: args.blocked_by.map(TeamTaskId) },
					...args.write_scopes === void 0 ? {} : { writeScopes: args.write_scopes }
				});
			}
		})));
		register(scoped.tools.register(defineTool({
			name: "team_task_list",
			capabilities: ["team-inspection"],
			description: "List shared tasks, including readiness, owner, revision, blockers, and write-scope warnings.",
			parameters: {
				status: {
					type: "string",
					enum: [
						"pending",
						"in_progress",
						"completed"
					],
					description: "Optional exact status filter."
				},
				owner: {
					type: "string",
					description: "Optional member-name filter; use unowned for tasks without an owner."
				},
				ready: {
					type: "boolean",
					description: "Optional readiness filter."
				},
				cursor: {
					type: "integer",
					description: "Zero-based result offset. Defaults to 0."
				},
				limit: {
					type: "integer",
					description: "Number of rows, 1 through 100. Defaults to 50."
				}
			},
			output: jsonOutput(TASK_LIST_VALUE_SCHEMA),
			execute(args, exec) {
				const status = args.status;
				const filtered = ctx.agentTeams.listTasks(callingAgent(exec.agent, "team_task_list")).filter((task) => (status === void 0 || task.status === status) && (args.owner === void 0 || (args.owner === "unowned" ? task.ownerName === void 0 : task.ownerName === args.owner)) && (args.ready === void 0 || task.ready === args.ready));
				const cursor = args.cursor ?? 0;
				const limit = args.limit ?? 50;
				if (!Number.isSafeInteger(cursor) || cursor < 0) throw new Error("cursor must be a non-negative safe integer");
				if (!Number.isSafeInteger(limit) || limit < 1 || limit > 100) throw new Error("limit must be an integer from 1 through 100");
				return Promise.resolve({
					tasks: filtered.slice(cursor, cursor + limit),
					...cursor + limit < filtered.length ? { nextCursor: cursor + limit } : {},
					preflight: preflight(callingAgent(exec.agent, "team_task_list"), ctx, config)
				});
			}
		})));
		register(scoped.tools.register(defineTool({
			name: "team_task_get",
			capabilities: ["team-inspection"],
			description: "Read the complete latest value of one shared task before changing or executing it.",
			parameters: { task_id: {
				type: "string",
				required: true,
				description: "Shared task id."
			} },
			output: jsonOutput(TASK_VIEW_SCHEMA),
			async execute(args, exec) {
				return Promise.resolve(ctx.agentTeams.getTask(callingAgent(exec.agent, "team_task_get"), TeamTaskId(args.task_id)));
			}
		})));
		register(scoped.tools.register(defineTool({
			name: "team_task_update",
			capabilities: ["team-structure"],
			description: "Compare-and-set a shared task action using the latest revision from team_task_get or team_task_list.",
			parameters: {
				task_id: {
					type: "string",
					required: true,
					description: "Shared task id."
				},
				expected_revision: {
					type: "integer",
					required: true,
					description: "Current task revision used as the CAS precondition."
				},
				action: {
					type: "string",
					required: true,
					enum: [
						"claim",
						"release",
						"edit",
						"set_dependencies",
						"complete",
						"reopen",
						"reassign",
						"delete"
					],
					description: "Task transition to apply."
				},
				subject: {
					type: "string",
					description: "Replacement title for edit."
				},
				description: {
					type: "string",
					description: "Replacement details for edit."
				},
				blocked_by: {
					type: "array",
					items: { type: "string" },
					description: "Complete blocker list for set_dependencies."
				},
				write_scopes: {
					type: "array",
					items: { type: "string" },
					description: "Replacement advisory write scopes for edit."
				},
				owner: {
					type: "string",
					description: "Member name for Lead-only reassign; omit to unassign."
				}
			},
			output: jsonOutput(TASK_VIEW_SCHEMA),
			async execute(args, exec) {
				return await ctx.agentTeams.updateTask(callingAgent(exec.agent, "team_task_update"), {
					taskId: TeamTaskId(args.task_id),
					expectedRevision: args.expected_revision,
					action: args.action,
					...args.subject === void 0 ? {} : { subject: args.subject },
					...args.description === void 0 ? {} : { description: args.description },
					...args.blocked_by === void 0 ? {} : { blockedBy: args.blocked_by.map(TeamTaskId) },
					...args.write_scopes === void 0 ? {} : { writeScopes: args.write_scopes },
					...args.owner === void 0 ? {} : { owner: args.owner }
				});
			}
		})));
	} catch (error) {
		for (const dispose of disposers.reverse()) dispose();
		throw error;
	}
	return () => {
		for (const dispose of disposers.reverse()) dispose();
	};
}
/** Install Team tools in every live or subsequently published Team member scope. */
function apply(ctx, config = {}) {
	const resolved = {
		freshProvider: config.freshProvider ?? "spawn",
		forkProvider: config.forkProvider ?? "fork",
		minExecutionMembers: config.minExecutionMembers ?? 2,
		maxExecutionMembers: config.maxExecutionMembers ?? 4,
		simpleMode: config.simpleMode ?? true,
		teamMembersMaxBytes: config.teamMembersMaxBytes ?? 65536,
		externalRestrictedTools: [...new Set((config.externalRestrictedTools ?? []).map((tool, index) => {
			if (typeof tool !== "string" || tool.length === 0) throw new Error(`externalRestrictedTools[${index}] must be a non-empty string`);
			return tool;
		}))].sort()
	};
	for (const key of [
		"minExecutionMembers",
		"maxExecutionMembers",
		"teamMembersMaxBytes"
	]) if (!Number.isSafeInteger(resolved[key]) || resolved[key] < 1) throw new TypeError(`${key} must be a positive safe integer`);
	if (resolved.maxExecutionMembers < resolved.minExecutionMembers) throw new RangeError("maxExecutionMembers must be greater than or equal to minExecutionMembers");
	ctx.agentTeams.configureExecutionPolicy(!resolved.simpleMode);
	ctx.effect(() => ctx.agentTeams.registerApprovalPreflight((agent, view) => completeEnvelopeDiagnostics(view, agent, ctx, resolved)), "tool-team.approvalPreflight()");
	const installed = /* @__PURE__ */ new Map();
	const maybeInstall = (agent) => {
		if (installed.has(agent.id) || ctx.agentTeams.tryMembership(agent) === void 0) return;
		if (resolved.simpleMode && !ctx.agentTeams.remoteView(agent).enabled) return;
		installed.set(agent.id, install(agent, ctx, resolved));
	};
	ctx.effect(() => ctx.agentTeams.registerInitializer(async (lead, signal) => {
		const parent = parentAgentOptionsForDelegation(lead);
		if (parent.provider === void 0) throw new Error("cannot build the default Team without the Lead LLM provider");
		const loaded = await loadTeamMembers(lead.session.header.cwd, parent.provider, resolved.maxExecutionMembers, resolved.teamMembersMaxBytes);
		const prepared = await Promise.all(loaded.members.map(async (member) => ({
			member,
			agentOptions: await childAgentOptions(ctx, lead, {
				provider: member.provider,
				model: member.model,
				...member.reasoningEffort === void 0 ? {} : { reasoning_effort: member.reasoningEffort }
			}, signal)
		})));
		signal.throwIfAborted();
		const members = prepared.map(({ member, agentOptions }) => ({
			name: member.name,
			description: member.description,
			initialTask: [{
				type: "text",
				text: member.prompt
			}],
			context: member.context,
			continuationProvider: member.context === "fork" ? resolved.forkProvider : resolved.freshProvider,
			...agentOptions === void 0 ? {} : { agentOptions },
			attachments: []
		}));
		return {
			source: loaded.source,
			diagnostics: [...loaded.diagnostics],
			members
		};
	}), "tool-team.initializer()");
	for (const agent of ctx.agents.list()) maybeInstall(agent);
	ctx.on("agent/created", ({ agent }) => {
		maybeInstall(agent);
	});
	ctx.on("session/event", (session, event) => {
		if (event.type !== "team/member") return;
		const lead = ctx.agents.get(session.id);
		if (lead !== void 0) maybeInstall(lead);
	});
	ctx.on("agent/disposed", ({ agent }) => {
		installed.get(agent.id)?.();
		installed.delete(agent.id);
	});
	ctx.effect(() => () => {
		for (const dispose of installed.values()) dispose();
		installed.clear();
	}, "tool-team.scopedTools()");
}
//#endregion
export { Config, apply, inject, name };
