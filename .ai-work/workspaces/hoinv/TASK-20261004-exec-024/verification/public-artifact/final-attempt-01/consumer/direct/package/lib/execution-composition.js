import { r as coordinatorFor, t as createDurableTools } from "./tools-BVkFAKbd.js";
import { realpath } from "node:fs/promises";
import { TeamError } from "@vuhoi/gat-core";
import { TextDecoder } from "node:util";
import { symbols } from "@deepseek-ai/cordis";
import z from "@deepseek-ai/schemastery";
import { DurableAgentConsumer, DurableAgentService, createReviewPacket, normalizeCompletionProposal, normalizeTaskContract, readReviewRef, reviewEvidenceRefs, reviewPacketSha256, taskContractSha256 } from "@deepseek-ai/dsh-durable-agent";
import { createHash } from "node:crypto";
//#region lib/types/execution-host.js
/** Current isolated execution ports; independent of the direct-member Host bridge. */
function unavailable$1() {
	throw new TeamError("Execution binding unavailable.", "TEAM_BINDING_UNAVAILABLE");
}
function record$1(value) {
	return value !== null && typeof value === "object" && !Array.isArray(value);
}
function port(value) {
	return record$1(value) && [
		"executionFor",
		"tryMembership",
		"getTask",
		"getExecution"
	].every((key) => typeof value[key] === "function");
}
/**
* Resolve callable current-Host operations while preserving their original receiver.
* @param ctx Plugin scope containing the registered Team service.
* @returns The exact underlying owner, or a binding failure on an incompatible Host.
*/
function resolveExecutionTeam(ctx) {
	const scoped = ctx.get("agentTeams");
	if (!record$1(scoped)) unavailable$1();
	const owner = Reflect.get(scoped, symbols.original) ?? scoped;
	if (!port(owner)) unavailable$1();
	return owner;
}
/**
* Check identity-bearing returned data before granting execution authority.
* @param snapshot Current public execution snapshot returned by the selected service.
*/
function assertExecutionSnapshot(snapshot) {
	if (!record$1(snapshot) || [
		"id",
		"requestId",
		"memberId",
		"memberName",
		"sessionId",
		"taskId",
		"provider"
	].some((key) => typeof snapshot[key] !== "string" || !snapshot[key].length) || !Number.isSafeInteger(snapshot.generation) || snapshot.generation < 1 || !Number.isSafeInteger(snapshot.taskRevision) || snapshot.taskRevision < 1 || ![
		"provisioning",
		"active",
		"closing",
		"completed",
		"failed",
		"cancelled"
	].includes(snapshot.phase) || !record$1(snapshot.brief) || !Array.isArray(snapshot.brief.inputs) || snapshot.brief.inputs.some((input) => !record$1(input) || typeof input.reference !== "string") || Buffer.byteLength(JSON.stringify(snapshot), "utf8") > 65536) unavailable$1();
}
//#endregion
//#region lib/types/execution-binding.js
/** Exact isolated execution memory lifetime; GAT Detail Design §§9–10. */
function denied() {
	throw new TeamError("task memory binding is unavailable", "TEAM_BINDING_UNAVAILABLE");
}
function registered(ctx) {
	const service = ctx.get("durableAgent");
	if (service === void 0) denied();
	const underlying = Reflect.get(service, symbols.original) ?? service;
	if (!(underlying instanceof DurableAgentService) || underlying.apiVersion !== 1 || underlying.features.selectiveMemoryRead !== true) denied();
	return underlying;
}
function record(value) {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}
function freeze(value) {
	if (value !== null && typeof value === "object") {
		for (const child of Object.values(value)) freeze(child);
		Object.freeze(value);
	}
	return value;
}
function selectedId(args) {
	if (!record(args) || Reflect.ownKeys(args).length !== 1) denied();
	const property = Object.getOwnPropertyDescriptor(args, "itemId");
	if (property === void 0 || !("value" in property) || typeof property.value !== "string" || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(property.value)) denied();
	return property.value;
}
var Binding = class {
	ctx;
	agent;
	execution;
	service;
	workspace;
	member;
	limits;
	configuration;
	reviewInstaller;
	onClosed;
	pending = /* @__PURE__ */ new Set();
	lateDisposals = /* @__PURE__ */ new Set();
	cleanupFailed = false;
	disposers = [];
	phase = "open";
	ref;
	cleanup;
	root;
	teamOwner;
	teamId;
	selected;
	releaseOwner;
	readCalls = 0;
	readResultBytes = 0;
	rendered = /* @__PURE__ */ new WeakMap();
	constructor(ctx, agent, execution, team, service, workspace, member, limits, configuration, reviewInstaller, onClosed) {
		this.ctx = ctx;
		this.agent = agent;
		this.execution = execution;
		this.service = service;
		this.workspace = workspace;
		this.member = member;
		this.limits = limits;
		this.configuration = configuration;
		this.reviewInstaller = reviewInstaller;
		this.onClosed = onClosed;
		const parentId = agent.session.header.parentSession;
		const root = parentId === void 0 ? void 0 : ctx.agents.get(parentId);
		const membership = team.tryMembership(agent);
		if (root === void 0 || membership === void 0 || membership.role !== "teammate" || membership.root !== root || String(membership.id) !== root.id) denied();
		this.root = root;
		this.teamOwner = team;
		this.teamId = String(membership.id);
		const ids = execution.brief.inputs.filter((input) => input.reference.startsWith("durable-memory:")).map((input) => input.reference.slice(15));
		if (ids.length > limits.maxSelectedItems || ids.some((id) => !/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(id))) denied();
		this.selected = new Set(ids);
		this.releaseOwner = coordinatorFor(service).reserve(workspace, member.declaration.name);
	}
	authority(provisioning = false) {
		if (this.phase !== "open" || this.ctx.agents.get(this.agent.id) !== this.agent || this.ctx.agents.get(this.root.id) !== this.root || registered(this.ctx) !== this.service) denied();
		if (resolveExecutionTeam(this.ctx) !== this.teamOwner) denied();
		const current = this.teamOwner.executionFor(this.agent);
		const membership = this.teamOwner.tryMembership(this.agent);
		if (current !== void 0) assertExecutionSnapshot(current);
		if (current?.id !== this.execution.id || current.sessionId !== this.agent.id || current.memberId !== this.execution.memberId || current.memberName !== this.execution.memberName || current.generation !== this.execution.generation || current.taskId !== this.execution.taskId || current.taskRevision !== this.execution.taskRevision || membership?.role !== "teammate" || String(membership.id) !== this.teamId || membership.root !== this.root || current.phase !== "active" && !(provisioning && current.phase === "provisioning") || JSON.stringify(current.brief) !== JSON.stringify(this.execution.brief)) denied();
		const task = this.teamOwner.getTask(this.root, current.taskId);
		if (task.id !== current.taskId || task.status !== "in_progress" || task.ownerMemberId !== current.memberId || task.revision !== current.taskRevision) denied();
	}
	async operation(run) {
		const pending = Promise.resolve().then(run);
		this.pending.add(pending);
		try {
			return await pending;
		} finally {
			this.pending.delete(pending);
		}
	}
	async install() {
		this.agent.ctx.effect(() => () => this.close(), "taskMemory.close()");
		try {
			await this.operation(async () => {
				this.authority(true);
				await this.service.validateDeclaration(this.workspace, this.member.declaration);
				this.authority(true);
				this.ref = await this.service.provision(this.workspace, this.member.declaration);
				this.authority(true);
			});
			const read = createDurableTools(new DurableAgentConsumer(this.service, this.ref), () => this.authority())[0];
			if (!record(read.schema)) denied();
			if (this.member.mode === "task" && this.selected.size > 0) {
				this.disposers.push(this.agent.ctx.tools.register({
					name: read.name,
					description: "Read a memory item explicitly selected in this task assignment.",
					parameters: read.schema,
					execute: async (args, exec) => {
						if (exec.agent !== this.agent || exec.parent !== void 0) denied();
						if (++this.readCalls > this.limits.maxReadCalls) denied();
						const id = selectedId(args);
						this.authority();
						if (!this.selected.has(id)) denied();
						return await this.operation(async () => {
							const item = await read.invoke(args);
							this.authority();
							if (!record(item) || item.id !== id || typeof item.content !== "string" || Buffer.byteLength(item.content, "utf8") > this.limits.maxBodyBytes || Buffer.byteLength(JSON.stringify(item), "utf8") > this.limits.maxResultBytes) denied();
							const encoded = JSON.stringify(item);
							this.readResultBytes += Buffer.byteLength(encoded, "utf8");
							if (this.readResultBytes > this.limits.maxReadResultBytes) denied();
							this.rendered.set(exec, encoded);
							return item;
						});
					},
					output: {
						schema: {},
						render: (_args, item) => [{
							type: "text",
							text: JSON.stringify(item)
						}]
					},
					finalizeContent: (exec, result) => {
						const denial = [{
							type: "text",
							text: "Task memory result unavailable."
						}];
						const withheld = Buffer.byteLength(JSON.stringify(denial), "utf8") <= this.limits.maxResultBytes ? denial : [];
						try {
							this.authority();
							const expected = this.rendered.get(exec);
							if (exec.agent !== this.agent || result.additionalContexts?.length || Buffer.byteLength(JSON.stringify(result.content), "utf8") > this.limits.maxResultBytes) return withheld;
							if (!result.isError && (expected === void 0 || JSON.stringify(result.value) !== expected)) return withheld;
							if (!result.isError && JSON.stringify(result.content) !== JSON.stringify([{
								type: "text",
								text: expected
							}])) return withheld;
							return;
						} catch {
							return withheld;
						}
					}
				}));
				this.agent.ctx.on("tools/post-execute", async (exec, result, next) => {
					const decision = await next();
					if (exec.name !== read.name) return decision;
					try {
						this.authority();
						if (decision.additionalContexts?.length || result.additionalContexts?.length) denied();
						if (decision.kind === "accept" && (Object.hasOwn(decision, "value") || decision.content !== void 0 && Buffer.byteLength(JSON.stringify(decision.content), "utf8") > this.limits.maxResultBytes)) denied();
						return decision;
					} catch {
						return {
							kind: "block",
							feedback: [{
								type: "text",
								text: "Task memory result unavailable."
							}]
						};
					}
				});
			}
			this.agent.ctx.on("agent/request", async ({ signal }, next) => {
				signal.throwIfAborted();
				this.authority();
				const route = await next();
				signal.throwIfAborted();
				this.authority();
				return route;
			});
			this.agent.ctx.tools.guard((exec) => this.member.mode === "reviewer" && [
				"durable_agent_read_memory",
				"durable_memory_read",
				"durable_agent_submit_candidate"
			].includes(exec.name) ? "This review assignment has no memory permission." : void 0);
			this.agent.ctx.tools.guard((exec) => exec.name === "durable_agent_read_memory" && exec.parent !== void 0 ? "Task memory is available only through a top-level native call." : void 0);
			if (this.member.mode === "reviewer") {
				if (this.reviewInstaller === void 0) denied();
				await this.operation(async () => this.reviewInstaller({
					ctx: this.ctx,
					team: this.teamOwner,
					agent: this.agent,
					root: this.root,
					execution: this.execution,
					configuration: this.configuration,
					assertCurrent: () => this.authority(true),
					assertActive: () => this.authority(),
					revoke: () => {
						this.close().catch(() => void 0);
					},
					track: (run) => this.operation(run),
					own: (dispose) => {
						if (this.phase !== "open") {
							this.dispose(dispose);
							denied();
						}
						this.disposers.push(dispose);
					}
				}));
				this.authority(true);
			}
		} catch {
			await this.close();
			denied();
		}
	}
	dispose(dispose) {
		try {
			const result = dispose();
			if (result !== void 0) {
				this.cleanupFailed = true;
				const observed = Promise.resolve(result);
				this.lateDisposals.add(observed);
				observed.finally(() => this.lateDisposals.delete(observed)).catch(() => void 0);
			}
		} catch {
			this.cleanupFailed = true;
		}
	}
	close() {
		if (this.cleanup !== void 0) return this.cleanup;
		this.phase = "closing";
		this.cleanup = Promise.resolve().then(async () => {
			while (this.pending.size) await Promise.allSettled([...this.pending]);
			while (this.lateDisposals.size) await Promise.allSettled([...this.lateDisposals]);
			if (this.ref !== void 0) await this.service.release(this.ref);
			if (this.cleanupFailed) denied();
			this.releaseOwner();
			this.phase = "closed";
			this.onClosed?.(this);
		}).catch(() => {
			this.phase = "failed";
			denied();
		});
		this.cleanup.catch(() => void 0);
		try {
			this.agent.cancel({
				kind: "hook",
				reason: "task memory binding closed"
			});
		} catch {
			this.cleanupFailed = true;
		}
		for (const dispose of this.disposers.splice(0).reverse()) this.dispose(dispose);
		return this.cleanup;
	}
};
/**
* Install exact task bindings and Agent-owned guards through the plugin scope.
* @param ctx Selected current Host context.
* @param config Explicit normalized topology/member policy.
* @param reviewInstaller Optional trusted reviewer installer; never used by ordinary tasks.
*/
async function installExecutionBindings(ctx, input, reviewInstaller) {
	const config = freeze(structuredClone(input));
	if (Object.keys(config).sort().join(",") !== "dedicatedProvider,limits,members,singleHostWorkspace,workspace" || config.dedicatedProvider !== true || config.singleHostWorkspace !== true || typeof config.workspace !== "string" || !Array.isArray(config.members) || Buffer.byteLength(JSON.stringify(config), "utf8") > 65536 || Object.keys(config.limits).sort().join(",") !== "maxBodyBytes,maxReadCalls,maxReadResultBytes,maxResultBytes,maxSelectedItems") denied();
	for (const value of Object.values(config.limits)) if (!Number.isSafeInteger(value) || value < 1) denied();
	if (config.limits.maxBodyBytes > 65536 || config.limits.maxResultBytes > 65536 || config.limits.maxResultBytes < 2 || config.limits.maxReadCalls > 32 || config.limits.maxReadResultBytes > 262144 || config.limits.maxSelectedItems > 32) denied();
	const team = resolveExecutionTeam(ctx);
	const workspace = await realpath(config.workspace);
	if (resolveExecutionTeam(ctx) !== team) denied();
	const limits = Object.freeze(structuredClone(config.limits));
	const members = freeze(structuredClone(config.members));
	const declarationKeys = [
		"name",
		"description",
		"prompt",
		"context",
		"provider",
		"model",
		"scope"
	];
	if (members.length > 32 || members.some((member) => !record(member.declaration) || Reflect.ownKeys(member.declaration).some((key) => typeof key !== "string" || ![...declarationKeys, "reasoningEffort"].includes(key)) || declarationKeys.some((key) => !Object.hasOwn(member.declaration, key)))) denied();
	const names = members.map((member) => member.declaration.name);
	if (new Set(names).size !== names.length || members.some((member) => member.declaration.context !== "fresh" || Object.keys(member).sort().join(",") !== "declaration,mode" || member.declaration.scope !== "workspace" || !["task", "reviewer"].includes(member.mode))) denied();
	const configuration = freeze({
		dedicatedProvider: true,
		singleHostWorkspace: true,
		workspace,
		members: structuredClone(members),
		limits
	});
	const bindings = /* @__PURE__ */ new Map();
	ctx.on("agent/created", async ({ agent }) => {
		if (resolveExecutionTeam(ctx) !== team) denied();
		const execution = team.executionFor(agent);
		if (execution === void 0) return;
		assertExecutionSnapshot(execution);
		const member = members.find((member) => member.declaration.name === execution.memberName);
		if (member === void 0) denied();
		const binding = new Binding(ctx, agent, execution, team, registered(ctx), workspace, member, limits, configuration, reviewInstaller, (closed) => {
			if (bindings.get(agent) === closed) bindings.delete(agent);
		});
		bindings.set(agent, binding);
		await binding.install();
	});
	ctx.on("subagent/closing-child", async (agent) => {
		await bindings.get(agent)?.close();
	});
	ctx.effect(() => async () => {
		if ((await Promise.allSettled([...bindings.values()].map((binding) => binding.close()))).some((result) => result.status === "rejected")) denied();
	}, "taskMemory.closeAll()");
}
//#endregion
//#region ../../packages/util/brand/src/index.ts
/**
* Apply a compile-time string brand without changing the value.
* @param value - string admitted by the domain that owns the target brand.
* @returns the same string with the requested compile-time brand.
*/
function brandString(value) {
	return value;
}
//#endregion
//#region lib/types/execution-review.js
/** Optional trusted reviewer input for the additive execution composition; GAT Detail Design §§9–10. */
const MAX_PACKET = 65536;
const MAX_PACKET_CALLS = 16;
const MAX_REF = 65536;
const MAX_VALIDATION_READS = 96;
const MAX_VALIDATION_BYTES = 262144;
const MAX_EVIDENCE_CALLS = 32;
const MAX_EVIDENCE_TOTAL = 262144;
const MAX_RATIONALE_CALLS = 16;
const MAX_RATIONALE_ATTEMPTS = 32;
const MAX_RATIONALE_TOTAL = 65536;
const HASH = /^[a-f0-9]{64}$/u;
const utf8 = new TextDecoder("utf-8", { fatal: true });
function deny() {
	throw new Error("REVIEW_BINDING_UNAVAILABLE");
}
function hash(bytes) {
	return createHash("sha256").update(bytes).digest("hex");
}
function bytes(value) {
	return Buffer.byteLength(JSON.stringify(value), "utf8");
}
function exact(value, keys) {
	if (!value || typeof value !== "object" || Array.isArray(value) || Reflect.ownKeys(value).length !== keys.length || keys.some((key) => !Object.hasOwn(value, key))) deny();
	return value;
}
function args(value, keys) {
	const result = exact(value, keys);
	if (keys.some((key) => typeof result[key] !== "string" || !result[key].length || Buffer.byteLength(result[key], "utf8") > 4096)) deny();
	return result;
}
function selection(scope) {
	const matches = scope.execution.brief.inputs.filter((item) => item.reference.startsWith("review-packet:"));
	if (matches.length !== 1) deny();
	const input = matches[0];
	const revision = input.revision;
	if (typeof revision !== "string" || !revision.length || revision.length > 128 || revision.trim() !== revision || revision.includes("\0") || !/^review-packet:[a-z0-9][a-z0-9-]{0,127}$/u.test(input.reference)) deny();
	return Object.freeze({
		reference: input.reference,
		revision
	});
}
function reviewer(scope) {
	const e = scope.execution;
	return Object.freeze({
		rootSessionId: scope.root.id,
		executionId: e.id,
		sessionId: scope.agent.id,
		memberId: String(e.memberId),
		generation: e.generation,
		taskId: e.taskId,
		taskRevision: e.taskRevision,
		configurationSha256: hash(JSON.stringify(scope.configuration))
	});
}
function equal(a, b) {
	return JSON.stringify(a) === JSON.stringify(b);
}
function verifyLimits(l) {
	const caps = {
		maxPacketValidationReads: MAX_VALIDATION_READS,
		maxPacketValidationBytes: MAX_VALIDATION_BYTES,
		maxEvidenceCalls: MAX_EVIDENCE_CALLS,
		maxEvidenceBytes: MAX_REF,
		maxEvidenceTotalBytes: MAX_EVIDENCE_TOTAL,
		maxRationaleCalls: MAX_RATIONALE_CALLS,
		maxRationaleAttempts: MAX_RATIONALE_ATTEMPTS,
		maxRationaleTotalBytes: MAX_RATIONALE_TOTAL
	};
	exact(l, Object.keys(caps));
	for (const [key, cap] of Object.entries(caps)) {
		const value = l[key];
		if (!Number.isSafeInteger(value) || value < 1 || value > cap) deny();
	}
	return Object.freeze(structuredClone(l));
}
const objectSchema = (properties, required) => ({
	type: "object",
	properties,
	required,
	additionalProperties: false
});
const textSchema = {
	type: "string",
	minLength: 1,
	maxLength: 4096
};
const unavailable = [{
	type: "text",
	text: "Review result unavailable."
}];
function registeredPort(ctx) {
	const scoped = ctx.get("gatDurableReviewInput");
	if (!scoped || typeof scoped !== "object") deny();
	const owner = Reflect.get(scoped, symbols.original) ?? scoped;
	if (!owner || typeof owner !== "object" || typeof Reflect.get(owner, "resolve") !== "function") deny();
	return owner;
}
/** Resolve the optional service only when a reviewer execution is created. */
function resolveReviewInstaller(ctx) {
	return async (scope) => {
		const port = registeredPort(ctx);
		const currentPort = () => registeredPort(ctx);
		const resolver = port.resolve;
		let cut = false;
		const cutoff = () => {
			if (!cut) {
				cut = true;
				scope.revoke();
			}
		};
		const ownerOf = (value) => value && typeof value === "object" ? Reflect.get(value, symbols.original) ?? value : value;
		const observePort = scope.ctx.on("internal/service", (name, value) => {
			if (name === "gatDurableReviewInput" && ownerOf(value) !== port) cutoff();
		});
		scope.own(() => {
			observePort();
		});
		const current = () => {
			try {
				scope.assertCurrent();
				if (cut || currentPort() !== port || port.resolve !== resolver) deny();
			} catch {
				cutoff();
				deny();
			}
		};
		current();
		const selected = selection(scope), assignment = reviewer(scope);
		const resolved = await scope.track(() => resolver.call(port, {
			selection: selected,
			reviewer: assignment
		}));
		current();
		if (resolved === void 0 || !equal(resolved.selection, selected) || !equal(resolved.reviewer, assignment)) deny();
		if (resolved.candidate.memberId === assignment.memberId || resolved.candidate.sessionId === assignment.sessionId || resolved.candidate.rootSessionId !== assignment.rootSessionId || resolved.candidate.configurationSha256 !== assignment.configurationSha256 || !HASH.test(resolved.candidate.candidateSha256)) deny();
		const candidate = Object.freeze(structuredClone(resolved.candidate));
		if (typeof resolved.assertCurrent !== "function" || typeof resolved.subscribeRevocation !== "function" || typeof resolved.readRef !== "function" || typeof resolved.verifyReceipt !== "function" || typeof resolved.audit !== "function") deny();
		const callbacks = {
			assertCurrent: resolved.assertCurrent,
			subscribeRevocation: resolved.subscribeRevocation,
			readRef: resolved.readRef,
			verifyReceipt: resolved.verifyReceipt,
			audit: resolved.audit
		};
		const authority = (active = false) => {
			try {
				current();
				if (active) scope.assertActive();
				if (!equal(resolved.selection, selected) || !equal(resolved.reviewer, assignment) || !equal(resolved.candidate, candidate) || resolved.assertCurrent !== callbacks.assertCurrent || resolved.subscribeRevocation !== callbacks.subscribeRevocation || resolved.readRef !== callbacks.readRef || resolved.verifyReceipt !== callbacks.verifyReceipt || resolved.audit !== callbacks.audit) deny();
				const assertion = callbacks.assertCurrent.call(resolved);
				if (assertion !== void 0) {
					if (assertion && typeof assertion === "object" && "then" in assertion) Promise.resolve(assertion).catch(() => void 0);
					deny();
				}
				const stored = scope.team.getExecution.call(scope.team, scope.root, brandString(candidate.executionId));
				if (stored.sessionId !== candidate.sessionId || String(stored.memberId) !== candidate.memberId || stored.generation !== candidate.generation || stored.taskId !== candidate.taskId || stored.taskRevision !== candidate.taskRevision || stored.result === void 0 || hash(stored.result) !== candidate.candidateSha256) deny();
				current();
				if (active) scope.assertActive();
			} catch {
				cutoff();
				deny();
			}
		};
		authority();
		let disposeSubscription;
		try {
			disposeSubscription = callbacks.subscribeRevocation.call(resolved, cutoff);
		} catch {
			cutoff();
			deny();
		}
		if (typeof disposeSubscription !== "function") {
			if (disposeSubscription && typeof disposeSubscription === "object" && "then" in disposeSubscription) scope.track(async () => {
				const late = await Promise.resolve(disposeSubscription);
				if (typeof late === "function") {
					const result = late.call(resolved);
					if (result !== void 0) await Promise.resolve(result);
				}
			}).catch(() => void 0);
			scope.own(() => {
				deny();
			});
			cutoff();
			deny();
		}
		scope.own(() => disposeSubscription.call(resolved));
		authority();
		scope.agent.ctx.on("agent/request", async ({ signal }, next) => {
			signal.throwIfAborted();
			authority(true);
			const route = await next();
			signal.throwIfAborted();
			authority(true);
			return route;
		});
		const limits = verifyLimits(resolved.limits);
		const contract = normalizeTaskContract(structuredClone(resolved.contract));
		const proposal = normalizeCompletionProposal(structuredClone(resolved.proposal));
		const policy = structuredClone(resolved.policy);
		exact(policy, [
			"testReceipts",
			"requiredTestSuites",
			"knownRisks",
			"rationaleRefs"
		]);
		if (bytes({
			contract,
			proposal,
			policy,
			candidate
		}) > MAX_PACKET || contract.taskId !== candidate.taskId || contract.revision !== candidate.taskRevision || taskContractSha256(contract) !== candidate.contractSha256 || proposal.contractSha256 !== candidate.contractSha256 || proposal.workerId !== candidate.memberId || proposal.attemptId !== candidate.attemptId || proposal.taskId !== candidate.taskId) deny();
		let validationReads = 0, validationBytes = 0;
		const read = async (ref, maxBytes, purpose) => {
			authority(purpose !== "packet-validation");
			const raw = await scope.track(() => callbacks.readRef.call(resolved, {
				ref,
				maxBytes,
				purpose
			}));
			authority(purpose !== "packet-validation");
			if (!(raw instanceof Uint8Array) || raw.byteLength > maxBytes) deny();
			return Uint8Array.from(raw);
		};
		const options = {
			attemptId: candidate.attemptId,
			workerId: candidate.memberId,
			reviewerId: assignment.memberId,
			testReceipts: policy.testReceipts,
			requiredTestSuites: policy.requiredTestSuites,
			knownRisks: policy.knownRisks,
			rationaleRefs: policy.rationaleRefs,
			readRef: async (ref) => {
				if (++validationReads > limits.maxPacketValidationReads) deny();
				const allocation = Math.min(MAX_REF, limits.maxPacketValidationBytes - validationBytes);
				if (allocation < 1) deny();
				const raw = await read(ref, allocation, "packet-validation");
				validationBytes += raw.byteLength;
				if (validationBytes > limits.maxPacketValidationBytes) deny();
				return raw;
			},
			verifyReceipt: async (receipt) => {
				authority();
				const verified = await scope.track(() => callbacks.verifyReceipt.call(resolved, receipt));
				authority();
				return verified === true;
			}
		};
		const packet = await scope.track(() => createReviewPacket(contract, proposal, options));
		authority();
		const packetSha256 = reviewPacketSha256(packet);
		if (packet.proposalSha256 !== candidate.proposalSha256 || packet.contractSha256 !== candidate.contractSha256) deny();
		const envelope = Object.freeze({
			selection: selected,
			reviewer: assignment,
			candidate,
			packetSha256,
			packet
		});
		if (bytes(envelope) > MAX_PACKET) deny();
		const evidence = new Map(reviewEvidenceRefs(packet).map((entry) => [entry.ref, entry.sha256]));
		const rationale = new Map(packet.rationaleRefs.map((entry) => [entry.id, entry]));
		let packetCalls = 0, evidenceCalls = 0, evidenceBytes = 0, evidenceReserved = 0, rationaleCalls = 0, rationaleAttempts = 0, rationaleBytes = 0, rationaleReserved = 0;
		const prepared = /* @__PURE__ */ new WeakMap();
		const audit = async (kind, status, ref, requestId, count, rationaleId, reasonSha256) => {
			authority(true);
			await scope.track(() => callbacks.audit.call(resolved, {
				kind,
				status,
				reviewerExecutionId: assignment.executionId,
				candidateExecutionId: candidate.executionId,
				candidateSha256: candidate.candidateSha256,
				packetSha256,
				...ref === void 0 ? {} : { ref },
				...requestId === void 0 ? {} : { requestId },
				...count === void 0 ? {} : { bytes: count },
				...rationaleId === void 0 ? {} : { rationaleId },
				...reasonSha256 === void 0 ? {} : { reasonSha256 }
			}));
			authority(true);
		};
		const safe = (exec, result) => {
			try {
				authority(true);
				if (result.isError) return unavailable;
				if (result.additionalContexts?.length || bytes(result.content) > MAX_PACKET) return unavailable;
				const expected = prepared.get(exec);
				if (expected === void 0 || JSON.stringify(result.value) !== expected || !equal(result.content, [{
					type: "text",
					text: expected
				}])) return unavailable;
				return;
			} catch {
				return unavailable;
			}
		};
		const make = (name, description, parameters, run, keys) => {
			scope.own(scope.agent.ctx.tools.register({
				name,
				description,
				parameters,
				execute: async (raw, exec) => {
					if (exec.agent !== scope.agent || exec.parent !== void 0) deny();
					const a = args(raw, keys);
					authority(true);
					return await scope.track(async () => {
						try {
							const value = await run(a, exec);
							authority(true);
							if (bytes(value) > MAX_PACKET) deny();
							prepared.set(exec, JSON.stringify(value));
							return value;
						} catch (error) {
							if (error instanceof TypeError && name !== "review_get_packet") try {
								await audit(name === "review_read_evidence" ? "evidence" : "rationale", "error", a.ref, String(exec.rootCallId), void 0, a.id, a.reason === void 0 ? void 0 : hash(a.reason));
							} catch {}
							deny();
						}
					});
				},
				output: {
					schema: {},
					render: (_a, value) => [{
						type: "text",
						text: JSON.stringify(value)
					}]
				},
				finalizeContent: (exec, result) => safe(exec, result)
			}));
			scope.agent.ctx.on("tools/post-execute", async (exec, result, next) => {
				const decision = await next();
				if (exec.name !== name || exec.agent !== scope.agent) return decision;
				try {
					authority(true);
					if (result.additionalContexts?.length || decision.additionalContexts?.length || decision.kind === "accept" && (Object.hasOwn(decision, "value") || decision.content !== void 0 && bytes(decision.content) > MAX_PACKET)) deny();
					return decision;
				} catch {
					return {
						kind: "block",
						feedback: unavailable
					};
				}
			});
		};
		const counted = /* @__PURE__ */ new WeakSet();
		scope.agent.ctx.tools.guard((exec) => {
			if (exec.agent !== scope.agent) return void 0;
			if (exec.parent !== void 0 || ![
				"review_get_packet",
				"review_read_evidence",
				"review_request_rationale",
				"team_execution_submit"
			].includes(exec.name)) return "Review tool unavailable.";
			if (exec.name === "review_get_packet" && !counted.has(exec)) {
				counted.add(exec);
				if (++packetCalls > MAX_PACKET_CALLS) return "Packet attempt budget exhausted.";
			}
			if (exec.name === "review_read_evidence" && !counted.has(exec)) {
				counted.add(exec);
				if (++evidenceCalls > limits.maxEvidenceCalls) return "Evidence attempt budget exhausted.";
			}
			if (exec.name === "review_request_rationale" && !counted.has(exec)) {
				counted.add(exec);
				if (++rationaleAttempts > limits.maxRationaleAttempts) return "Rationale attempt budget exhausted.";
			}
			try {
				authority(true);
				return;
			} catch {
				return "Review binding unavailable.";
			}
		});
		make("review_get_packet", "Get the frozen public review packet for this exact assignment.", objectSchema({}, []), async (_a, exec) => {
			await audit("packet", "requested", void 0, String(exec.rootCallId));
			await audit("packet", "prepared", void 0, String(exec.rootCallId), bytes(envelope));
			return envelope;
		}, []);
		make("review_read_evidence", "Read one allowlisted review evidence ref.", objectSchema({ ref: textSchema }, ["ref"]), async (a, exec) => {
			const ref = a.ref;
			if (ref === void 0) deny();
			const digest = evidence.get(ref);
			if (digest === void 0) {
				await audit("evidence", "denied", ref, String(exec.rootCallId));
				deny();
			}
			await audit("evidence", "requested", ref, String(exec.rootCallId));
			const allocation = Math.min(limits.maxEvidenceBytes, limits.maxEvidenceTotalBytes - evidenceBytes - evidenceReserved);
			if (allocation < 1) {
				await audit("evidence", "denied", ref, String(exec.rootCallId));
				deny();
			}
			evidenceReserved += allocation;
			let raw;
			try {
				raw = await readReviewRef({
					ref,
					sha256: digest
				}, (ref) => read(ref, allocation, "evidence"));
			} finally {
				evidenceReserved -= allocation;
			}
			evidenceBytes += raw.byteLength;
			if (evidenceBytes > limits.maxEvidenceTotalBytes) {
				await audit("evidence", "denied", ref, String(exec.rootCallId));
				deny();
			}
			const value = Object.freeze({
				ref,
				sha256: digest,
				content: utf8.decode(raw)
			});
			await audit("evidence", "prepared", ref, String(exec.rootCallId), raw.byteLength);
			return value;
		}, ["ref"]);
		make("review_request_rationale", "Request declared rationale with a specific reason; rationale is not evidence.", objectSchema({
			id: textSchema,
			reason: textSchema
		}, ["id", "reason"]), async (a, exec) => {
			const id = a.id, reason = a.reason;
			if (id === void 0 || reason === void 0) deny();
			if (reason.trim() !== reason || reason.includes("\0")) {
				await audit("rationale", "denied", void 0, String(exec.rootCallId), void 0, id, hash(reason));
				deny();
			}
			const entry = rationale.get(id);
			if (entry === void 0 || rationaleCalls >= limits.maxRationaleCalls) {
				await audit("rationale", "denied", entry?.ref, String(exec.rootCallId), void 0, id, hash(reason));
				deny();
			}
			rationaleCalls++;
			await audit("rationale", "requested", entry.ref, String(exec.rootCallId), void 0, id, hash(reason));
			const allocation = Math.min(MAX_REF, limits.maxRationaleTotalBytes - rationaleBytes - rationaleReserved);
			if (allocation < 1) {
				await audit("rationale", "denied", entry.ref, String(exec.rootCallId), void 0, id, hash(reason));
				deny();
			}
			rationaleReserved += allocation;
			let raw;
			try {
				raw = await readReviewRef(entry, (ref) => read(ref, allocation, "rationale"));
			} finally {
				rationaleReserved -= allocation;
			}
			rationaleBytes += raw.byteLength;
			if (rationaleBytes > limits.maxRationaleTotalBytes) {
				await audit("rationale", "denied", entry.ref, String(exec.rootCallId), void 0, id, hash(reason));
				deny();
			}
			const value = Object.freeze({
				id,
				ref: entry.ref,
				sha256: entry.sha256,
				content: utf8.decode(raw)
			});
			await audit("rationale", "prepared", entry.ref, String(exec.rootCallId), raw.byteLength, id, hash(reason));
			return value;
		}, ["id", "reason"]);
	};
}
//#endregion
//#region lib/types/execution-composition.js
/** Cordis plugin name, separate from the direct-continuable composition. */
const name = "gat-durable-execution";
/** Required selected Host services; the review input service is optional. */
const inject = [
	"agentTeams",
	"agents",
	"tools",
	"durableAgent"
];
/** Loader validation; no topology assertions or limits are defaulted. */
const Config = z.object({
	workspace: z.string().min(1).required(),
	dedicatedProvider: z.const(true).required(),
	singleHostWorkspace: z.const(true).required(),
	members: z.array(z.object({
		mode: z.union(["task", "reviewer"]).required(),
		declaration: z.object({
			name: z.string().min(1).required(),
			description: z.string().required(),
			prompt: z.string().required(),
			context: z.const("fresh").required(),
			scope: z.const("workspace").required(),
			provider: z.string().min(1).required(),
			model: z.string().min(1).required(),
			reasoningEffort: z.string().min(1)
		}).required()
	}).required()).max(32).required(),
	limits: z.object({
		maxBodyBytes: z.number().step(1).min(1).max(65536).required(),
		maxResultBytes: z.number().step(1).min(2).max(65536).required(),
		maxSelectedItems: z.number().step(1).min(1).max(32).required(),
		maxReadCalls: z.number().step(1).min(1).max(32).required(),
		maxReadResultBytes: z.number().step(1).min(1).max(262144).required()
	}).required()
});
/**
* Bind current task executions before first request without adding system memory.
* @param ctx Scope owning binding listeners and physical cleanup.
* @param config Explicit dedicated single-Host policy and member mappings.
*/
async function apply(ctx, config) {
	z.resolve(config, Config, {});
	await installExecutionBindings(ctx, config, resolveReviewInstaller(ctx));
}
//#endregion
export { Config, apply, inject, name };
