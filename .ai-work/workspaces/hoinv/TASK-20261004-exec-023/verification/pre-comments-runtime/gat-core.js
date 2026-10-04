import z from "@deepseek-ai/schemastery";
import { Remote, TypertRemoteService } from "@deepseek-ai/dsh-typert-protocol";
import { inspect } from "node:util";
import { HarnessError, createUserMessage } from "@deepseek-ai/dsh-llm";
import { consumeHumanControl } from "@deepseek-ai/dsh-client-connection";
import { createHash, randomUUID } from "node:crypto";
import { brandString } from "@deepseek-ai/dsh-brand";
import { foldSubagentDescriptor } from "@deepseek-ai/dsh-subagent";
import { z as z$1 } from "zod";
//#region lib/types/error.js
/** Typed Agent Teams failures. */
/** Stable failure raised by the Team domain. */
var TeamError = class extends HarnessError {
	constructor(message, code, options) {
		super(message, code, options);
		this.name = "TeamError";
	}
};
/**
* Render an arbitrary thrown value without replacing the original rejection.
* @param error - caught value used in a diagnostic or durable failure record.
* @returns one bounded single-line description.
*/
function errorMessage(error) {
	if (error instanceof Error) return error.message;
	if (typeof error === "string") return error;
	return inspect(error, {
		breakLength: Infinity,
		compact: true,
		depth: 4
	});
}
//#endregion
//#region lib/types/validation.js
/** Input normalization shared by Team roster and task commands. */
/**
* Normalize one required human-authored string.
* @param value - raw input value.
* @param field - diagnostic field name.
* @param maxLength - maximum normalized character count.
* @returns trimmed non-empty text.
*/
function requiredText(value, field, maxLength) {
	const text = value.trim();
	if (text.length === 0) throw new TeamError(`${field} must be non-empty`, "TEAM_INVALID_ARGUMENT");
	if (text.length > maxLength) throw new TeamError(`${field} exceeds ${maxLength} characters`, "TEAM_INVALID_ARGUMENT");
	return text;
}
/**
* Normalize one workspace-relative path prefix without treating it as a lock.
* @param value - user-authored path prefix.
* @returns normalized slash-separated prefix.
*/
function writeScope(value) {
	const normalized = value.replaceAll("\\", "/").replace(/^\.\//u, "").replace(/\/+$/u, "");
	const segments = normalized.split("/");
	if (normalized.length === 0 || normalized.startsWith("/") || /^[a-z]:/iu.test(normalized) || segments.some((segment) => segment.length === 0 || segment === "." || segment === "..")) throw new TeamError(`invalid workspace-relative write scope ${JSON.stringify(value)}`, "TEAM_INVALID_WRITE_SCOPE");
	return normalized;
}
//#endregion
//#region lib/types/approved-plan-import.js
/** Select and parse the latest HUMAN-approved DSH plan from Lead Session history. */
const MAX_PLAN_MARKDOWN_CHARACTERS = 1e6;
const TASKS_HEADING = /^##[ \t]+Tasks[ \t]*$/u;
const SECTION_ENDING_HEADING = /^#{1,2}(?:[ \t]+|$)/u;
const CHECKLIST_PREFIX = /^[ \t]{0,3}[-+*][ \t]+\[/u;
const VALID_CHECKLIST = /^[ \t]{0,3}[-+*][ \t]+\[[ xX]\][ \t]+.+?[ \t]*$/u;
const TASK_LINE = /^[ \t]{0,3}(?:[-+*][ \t]+\[[ xX]\][ \t]+|[-+*][ \t]+|\d+[.)][ \t]+)(.+?)[ \t]*$/u;
/** Normalize a subject deterministically for plan-import de-duplication only. */
function normalizedTaskSubject(value) {
	return value.normalize("NFKC").trim().replace(/\s+/gu, " ").toLocaleLowerCase("en-US");
}
function invalid$2(message) {
	throw new TeamError(`approved plan import rejected: ${message}`, "TEAM_PLAN_IMPORT_INVALID");
}
/** Check that a result event is the one exact, successful result for a call. */
function isSuccessfulResultForCall(event, callId) {
	if (event.type !== "tool/result") return false;
	const { message } = event.data;
	const block = message.content[0];
	return message.source.kind === "tool" && String(message.source.callId) === callId && block?.type === "tool-result" && String(block.toolCallId) === callId && block.isError === false;
}
/** Identify result events which claim to belong to a given call, including malformed ones. */
function isResultForCall(event, callId) {
	if (event.type !== "tool/result") return false;
	const { message } = event.data;
	return message.source.kind === "tool" && String(message.source.callId) === callId || message.content.some((block) => block.type === "tool-result" && String(block.toolCallId) === callId);
}
/**
* Parse subjects from only the explicit `## Tasks` section of an approved plan.
* Any unrecognized non-blank line inside that section makes the import fail closed.
*/
function parseApprovedPlanTasks(plan) {
	if (plan.length > MAX_PLAN_MARKDOWN_CHARACTERS) invalid$2("plan exceeds import length limit");
	const lines = plan.replace(/\r\n?/gu, "\n").split("\n");
	const start = lines.findIndex((line) => TASKS_HEADING.test(line));
	if (start < 0) invalid$2("missing explicit ## Tasks section");
	const subjects = [];
	for (let index = start + 1; index < lines.length; index += 1) {
		const line = lines[index];
		if (SECTION_ENDING_HEADING.test(line)) break;
		if (/^[ \t]*$/u.test(line)) continue;
		if (CHECKLIST_PREFIX.test(line) && !VALID_CHECKLIST.test(line)) invalid$2(`malformed checklist task line ${index + 1}`);
		const matched = TASK_LINE.exec(line);
		if (matched === null) invalid$2(`malformed task line ${index + 1}`);
		let subject;
		try {
			subject = requiredText(matched[1].normalize("NFKC").replace(/\s+/gu, " "), "task subject", 200);
		} catch {
			invalid$2(`invalid task subject on line ${index + 1}`);
		}
		if (normalizedTaskSubject(subject) === "") invalid$2(`empty task line ${index + 1}`);
		subjects.push(subject);
	}
	if (subjects.length === 0) invalid$2("## Tasks section is empty");
	return subjects;
}
/**
* Select the latest `exit_plan_mode` call from exactly one Lead log and require
* its one matching successful result. Failed, incomplete, and older calls are
* never used as an import source.
*/
function approvedPlanTaskSubjects(events) {
	const callIndex = events.findLastIndex((event) => event.type === "tool/call" && event.data.name === "exit_plan_mode");
	if (callIndex < 0) invalid$2("no exit_plan_mode call exists in the Lead Session");
	const call = events[callIndex];
	const callId = String(call.data.callId);
	const results = events.slice(callIndex + 1).filter((event) => isResultForCall(event, callId));
	if (results.length !== 1 || !isSuccessfulResultForCall(results[0], callId)) invalid$2("latest exit_plan_mode call lacks one matching successful result");
	let parsed;
	try {
		parsed = JSON.parse(call.data.arguments);
	} catch {
		invalid$2("latest exit_plan_mode call has malformed arguments");
	}
	if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed) || typeof parsed.plan !== "string") invalid$2("latest exit_plan_mode call has no markdown plan argument");
	return parseApprovedPlanTasks(parsed.plan);
}
//#endregion
//#region lib/types/authority.js
/** Owns non-transferable Agent-generation leases and legacy plan policy. */
var TeamExecutionAuthority = class {
	journal;
	leases = /* @__PURE__ */ new WeakMap();
	requirePlan = false;
	nextIssuanceGeneration = 1;
	constructor(journal) {
		this.journal = journal;
	}
	/** Configure the additional exact HUMAN plan requirement for governed mode. */
	configure(requirePlan) {
		this.requirePlan = requirePlan;
	}
	/** Bind exactly one host-selected or canonical task-derived authorized mission. */
	bind(agent, membership, request) {
		this.journal.assertCommitted(membership.root);
		this.assertActiveMember(agent, membership);
		const state = this.journal.state(membership.root);
		const mission = state.missions.find((value) => value.id === request.missionId);
		const approval = mission?.approval;
		if (!mission || mission.status !== "approved" || mission.revision !== request.expectedRevision || approval?.approvedRevision !== mission.revision || !approval.eventId || !approval.digest || approval.humanSessionId !== state.id) throw new TeamError("exact mission revision lacks current host-attested HUMAN authorization", "TEAM_MISSION_UNAUTHORIZED");
		if (request.taskId !== void 0) {
			const task = state.tasks.find((value) => value.id === request.taskId);
			if (!task || task.status !== "in_progress" || task.ownerId !== agent.id || task.missionId !== mission.id || !mission.plan.taskIds?.includes(task.id)) throw new TeamError("canonical task mission association is missing or mismatched", "TEAM_TASK_MISSION_REQUIRED");
		}
		this.assertPlan(membership);
		this.leases.set(agent, Object.freeze({
			...request,
			teamId: state.id,
			eventId: approval.eventId,
			digest: approval.digest,
			issuanceGeneration: this.nextIssuanceGeneration++,
			authorizationGeneration: mission.authorizationGeneration ?? 0,
			revocationGeneration: mission.revocationGeneration ?? 0,
			...this.requirePlan ? {
				planRevision: state.planRevision,
				planEventId: state.planApproval.eventId
			} : {}
		}));
	}
	/** Validate one explicit canonical claim without publishing any Agent execution lease. */
	validateClaim(agent, membership, taskId) {
		this.journal.assertCommitted(membership.root);
		this.assertActiveMember(agent, membership);
		const state = this.journal.state(membership.root);
		const task = state.tasks.find((value) => value.id === taskId);
		const mission = state.missions.find((value) => value.id === task?.missionId);
		if (!task || !mission || !mission.plan.taskIds?.includes(task.id) || mission.status !== "approved" || mission.approval?.approvedRevision !== mission.revision || !mission.approval.eventId || !mission.approval.digest || mission.approval.humanSessionId !== state.id) throw new TeamError("canonical claim mission lacks exact HUMAN approval", "TEAM_MISSION_UNAUTHORIZED");
		this.assertPlan(membership);
	}
	/** Admit Lead administration through its explicit host mission scope, or task work through its claimed scope. */
	assertTaskOperation(agent, membership, taskId) {
		const lease = this.leases.get(agent);
		if (membership.role === "lead" && lease?.taskId === void 0) {
			this.assert(agent, membership);
			const task = this.journal.state(membership.root).tasks.find((value) => value.id === taskId);
			if (!task || task.missionId !== lease?.missionId) throw new TeamError("Lead task operation has a different canonical mission", "TEAM_EXECUTION_DENIED");
			return;
		}
		this.assert(agent, membership, taskId);
	}
	/** Derive task admission only from one explicitly selected canonical task. */
	bindTask(agent, membership, taskId) {
		this.journal.assertCommitted(membership.root);
		const state = this.journal.state(membership.root);
		const task = state.tasks.find((value) => value.id === taskId);
		if (!task?.missionId) throw new TeamError("task has no canonical mission association", "TEAM_TASK_MISSION_REQUIRED");
		const mission = state.missions.find((value) => value.id === task.missionId);
		if (!mission) throw new TeamError("task mission is missing", "TEAM_MISSION_UNAUTHORIZED");
		this.bind(agent, membership, {
			missionId: mission.id,
			expectedRevision: mission.revision,
			taskId
		});
	}
	/** Revalidate the exact lease immediately before an effect or model request. */
	assert(agent, membership, taskId) {
		this.journal.assertCommitted(membership.root);
		this.assertActiveMember(agent, membership);
		const state = this.journal.state(membership.root);
		const lease = this.leases.get(agent);
		const mission = state.missions.find((value) => value.id === lease?.missionId);
		if (!lease || lease.teamId !== state.id || !mission || mission.status !== "approved" || lease.expectedRevision !== mission.revision || lease.eventId !== mission.approval?.eventId || lease.digest !== mission.approval?.digest || lease.authorizationGeneration !== (mission.authorizationGeneration ?? 0) || lease.revocationGeneration !== (mission.revocationGeneration ?? 0) || mission.approval.approvedRevision !== mission.revision) throw new TeamError("exact Agent mission lease is absent, stale, closed, or revoked", "TEAM_EXECUTION_DENIED");
		const selectedTask = taskId ?? lease.taskId;
		if (taskId !== void 0 && lease.taskId !== taskId) throw new TeamError("execution lease is bound to a different task", "TEAM_EXECUTION_DENIED");
		if (selectedTask !== void 0) {
			const task = state.tasks.find((value) => value.id === selectedTask);
			if (!task || task.status !== "in_progress" || task.ownerId !== agent.id || task.missionId !== mission.id || !mission.plan.taskIds?.includes(task.id)) throw new TeamError("execution lease canonical task association or owner changed", "TEAM_EXECUTION_DENIED");
		}
		this.assertPlan(membership);
		if (this.requirePlan && (lease.planRevision !== state.planRevision || lease.planEventId !== state.planApproval?.eventId)) throw new TeamError("exact Agent current-plan lease is absent or stale", "TEAM_PLAN_UNAUTHORIZED");
	}
	assertPlan(membership) {
		this.journal.assertCommitted(membership.root);
		const state = this.journal.state(membership.root);
		if (this.requirePlan && (state.planPhase !== "approved" || state.planApproval?.approvedRevision !== state.planRevision || !state.planApproval.eventId || !state.planApproval.digest || state.planApproval.humanSessionId !== state.id)) throw new TeamError("current Team plan lacks exact host-attested HUMAN approval", "TEAM_PLAN_UNAUTHORIZED");
	}
	assertActiveMember(agent, membership) {
		if (membership.role !== "teammate") return;
		if (this.journal.state(membership.root).members.find((value) => value.id === agent.id)?.phase !== "active") throw new TeamError("canonical teammate is not active for execution", "TEAM_EXECUTION_DENIED");
	}
};
//#endregion
//#region lib/types/activity.js
/** One-shot Team change waiters independent of durable state projection. */
/** Owns current Team change waiters and releases each at most once. */
var TeamActivity = class {
	waiters = /* @__PURE__ */ new Map();
	closed = false;
	/**
	* Wait for one later Team-domain or member-status change.
	* @param id - Team whose next edge wakes the caller.
	* @param timeoutMs - bounded wait duration from ten seconds through one hour.
	* @param signal - caller cancellation for this wait only.
	* @returns whether the wait ended by timeout.
	*/
	async wait(id, timeoutMs, signal) {
		if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1e4 || timeoutMs > 36e5) throw new TeamError("timeoutMs must be an integer from 10000 through 3600000", "TEAM_INVALID_TIMEOUT");
		signal.throwIfAborted();
		if (this.closed) return { timedOut: false };
		return { timedOut: !await new Promise((resolve, reject) => {
			let waiters = this.waiters.get(id);
			if (waiters === void 0) {
				waiters = /* @__PURE__ */ new Set();
				this.waiters.set(id, waiters);
			}
			let settled = false;
			const finish = (settle) => {
				/* v8 ignore next -- timeout, abort, and notification may race after one winner removes the others. */
				if (settled) return;
				settled = true;
				clearTimeout(timer);
				signal.removeEventListener("abort", onAbort);
				waiters.delete(waiter);
				if (waiters.size === 0) this.waiters.delete(id);
				settle();
			};
			const onAbort = () => {
				finish(() => {
					const reason = signal.reason;
					reject(reason instanceof Error ? reason : new TeamError(`wait_agent aborted: ${errorMessage(reason)}`, "TEAM_WAIT_ABORTED"));
				});
			};
			const waiter = { resolve: () => {
				finish(() => {
					resolve(true);
				});
			} };
			waiters.add(waiter);
			const timer = setTimeout(() => {
				finish(() => {
					resolve(false);
				});
			}, timeoutMs);
			signal.addEventListener("abort", onAbort, { once: true });
			/* v8 ignore next -- requires an abort in the synchronous gap between the pre-check and listener registration. */
			if (signal.aborted) onAbort();
		}) };
	}
	/**
	* Wake and remove every current waiter for one Team.
	* @param id - Team whose current waiters observe the change.
	*/
	notify(id) {
		const waiters = this.waiters.get(id);
		if (waiters === void 0) return;
		this.waiters.delete(id);
		for (const waiter of waiters) waiter.resolve();
	}
	/** Close admission and wake every current waiter during runtime disposal. */
	close() {
		this.closed = true;
		for (const waiters of this.waiters.values()) for (const waiter of waiters) waiter.resolve();
		this.waiters.clear();
	}
};
//#endregion
//#region lib/types/journal.js
/** Serialized Team transactions over the exact live Lead Session log. */
const AUTHORITY_EVENT_TYPES = new Set([
	"team/member-add-approved",
	"team/member",
	"team/task",
	"team/mission",
	"team/plan-approved"
]);
/** Owns per-Lead transaction order and committed Team event publication. */
var TeamJournal = class {
	ctx;
	onCommit;
	assertAdmission;
	pendingPublication = /* @__PURE__ */ new Set();
	failedPublication = /* @__PURE__ */ new Set();
	tails = /* @__PURE__ */ new Map();
	/**
	* @param ctx - Team service context with the injected Session service.
	* @param onCommit - synchronous notification after the Team event flush succeeds.
	* @param assertAdmission - synchronous runtime withdrawal cutoff for bindings and new publication.
	*/
	constructor(ctx, onCommit, assertAdmission) {
		this.ctx = ctx;
		this.onCommit = onCommit;
		this.assertAdmission = assertAdmission;
	}
	/**
	* Read authoritative Team state for one exact live Lead.
	* @param root - exact live Team Lead.
	* @returns current projected state selected by the Lead Team id.
	*/
	state(root) {
		const projection = this.ctx.sessionProjections.stateOf(root.session, "agentTeam");
		if (projection === void 0) throw new Error("Agent Teams projection is not registered");
		if (projection.failure !== void 0) throw new Error(projection.failure);
		return projection;
	}
	/** Reject memory-only canonical authorization while publication is pending or failed. */
	assertCommitted(root) {
		this.assertAdmission();
		if (this.pendingPublication.has(root.id) || this.failedPublication.has(root.id)) throw new TeamError("canonical Team authority is pending or failed durability publication", "TEAM_AUTHORITY_NOT_DURABLE");
	}
	/**
	* Serialize one Lead's asynchronous mutation operation.
	* @param rootId - Lead Session identity selecting the transaction queue.
	* @param operation - complete read-check-append operation.
	* @returns the operation result.
	*/
	async transact(rootId, operation) {
		const run = (this.tails.get(rootId) ?? Promise.resolve()).then(operation, operation);
		const tail = run.then(() => void 0, () => void 0);
		this.tails.set(rootId, tail);
		try {
			return await run;
		} finally {
			if (this.tails.get(rootId) === tail) this.tails.delete(rootId);
		}
	}
	/**
	* Append and checkpoint one root-owned Team event before publication.
	* @param root - exact live Lead whose Session owns the event.
	* @param type - Team event discriminant.
	* @param data - payload correlated with the event type.
	*/
	async appendAndFlush(root, type, data) {
		await this.appendManyAndFlush(root, [{
			type,
			data
		}]);
	}
	/**
	* Append several already-validated Team events, then checkpoint them in one
	* flush and publish only after that flush succeeds. Callers must make all
	* validation decisions before this method so an invalid batch never appends
	* any prefix.
	*/
	async appendManyAndFlush(root, events) {
		this.assertAdmission();
		const append = root.session.append.bind(root.session);
		const publishesAuthority = events.some((event) => AUTHORITY_EVENT_TYPES.has(event.type));
		if (publishesAuthority) this.pendingPublication.add(root.id);
		try {
			for (const event of events) append(event.type, event.data);
			if (!await this.ctx.sessions.flush(root.session)) throw new TeamError("canonical Team authority flush did not succeed", "TEAM_AUTHORITY_NOT_DURABLE");
			this.onCommit(root);
		} catch (error) {
			if (publishesAuthority) this.failedPublication.add(root.id);
			throw error;
		} finally {
			if (publishesAuthority) this.pendingPublication.delete(root.id);
		}
	}
};
//#endregion
//#region lib/types/binding-deadline.js
/** A single total cleanup budget. Every callback is invoked, even after expiry. */
var BindingDeadline = class {
	signal;
	controller = new AbortController();
	expired;
	timer;
	constructor(timeoutMs) {
		if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1) throw new TeamError("invalid lifecycle deadline", "TEAM_INVALID_CONFIG");
		this.signal = this.controller.signal;
		this.expired = new Promise((_, reject) => {
			this.timer = setTimeout(() => {
				const error = new TeamError("member binding cleanup deadline exceeded", "TEAM_DISPOSAL_TIMEOUT");
				this.controller.abort(error);
				reject(error);
			}, timeoutMs);
		});
		this.expired.catch(() => void 0);
	}
	async run(operation) {
		const pending = Promise.resolve().then(() => operation(this.signal));
		pending.catch(() => void 0);
		return await Promise.race([pending, this.expired]);
	}
	finish() {
		clearTimeout(this.timer);
	}
};
/** Cancellation closes admission promptly; late successful acquisitions still have an owner. */
function acquireBindingResource(operation, signal, late) {
	signal.throwIfAborted();
	return new Promise((resolve, reject) => {
		let settled = false;
		const onAbort = () => {
			if (settled) return;
			settled = true;
			signal.removeEventListener("abort", onAbort);
			reject(signal.reason);
		};
		signal.addEventListener("abort", onAbort, { once: true });
		Promise.resolve().then(operation).then((resource) => {
			if (signal.aborted && !settled) onAbort();
			if (settled) return Promise.resolve().then(() => late(resource));
			settled = true;
			signal.removeEventListener("abort", onAbort);
			resolve(resource);
		}, (error) => {
			if (!settled) {
				settled = true;
				signal.removeEventListener("abort", onAbort);
				reject(error);
			}
		}).catch(() => void 0);
	});
}
//#endregion
//#region lib/types/lifecycle.js
/** Shared admission cutoff and bounded settlement for the Team runtime. */
/** Owns the single Team runtime cancellation fact and disposal timeout. */
var TeamRuntimeLifecycle = class {
	disposalTimeoutMs;
	controller = new AbortController();
	mutations = /* @__PURE__ */ new Set();
	/**
	* @param disposalTimeoutMs - maximum wait for one disposal settlement operation.
	*/
	constructor(disposalTimeoutMs) {
		this.disposalTimeoutMs = disposalTimeoutMs;
	}
	/** Signal aborted exactly when Team runtime admission closes. */
	get signal() {
		return this.controller.signal;
	}
	/** Whether Team runtime admission is closed. */
	get disposed() {
		return this.signal.aborted;
	}
	/** The exact cancellation reason used to distinguish expected disposal rejection. */
	get reason() {
		return this.signal.reason;
	}
	/** Whether a rejection is the runtime cancellation, directly or through an Error cause chain. */
	isCancellation(reason) {
		const seen = /* @__PURE__ */ new Set();
		let current = reason;
		while (!seen.has(current)) {
			if (this.disposed && current === this.reason) return true;
			if (this.disposed && current instanceof TeamError && current.code === "TEAM_DISPOSED") return true;
			if (!(current instanceof Error)) return false;
			seen.add(current);
			current = current.cause;
		}
		return false;
	}
	/** Create one fresh total cleanup deadline independent of a cancelled execution signal.
	* @returns the configured cleanup budget, owned and finished by its caller.
	*/
	cleanupDeadline() {
		return new BindingDeadline(this.disposalTimeoutMs);
	}
	/** Reject admission synchronously after Team withdrawal begins. */
	assertOpen() {
		if (this.disposed) throw this.reason;
	}
	/** Close Team runtime admission and cancel admitted interruptible work. */
	close() {
		this.controller.abort(new TeamError("Agent Teams service disposed", "TEAM_DISPOSED"));
	}
	/**
	* Admit one journal mutation atomically with the lifecycle cutoff.
	* @param start - deferred journal mutation to start after admission.
	* @returns the admitted mutation operation.
	*/
	admitMutation(start) {
		if (this.disposed) throw this.reason;
		const operation = start();
		this.mutations.add(operation);
		operation.then(() => {
			this.mutations.delete(operation);
		}, () => {
			this.mutations.delete(operation);
		});
		return operation;
	}
	/**
	* Snapshot mutations admitted before the lifecycle cutoff.
	* @returns mutations currently awaiting physical settlement.
	*/
	pendingMutations() {
		return [...this.mutations];
	}
	/**
	* Report the bounded mutation-drain timeout but retain projection lifetime until physical settlement.
	* @param failures - aggregate destination for unexpected rejection or timeout.
	*/
	async settleMutations(failures) {
		const operations = this.pendingMutations();
		if (operations.length === 0) return;
		const settlement = Promise.allSettled(operations);
		let outcomes;
		try {
			outcomes = await this.withTimeout(settlement);
		} catch (error) {
			failures.push(error);
			outcomes = await settlement;
		}
		this.retainFailures(outcomes, failures);
	}
	/**
	* Await admitted operations and retain failures other than runtime cancellation.
	* @param operations - admitted operations captured after the admission cutoff.
	* @param failures - aggregate destination for unexpected rejection or timeout.
	*/
	async settle(operations, failures) {
		if (operations.length === 0) return;
		try {
			const outcomes = await this.withTimeout(Promise.allSettled(operations));
			this.retainFailures(outcomes, failures);
		} catch (error) {
			failures.push(error);
		}
	}
	/** Retain every non-cancellation rejection from one completed settlement. */
	retainFailures(outcomes, failures) {
		for (const outcome of outcomes) if (outcome.status === "rejected" && !this.isCancellation(outcome.reason)) failures.push(outcome.reason);
	}
	/**
	* Bound one runtime settlement operation.
	* @param operation - settlement that may otherwise block HMR or process shutdown.
	* @returns the operation result.
	*/
	async withTimeout(operation) {
		let timer;
		const timeout = new Promise((_resolve, reject) => {
			timer = setTimeout(() => {
				reject(new TeamError(`Agent Teams runtime disposal exceeded ${this.disposalTimeoutMs}ms`, "TEAM_DISPOSAL_TIMEOUT"));
			}, this.disposalTimeoutMs);
		});
		try {
			return await Promise.race([operation, timeout]);
		} finally {
			clearTimeout(timer);
		}
	}
};
//#endregion
//#region lib/types/persisted.js
/** Short-lived read-handle access to persisted Team member Sessions. */
/**
* Read one stored session's header and complete event log through a
* short-lived read handle, closing the handle before returning.
* @param persistence - the durable session store.
* @param id - the stored session to read.
* @param signal - cancellation observed by open and read.
* @returns the stored header and every committed event.
*/
async function readPersistedSession(persistence, id, signal) {
	const handle = await persistence.open(id, "read", { signal });
	try {
		const { events } = await handle.read(0, void 0, { signal });
		return {
			header: handle.header,
			inheritedEventCount: handle.inheritedEventCount,
			events
		};
	} finally {
		await handle.close();
	}
}
//#endregion
//#region lib/types/types.js
/** Public Agent Teams identities, durable records, and service request values. */
/**
* Brand one root Session identity as its implicit Team identity.
* @param id - Root Session identity.
* @returns the same string branded as a Team identity.
*/
function TeamId(id) {
	return id;
}
/** Brand a validated Team-local mission id. */
function TeamMissionId(id) {
	return id;
}
/**
* Brand a validated task id.
* @param id - Team-local task identity.
* @returns the same string branded as a Team task identity.
*/
function TeamTaskId(id) {
	return id;
}
/**
* Brand a generated peer-message id.
* @param id - Durable mailbox message identity.
* @returns the same string branded as a Team message identity.
*/
function TeamMessageId(id) {
	return id;
}
//#endregion
//#region lib/types/attachments.js
/** Frozen required-attachment validation, canonical value detachment and digest integrity. */
const ATTACHMENT_LIMITS = Object.freeze({
	records: 8,
	recordBytes: 65536,
	aggregateBytes: 262144,
	depth: 16,
	nodes: 4096,
	stringBytes: 16384,
	binderId: 64
});
function invalid$1() {
	throw new TeamError("invalid or oversized required member attachment", "TEAM_INVALID_ATTACHMENT");
}
function validString(value) {
	if (Buffer.byteLength(value, "utf8") > ATTACHMENT_LIMITS.stringBytes) invalid$1();
	for (let i = 0; i < value.length; i++) {
		const c = value.charCodeAt(i);
		if (c >= 55296 && c <= 56319) {
			const next = value.charCodeAt(++i);
			if (!(next >= 56320 && next <= 57343)) invalid$1();
		} else if (c >= 56320 && c <= 57343) invalid$1();
	}
	return value;
}
/** Read only own data descriptors; never invoke a caller's accessor or toJSON. */
function detachJson(value, depth = 0, budget = { nodes: 0 }, ancestors = /* @__PURE__ */ new Set()) {
	if (depth > ATTACHMENT_LIMITS.depth || ++budget.nodes > ATTACHMENT_LIMITS.nodes) invalid$1();
	if (value === null || typeof value === "boolean") return value;
	if (typeof value === "string") return validString(value);
	if (typeof value === "number") {
		if (!Number.isFinite(value)) invalid$1();
		return Object.is(value, -0) ? 0 : value;
	}
	if (typeof value !== "object" || ancestors.has(value)) invalid$1();
	const prototype = Object.getPrototypeOf(value);
	if (Array.isArray(value) ? prototype !== Array.prototype : prototype !== Object.prototype && prototype !== null) invalid$1();
	ancestors.add(value);
	try {
		const descriptors = Object.getOwnPropertyDescriptors(value);
		if (Object.getOwnPropertySymbols(value).length > 0) invalid$1();
		if (Array.isArray(value)) {
			const keys = Object.keys(descriptors);
			if (keys.length !== value.length + 1 || !keys.includes("length")) invalid$1();
			const result = [];
			for (let i = 0; i < value.length; i++) {
				const entry = descriptors[String(i)];
				if (!entry || !("value" in entry) || !entry.enumerable) invalid$1();
				result.push(detachJson(entry.value, depth + 1, budget, ancestors));
			}
			return Object.freeze(result);
		}
		const result = {};
		for (const key of Object.keys(descriptors).sort()) {
			validString(key);
			const entry = descriptors[key];
			if (!("value" in entry) || !entry.enumerable) invalid$1();
			Object.defineProperty(result, key, {
				value: detachJson(entry.value, depth + 1, budget, ancestors),
				enumerable: true
			});
		}
		return Object.freeze(result);
	} finally {
		ancestors.delete(value);
	}
}
function encode(value) {
	if (value === null || typeof value !== "object") return JSON.stringify(value);
	if (Array.isArray(value)) return `[${value.map(encode).join(",")}]`;
	return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${encode(value[key])}`).join(",")}}`;
}
/** RFC 8785 UTF-16 key order and ECMAScript number/string rendering. */
function canonicalJson(value) {
	return encode(detachJson(value));
}
function payloadSha256(value) {
	return createHash("sha256").update(canonicalJson(value), "utf8").digest("hex");
}
function envelope(value, replay, budget) {
	const detached = detachJson(value, 0, budget);
	if (detached === null || typeof detached !== "object" || Array.isArray(detached)) invalid$1();
	const expected = replay ? [
		"binderId",
		"payload",
		"payloadSha256",
		"protocolVersion",
		"required"
	] : [
		"binderId",
		"payload",
		"protocolVersion",
		"required"
	];
	if (Object.keys(detached).join("|") !== expected.join("|")) invalid$1();
	const { binderId, protocolVersion, required, payload } = detached;
	if (typeof binderId !== "string" || binderId.length > ATTACHMENT_LIMITS.binderId || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(binderId)) invalid$1();
	if (typeof protocolVersion !== "number" || !Number.isSafeInteger(protocolVersion) || protocolVersion < 1 || required !== true) invalid$1();
	if (Buffer.byteLength(encode(detached), "utf8") > ATTACHMENT_LIMITS.recordBytes) invalid$1();
	if (replay && (typeof detached.payloadSha256 !== "string" || !/^[a-f0-9]{64}$/u.test(detached.payloadSha256) || detached.payloadSha256 !== payloadSha256(payload))) invalid$1();
	return detached;
}
function validateList(values, replay) {
	if (!Array.isArray(values) || Object.getPrototypeOf(values) !== Array.prototype || values.length > ATTACHMENT_LIMITS.records) invalid$1();
	const descriptors = Object.getOwnPropertyDescriptors(values);
	if (Reflect.ownKeys(descriptors).length !== values.length + 1) invalid$1();
	const budget = { nodes: 0 };
	const names = /* @__PURE__ */ new Set();
	const result = Array.from({ length: values.length }, (_, index) => {
		const descriptor = descriptors[String(index)];
		if (!descriptor || !("value" in descriptor) || !descriptor.enumerable) invalid$1();
		const record = envelope(descriptor.value, replay, budget);
		if (names.has(record.binderId)) invalid$1();
		names.add(record.binderId);
		return record;
	});
	if (Buffer.byteLength(`[${result.map((value) => encode(value)).join(",")}]`, "utf8") > ATTACHMENT_LIMITS.aggregateBytes) invalid$1();
	return Object.freeze(result);
}
function validateAttachmentRequests(value) {
	return validateList(value, false);
}
function validateAttachmentRecords(value) {
	return validateList(value, true);
}
function attachmentRecord(request, preparedPayload) {
	const payload = detachJson(preparedPayload);
	return validateAttachmentRecords([{
		binderId: request.binderId,
		protocolVersion: request.protocolVersion,
		required: true,
		payload,
		payloadSha256: payloadSha256(payload)
	}])[0];
}
//#endregion
//#region lib/types/roster.js
/** Team membership, continuable-child provisioning, and roster-owned teardown. */
const MEMBER_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/u;
/**
* Resolve one active Team member by model-facing name, including the Lead pseudo-row.
* @param root - exact live Team Lead.
* @param state - current Team state.
* @param rawName - candidate member name.
* @returns resolved durable id and normalized name.
*/
function resolveActiveMember(root, state, rawName) {
	const name = rawName.trim();
	if (name === "lead") return {
		id: root.id,
		name
	};
	const member = state.members.find((candidate) => candidate.name === name);
	if (member?.attachments.length) throw new TeamError("required member bindings unavailable", "TEAM_BINDING_UNAVAILABLE");
	if (member === void 0 || member.phase !== "active") throw new TeamError(`active teammate "${name}" not found`, "TEAM_MEMBER_NOT_FOUND");
	return {
		id: member.id,
		name
	};
}
/** Owns Team identities and the lifecycle of rostered continuable children. */
var TeamRoster = class {
	ctx;
	journal;
	lifecycle;
	maxMembers;
	assertExecution;
	consumeMemberAdd;
	reservations = /* @__PURE__ */ new Map();
	releasedReservations = /* @__PURE__ */ new WeakSet();
	inFlightCreations = /* @__PURE__ */ new Set();
	inFlightCleanups = /* @__PURE__ */ new Set();
	cleanupFailures = [];
	/**
	* @param ctx - Team service context with Agent, Session, persistence, and subagent services.
	* @param journal - authoritative Lead-log transaction owner.
	* @param lifecycle - shared Team runtime admission cutoff.
	* @param maxMembers - maximum immutable roster entries per Team.
	*/
	constructor(ctx, journal, lifecycle, maxMembers, assertExecution, consumeMemberAdd) {
		this.ctx = ctx;
		this.journal = journal;
		this.lifecycle = lifecycle;
		this.maxMembers = maxMembers;
		this.assertExecution = assertExecution;
		this.consumeMemberAdd = consumeMemberAdd;
	}
	/**
	* Resolve one exact live Agent's Team role.
	* @param agent - exact live Agent used as the authority credential.
	* @returns its root, Team identity, role, and model-facing name.
	*/
	membership(agent) {
		const membership = this.tryMembership(agent);
		if (membership === void 0) throw new TeamError(`agent "${agent.id}" is not a member of an active Agent Team`, "TEAM_NOT_MEMBER");
		return membership;
	}
	/**
	* Resolve a caller without throwing for scoped installation and lifecycle observers.
	* @param agent - candidate exact live Agent.
	* @returns Team membership, or undefined for non-Team subagents and stale identities.
	*/
	tryMembership(agent) {
		if (this.ctx.agents.get(agent.id) !== agent) return void 0;
		try {
			const parentId = agent.session.header.parentSession;
			if (parentId !== void 0) {
				const root = this.ctx.agents.get(parentId);
				if (root !== void 0) {
					const member = this.journal.state(root).members.find((candidate) => candidate.id === agent.id);
					if (member?.attachments.length) return void 0;
					if (member?.phase === "active" || member?.phase === "provisioning") return {
						root,
						id: TeamId(root.id),
						role: "teammate",
						name: member.name
					};
					if (this.subagentDescriptor(agent)) return void 0;
					return {
						root: agent,
						id: TeamId(agent.id),
						role: "lead",
						name: "lead"
					};
				}
			}
			if (this.subagentDescriptor(agent)) return void 0;
			return {
				root: agent,
				id: TeamId(agent.id),
				role: "lead",
				name: "lead"
			};
		} catch {
			return;
		}
	}
	/**
	* List the runtime-enriched roster visible to one Team member.
	* @param membership - exact caller membership resolved by this roster.
	* @returns Lead and teammate rows in creation order.
	*/
	list(membership) {
		const { root } = membership;
		const state = this.journal.state(root);
		const result = [{
			id: root.id,
			name: "lead",
			role: "lead",
			status: root.status,
			...root.options.model === void 0 ? {} : { model: root.options.model },
			diagnostics: []
		}];
		for (const member of state.members) {
			const live = this.ctx.agents.get(member.id);
			const model = live?.options.model ?? member.model;
			result.push({
				id: member.id,
				name: member.name,
				role: "teammate",
				status: member.phase === "failed" ? "failed" : member.phase === "provisioning" ? "provisioning" : member.attachments.length > 0 ? "inactive" : live?.status ?? "inactive",
				description: member.description,
				provider: member.provider,
				context: member.context,
				...model === void 0 ? {} : { model },
				diagnostics: member.error === void 0 ? [] : [member.error],
				...member.attachments.length === 0 ? {} : { bindings: member.attachments.map((record) => ({
					binderId: record.binderId,
					protocolVersion: record.protocolVersion,
					readiness: member.phase === "failed" ? "failed" : "unavailable"
				})) }
			});
		}
		return result;
	}
	/**
	* Create one named, continuable direct child of the Team Lead.
	* @param caller - exact live Lead Agent.
	* @param request - immutable name, description, prompt, context mode, provider, and cancellation.
	* @returns the active roster row.
	*/
	async spawn(caller, request) {
		if (this.lifecycle.disposed) throw new TeamError("Agent Teams service is disposing", "TEAM_DISPOSED");
		const operation = this.spawnAdmitted(caller, request);
		this.inFlightCreations.add(operation);
		try {
			return await operation;
		} finally {
			this.inFlightCreations.delete(operation);
		}
	}
	/**
	* Return admitted creation operations captured for ordered disposal.
	* @returns detached snapshot ordered only by Set insertion.
	*/
	pendingCreations() {
		return [...this.inFlightCreations, ...this.inFlightCleanups];
	}
	/** Close every reserved child gate synchronously before runtime drain awaits. */
	cutoffRuntime() {
		const failures = [];
		for (const reserved of this.reservations.values()) {
			let disposal;
			try {
				disposal = reserved.dispose();
			} catch (error) {
				disposal = Promise.reject(error);
			}
			this.inFlightCleanups.add(disposal);
			disposal.then(() => this.inFlightCleanups.delete(disposal), (error) => {
				this.inFlightCleanups.delete(disposal);
				this.cleanupFailures.push(error);
				this.ctx.logger.warn(`reserved child disposal: ${errorMessage(error)}`);
			});
		}
		for (const [root, ids] of this.liveChildrenByRoot()) for (const id of ids) try {
			this.ctx.subagents.interrupt(id, {
				kind: "ancestor",
				agent: root
			});
		} catch (error) {
			failures.push(error);
		}
		if (failures.length) throw new AggregateError(failures, "synchronous Team child cutoff failed");
	}
	/** Retain physically settled cleanup failures even when their deadline returned first. */
	takeCleanupFailures() {
		return this.cleanupFailures.splice(0);
	}
	/**
	* Reconcile provisioning state when one Team member Session starts.
	* @param agent - newly started exact live Agent.
	* @param signal - shared runtime cancellation.
	*/
	async recoverFor(agent, signal) {
		signal.throwIfAborted();
		const membership = this.tryMembership(agent);
		if (membership?.role === "lead") await this.reconcileProvisioning(membership.root, signal);
	}
	/** Reconstruct one exact roster child with its host gate closed and no model admission. */
	async recoverMember(root, childId, signal) {
		const member = this.journal.state(root).members.find((value) => value.id === childId);
		if (!member || member.phase !== "active" || member.attachments.length) throw new TeamError("exact active member is unavailable", "TEAM_MEMBER_NOT_FOUND");
		const existing = this.reservations.get(childId);
		if (existing && this.ctx.agents.get(childId) === existing.agent) return existing.agent;
		const reserved = await this.ctx.subagents.recoverContinuable({
			childId,
			parent: root,
			provider: member.provider,
			signal
		});
		this.reservations.set(childId, reserved);
		return reserved.agent;
	}
	/** Activate an already-persisted initial item only after exact target authorization. */
	async activateMember(agent, signal) {
		this.assertExecution(agent);
		const reserved = this.reservations.get(agent.id);
		if (reserved) {
			if (reserved.agent !== agent) throw new TeamError("reserved child generation changed", "TEAM_EXECUTION_DENIED");
			this.assertExecution(agent);
			if (!this.releasedReservations.has(reserved)) {
				await reserved.activate(signal);
				this.releasedReservations.add(reserved);
			}
		}
	}
	/**
	* Interrupt one live teammate turn without clearing its pending inbox.
	* @param caller - exact live Lead Agent.
	* @param targetName - durable teammate name.
	* @returns the target status sampled before cancellation.
	*/
	interrupt(caller, targetName) {
		const membership = this.membership(caller);
		if (membership.role !== "lead") throw new TeamError("only the Team Lead can interrupt teammates", "TEAM_LEAD_REQUIRED");
		const state = this.journal.state(membership.root);
		const target = resolveActiveMember(membership.root, state, targetName);
		if (target.id === membership.root.id) throw new TeamError("the Team Lead cannot interrupt itself", "TEAM_INVALID_TARGET");
		const live = this.ctx.agents.get(target.id);
		if (live === void 0) return { previousStatus: "inactive" };
		const previousStatus = live.status;
		this.ctx.subagents.interrupt(target.id, {
			kind: "ancestor",
			agent: caller
		});
		return { previousStatus };
	}
	/**
	* Group exact live roster children by their current Lead for runtime teardown.
	* @returns each live Lead and the roster child ids currently in the Agent registry.
	*/
	liveChildrenByRoot() {
		const teams = /* @__PURE__ */ new Map();
		for (const agent of this.ctx.agents.list()) {
			const rootId = agent.session.header.parentSession;
			if (rootId === void 0) continue;
			const root = this.ctx.agents.get(rootId);
			if (root === void 0 || !this.journal.state(root).members.some((member) => member.id === agent.id)) continue;
			const children = teams.get(root) ?? [];
			children.push(agent.id);
			teams.set(root, children);
		}
		return teams;
	}
	/**
	* Release exact teammate Activations through the continuation lifecycle owner.
	* @param root - exact live Team Lead authorizing release.
	* @param childIds - selected roster child ids.
	*/
	async stopTeammates(root, childIds) {
		await this.lifecycle.withTimeout(this.ctx.subagents.drainContinuableChildren(root, childIds));
	}
	/** Perform one creation admitted before the Team runtime disposal cutoff. */
	async spawnAdmitted(caller, request) {
		const membership = this.membership(caller);
		if (membership.role !== "lead") throw new TeamError("only the Team Lead can create teammates", "TEAM_LEAD_REQUIRED");
		const signal = AbortSignal.any([request.signal, this.lifecycle.signal]);
		signal.throwIfAborted();
		if (validateAttachmentRequests(request.attachments ?? []).length > 0) throw new TeamError("required attachments need a qualified reserved-child host", "TEAM_BINDER_UNAVAILABLE");
		const root = membership.root;
		const name = this.memberName(request.name);
		const description = requiredText(request.description, "description", 200);
		const childId = brandString(randomUUID());
		const member = {
			id: childId,
			name,
			description,
			provider: requiredText(request.provider, "provider", 200),
			context: request.context,
			...request.agentOptions?.model === void 0 ? {} : { model: request.agentOptions.model },
			phase: "provisioning",
			attachments: []
		};
		await this.journal.transact(root.id, async () => {
			const state = this.journal.state(root);
			if (state.members.some((member) => member.name === name)) throw new TeamError(`teammate name "${name}" was already used in this Team`, "TEAM_MEMBER_NAME_TAKEN");
			if (state.members.length >= this.maxMembers) throw new TeamError(`Team member limit ${this.maxMembers} reached`, "TEAM_MEMBER_LIMIT");
			this.consumeMemberAdd(caller, request);
			await this.journal.appendAndFlush(root, "team/member", {
				version: 3,
				teamId: TeamId(root.id),
				member
			});
		});
		let reserved;
		try {
			reserved = await this.ctx.subagents.materializeContinuable({
				childId,
				provider: request.provider,
				label: description,
				request: {
					parent: root,
					...request.agentOptions === void 0 ? {} : { agentOptions: request.agentOptions }
				},
				signal
			});
			this.reservations.set(childId, reserved);
			await reserved.persistInitialPrompt(request.prompt, `gat:${root.id}:${childId}:initial`, signal);
		} catch (error) {
			const cleanupFailures = [];
			if (reserved) {
				const deadline = this.lifecycle.cleanupDeadline();
				const invoke = (operation) => {
					try {
						return operation();
					} catch (failure) {
						return Promise.reject(failure);
					}
				};
				const aborting = invoke(() => reserved.abort(deadline.signal));
				const disposing = invoke(() => reserved.dispose());
				const physical = Promise.allSettled([aborting, disposing]).then((outcomes) => {
					const failures = outcomes.flatMap((outcome) => outcome.status === "rejected" ? [outcome.reason] : []);
					if (failures.length) throw new AggregateError(failures, "failed child physical cleanup failed");
				});
				this.inFlightCleanups.add(physical);
				physical.then(() => this.inFlightCleanups.delete(physical), (failure) => {
					this.inFlightCleanups.delete(physical);
					this.cleanupFailures.push(failure);
					this.ctx.logger.warn(`failed child cleanup: ${errorMessage(failure)}`);
				});
				try {
					await deadline.run(() => physical);
				} catch (failure) {
					cleanupFailures.push(failure);
				} finally {
					deadline.finish();
				}
				this.reservations.delete(childId);
			}
			const failed = {
				...member,
				phase: "failed",
				error: errorMessage(error)
			};
			try {
				const phase = await this.settleProvisioning(root, failed);
				if (!reserved) await this.stopTeammates(root, [childId]);
				if (phase === "active") throw new TeamError(`teammate "${name}" became active while its creator reported failure`, "TEAM_PROVISIONING_CONFLICT", { cause: error });
			} catch (recordError) {
				throw new AggregateError([
					error,
					...cleanupFailures,
					recordError
				], "teammate creation and durable failure recording both failed");
			}
			if (cleanupFailures.length) throw new AggregateError([error, ...cleanupFailures], `teammate creation failed: ${errorMessage(error)}; cleanup failed`);
			throw error;
		}
		const active = {
			...member,
			phase: "active"
		};
		if (await this.settleProvisioning(root, active) === "failed") {
			const conflict = new TeamError(`teammate "${name}" was reconciled as failed while creation was in progress`, "TEAM_PROVISIONING_CONFLICT");
			try {
				await this.stopTeammates(root, [childId]);
			} catch (cleanupError) {
				/* v8 ignore next -- requires the independently tested HMR settlement conflict and cleanup failure together. */
				throw new AggregateError([conflict, cleanupError], "provisioning conflict cleanup failed");
			}
			throw conflict;
		}
		return { member: this.memberView(active) };
	}
	/** Settle provisioning-only members from their independently durable child Sessions. */
	async reconcileProvisioning(root, signal) {
		const provisioning = this.journal.state(root).members.filter((member) => member.phase === "provisioning");
		for (const member of provisioning) {
			signal.throwIfAborted();
			if (member.attachments.length > 0) continue;
			if (this.ctx.agents.get(member.id) !== void 0) continue;
			let phase = "failed";
			let failure = "provisioning did not leave a resumable child Session";
			try {
				const loaded = await readPersistedSession(this.ctx.sessionPersistence, member.id, signal);
				const descriptor = foldSubagentDescriptor(loaded.events.slice(loaded.inheritedEventCount));
				const recovered = await this.ctx.subagents.recoverContinuable({
					childId: member.id,
					parent: root,
					provider: member.provider,
					signal
				});
				this.reservations.set(member.id, recovered);
				const acceptedInitialPrompt = recovered.initialMessageId !== void 0 && recovered.state !== "aborted" && recovered.state !== "disposed";
				if (loaded.header.parentSession === root.id && descriptor?.mode === "continuable" && descriptor.provider === member.provider && acceptedInitialPrompt) phase = "active";
				else failure = "persisted child Session does not match the provisioned continuation";
			} catch (error) {
				failure = `child Session recovery failed: ${errorMessage(error)}`;
			}
			signal.throwIfAborted();
			await this.journal.transact(root.id, async () => {
				signal.throwIfAborted();
				const current = this.journal.state(root).members.find((candidate) => candidate.id === member.id);
				if (current?.phase !== "provisioning") return;
				const settled = {
					...current,
					phase,
					...phase === "failed" ? { error: failure } : {}
				};
				await this.journal.appendAndFlush(root, "team/member", {
					version: 3,
					teamId: TeamId(root.id),
					member: settled
				});
			});
		}
	}
	/** Build one runtime member row after successful creation. */
	memberView(member) {
		const live = this.ctx.agents.get(member.id);
		const model = live?.options.model ?? member.model;
		return {
			id: member.id,
			name: member.name,
			role: "teammate",
			status: live?.status ?? "inactive",
			description: member.description,
			provider: member.provider,
			context: member.context,
			...model === void 0 ? {} : { model },
			diagnostics: []
		};
	}
	/** Validate a never-reused model-facing teammate name. */
	memberName(value) {
		if (!MEMBER_NAME.test(value) || value.length > 64 || value === "lead") throw new TeamError("teammate name must be lower-kebab-case, at most 64 characters, and not \"lead\"", "TEAM_INVALID_MEMBER_NAME");
		return value;
	}
	/** Append one terminal provisioning edge unless recovery already settled it. */
	async settleProvisioning(root, terminal) {
		return this.journal.transact(root.id, async () => {
			const current = this.journal.state(root).members.find((member) => member.id === terminal.id);
			/* v8 ignore next 3 -- the append-only provisioning event is committed by this operation before settlement. */
			if (current === void 0) throw new TeamError(`provisioned teammate "${terminal.id}" disappeared`, "TEAM_PROVISIONING_CONFLICT");
			if (current.phase !== "provisioning") return current.phase;
			await this.journal.appendAndFlush(root, "team/member", {
				version: 3,
				teamId: TeamId(root.id),
				member: terminal
			});
			return terminal.phase === "active" ? "active" : "failed";
		});
	}
	/** Whether a Session's own suffix identifies a provider-owned subagent child. */
	subagentDescriptor(agent) {
		return foldSubagentDescriptor(agent.session.snapshotEvents(agent.session.inheritedEventCount)) !== void 0;
	}
};
//#endregion
//#region lib/types/session-message.js
/** Durable Session-message acceptance checks shared by provisioning and mailbox recovery. */
/** Fold the durable inbox suffix into the messages still awaiting a claim. */
function pendingInboxMessages(events) {
	const inbox = {
		"next-turn": [],
		"next-step": []
	};
	for (const event of events) {
		if (event.type !== "agent/inbox/spliced") continue;
		inbox[event.data.target].splice(event.data.start, event.data.removedCount ?? 0, ...event.data.inserted);
	}
	return [...inbox["next-turn"], ...inbox["next-step"]];
}
/**
* Test whether one message is model-visible or still durably pending.
* @param events - one Session's non-inherited event suffix.
* @param predicate - identity check for the accepted message.
* @returns whether history or the current inbox contains a match.
*/
function messageAccepted(events, predicate) {
	return events.some((event) => event.type === "user/message" && predicate(event.data)) || pendingInboxMessages(events).some(predicate);
}
//#endregion
//#region lib/types/mailbox.js
/** Durable Team mailbox admission, target-local dispatch, acknowledgement, and recovery. */
/** Owns every process-local state transition for the durable Team mailbox. */
var TeamMailbox = class {
	ctx;
	journal;
	roster;
	lifecycle;
	maxPendingMessagesPerMember;
	maxMessageBytes;
	assertExecution;
	dispatchTails = /* @__PURE__ */ new Map();
	inFlightMessages = /* @__PURE__ */ new Set();
	inFlightDispatches = /* @__PURE__ */ new Set();
	/**
	* @param ctx - Team service context with Agent, Session, persistence, and subagent services.
	* @param journal - authoritative Lead-log transaction owner.
	* @param roster - Team membership and member-name resolver.
	* @param lifecycle - shared Team runtime admission cutoff.
	* @param maxPendingMessagesPerMember - per-target queued-minus-delivered limit.
	* @param maxMessageBytes - maximum complete sender-framed delivery size.
	*/
	constructor(ctx, journal, roster, lifecycle, maxPendingMessagesPerMember, maxMessageBytes, assertExecution) {
		this.ctx = ctx;
		this.journal = journal;
		this.roster = roster;
		this.lifecycle = lifecycle;
		this.maxPendingMessagesPerMember = maxPendingMessagesPerMember;
		this.maxMessageBytes = maxMessageBytes;
		this.assertExecution = assertExecution;
	}
	/**
	* Queue one durable peer message, then attempt immediate delivery.
	* @param caller - exact live sending Team member.
	* @param request - target name, content, and pre-queue cancellation.
	* @returns durable message identity and immediate-delivery observation.
	*/
	async send(caller, request) {
		if (this.lifecycle.disposed) throw new TeamError("Agent Teams service is disposing", "TEAM_DISPOSED");
		const operation = this.sendAdmitted(caller, {
			...request,
			signal: AbortSignal.any([request.signal, this.lifecycle.signal])
		});
		return await this.trackDispatch(operation);
	}
	/**
	* Observe target-side durable receipts and checkpoint their Lead-log acknowledgement.
	* @param session - exact target Session receiving the event.
	* @param event - newly appended Session event.
	*/
	observeSessionEvent(session, event) {
		if (this.lifecycle.disposed || event.type !== "user/message" || event.data.source.kind !== "team-message") return;
		const source = event.data.source;
		const acknowledgement = Promise.resolve().then(async () => {
			const root = this.ctx.agents.get(brandString(source.teamId));
			if (root !== void 0) await this.checkpointDelivered(root, session, source.messageId);
		}).catch((error) => {
			this.ctx.logger.warn(`Team message "${source.messageId}" acknowledgement failed: ${errorMessage(error)}`);
		});
		this.trackDispatch(acknowledgement);
	}
	/**
	* Retry durable pending messages relevant to one started Team member.
	* @param agent - newly started exact live Agent.
	* @param signal - shared runtime cancellation.
	*/
	async recoverFor(agent, signal) {
		signal.throwIfAborted();
		const membership = this.roster.tryMembership(agent);
		if (membership === void 0) return;
		const state = this.journal.state(membership.root);
		const messages = state.messages.filter((message) => !state.delivered.includes(message.id) && (membership.role === "lead" || message.targetId === agent.id));
		for (const message of messages) {
			signal.throwIfAborted();
			await this.tryDispatch(membership.root, message, signal);
		}
	}
	/**
	* Return admitted dispatch and acknowledgement operations captured for disposal.
	* @returns detached snapshot ordered only by Set insertion.
	*/
	pendingDispatches() {
		return [...this.inFlightDispatches];
	}
	/** Queue and dispatch one mailbox item admitted before the disposal cutoff. */
	async sendAdmitted(caller, request) {
		const membership = this.roster.membership(caller);
		request.signal.throwIfAborted();
		const root = membership.root;
		const content = structuredClone(request.content);
		const queued = await this.journal.transact(root.id, async () => {
			request.signal.throwIfAborted();
			const state = this.journal.state(root);
			const target = resolveActiveMember(root, state, request.target);
			if (target.id === caller.id) throw new TeamError("a Team member cannot message itself", "TEAM_SELF_MESSAGE");
			const pendingForTarget = state.messages.filter((candidate) => candidate.targetId === target.id && !state.delivered.includes(candidate.id)).length;
			if (pendingForTarget >= this.maxPendingMessagesPerMember) throw new TeamError(`teammate "${target.name}" has ${pendingForTarget} pending messages`, "TEAM_MAILBOX_FULL");
			const queued = {
				id: TeamMessageId(`team-message-${randomUUID()}`),
				senderId: caller.id,
				senderName: membership.name,
				targetId: target.id,
				content
			};
			if (Buffer.byteLength(JSON.stringify(this.deliveryContent(queued)), "utf8") > this.maxMessageBytes) throw new TeamError(`team message exceeds ${this.maxMessageBytes} bytes`, "TEAM_MESSAGE_TOO_LARGE");
			await this.journal.appendAndFlush(root, "team/message/queued", {
				version: 2,
				teamId: TeamId(root.id),
				message: queued
			});
			return {
				message: queued,
				dispatch: this.tryDispatch(root, queued, request.signal)
			};
		});
		const accepted = await queued.dispatch;
		return {
			messageId: queued.message.id,
			status: accepted ? "accepted" : "queued"
		};
	}
	/** Attempt one queued message exactly once in this process at a time. */
	tryDispatch(root, message, signal) {
		if (this.lifecycle.disposed) return Promise.resolve(false);
		if (this.inFlightMessages.has(message.id)) return Promise.resolve(false);
		this.inFlightMessages.add(message.id);
		const operation = this.trackDispatch(this.tryDispatchAdmitted(root, message, AbortSignal.any([signal, this.lifecycle.signal])));
		const forget = () => {
			this.inFlightMessages.delete(message.id);
		};
		operation.then(forget, forget);
		return operation;
	}
	/** Track one dispatch transaction through delivery admission or contained failure. */
	trackDispatch(operation) {
		this.inFlightDispatches.add(operation);
		operation.then(() => {
			this.inFlightDispatches.delete(operation);
		}, () => {
			this.inFlightDispatches.delete(operation);
		});
		return operation;
	}
	/** Attempt one queued message admitted before the service lifecycle cutoff. */
	async tryDispatchAdmitted(root, message, signal) {
		return await this.serializeDispatch(message, () => this.dispatchThrough(root, message, signal));
	}
	/** Serialize delivery admission for one durable target in queued order. */
	async serializeDispatch(message, operation) {
		const targetId = message.targetId;
		/* v8 ignore next -- dispatch tails absorb rejection, so the recovery callback is a fail-safe backstop. */
		const run = (this.dispatchTails.get(targetId) ?? Promise.resolve()).then(operation, operation);
		/* v8 ignore next -- dispatchOnce contains delivery failures and serializeDispatch itself does not throw. */
		const tail = run.then(() => void 0, () => void 0);
		this.dispatchTails.set(targetId, tail);
		try {
			return await run;
		} finally {
			if (this.dispatchTails.get(targetId) === tail) this.dispatchTails.delete(targetId);
		}
	}
	/** Deliver every pending target message through `message` in durable queue order. */
	async dispatchThrough(root, message, signal) {
		const state = this.journal.state(root);
		const pending = state.messages.filter((candidate) => candidate.targetId === message.targetId && !state.delivered.includes(candidate.id));
		const requested = pending.findIndex((candidate) => candidate.id === message.id);
		if (requested < 0) return state.delivered.includes(message.id);
		for (const candidate of pending.slice(0, requested + 1)) {
			const ownsInFlight = !this.inFlightMessages.has(candidate.id);
			if (ownsInFlight) this.inFlightMessages.add(candidate.id);
			try {
				if (!await this.dispatchOnce(root, candidate, signal)) return false;
			} finally {
				if (ownsInFlight) this.inFlightMessages.delete(candidate.id);
			}
		}
		return true;
	}
	/** Attempt one queued delivery after target-local ordering admits it. */
	async dispatchOnce(root, message, signal) {
		try {
			if (this.journal.state(root).members.find((candidate) => candidate.id === message.targetId)?.attachments.length) return false;
			const target = message.targetId === root.id ? root : this.ctx.agents.get(message.targetId);
			if (target !== void 0 && this.targetRecorded(target.session, message.id)) return await this.checkpointDelivered(root, target.session, message.id);
			if (target === void 0) return false;
			this.assertExecution(target);
			await this.roster.activateMember(target, signal);
			this.assertExecution(target);
			const source = {
				kind: "team-message",
				teamId: TeamId(root.id),
				messageId: message.id,
				senderId: message.senderId,
				senderName: message.senderName
			};
			const content = this.deliveryContent(message);
			signal.throwIfAborted();
			this.assertExecution(target);
			target.steer(createUserMessage({
				content,
				source
			}));
			return await this.checkpointDelivered(root, target.session, message.id);
		} catch (error) {
			this.ctx.logger.warn(`team message "${message.id}" remains queued: ${errorMessage(error)}`);
			return false;
		}
	}
	/** Flush one live target receipt before the Lead records its delivered edge. */
	async checkpointDelivered(root, target, messageId) {
		if (!await this.ctx.sessions.flush(target)) return false;
		if (!this.targetRecorded(target, messageId)) return false;
		await this.markDelivered(root, messageId, target.id);
		return true;
	}
	/** Record delivery unless the acknowledgement already exists. */
	async markDelivered(root, messageId, targetId) {
		await this.journal.transact(root.id, async () => {
			const state = this.journal.state(root);
			if (state.delivered.includes(messageId)) return;
			const queued = state.messages.find((message) => message.id === messageId);
			if (queued === void 0 || queued.targetId !== targetId) return;
			await this.journal.appendAndFlush(root, "team/message/delivered", {
				version: 2,
				teamId: TeamId(root.id),
				messageId,
				targetId
			});
		});
	}
	/** Whether a target Session already contains the durable message identity. */
	targetRecorded(session, messageId) {
		return messageAccepted(session.snapshotEvents(session.inheritedEventCount), (message) => message.source.kind === "team-message" && message.source.messageId === messageId);
	}
	/** Frame peer content with stable sender and message identity for the receiving model. */
	deliveryContent(message) {
		return [{
			type: "text",
			text: `Team message ${message.id} from ${message.senderName}:`
		}, ...structuredClone(message.content)];
	}
};
//#endregion
//#region lib/types/mission-board.js
/** Owns exact mission authorization; Lead credentials alone never prove HUMAN intent. */
var TeamMissionBoard = class {
	journal;
	constructor(journal) {
		this.journal = journal;
	}
	/** Create a draft only; executable tasks are separately created on the canonical board. */
	async create(membership, request) {
		if (membership.role !== "lead") throw new TeamError("only the Team Lead can create a mission", "TEAM_LEAD_REQUIRED");
		if (request.tasks !== void 0 && !Array.isArray(request.tasks)) throw new TeamError("tasks must be an array", "TEAM_INVALID_ARGUMENT");
		if (request.tasks?.length) throw new TeamError("create canonical tasks with explicit missionId; embedded mission task snapshots are historical only", "TEAM_TASK_MISSION_REQUIRED");
		const { root } = membership;
		return this.journal.transact(root.id, async () => {
			const state = this.journal.state(root);
			let number = 1;
			while (state.missions.some((mission) => mission.id === `mission-${number}`)) number += 1;
			const mission = {
				id: TeamMissionId(`mission-${number}`),
				revision: 1,
				title: requiredText(request.title, "title", 200),
				objective: requiredText(request.objective, "objective", 16384),
				status: "draft",
				plan: {
					tasks: [],
					taskIds: []
				},
				authorizationGeneration: 0,
				revocationGeneration: 0
			};
			await this.journal.appendAndFlush(root, "team/mission", {
				version: 3,
				teamId: TeamId(root.id),
				mission
			});
			return structuredClone(mission);
		});
	}
	/** Get one detached mission record. */
	get(membership, id) {
		const mission = this.journal.state(membership.root).missions.find((value) => value.id === id);
		if (!mission) throw new TeamError(`team mission "${id}" not found`, "TEAM_MISSION_NOT_FOUND");
		return structuredClone(mission);
	}
	/** List detached mission records; list order carries no execution authority. */
	list(membership) {
		return this.journal.state(membership.root).missions.map((value) => structuredClone(value));
	}
	/** Consume the exact host-attested approval action inside the canonical transaction. */
	async approve(caller, membership, request) {
		return this.control(caller, membership, request, "approveMission");
	}
	/** Close or revoke the exact current mission revision. */
	async end(caller, membership, request, action) {
		return this.control(caller, membership, request, action);
	}
	async control(caller, membership, request, action) {
		if (membership.role !== "lead") throw new TeamError("only the Team Lead can control missions", "TEAM_LEAD_REQUIRED");
		const { root } = membership;
		return this.journal.transact(root.id, async () => {
			const current = this.get(membership, request.missionId);
			if (current.revision !== request.expectedRevision || !Number.isSafeInteger(request.expectedRevision) || request.expectedRevision < 1 || (action === "approveMission" ? current.status !== "draft" : current.status === "closed" || current.status === "revoked")) throw new TeamError("mission revision or lifecycle is stale", "TEAM_MISSION_STALE_REVISION");
			let receipt;
			try {
				receipt = consumeHumanControl(`agentTeams/${action}`, caller, request);
			} catch (cause) {
				throw new TeamError("exact host-attested HUMAN control receipt required", "TEAM_HUMAN_CONTROL_REQUIRED", { cause });
			}
			const { approval: _oldApproval, ...withoutApproval } = current;
			const generation = (current.authorizationGeneration ?? 0) + 1;
			const mission = action === "approveMission" ? {
				...current,
				status: "approved",
				authorizationGeneration: generation,
				approval: {
					approvedRevision: current.revision,
					eventId: receipt.id,
					digest: receipt.digest,
					humanSessionId: receipt.sessionId,
					generation
				}
			} : {
				...withoutApproval,
				revision: current.revision + 1,
				status: action === "closeMission" ? "closed" : "revoked",
				revocationGeneration: (current.revocationGeneration ?? 0) + 1
			};
			await this.journal.appendAndFlush(root, "team/mission", {
				version: 3,
				teamId: TeamId(root.id),
				mission
			});
			return structuredClone(mission);
		});
	}
};
//#endregion
//#region lib/types/task-graph.js
/** Complete dependency validation for current Team task snapshots. */
/** Package-private task dependency failure retained for command error mapping. */
var TeamTaskGraphError = class extends Error {
	violation;
	/**
	* @param message - concrete invalid dependency relation.
	* @param violation - stable relation category used by Team commands.
	*/
	constructor(message, violation) {
		super(message);
		this.violation = violation;
		this.name = "TeamTaskGraphError";
	}
};
/**
* Validate the complete active task graph after replacing one candidate snapshot.
* @param current - current task snapshots before the candidate event.
* @param candidate - new or next-revision task snapshot.
* @throws {TeamTaskGraphError} when an active dependency is missing, duplicated, self-referential, or cyclic.
*/
function assertTaskGraphCandidate(current, candidate) {
	const tasks = new Map(current.map((task) => [task.id, task]));
	tasks.set(candidate.id, candidate);
	for (const task of tasks.values()) {
		if (task.status === "deleted") continue;
		const seen = /* @__PURE__ */ new Set();
		for (const blockerId of task.blockedBy) {
			if (blockerId === task.id) throw new TeamTaskGraphError(`team task "${task.id}" cannot block itself`, "cycle");
			if (seen.has(blockerId)) throw new TeamTaskGraphError(`team task "${task.id}" repeats blocker "${blockerId}"`, "duplicate");
			const blocker = tasks.get(blockerId);
			if (blocker === void 0 || blocker.status === "deleted") throw new TeamTaskGraphError(`blocker task "${blockerId}" for "${task.id}" is missing or deleted`, "missing");
			seen.add(blockerId);
		}
	}
	const visiting = /* @__PURE__ */ new Set();
	const visited = /* @__PURE__ */ new Set();
	const visit = (id) => {
		if (visiting.has(id)) throw new TeamTaskGraphError(`task dependency cycle includes "${id}"`, "cycle");
		if (visited.has(id)) return;
		const task = tasks.get(id);
		if (task === void 0 || task.status === "deleted") return;
		visiting.add(id);
		for (const blockerId of task.blockedBy) visit(blockerId);
		visiting.delete(id);
		visited.add(id);
	};
	for (const task of tasks.values()) visit(task.id);
}
//#endregion
//#region lib/types/mission-plan.js
/** Initial task-plan invariants shared by mission creation and durable replay. */
const numericTaskIdPattern$1 = /^task-(\d+)$/u;
const taskFields = new Set([
	"id",
	"revision",
	"subject",
	"description",
	"status",
	"ownerId",
	"blockedBy",
	"writeScopes"
]);
function invalid(message) {
	throw new TeamError(`invalid initial mission task plan: ${message}`, "TEAM_INVALID_ARGUMENT");
}
function assertTaskId(value, field) {
	if (typeof value !== "string" || value.length === 0) invalid(`${field} must be a non-empty task id`);
	const match = numericTaskIdPattern$1.exec(value);
	if (match !== null && !Number.isSafeInteger(Number(match[1]))) invalid(`${field} numeric suffix must be a safe integer`);
}
/**
* Validate a mission's immutable, creation-time task plan.
*
* Mission tasks are snapshots rather than mutable global Team tasks. They must
* therefore all be new, pending, unowned revision-one tasks whose complete
* dependency graph is valid before the mission event is committed or replayed.
*/
function assertInitialMissionTaskPlan(tasks) {
	if (!Array.isArray(tasks)) invalid("tasks must be an array");
	const ids = /* @__PURE__ */ new Set();
	for (const [index, task] of tasks.entries()) {
		const path = `tasks[${index}]`;
		if (task === null || typeof task !== "object" || Array.isArray(task)) invalid(`${path} must be an object`);
		const record = task;
		if (Object.keys(record).some((field) => !taskFields.has(field))) invalid(`${path} contains an unknown field`);
		assertTaskId(record.id, `${path}.id`);
		if (ids.has(record.id)) invalid(`duplicate task id "${record.id}"`);
		ids.add(record.id);
		if (record.revision !== 1) invalid(`${path} must begin at revision 1`);
		if (record.status !== "pending") invalid(`${path} must begin pending`);
		if (record.ownerId !== void 0) invalid(`${path} must begin unowned`);
		if (typeof record.subject !== "string" || requiredText(record.subject, `${path}.subject`, 200) !== record.subject) invalid(`${path}.subject must be normalized non-empty text`);
		if (typeof record.description !== "string" || requiredText(record.description, `${path}.description`, 16384) !== record.description) invalid(`${path}.description must be normalized non-empty text`);
		if (!Array.isArray(record.blockedBy)) invalid(`${path}.blockedBy must be an array`);
		record.blockedBy.forEach((blocker, blockerIndex) => assertTaskId(blocker, `${path}.blockedBy[${blockerIndex}]`));
		if (!Array.isArray(record.writeScopes)) invalid(`${path}.writeScopes must be an array`);
		const scopes = /* @__PURE__ */ new Set();
		record.writeScopes.forEach((scope, scopeIndex) => {
			if (typeof scope !== "string" || writeScope(scope) !== scope) invalid(`${path}.writeScopes[${scopeIndex}] must be normalized`);
			if (scopes.has(scope)) invalid(`${path} repeats write scope "${scope}"`);
			scopes.add(scope);
		});
	}
	const firstTask = tasks[0];
	if (!firstTask) return;
	try {
		assertTaskGraphCandidate(tasks, firstTask);
	} catch (error) {
		if (error instanceof TeamTaskGraphError) invalid(error.message);
		throw error;
	}
}
//#endregion
//#region lib/types/task-board.js
/** Shared Team task DAG commands and runtime-enriched views. */
/**
* Whether two normalized file or directory prefixes overlap on path components.
* @param left - first normalized file or directory prefix.
* @param right - second normalized file or directory prefix.
* @returns whether either prefix contains the other on path boundaries.
*/
function scopesOverlap(left, right) {
	return left === right || left.startsWith(`${right}/`) || right.startsWith(`${left}/`);
}
const TASK_GRAPH_ERROR_CODES = {
	missing: "TEAM_TASK_NOT_FOUND",
	duplicate: "TEAM_INVALID_ARGUMENT",
	cycle: "TEAM_TASK_DEPENDENCY_CYCLE"
};
/**
* Whether one committed task snapshot changes the structural WBS.
* @param prior - previously committed snapshot, absent for task creation.
* @param next - candidate replacement snapshot.
* @returns whether the candidate invalidates plan approval.
*/
function isStructuralTaskMutation(prior, next) {
	if (prior === void 0) return true;
	return prior.subject !== next.subject || prior.description !== next.description || prior.status !== "deleted" && next.status === "deleted" || prior.blockedBy.length !== next.blockedBy.length || prior.blockedBy.some((id, index) => id !== next.blockedBy[index]) || prior.writeScopes.length !== next.writeScopes.length || prior.writeScopes.some((scope, index) => scope !== next.writeScopes[index]);
}
/** Owns Team task limits, authorization, transitions, and derived views. */
var TeamTaskBoard = class {
	journal;
	maxTasks;
	assertExecution;
	validateClaim;
	bindClaimedTask;
	/**
	* @param journal - authoritative Lead-log transaction owner.
	* @param maxTasks - maximum non-deleted tasks retained by one Team.
	*/
	constructor(journal, maxTasks, assertExecution, validateClaim, bindClaimedTask) {
		this.journal = journal;
		this.maxTasks = maxTasks;
		this.assertExecution = assertExecution;
		this.validateClaim = validateClaim;
		this.bindClaimedTask = bindClaimedTask;
	}
	/**
	* Create one unowned pending task in the Team Lead log.
	* @param membership - exact caller membership resolved by the Team roster.
	* @param request - task text, blockers, and advisory write scopes.
	* @returns the revision-one task view.
	*/
	async create(membership, request) {
		const { root } = membership;
		return this.journal.transact(root.id, async () => {
			const state = this.journal.state(root);
			if (state.tasks.filter((task) => task.status !== "deleted").length >= this.maxTasks) throw new TeamError(`Team task limit ${this.maxTasks} reached`, "TEAM_TASK_LIMIT");
			const mission = state.missions.find((value) => value.id === request.missionId);
			if (!mission || mission.status === "closed" || mission.status === "revoked") throw new TeamError("new tasks require an explicit live canonical missionId", "TEAM_TASK_MISSION_REQUIRED");
			const id = TeamTaskId(`task-${state.nextTaskNumber}`);
			if (state.tasks.some((task) => task.id === id)) throw new TeamError("Team task id space exhausted", "TEAM_TASK_LIMIT");
			const task = {
				id,
				missionId: mission.id,
				revision: 1,
				subject: requiredText(request.subject, "subject", 200),
				description: requiredText(request.description, "description", 16384),
				status: "pending",
				blockedBy: this.dependencies(request.blockedBy ?? [], state),
				writeScopes: this.writeScopes(request.writeScopes ?? [])
			};
			this.assertTaskGraph(state, task);
			await this.journal.appendAndFlush(root, "team/task", {
				version: 3,
				teamId: TeamId(root.id),
				task
			});
			return this.taskView(root, state, task);
		});
	}
	/**
	* Return one task, including a deleted tombstone.
	* @param membership - exact caller membership resolved by the Team roster.
	* @param id - Team-local task identity.
	* @returns the latest task value and derived readiness diagnostics.
	*/
	get(membership, id) {
		const { root } = membership;
		const state = this.journal.state(root);
		const task = state.tasks.find((candidate) => candidate.id === id);
		if (task === void 0) throw new TeamError(`team task "${id}" not found`, "TEAM_TASK_NOT_FOUND");
		return this.taskView(root, state, task);
	}
	/**
	* List current non-deleted tasks in numeric creation order.
	* @param membership - exact caller membership resolved by the Team roster.
	* @returns detached current task views.
	*/
	list(membership) {
		const { root } = membership;
		return this.views(root, this.journal.state(root));
	}
	/** Build detached views for a prepared state that has not yet been appended. */
	views(root, state) {
		return state.tasks.filter((task) => task.status !== "deleted").map((task) => this.taskView(root, state, task));
	}
	/**
	* Fully validate and prepare missing tasks for one approved-plan import.
	* This performs no append, allowing its caller to atomically batch tasks with
	* the plan-approval event after all preflights have passed.
	*/
	prepareApprovedPlanImport(state, subjects, missionId) {
		const knownSubjects = new Set(state.tasks.filter((task) => task.status !== "deleted").map((task) => normalizedTaskSubject(task.subject)));
		const pendingSubjects = [];
		for (const rawSubject of subjects) {
			const subject = requiredText(rawSubject.normalize("NFKC").replace(/\s+/gu, " "), "task subject", 200);
			const normalized = normalizedTaskSubject(subject);
			if (knownSubjects.has(normalized)) continue;
			knownSubjects.add(normalized);
			pendingSubjects.push(subject);
		}
		if (state.tasks.filter((task) => task.status !== "deleted").length + pendingSubjects.length > this.maxTasks) throw new TeamError(`Team task limit ${this.maxTasks} reached`, "TEAM_TASK_LIMIT");
		const ids = new Set(state.tasks.map((task) => task.id));
		let nextNumber = state.nextTaskNumber;
		const prepared = [];
		for (const subject of pendingSubjects) {
			if (!Number.isSafeInteger(nextNumber) || nextNumber < 1) throw new TeamError("Team task id space exhausted", "TEAM_TASK_LIMIT");
			const id = TeamTaskId(`task-${nextNumber}`);
			if (ids.has(id)) throw new TeamError("Team task id space exhausted", "TEAM_TASK_LIMIT");
			ids.add(id);
			prepared.push({
				id,
				missionId,
				revision: 1,
				subject,
				description: "Imported from approved plan.",
				status: "pending",
				blockedBy: [],
				writeScopes: []
			});
			if (nextNumber === Number.MAX_SAFE_INTEGER && pendingSubjects.length > prepared.length) throw new TeamError("Team task id space exhausted", "TEAM_TASK_LIMIT");
			nextNumber += 1;
		}
		return prepared;
	}
	/**
	* Compare-and-set one authorized task transition.
	* @param caller - exact live Team member authorizing the mutation.
	* @param membership - caller role and exact live Lead.
	* @param request - task identity, expected revision, action, and action fields.
	* @returns the committed next task revision.
	*/
	async update(caller, membership, request) {
		const root = membership.root;
		return this.journal.transact(root.id, async () => {
			const state = this.journal.state(root);
			if (![
				"edit",
				"set_dependencies",
				"delete"
			].includes(request.action)) if (request.action === "claim") this.validateClaim(caller, membership, request.taskId);
			else this.assertExecution(caller, request.taskId);
			const current = state.tasks.find((task) => task.id === request.taskId);
			if (current === void 0) throw new TeamError(`team task "${request.taskId}" not found`, "TEAM_TASK_NOT_FOUND");
			if (current.revision !== request.expectedRevision) throw new TeamError(`stale team task "${current.id}" revision ${request.expectedRevision}; current revision is ${current.revision}`, "TEAM_TASK_STALE_REVISION");
			if (current.status === "deleted") throw new TeamError(`team task "${current.id}" is deleted`, "TEAM_TASK_DELETED");
			const lead = membership.role === "lead";
			const owner = current.ownerId === caller.id;
			const authorizeOwner = () => {
				if (!lead && !owner) throw new TeamError("task mutation requires its owner or Team Lead", "TEAM_TASK_UNAUTHORIZED");
			};
			let next;
			switch (request.action) {
				case "claim":
					if (current.ownerId !== void 0 && current.ownerId !== caller.id) throw new TeamError(`team task "${current.id}" is owned by another member`, "TEAM_TASK_ALREADY_CLAIMED");
					if (current.status !== "pending" || !this.taskReady(state, current)) throw new TeamError(`team task "${current.id}" is not ready to claim`, "TEAM_TASK_BLOCKED");
					next = {
						...current,
						status: "in_progress",
						ownerId: caller.id
					};
					break;
				case "release":
					authorizeOwner();
					if (current.status !== "in_progress") throw new TeamError("only an in-progress task can be released", "TEAM_TASK_INVALID_TRANSITION");
					next = this.withoutOwner({
						...current,
						status: "pending"
					});
					break;
				case "edit":
					authorizeOwner();
					if (request.subject === void 0 && request.description === void 0 && request.writeScopes === void 0) throw new TeamError("task edit requires subject, description, or write_scopes", "TEAM_INVALID_ARGUMENT");
					next = {
						...current,
						...request.subject === void 0 ? {} : { subject: requiredText(request.subject, "subject", 200) },
						...request.description === void 0 ? {} : { description: requiredText(request.description, "description", 16384) },
						...request.writeScopes === void 0 ? {} : { writeScopes: this.writeScopes(request.writeScopes) }
					};
					break;
				case "set_dependencies":
					authorizeOwner();
					if (request.blockedBy === void 0) throw new TeamError("set_dependencies requires blocked_by", "TEAM_INVALID_ARGUMENT");
					next = {
						...current,
						blockedBy: this.dependencies(request.blockedBy, state, current.id)
					};
					break;
				case "complete":
					authorizeOwner();
					if (current.status !== "in_progress") throw new TeamError("only an in-progress task can complete", "TEAM_TASK_INVALID_TRANSITION");
					next = {
						...current,
						status: "completed"
					};
					break;
				case "reopen":
					authorizeOwner();
					if (current.status !== "completed") throw new TeamError("only a completed task can reopen", "TEAM_TASK_INVALID_TRANSITION");
					next = this.withoutOwner({
						...current,
						status: "pending"
					});
					break;
				case "reassign": {
					if (!lead) throw new TeamError("only the Team Lead can reassign tasks", "TEAM_LEAD_REQUIRED");
					if (current.status !== "pending" && current.status !== "in_progress") throw new TeamError("only a pending or in-progress task can be reassigned", "TEAM_TASK_INVALID_TRANSITION");
					if (request.owner === void 0 || request.owner.trim().length === 0) {
						next = this.withoutOwner({
							...current,
							status: "pending"
						});
						break;
					}
					if (!this.taskReady(state, current)) throw new TeamError(`team task "${current.id}" is blocked`, "TEAM_TASK_BLOCKED");
					const assignee = resolveActiveMember(root, state, request.owner);
					next = {
						...current,
						status: "in_progress",
						ownerId: assignee.id
					};
					break;
				}
				case "delete": {
					authorizeOwner();
					const dependent = state.tasks.find((task) => task.status !== "deleted" && task.id !== current.id && task.blockedBy.includes(current.id));
					if (dependent !== void 0) throw new TeamError(`team task "${current.id}" still blocks "${dependent.id}"`, "TEAM_TASK_HAS_DEPENDENTS");
					next = {
						...current,
						status: "deleted"
					};
					break;
				}
				/* v8 ignore next 2 -- TeamTaskAction is closed and every member is handled above. */
				default: throw new TeamError(`unsupported task action ${String(request.action)}`, "TEAM_INVALID_ARGUMENT");
			}
			const task = {
				...next,
				revision: current.revision + 1
			};
			if (isStructuralTaskMutation(current, task) && current.missionId !== void 0) {
				const mission = state.missions.find((value) => value.id === current.missionId);
				if (!mission || mission.status === "closed" || mission.status === "revoked") throw new TeamError("closed mission structural mutation denied", "TEAM_MISSION_UNAUTHORIZED");
			}
			this.assertTaskGraph(state, task);
			await this.journal.appendAndFlush(root, "team/task", {
				version: 3,
				teamId: TeamId(root.id),
				task
			});
			if (request.action === "claim") this.bindClaimedTask(caller, membership, task.id);
			return this.taskView(root, state, task);
		});
	}
	/** Validate and de-duplicate dependency ids against the current task graph. */
	dependencies(values, state, self) {
		const seen = /* @__PURE__ */ new Set();
		const result = [];
		for (const id of values) {
			if (id === self) throw new TeamError("a team task cannot block itself", "TEAM_TASK_DEPENDENCY_CYCLE");
			if (seen.has(id)) throw new TeamError(`duplicate blocker "${id}"`, "TEAM_INVALID_ARGUMENT");
			const task = state.tasks.find((candidate) => candidate.id === id);
			if (task === void 0 || task.status === "deleted") throw new TeamError(`blocker task "${id}" not found`, "TEAM_TASK_NOT_FOUND");
			seen.add(id);
			result.push(id);
		}
		return result;
	}
	/** Normalize and de-duplicate task write scopes. */
	writeScopes(values) {
		return [...new Set(values.map(writeScope))];
	}
	/** Map shared task-graph validation onto stable command error codes. */
	assertTaskGraph(state, candidate) {
		try {
			assertTaskGraphCandidate(state.tasks, candidate);
		} catch (error) {
			/* v8 ignore next -- the shared validator is the only statement in the try and throws this exact error. */
			if (!(error instanceof TeamTaskGraphError)) throw error;
			throw new TeamError(error.message, TASK_GRAPH_ERROR_CODES[error.violation], { cause: error });
		}
	}
	/** Whether all current blockers completed. */
	taskReady(state, task) {
		return task.blockedBy.every((id) => state.tasks.find((candidate) => candidate.id === id)?.status === "completed");
	}
	/** Remove an optional owner field under exactOptionalPropertyTypes. */
	withoutOwner(task) {
		const { ownerId: _ownerId, ...without } = task;
		return without;
	}
	/**
	* Build one task view with owner name, readiness, and advisory write overlaps.
	* A committing caller may pass its pre-append state because `task` supplies the
	* new value explicitly; owner names, blocker readiness, and other task scopes
	* do not change when that snapshot is appended.
	*/
	taskView(root, state, task) {
		const ownerName = task.ownerId === void 0 ? void 0 : task.ownerId === root.id ? "lead" : state.members.find((member) => member.id === task.ownerId)?.name;
		const warnings = /* @__PURE__ */ new Set();
		for (const other of state.tasks) {
			if (other.id === task.id || other.status !== "in_progress") continue;
			if (task.writeScopes.some((left) => other.writeScopes.some((right) => scopesOverlap(left, right)))) warnings.add(`write scopes overlap with ${other.id}`);
		}
		return {
			id: task.id,
			...task.missionId === void 0 ? {} : { missionId: task.missionId },
			revision: task.revision,
			subject: task.subject,
			description: task.description,
			status: task.status,
			blockedBy: structuredClone(task.blockedBy),
			writeScopes: structuredClone(task.writeScopes),
			...ownerName === void 0 ? {} : { ownerName },
			ready: task.status === "pending" && this.taskReady(state, task),
			writeScopeWarnings: [...warnings]
		};
	}
};
//#endregion
//#region lib/types/projection.js
/** Host-only Team state projected incrementally from committed Session events. */
const nonNegativeSafeInteger = z$1.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER);
const positiveSafeInteger = nonNegativeSafeInteger.min(1);
const sessionIdSchema = z$1.string().min(1).transform((value) => brandString(value));
const teamIdSchema = z$1.string().min(1).transform((value) => TeamId(value));
const numericTaskIdPattern = /^task-(\d+)$/u;
const teamTaskIdSchema = z$1.string().min(1).refine((value) => {
	const match = numericTaskIdPattern.exec(value);
	return match === null || Number.isSafeInteger(Number(match[1]));
}, { message: "numeric task id suffix must be a safe integer" }).transform((value) => TeamTaskId(value));
const teamMissionIdSchema = z$1.string().min(1).transform((value) => TeamMissionId(value));
const teamMessageIdSchema = z$1.string().min(1).transform((value) => TeamMessageId(value));
const coreContentBlockTypes = new Set([
	"text",
	"reasoning",
	"image",
	"tool-call",
	"tool-result"
]);
const imageAttachmentSchema = z$1.object({
	attachmentId: z$1.string().min(1),
	mediaType: z$1.enum([
		"image/png",
		"image/jpeg",
		"image/webp",
		"image/gif"
	]),
	bytes: nonNegativeSafeInteger,
	width: positiveSafeInteger,
	height: positiveSafeInteger,
	name: z$1.string().optional()
}).strict();
const contentBlockSchema = z$1.lazy(() => z$1.union([
	z$1.object({
		type: z$1.literal("text"),
		text: z$1.string()
	}).strict(),
	z$1.object({
		type: z$1.literal("reasoning"),
		text: z$1.string()
	}).strict(),
	z$1.object({
		type: z$1.literal("image"),
		attachment: imageAttachmentSchema
	}).strict(),
	z$1.object({
		type: z$1.literal("tool-call"),
		id: z$1.string().min(1),
		name: z$1.string(),
		arguments: z$1.string()
	}).strict(),
	z$1.object({
		type: z$1.literal("tool-result"),
		toolCallId: z$1.string().min(1),
		content: z$1.array(contentBlockSchema),
		isError: z$1.boolean().optional()
	}).strict(),
	z$1.object({ type: z$1.string().min(1) }).loose().refine((block) => !coreContentBlockTypes.has(block.type), { message: "known content block types must match their declared fields" })
]));
/** Shared initializer/replay contract; preflight all members before creating any row. */
function validateInitialTask(value) {
	return z$1.array(contentBlockSchema).min(1).parse(value);
}
const legacyTeamMemberSnapshotObject = z$1.object({
	id: sessionIdSchema,
	name: z$1.string(),
	description: z$1.string(),
	provider: z$1.string(),
	context: z$1.enum(["fresh", "fork"]),
	model: z$1.string().optional(),
	phase: z$1.enum([
		"provisioning",
		"active",
		"failed"
	]),
	error: z$1.string().optional()
}).strict();
const teamMemberSnapshotSchema = legacyTeamMemberSnapshotObject.extend({ attachments: z$1.unknown().transform((value, ctx) => {
	try {
		return validateAttachmentRecords(value);
	} catch {
		ctx.addIssue({
			code: "custom",
			message: "invalid required member attachment records"
		});
		return z$1.NEVER;
	}
}) }).strict();
const teamTaskSnapshotSchema = z$1.object({
	id: teamTaskIdSchema,
	missionId: teamMissionIdSchema.optional(),
	revision: positiveSafeInteger,
	subject: z$1.string(),
	description: z$1.string(),
	status: z$1.enum([
		"pending",
		"in_progress",
		"completed",
		"deleted"
	]),
	ownerId: sessionIdSchema.optional(),
	blockedBy: z$1.array(teamTaskIdSchema),
	writeScopes: z$1.array(z$1.string())
}).strict();
const teamMissionSnapshotSchema = z$1.object({
	id: teamMissionIdSchema,
	revision: positiveSafeInteger,
	title: z$1.string().min(1),
	objective: z$1.string().min(1),
	authorizationGeneration: nonNegativeSafeInteger.optional(),
	revocationGeneration: nonNegativeSafeInteger.optional(),
	status: z$1.enum([
		"draft",
		"approved",
		"active",
		"completed",
		"closed",
		"revoked"
	]),
	plan: z$1.object({
		tasks: z$1.array(teamTaskSnapshotSchema),
		taskIds: z$1.array(teamTaskIdSchema).optional()
	}).strict(),
	approval: z$1.object({
		approvedRevision: positiveSafeInteger,
		eventId: z$1.string().min(1).optional(),
		digest: z$1.string().min(1).optional(),
		humanSessionId: z$1.string().min(1).optional(),
		generation: nonNegativeSafeInteger.optional()
	}).strict().optional()
}).strict().superRefine((mission, ctx) => {
	if (mission.status === "approved" !== (mission.approval?.approvedRevision === mission.revision)) ctx.addIssue({
		code: "custom",
		message: "mission status must be approved exactly when approval matches revision"
	});
});
const teamMessageSnapshotSchema = z$1.object({
	id: teamMessageIdSchema,
	senderId: sessionIdSchema,
	senderName: z$1.string(),
	targetId: sessionIdSchema,
	content: z$1.array(contentBlockSchema)
}).strict();
const teamEventSelectorSchema = z$1.object({
	version: nonNegativeSafeInteger,
	teamId: teamIdSchema
}).loose();
const teamMemberEventSchema = z$1.union([z$1.object({
	version: z$1.literal(2),
	teamId: teamIdSchema,
	member: legacyTeamMemberSnapshotObject
}).strict(), z$1.object({
	version: z$1.literal(3),
	teamId: teamIdSchema,
	member: teamMemberSnapshotSchema
}).strict()]);
const teamTaskEventSchema = z$1.object({
	version: z$1.union([z$1.literal(2), z$1.literal(3)]),
	teamId: teamIdSchema,
	task: teamTaskSnapshotSchema
}).strict();
const teamMissionEventSchema = z$1.object({
	version: z$1.union([z$1.literal(2), z$1.literal(3)]),
	teamId: teamIdSchema,
	mission: teamMissionSnapshotSchema
}).strict();
const teamPlanApprovedEventSchema = z$1.object({
	version: z$1.union([z$1.literal(2), z$1.literal(3)]),
	teamId: teamIdSchema,
	approval: z$1.object({
		approvedRevision: nonNegativeSafeInteger,
		eventId: z$1.string().optional(),
		digest: z$1.string().optional(),
		humanSessionId: z$1.string().optional()
	}).strict()
}).strict();
const teamWorkSnapshotObject = z$1.object({
	memberId: sessionIdSchema,
	state: z$1.enum([
		"working",
		"blocked",
		"review_required",
		"done"
	]),
	summary: z$1.string().min(1).refine((value) => value.trim() === value),
	reason: z$1.string().min(1).refine((value) => value.trim() === value).optional(),
	taskId: teamTaskIdSchema.optional(),
	files: z$1.array(z$1.string()).refine((files) => {
		if (new Set(files).size !== files.length) return false;
		return files.every((file) => {
			try {
				return writeScope(file) === file;
			} catch {
				return false;
			}
		});
	})
}).strict();
const teamWorkSnapshotSchema = teamWorkSnapshotObject;
const teamWorkEventSchema = z$1.object({
	version: z$1.literal(2),
	teamId: teamIdSchema,
	work: teamWorkSnapshotSchema
}).strict();
const teamWorkViewSchema = teamWorkSnapshotObject.extend({ updatedAt: nonNegativeSafeInteger });
const teamMessageQueuedEventSchema = z$1.object({
	version: z$1.literal(2),
	teamId: teamIdSchema,
	message: teamMessageSnapshotSchema
}).strict();
const teamMessageDeliveredEventSchema = z$1.object({
	version: z$1.literal(2),
	teamId: teamIdSchema,
	messageId: teamMessageIdSchema,
	targetId: sessionIdSchema
}).strict();
/**
* Construct empty state for one Team identity.
* @param rootId - root Session identity.
* @returns mutable empty Team state.
*/
function emptyTeamState(rootId) {
	return {
		id: TeamId(rootId),
		planRevision: 0,
		planPhase: "draft",
		work: [],
		members: [],
		missions: [],
		tasks: [],
		messages: [],
		delivered: [],
		nextTaskNumber: 1
	};
}
const teamProjectionEntrySchema = z$1.object({
	id: teamIdSchema,
	planRevision: nonNegativeSafeInteger,
	planPhase: z$1.enum(["draft", "approved"]),
	planApproval: z$1.object({
		approvedRevision: nonNegativeSafeInteger,
		eventId: z$1.string().optional(),
		digest: z$1.string().optional(),
		humanSessionId: z$1.string().optional()
	}).strict().optional(),
	work: z$1.array(teamWorkViewSchema),
	members: z$1.array(teamMemberSnapshotSchema),
	missions: z$1.array(teamMissionSnapshotSchema),
	tasks: z$1.array(teamTaskSnapshotSchema),
	messages: z$1.array(teamMessageSnapshotSchema),
	delivered: z$1.array(teamMessageIdSchema),
	nextTaskNumber: positiveSafeInteger,
	failure: z$1.string().optional()
}).strict().superRefine((state, ctx) => {
	const approvalMatches = state.planApproval?.approvedRevision === state.planRevision;
	const futureApproval = state.planApproval !== void 0 && state.planApproval.approvedRevision > state.planRevision;
	if (state.planPhase === "approved" !== approvalMatches || futureApproval) ctx.addIssue({
		code: "custom",
		message: "planPhase must be approved exactly when approval matches planRevision"
	});
});
/**
* Test whether a Session event belongs to the Team domain.
* @param event - candidate Session event.
* @returns whether the event has a Team-owned type.
*/
function isTeamEvent(event) {
	return event.type === "team/member" || event.type === "team/task" || event.type === "team/mission" || event.type === "team/plan-approved" || event.type === "team/work" || event.type === "team/message/queued" || event.type === "team/message/delivered";
}
/** Decode one persisted Team value and retain the schema failure as its cause. */
function parsePersisted(type, schema, value) {
	try {
		return schema.parse(value);
	} catch (error) {
		throw new Error(`persisted Agent Teams ${type} payload is invalid`, { cause: error });
	}
}
/** Decode the complete current-version payload selected by one Team event type. */
function parseCurrentTeamEvent(event) {
	switch (event.type) {
		case "team/member": return {
			...event,
			data: parsePersisted(event.type, teamMemberEventSchema, event.data)
		};
		case "team/task": return {
			...event,
			data: parsePersisted(event.type, teamTaskEventSchema, event.data)
		};
		case "team/mission": return {
			...event,
			data: parsePersisted(event.type, teamMissionEventSchema, event.data)
		};
		case "team/plan-approved": return {
			...event,
			data: parsePersisted(event.type, teamPlanApprovedEventSchema, event.data)
		};
		case "team/work": return {
			...event,
			data: parsePersisted(event.type, teamWorkEventSchema, event.data)
		};
		case "team/message/queued": return {
			...event,
			data: parsePersisted(event.type, teamMessageQueuedEventSchema, event.data)
		};
		case "team/message/delivered": return {
			...event,
			data: parsePersisted(event.type, teamMessageDeliveredEventSchema, event.data)
		};
		/* v8 ignore next 2 -- TeamEventType is closed and every member is handled above. */
		default: return event;
	}
}
function applyProjectionEvent(state, event) {
	if (state.failure !== void 0) return;
	if (!isTeamEvent(event)) return;
	try {
		const selector = parsePersisted(event.type, teamEventSelectorSchema, event.data);
		if (selector.teamId !== state.id) return;
		if ([
			"team/member",
			"team/task",
			"team/mission",
			"team/plan-approved"
		].includes(event.type) ? selector.version !== 2 && selector.version !== 3 : selector.version !== 2) throw new Error(`unsupported Agent Teams event version ${String(selector.version)}`);
		applyCurrentTeamEvent(state, parseCurrentTeamEvent(event));
	} catch (error) {
		/* v8 ignore next -- the owned Team transition throws Error instances. */
		state.failure = error instanceof Error ? error.message : String(error);
	}
}
function applyCurrentTeamEvent(state, event) {
	switch (event.type) {
		case "team/member": {
			const member = event.data.version === 2 ? {
				...event.data.member,
				attachments: []
			} : event.data.member;
			const index = state.members.findIndex((candidate) => candidate.id === member.id);
			const prior = state.members[index];
			const named = state.members.find((candidate) => candidate.name === member.name);
			if (named !== void 0 && named.id !== member.id) throw new Error(`teammate name "${member.name}" is reused by another member`);
			if (prior === void 0) {
				if (member.phase !== "provisioning") throw new Error(`teammate "${member.name}" must begin provisioning`);
			} else {
				if (prior.name !== member.name || prior.provider !== member.provider || prior.context !== member.context || prior.model !== member.model || JSON.stringify(prior.attachments) !== JSON.stringify(member.attachments)) throw new Error(`teammate "${member.id}" changed immutable identity fields`);
				if (prior.phase !== "provisioning" || member.phase === "provisioning") throw new Error(`teammate "${member.name}" has an invalid ${prior.phase} -> ${member.phase} transition`);
			}
			if (index < 0) state.members.push(member);
			else state.members[index] = member;
			break;
		}
		case "team/mission": {
			const rawMission = event.data.mission;
			const mission = event.data.version === 2 ? {
				...rawMission,
				...rawMission.approval === void 0 ? {} : { approval: { approvedRevision: rawMission.approval.approvedRevision } },
				plan: {
					tasks: rawMission.plan.tasks,
					taskIds: []
				},
				authorizationGeneration: 0,
				revocationGeneration: 0
			} : rawMission;
			if (event.data.version === 3 && (mission.plan.tasks.length !== 0 || mission.plan.taskIds === void 0)) throw new Error("v3 mission requires canonical task references");
			if (event.data.version === 3 && mission.status === "approved" && (!mission.approval?.eventId || !mission.approval.digest || !mission.approval.humanSessionId)) throw new Error("v3 mission approval requires HUMAN receipt evidence");
			assertInitialMissionTaskPlan(mission.plan.tasks);
			const index = state.missions.findIndex((candidate) => candidate.id === mission.id);
			const prior = state.missions[index];
			if (prior === void 0) {
				const legacyDraft = mission.status === "draft" && mission.approval === void 0;
				const authorized = mission.status === "approved" && mission.approval?.approvedRevision === 1;
				if (mission.revision !== 1 || !legacyDraft && !authorized) throw new Error(`team mission "${mission.id}" must begin as revision 1`);
			} else if (mission.revision !== prior.revision + 1 && !(event.data.version === 3 && mission.revision === prior.revision && prior.status === "draft" && mission.status === "approved")) throw new Error(`team mission "${mission.id}" revision is not contiguous`);
			if (index < 0) state.missions.push(mission);
			else state.missions[index] = mission;
			break;
		}
		case "team/task": {
			const { missionId: _legacyMissionId, ...historicalTask } = event.data.task;
			const task = event.data.version === 2 ? historicalTask : event.data.task;
			if (event.data.version === 3 && !task.missionId) throw new Error("v3 task requires canonical mission association");
			const index = state.tasks.findIndex((candidate) => candidate.id === task.id);
			const prior = state.tasks[index];
			if (prior === void 0 && task.revision !== 1) throw new Error(`team task "${task.id}" must begin at revision 1`);
			if (prior !== void 0 && task.revision !== prior.revision + 1) throw new Error(`team task "${task.id}" revision is not contiguous`);
			if (prior !== void 0 && prior.missionId !== task.missionId) throw new Error("canonical task mission association is immutable");
			assertTaskGraphCandidate(state.tasks, task);
			if (isStructuralTaskMutation(prior, task)) {
				state.planRevision += 1;
				state.planPhase = "draft";
				if (task.missionId !== void 0) {
					const missionIndex = state.missions.findIndex((value) => value.id === task.missionId);
					const mission = state.missions[missionIndex];
					if (!mission) throw new Error("canonical task mission does not exist");
					if (mission.status === "closed" || mission.status === "revoked") throw new Error("closed mission cannot accept structural task mutation");
					const { approval: _approval, ...draft } = mission;
					state.missions[missionIndex] = {
						...draft,
						revision: mission.revision + 1,
						status: "draft",
						revocationGeneration: (mission.revocationGeneration ?? 0) + 1,
						plan: {
							tasks: [],
							taskIds: [...new Set([...mission.plan.taskIds ?? [], task.id])]
						}
					};
				}
			}
			const match = numericTaskIdPattern.exec(task.id);
			if (match !== null) {
				const number = Number(match[1]);
				state.nextTaskNumber = Math.max(state.nextTaskNumber, number === Number.MAX_SAFE_INTEGER ? number : number + 1);
			}
			if (index < 0) state.tasks.push(task);
			else state.tasks[index] = task;
			break;
		}
		case "team/plan-approved": {
			const approval = event.data.version === 2 ? { approvedRevision: event.data.approval.approvedRevision } : event.data.approval;
			if (!state.tasks.some((task) => task.status !== "deleted")) throw new Error("an empty Team plan cannot be approved");
			if (approval.approvedRevision !== state.planRevision) throw new Error(`Team plan approval revision ${approval.approvedRevision} does not match current revision ${state.planRevision}`);
			if (state.planApproval !== void 0 && approval.approvedRevision <= state.planApproval.approvedRevision) throw new Error(`Team plan approval revision ${approval.approvedRevision} is not monotonic`);
			state.planApproval = approval;
			state.planPhase = "approved";
			break;
		}
		case "team/work": {
			const work = event.data.work;
			const reporterIsLead = String(work.memberId) === String(state.id);
			const reporterIsActive = state.members.some((member) => member.id === work.memberId && member.phase === "active");
			if (!reporterIsLead && !reporterIsActive) throw new Error(`work reporter "${work.memberId}" is not active`);
			if (work.state === "blocked" && work.reason === void 0) throw new Error("blocked work requires a reason");
			if ((work.state === "working" || work.state === "done") && work.reason !== void 0) throw new Error(`${work.state} work must not include a reason`);
			if (work.state === "review_required" && work.files.length === 0) throw new Error("review_required work requires at least one file");
			if (work.taskId !== void 0) {
				const task = state.tasks.find((candidate) => candidate.id === work.taskId);
				if (task === void 0) throw new Error(`work task "${work.taskId}" does not exist`);
				if (task.status === "deleted") throw new Error(`work task "${work.taskId}" is deleted`);
				if (task.ownerId !== work.memberId) throw new Error(`work task "${work.taskId}" is not owned by reporter`);
			}
			const next = {
				...work,
				files: [...work.files],
				updatedAt: event.time
			};
			const index = state.work.findIndex((candidate) => candidate.memberId === work.memberId);
			if (index < 0) state.work.push(next);
			else state.work[index] = next;
			break;
		}
		case "team/message/queued": {
			const message = event.data.message;
			if (state.messages.some((candidate) => candidate.id === message.id)) throw new Error(`team message "${message.id}" was queued twice`);
			state.messages.push(message);
			break;
		}
		case "team/message/delivered": {
			const queued = state.messages.find((message) => message.id === event.data.messageId);
			if (queued === void 0) throw new Error(`team message "${event.data.messageId}" was delivered before queueing`);
			if (queued.targetId !== event.data.targetId) throw new Error(`team message "${event.data.messageId}" target changed`);
			if (state.delivered.includes(event.data.messageId)) throw new Error(`team message "${event.data.messageId}" was delivered twice`);
			state.delivered.push(event.data.messageId);
			break;
		}
		/* v8 ignore next 2 -- TeamEventType is closed and every member is handled above. */
		default: return;
	}
}
/** Host-only Team projection selected by the projected Session identity. */
const teamProjectionDefinition = {
	key: "agentTeam",
	stateVersion: 9,
	stateSchema: teamProjectionEntrySchema,
	init: (header) => emptyTeamState(header.id),
	apply: (state, event) => {
		applyProjectionEvent(state, event);
		return state;
	}
};
//#endregion
//#region lib/types/work-state.js
/** Canonical durable member-work reporting over the Team event journal. */
const MAX_WORK_SUMMARY_LENGTH = 4096;
const MAX_WORK_REASON_LENGTH = 4096;
function isWorkState(state) {
	return state === "working" || state === "blocked" || state === "review_required" || state === "done";
}
/** Owns validation and durable replacement of each Team member's current work state. */
var TeamWorkBoard = class {
	journal;
	assertExecution;
	constructor(journal, assertExecution) {
		this.journal = journal;
		this.assertExecution = assertExecution;
	}
	/**
	* Validate, append, flush, then return the complete committed work view.
	* @param caller - member reporting its own current work state.
	* @param membership - caller's authoritative Team membership.
	* @param request - candidate durable work snapshot.
	* @returns complete committed Team work projection after the append flushes.
	*/
	async report(caller, membership, request) {
		return this.journal.transact(membership.root.id, async () => {
			const state = this.journal.state(membership.root);
			if (request.state === "working" || request.state === "done") this.assertExecution(caller, request.taskId);
			if (membership.role === "teammate" && !state.members.some((member) => member.id === caller.id && member.phase === "active")) throw new TeamError(`work reporter "${membership.name}" is not active`, "TEAM_NOT_MEMBER");
			const summary = requiredText(request.summary, "summary", MAX_WORK_SUMMARY_LENGTH);
			if (!isWorkState(request.state)) throw new TeamError(`unsupported work state ${String(request.state)}`, "TEAM_INVALID_ARGUMENT");
			const reason = request.reason === void 0 ? void 0 : requiredText(request.reason, "reason", MAX_WORK_REASON_LENGTH);
			if (request.state === "blocked" && reason === void 0) throw new TeamError("blocked work requires a non-empty reason", "TEAM_INVALID_ARGUMENT");
			if ((request.state === "working" || request.state === "done") && reason !== void 0) throw new TeamError(`${request.state} work must not include a blocker reason`, "TEAM_INVALID_ARGUMENT");
			const files = request.files.map((file) => writeScope(file));
			if (request.state === "review_required" && files.length === 0) throw new TeamError("review_required work requires at least one workspace-relative file", "TEAM_INVALID_ARGUMENT");
			if (new Set(files).size !== files.length) throw new TeamError("work files must not contain duplicates", "TEAM_INVALID_ARGUMENT");
			if (request.taskId !== void 0) {
				if (state.tasks.find((candidate) => candidate.id === request.taskId && candidate.status !== "deleted")?.ownerId !== caller.id) throw new TeamError(`task "${request.taskId}" is not owned by the reporting member`, "TEAM_INVALID_ARGUMENT");
			}
			const work = {
				memberId: caller.id,
				state: request.state,
				summary,
				...reason === void 0 ? {} : { reason },
				...request.taskId === void 0 ? {} : { taskId: request.taskId },
				files
			};
			await this.journal.appendAndFlush(membership.root, "team/work", {
				version: 2,
				teamId: TeamId(membership.root.id),
				work
			});
			const committed = this.journal.state(membership.root).work.find((item) => item.memberId === caller.id);
			if (committed === void 0) throw new Error("committed Team work state is missing from projection");
			return {
				...committed,
				files: [...committed.files]
			};
		});
	}
};
//#endregion
//#region lib/types/member-binders.js
/** Generic required binder registry and exactly-once prepared ownership. No production host wiring. */
function unavailable() {
	throw new TeamError("required member binder is unavailable", "TEAM_BINDER_UNAVAILABLE");
}
/** Reference provider MUST enumerate authoritative durable records, including inactive members. */
var TeamMemberBinderRegistry = class {
	registrations = /* @__PURE__ */ new Map();
	pins = /* @__PURE__ */ new Map();
	references;
	constructor(references) {
		this.references = references;
	}
	key(id, version) {
		return `${id}:${version}`;
	}
	register(binder) {
		validateAttachmentRequests([{
			binderId: binder.id,
			protocolVersion: binder.protocolVersion,
			required: true,
			payload: null
		}]);
		const key = this.key(binder.id, binder.protocolVersion);
		if (this.registrations.has(key)) throw new TeamError("member binder already registered", "TEAM_BINDER_CONFLICT");
		const captured = Object.freeze({
			id: binder.id,
			protocolVersion: binder.protocolVersion,
			prepare: binder.prepare.bind(binder),
			bind: binder.bind.bind(binder),
			recover: binder.recover.bind(binder)
		});
		this.registrations.set(key, captured);
		return () => {
			if (this.registrations.get(key) !== captured) return;
			if (this.pins.get(key)) throw new TeamError("member binder has a pending owner", "TEAM_BINDER_REFERENCED");
			for (const records of this.references()) if (records.some((record) => this.key(record.binderId, record.protocolVersion) === key)) throw new TeamError("durable member still references binder", "TEAM_BINDER_REFERENCED");
			this.registrations.delete(key);
		};
	}
	resolve(request) {
		return this.registrations.get(this.key(request.binderId, request.protocolVersion)) ?? unavailable();
	}
	pin(request) {
		this.resolve(request);
		const key = this.key(request.binderId, request.protocolVersion);
		this.pins.set(key, (this.pins.get(key) ?? 0) + 1);
		let released = false;
		return () => {
			if (released) return;
			released = true;
			this.pins.set(key, this.pins.get(key) - 1);
		};
	}
};
/** A lease's original callback is never called twice or after successful transfer. */
var PreparedMemberAttachment = class {
	unpin;
	binder;
	record;
	value;
	state = "prepared";
	abortPromise;
	abortCallback;
	constructor(binder, record, prepared, unpin = () => {}) {
		this.unpin = unpin;
		this.binder = binder;
		this.record = record;
		this.value = prepared.value;
		this.abortCallback = prepared.abort.bind(prepared);
	}
	transfer() {
		if (this.state !== "prepared") throw new TeamError("prepared ownership conflict", "TEAM_BINDING_CONFLICT");
		this.state = "transferred";
		this.unpin();
	}
	abort(signal) {
		if (this.state === "transferred") return Promise.resolve();
		if (!this.abortPromise) {
			this.state = "aborted";
			this.abortPromise = Promise.resolve().then(() => this.abortCallback(signal)).finally(this.unpin);
			this.abortPromise.catch(() => void 0);
		}
		return this.abortPromise;
	}
};
async function abortPrepared(leases, signal, deadline) {
	const failures = [];
	for (const lease of [...leases].reverse()) try {
		await (deadline ? deadline.run((remaining) => lease.abort(remaining)) : lease.abort(signal));
	} catch (error) {
		failures.push(error);
	}
	if (failures.length) throw new AggregateError(failures, "required attachment preparation cleanup failed");
}
/** Normalized spec detachment is independent of attachment envelope depth/node/string limits. */
function freezeSpec(value, ancestors = /* @__PURE__ */ new Set()) {
	if (value === null || value === void 0 || typeof value === "string" || typeof value === "boolean") return value;
	if (typeof value === "number" && Number.isFinite(value)) return value;
	if (typeof value !== "object" || ancestors.has(value)) throw new TeamError("invalid normalized binding spec", "TEAM_INVALID_CONFIG");
	const prototype = Object.getPrototypeOf(value);
	if (Array.isArray(value) ? prototype !== Array.prototype : prototype !== Object.prototype && prototype !== null) throw new TeamError("invalid normalized binding spec", "TEAM_INVALID_CONFIG");
	ancestors.add(value);
	try {
		const descriptors = Object.getOwnPropertyDescriptors(value);
		if (Object.getOwnPropertySymbols(value).length) throw new TeamError("invalid normalized binding spec", "TEAM_INVALID_CONFIG");
		const result = Array.isArray(value) ? [] : {};
		for (const key of Object.keys(descriptors)) {
			if (Array.isArray(value) && key === "length") continue;
			const entry = descriptors[key];
			if (!("value" in entry) || !entry.enumerable) throw new TeamError("invalid normalized binding spec", "TEAM_INVALID_CONFIG");
			Object.defineProperty(result, key, {
				value: freezeSpec(entry.value, ancestors),
				enumerable: true
			});
		}
		return Object.freeze(result);
	} finally {
		ancestors.delete(value);
	}
}
/** Validate/resolve ALL requests first, then prepare in declaration order. No row/child is created. */
async function prepareMembers(registry, rawInputs, signal, cleanupTimeoutMs = 5e3) {
	const inputs = rawInputs.map((input) => Object.freeze({
		...input,
		spec: freezeSpec(input.spec)
	}));
	const requested = inputs.map((input) => validateAttachmentRequests(input.spec.attachments ?? []).map((request) => ({
		request,
		binder: registry.resolve(request)
	})));
	const leases = [];
	const members = [];
	let cleanupDeadline;
	const cleanup = () => cleanupDeadline ??= new BindingDeadline(cleanupTimeoutMs);
	try {
		for (let index = 0; index < inputs.length; index++) {
			const input = inputs[index];
			const memberLeases = [];
			for (const { request, binder } of requested[index]) {
				signal.throwIfAborted();
				const unpin = registry.pin(request);
				let acquired = false;
				const lateAbort = async (prepared, shared) => {
					const deadline = shared ?? new BindingDeadline(cleanupTimeoutMs);
					try {
						await deadline.run((remaining) => {
							const pending = Promise.resolve().then(() => prepared.abort(remaining)).finally(unpin);
							pending.catch(() => void 0);
							return pending;
						});
					} finally {
						if (!shared) deadline.finish();
					}
				};
				let prepared;
				try {
					prepared = await acquireBindingResource(() => Promise.resolve().then(() => binder.prepare({
						...input,
						payload: request.payload
					}, signal)).then((value) => {
						acquired = true;
						return value;
					}, (error) => {
						unpin();
						throw error;
					}), signal, (value) => lateAbort(value));
				} catch (error) {
					if (!signal.aborted && !acquired) unpin();
					throw error;
				}
				let record;
				try {
					if (!prepared || typeof prepared.abort !== "function") throw new TeamError("invalid prepared binding resource", "TEAM_BINDING_CONFLICT");
					record = attachmentRecord(request, prepared.attachment);
				} catch (error) {
					try {
						await lateAbort(prepared, cleanup());
					} catch (failure) {
						throw new AggregateError([error, failure], "prepared output rejected and abort failed");
					}
					throw error;
				}
				const lease = new PreparedMemberAttachment(binder, record, prepared, unpin);
				leases.push(lease);
				memberLeases.push(lease);
				signal.throwIfAborted();
			}
			const records = validateAttachmentRecords(memberLeases.map((lease) => lease.record));
			members.push(Object.freeze({
				input: {
					...input,
					payload: null
				},
				leases: Object.freeze(memberLeases),
				records
			}));
		}
		return Object.freeze(members);
	} catch (error) {
		const deadline = cleanup();
		try {
			await abortPrepared(leases, deadline.signal, deadline);
		} catch (cleanup) {
			throw new AggregateError([error, cleanup], "required attachment prepare-all failed");
		} finally {
			deadline.finish();
		}
		throw error;
	}
}
//#endregion
//#region lib/types/member-binding.js
/** Frozen lifecycle orchestration over qualified ports; not wired to legacy DSH creation. */
var BoundMemberRuntime = class {
	input;
	records;
	child;
	bindings;
	authority;
	closed = false;
	activation;
	disposal;
	activated = false;
	cancellation = new AbortController();
	/** Host-only failure evidence; callers must redact before any model/view exposure. */
	lastFailure;
	constructor(input, records, child, bindings, authority) {
		this.input = input;
		this.records = records;
		this.child = child;
		this.bindings = bindings;
		this.authority = authority;
	}
	/** Same-generation retry retains valid bindings and the existing quarantined initial item. */
	activate(signal) {
		signal.throwIfAborted();
		if (this.closed || !this.child.isValid() || !this.input.scope.isCurrent()) throw new TeamError("binding reconstruction required", "TEAM_BINDING_UNAVAILABLE");
		this.authority.authorize(this.input, "activate");
		if (this.activation) return this.activation;
		this.authority.publish(this.input, "ready");
		if (this.activated) return Promise.resolve();
		const combined = AbortSignal.any([signal, this.cancellation.signal]);
		const operation = this.child.activate(combined).then(() => {
			combined.throwIfAborted();
			if (!this.child.isValid() || !this.input.scope.isCurrent()) throw new TeamError("binding reconstruction required", "TEAM_BINDING_UNAVAILABLE");
			this.activated = true;
			this.lastFailure = void 0;
		}).catch((error) => {
			this.lastFailure = error;
			try {
				this.authority.publish(this.input, "unavailable");
			} catch {}
			throw error;
		});
		this.activation = operation;
		operation.then(() => {
			this.activation = void 0;
		}, () => {
			this.activation = void 0;
		});
		return operation;
	}
	/** Callback invoked only after current generation/lease and binding readiness are proven. */
	async releaseMailbox(deliver) {
		if (this.closed || !this.child.isValid() || !this.input.scope.isCurrent()) throw new TeamError("member bindings unavailable", "TEAM_BINDING_UNAVAILABLE");
		this.authority.authorize(this.input, "mailbox");
		await deliver();
	}
	closeAdmission() {
		if (this.closed) return;
		this.closed = true;
		this.cancellation.abort(new TeamError("member bindings closed", "TEAM_BINDING_UNAVAILABLE"));
		const failures = [];
		try {
			this.authority.publish(this.input, "unavailable");
		} catch (error) {
			failures.push(error);
		}
		for (const binding of [...this.bindings].reverse()) try {
			binding.closeAdmission();
		} catch (error) {
			failures.push(error);
		}
		if (failures.length) throw new AggregateError(failures, "binding admission cutoff failed");
	}
	dispose(timeoutMs) {
		if (this.disposal) return this.disposal;
		const failures = [];
		try {
			this.closeAdmission();
		} catch (error) {
			failures.push(error);
		}
		const deadline = new BindingDeadline(timeoutMs);
		this.disposal = (async () => {
			try {
				for (const binding of [...this.bindings].reverse()) {
					try {
						await deadline.run((signal) => binding.settle(signal));
					} catch (error) {
						failures.push(error);
					}
					try {
						await deadline.run((signal) => binding.release(signal));
					} catch (error) {
						failures.push(error);
					}
				}
				try {
					await deadline.run((signal) => this.child.dispose(signal));
				} catch (error) {
					failures.push(error);
				}
			} finally {
				deadline.finish();
			}
			if (failures.length) throw new AggregateError(failures, "member binding disposal failed");
		})();
		this.disposal.catch(() => void 0);
		return this.disposal;
	}
};
async function rollback(prepared, child, bindings, ports, abortChild = true) {
	const failures = [];
	for (const binding of [...bindings].reverse()) try {
		binding.closeAdmission();
	} catch (error) {
		failures.push(error);
	}
	try {
		ports.authority.publish(prepared.input, "unavailable");
	} catch (error) {
		failures.push(error);
	}
	const deadline = new BindingDeadline(ports.cleanupTimeoutMs);
	try {
		if (child && abortChild) try {
			await deadline.run((signal) => child.abort(signal));
		} catch (error) {
			failures.push(error);
		}
		try {
			await abortPrepared(prepared.leases, deadline.signal, deadline);
		} catch (error) {
			failures.push(error);
		}
		for (const binding of [...bindings].reverse()) {
			try {
				await deadline.run((signal) => binding.settle(signal));
			} catch (error) {
				failures.push(error);
			}
			try {
				await deadline.run((signal) => binding.release(signal));
			} catch (error) {
				failures.push(error);
			}
		}
		if (child) try {
			await deadline.run((signal) => child.dispose(signal));
		} catch (error) {
			failures.push(error);
		}
	} finally {
		deadline.finish();
	}
	if (failures.length) throw new AggregateError(failures, "pre-active binding cleanup failed");
}
/** One member of an already prepared roster. Roster owner must abort all unused sibling leases. */
async function provisionPreparedMember(prepared, ports, signal) {
	let child;
	const bindings = [];
	let runtime;
	try {
		signal.throwIfAborted();
		await ports.journal.provisioning(prepared.input, prepared.records);
		signal.throwIfAborted();
		child = await acquireBindingResource(() => ports.host.materialize(prepared.input, signal), signal, (late) => rollback(prepared, late, [], ports));
		signal.throwIfAborted();
		const input = {
			...prepared.input,
			scope: child.scope
		};
		for (const lease of prepared.leases) {
			signal.throwIfAborted();
			const binding = await acquireBindingResource(() => lease.binder.bind(input, lease.record.payload, lease.value, signal), signal, async (late) => {
				await rollback(prepared, void 0, [await acceptBinding(late, ports.cleanupTimeoutMs)], ports, false);
			});
			await acceptBinding(binding, ports.cleanupTimeoutMs);
			bindings.push(binding);
			lease.transfer();
			signal.throwIfAborted();
		}
		await child.persistInitialPrompt(prepared.input.spec.initialTask, `gat-initial:${prepared.input.teamId}:${prepared.input.memberId}`, signal);
		signal.throwIfAborted();
		await ports.journal.active(prepared.input, prepared.records);
		runtime = new BoundMemberRuntime(input, prepared.records, child, Object.freeze(bindings), ports.authority);
	} catch (error) {
		let phase;
		try {
			phase = await ports.journal.committedPhase(prepared.input);
		} catch (observation) {
			const failures = [error, observation];
			try {
				await rollback(prepared, child, bindings, ports, false);
			} catch (cleanup) {
				failures.push(cleanup);
			}
			throw new AggregateError(failures, "member commit outcome unknown; execution unavailable");
		}
		if (phase === "active" && child && child.isValid() && child.scope.isCurrent()) {
			runtime = new BoundMemberRuntime({
				...prepared.input,
				scope: child.scope
			}, prepared.records, child, Object.freeze(bindings), ports.authority);
			runtime.lastFailure = error;
			try {
				ports.authority.publish(prepared.input, "unavailable");
			} catch {}
			return runtime;
		}
		const failures = [error];
		try {
			await rollback(prepared, child, bindings, ports, phase !== "active");
		} catch (cleanup) {
			failures.push(cleanup);
		}
		if (phase === "provisioning") try {
			await ports.journal.failed(prepared.input, prepared.records, "required member binding failed");
		} catch (recording) {
			failures.push(recording);
		}
		throw new AggregateError(failures, "required member binding failed");
	}
	try {
		await runtime.activate(signal);
	} catch (error) {
		try {
			ports.authority.publish(prepared.input, "unavailable");
		} catch {}
		runtime.lastFailure = error;
	}
	return runtime;
}
/** Serialized generation reconstruction; caller must settle previous owner before invoking. */
async function recoverBoundMember(input, recordsValue, registry, ports, signal) {
	const records = validateAttachmentRecords(recordsValue);
	const binders = records.map((record) => registry.resolve(record));
	signal.throwIfAborted();
	await ports.host.verifyPersistedChild(input, signal);
	const cleanupChild = async (child, bindings = []) => {
		await new BoundMemberRuntime({
			...input,
			scope: child.scope
		}, records, child, bindings, ports.authority).dispose(ports.cleanupTimeoutMs);
	};
	const child = await acquireBindingResource(() => ports.host.recover(input, signal), signal, cleanupChild);
	const bindings = [];
	try {
		for (let i = 0; i < records.length; i++) {
			signal.throwIfAborted();
			const binding = await acquireBindingResource(() => binders[i].recover({
				...input,
				scope: child.scope
			}, records[i].payload, signal), signal, async (late) => {
				const binding = await acceptBinding(late, ports.cleanupTimeoutMs);
				const deadline = new BindingDeadline(ports.cleanupTimeoutMs);
				const failures = [];
				try {
					try {
						binding.closeAdmission();
					} catch (error) {
						failures.push(error);
					}
					try {
						await deadline.run((remaining) => binding.settle(remaining));
					} catch (error) {
						failures.push(error);
					}
					try {
						await deadline.run((remaining) => binding.release(remaining));
					} catch (error) {
						failures.push(error);
					}
				} finally {
					deadline.finish();
				}
				if (failures.length) throw new AggregateError(failures, "late recovered binding cleanup failed");
			});
			bindings.push(await acceptBinding(binding, ports.cleanupTimeoutMs));
			signal.throwIfAborted();
		}
		const runtime = new BoundMemberRuntime({
			...input,
			scope: child.scope
		}, records, child, Object.freeze(bindings), ports.authority);
		try {
			await runtime.activate(signal);
		} catch (error) {
			runtime.lastFailure = error;
			try {
				ports.authority.publish(input, "unavailable");
			} catch {}
		}
		return runtime;
	} catch (error) {
		const runtime = new BoundMemberRuntime({
			...input,
			scope: child.scope
		}, records, child, bindings, ports.authority);
		try {
			await runtime.dispose(ports.cleanupTimeoutMs);
		} catch (cleanup) {
			throw new AggregateError([error, cleanup], "member recovery and cleanup failed");
		}
		throw error;
	}
}
async function acceptBinding(value, timeoutMs) {
	if (!value || typeof value.closeAdmission !== "function" || typeof value.settle !== "function" || typeof value.release !== "function") {
		const failures = [new TeamError("invalid disposable binding resource", "TEAM_BINDING_CONFLICT")];
		const deadline = new BindingDeadline(timeoutMs);
		try {
			if (typeof value?.closeAdmission === "function") try {
				value.closeAdmission();
			} catch (error) {
				failures.push(error);
			}
			if (typeof value?.settle === "function") try {
				await deadline.run((signal) => value.settle(signal));
			} catch (error) {
				failures.push(error);
			}
			if (typeof value?.release === "function") try {
				await deadline.run((signal) => value.release(signal));
			} catch (error) {
				failures.push(error);
			}
		} finally {
			deadline.finish();
		}
		throw new AggregateError(failures, "invalid disposable binding resource");
	}
	return value;
}
/** GAT-owned serialization: live retry does not reinstall; reconstruction settles the prior owner. */
var MemberBindingOwner = class {
	ports;
	entries = /* @__PURE__ */ new Map();
	queues = /* @__PURE__ */ new Map();
	constructor(ports) {
		this.ports = ports;
	}
	run(input, create, signal) {
		const key = JSON.stringify([input.teamId, input.memberId]);
		const operation = (this.queues.get(key) ?? Promise.resolve()).catch(() => void 0).then(async () => {
			signal.throwIfAborted();
			const existing = this.entries.get(key);
			if (existing?.generation === input.generation) {
				const runtime = await existing.operation;
				await runtime.activate(signal);
				return runtime;
			}
			if (existing) await (await existing.operation).dispose(this.ports.cleanupTimeoutMs);
			const next = create();
			this.entries.set(key, {
				generation: input.generation,
				operation: next
			});
			try {
				return await next;
			} catch (error) {
				this.entries.delete(key);
				throw error;
			}
		});
		this.queues.set(key, operation);
		operation.catch(() => void 0);
		return operation;
	}
};
//#endregion
//#region lib/types/index.js
/** Agent Teams service façade over roster, mailbox, task, and runtime lifecycle owners. */
var __runInitializers = function(thisArg, initializers, value) {
	var useValue = arguments.length > 2;
	for (var i = 0; i < initializers.length; i++) value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
	return useValue ? value : void 0;
};
var __esDecorate = function(ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
	function accept(f) {
		if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected");
		return f;
	}
	var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
	var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
	var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
	var _, done = false;
	for (var i = decorators.length - 1; i >= 0; i--) {
		var context = {};
		for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
		for (var p in contextIn.access) context.access[p] = contextIn.access[p];
		context.addInitializer = function(f) {
			if (done) throw new TypeError("Cannot add initializers after decoration has completed");
			extraInitializers.push(accept(f || null));
		};
		var result = (0, decorators[i])(kind === "accessor" ? {
			get: descriptor.get,
			set: descriptor.set
		} : descriptor[key], context);
		if (kind === "accessor") {
			if (result === void 0) continue;
			if (result === null || typeof result !== "object") throw new TypeError("Object expected");
			if (_ = accept(result.get)) descriptor.get = _;
			if (_ = accept(result.set)) descriptor.set = _;
			if (_ = accept(result.init)) initializers.unshift(_);
		} else if (_ = accept(result)) if (kind === "field") initializers.unshift(_);
		else descriptor[key] = _;
	}
	if (target) Object.defineProperty(target, contextIn.name, descriptor);
	done = true;
};
const DEFAULT_MAX_MEMBERS = 8;
const DEFAULT_MAX_TASKS = 256;
const DEFAULT_MAX_PENDING_MESSAGES = 64;
const DEFAULT_MAX_MESSAGE_BYTES = 65536;
const DEFAULT_DISPOSAL_TIMEOUT_MS = 5e3;
/** Validate one positive safe-integer deployment limit. */
function positiveLimit(name, value) {
	if (!Number.isSafeInteger(value) || value < 1) throw new TeamError(`${name} must be a positive safe integer`, "TEAM_INVALID_CONFIG");
	return value;
}
/** Agent Teams service backed by the exact live Lead Session log. */
let TeamService = (() => {
	let _classSuper = TypertRemoteService;
	let _instanceExtraInitializers = [];
	let _remoteApproveMemberAdd_decorators;
	let _remoteView_decorators;
	let _remoteEnable_decorators;
	let _remoteCreateMission_decorators;
	let _remoteListMissions_decorators;
	let _remoteGetMission_decorators;
	let _remoteApproveMission_decorators;
	let _remoteCloseMission_decorators;
	let _remoteRevokeMission_decorators;
	let _remoteCreateTask_decorators;
	let _remoteUpdateTask_decorators;
	let _remoteApprovePlan_decorators;
	let _remoteImportApprovedPlan_decorators;
	let _remoteReportWork_decorators;
	return class TeamService extends _classSuper {
		static {
			const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(_classSuper[Symbol.metadata] ?? null) : void 0;
			_remoteApproveMemberAdd_decorators = [Remote("approveMemberAdd")];
			_remoteView_decorators = [Remote("view")];
			_remoteEnable_decorators = [Remote("enable")];
			_remoteCreateMission_decorators = [Remote("createMission")];
			_remoteListMissions_decorators = [Remote("listMissions")];
			_remoteGetMission_decorators = [Remote("getMission")];
			_remoteApproveMission_decorators = [Remote("approveMission")];
			_remoteCloseMission_decorators = [Remote("closeMission")];
			_remoteRevokeMission_decorators = [Remote("revokeMission")];
			_remoteCreateTask_decorators = [Remote("createTask")];
			_remoteUpdateTask_decorators = [Remote("updateTask")];
			_remoteApprovePlan_decorators = [Remote("approvePlan")];
			_remoteImportApprovedPlan_decorators = [Remote("importApprovedPlan")];
			_remoteReportWork_decorators = [Remote("reportWork")];
			__esDecorate(this, null, _remoteApproveMemberAdd_decorators, {
				kind: "method",
				name: "remoteApproveMemberAdd",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteApproveMemberAdd" in obj,
					get: (obj) => obj.remoteApproveMemberAdd
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteView_decorators, {
				kind: "method",
				name: "remoteView",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteView" in obj,
					get: (obj) => obj.remoteView
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteEnable_decorators, {
				kind: "method",
				name: "remoteEnable",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteEnable" in obj,
					get: (obj) => obj.remoteEnable
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteCreateMission_decorators, {
				kind: "method",
				name: "remoteCreateMission",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteCreateMission" in obj,
					get: (obj) => obj.remoteCreateMission
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteListMissions_decorators, {
				kind: "method",
				name: "remoteListMissions",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteListMissions" in obj,
					get: (obj) => obj.remoteListMissions
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteGetMission_decorators, {
				kind: "method",
				name: "remoteGetMission",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteGetMission" in obj,
					get: (obj) => obj.remoteGetMission
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteApproveMission_decorators, {
				kind: "method",
				name: "remoteApproveMission",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteApproveMission" in obj,
					get: (obj) => obj.remoteApproveMission
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteCloseMission_decorators, {
				kind: "method",
				name: "remoteCloseMission",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteCloseMission" in obj,
					get: (obj) => obj.remoteCloseMission
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteRevokeMission_decorators, {
				kind: "method",
				name: "remoteRevokeMission",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteRevokeMission" in obj,
					get: (obj) => obj.remoteRevokeMission
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteCreateTask_decorators, {
				kind: "method",
				name: "remoteCreateTask",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteCreateTask" in obj,
					get: (obj) => obj.remoteCreateTask
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteUpdateTask_decorators, {
				kind: "method",
				name: "remoteUpdateTask",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteUpdateTask" in obj,
					get: (obj) => obj.remoteUpdateTask
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteApprovePlan_decorators, {
				kind: "method",
				name: "remoteApprovePlan",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteApprovePlan" in obj,
					get: (obj) => obj.remoteApprovePlan
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteImportApprovedPlan_decorators, {
				kind: "method",
				name: "remoteImportApprovedPlan",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteImportApprovedPlan" in obj,
					get: (obj) => obj.remoteImportApprovedPlan
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			__esDecorate(this, null, _remoteReportWork_decorators, {
				kind: "method",
				name: "remoteReportWork",
				static: false,
				private: false,
				access: {
					has: (obj) => "remoteReportWork" in obj,
					get: (obj) => obj.remoteReportWork
				},
				metadata: _metadata
			}, null, _instanceExtraInitializers);
			if (_metadata) Object.defineProperty(this, Symbol.metadata, {
				enumerable: true,
				configurable: true,
				writable: true,
				value: _metadata
			});
		}
		static inject = [
			"agents",
			"sessions",
			"sessionPersistence",
			"sessionProjections",
			"subagents",
			"llm"
		];
		static Config = z.object({
			maxMembers: z.number().step(1).min(1).default(DEFAULT_MAX_MEMBERS),
			maxTasks: z.number().step(1).min(1).default(DEFAULT_MAX_TASKS),
			maxPendingMessagesPerMember: z.number().step(1).min(1).default(DEFAULT_MAX_PENDING_MESSAGES),
			maxMessageBytes: z.number().step(1).min(1).default(DEFAULT_MAX_MESSAGE_BYTES),
			disposalTimeoutMs: z.number().step(1).min(1).default(DEFAULT_DISPOSAL_TIMEOUT_MS)
		});
		/** Validated deployment limits used by every Team operation. */
		config = __runInitializers(this, _instanceExtraInitializers);
		activity;
		lifecycle;
		journal;
		roster;
		mailbox;
		authority;
		missions;
		tasks;
		work;
		approvalPreflights = /* @__PURE__ */ new Set();
		memberAddGrants = /* @__PURE__ */ new WeakMap();
		initializers = /* @__PURE__ */ new Set();
		enabling = /* @__PURE__ */ new WeakMap();
		constructor(ctx, config = {}) {
			super(ctx, "agentTeams");
			this.config = {
				maxMembers: positiveLimit("maxMembers", config.maxMembers ?? DEFAULT_MAX_MEMBERS),
				maxTasks: positiveLimit("maxTasks", config.maxTasks ?? DEFAULT_MAX_TASKS),
				maxPendingMessagesPerMember: positiveLimit("maxPendingMessagesPerMember", config.maxPendingMessagesPerMember ?? DEFAULT_MAX_PENDING_MESSAGES),
				maxMessageBytes: positiveLimit("maxMessageBytes", config.maxMessageBytes ?? DEFAULT_MAX_MESSAGE_BYTES),
				disposalTimeoutMs: positiveLimit("disposalTimeoutMs", config.disposalTimeoutMs ?? DEFAULT_DISPOSAL_TIMEOUT_MS)
			};
			this.activity = new TeamActivity();
			this.lifecycle = new TeamRuntimeLifecycle(this.config.disposalTimeoutMs);
			this.journal = new TeamJournal(ctx, (root) => {
				this.activity.notify(TeamId(root.id));
			}, () => this.lifecycle.assertOpen());
			this.authority = new TeamExecutionAuthority(this.journal);
			this.roster = new TeamRoster(ctx, this.journal, this.lifecycle, this.config.maxMembers, (agent) => this.assertExecution(agent), (caller, request) => this.consumeMemberAdd(caller, request));
			this.mailbox = new TeamMailbox(ctx, this.journal, this.roster, this.lifecycle, this.config.maxPendingMessagesPerMember, this.config.maxMessageBytes, (agent) => this.assertExecution(agent));
			this.missions = new TeamMissionBoard(this.journal);
			this.tasks = new TeamTaskBoard(this.journal, this.config.maxTasks, (caller, taskId) => this.authority.assertTaskOperation(caller, this.roster.membership(caller), taskId), (caller, _membership, taskId) => this.authority.validateClaim(caller, this.roster.membership(caller), taskId), (caller, _membership, taskId) => this.authority.bindTask(caller, this.roster.membership(caller), taskId));
			this.work = new TeamWorkBoard(this.journal, (caller, taskId) => this.assertExecution(caller, taskId));
			ctx.effect(() => {
				const disposeProjection = ctx.root.sessionProjections.register(teamProjectionDefinition);
				return async () => {
					try {
						await this.disposeRuntime();
					} finally {
						disposeProjection();
					}
				};
			}, "agentTeams.runtimeLifecycle()");
			const guardedAgents = /* @__PURE__ */ new WeakSet();
			const installExecutionGuard = (agent) => {
				if (guardedAgents.has(agent)) return;
				guardedAgents.add(agent);
				const initialMembership = this.roster.tryMembership(agent);
				let executionRequired = initialMembership !== void 0 && this.journal.state(initialMembership.root).members.length > 0;
				ctx.effect(() => {
					const removeGuard = agent.ctx.agents.guardExecution(agent, () => {
						const membership = this.roster.tryMembership(agent);
						const parentId = agent.session.header.parentSession;
						const parent = parentId === void 0 ? void 0 : this.ctx.agents.get(parentId);
						if (parent !== void 0 && this.journal.state(parent).members.some((member) => member.id === agent.id) || membership && this.journal.state(membership.root).members.length > 0) executionRequired = true;
						if (executionRequired) this.assertExecution(agent);
					});
					return async () => {
						this.lifecycle.close();
						try {
							await this.disposeRuntime();
						} finally {
							removeGuard();
						}
					};
				}, "agentTeams.exactExecutionAdmission()");
			};
			ctx.on("agent/created", ({ agent }) => {
				installExecutionGuard(agent);
			});
			for (const agent of ctx.agents.list()) installExecutionGuard(agent);
			ctx.on("agent/prepare-prompt", async ({ agent }) => {
				const membership = this.roster.tryMembership(agent);
				if (membership && this.journal.state(membership.root).members.length > 0) this.assertExecution(agent);
			});
			ctx.on("agent/model-admission", async ({ agent }) => {
				const membership = this.roster.tryMembership(agent);
				if (membership && this.journal.state(membership.root).members.length > 0) this.assertExecution(agent);
			});
			ctx.on("session/event", (session, event) => {
				this.mailbox.observeSessionEvent(session, event);
			});
			ctx.on("agent/session-start", ({ agent }) => {
				this.scheduleRecovery(agent);
			});
			ctx.on("agent/status", ({ agent }) => {
				const membership = this.roster.tryMembership(agent);
				if (membership !== void 0) this.activity.notify(membership.id);
			});
			for (const agent of ctx.agents.list()) this.scheduleRecovery(agent);
		}
		/**
		* Set the additional exact HUMAN current-plan requirement for non-simple mode.
		* @param requireCurrentPlan - whether admission additionally requires the exact current HUMAN-approved Team plan.
		*/
		configureExecutionPolicy(requireCurrentPlan) {
			this.authority.configure(requireCurrentPlan);
		}
		/**
		* Host-only binding of an opaque lease to the exact live Agent generation.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @param request - explicit mission identity/revision and optional claimed task selected by trusted host code.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		bindExecution(caller, request) {
			this.authority.bind(caller, this.roster.membership(caller), request);
		}
		/**
		* Revalidate exact canonical mission and task authorization before execution.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @param taskId - optional exact claimed canonical task to revalidate.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		assertExecution(caller, taskId) {
			this.authority.assert(caller, this.roster.membership(caller), taskId);
		}
		/**
		* Release one prepared member initial item after its host-selected exact lease is bound.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @param signal - cancellation checked before admission and during host preparation.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		async activateMember(caller, signal) {
			return await this.lifecycle.admitMutation(async () => {
				const combined = AbortSignal.any([signal, this.lifecycle.signal]);
				this.assertExecution(caller);
				await this.roster.activateMember(caller, combined);
			});
		}
		/**
		* Cold-recover one explicitly selected member and bind its exact host-selected mission scope.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @param targetName - explicit durable active member name selected by trusted host control.
		* @param request - explicit mission identity/revision and optional claimed task for the recovered generation.
		* @param signal - cancellation checked before admission and during host preparation.
		* @returns the newly recovered exact Agent after binding and gated activation.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		async recoverMember(caller, targetName, request, signal) {
			return await this.lifecycle.admitMutation(async () => {
				const combined = AbortSignal.any([signal, this.lifecycle.signal]);
				const membership = this.roster.membership(caller);
				if (membership.role !== "lead") throw new TeamError("only Lead host control may recover a member", "TEAM_LEAD_REQUIRED");
				this.assertExecution(caller);
				const member = this.journal.state(membership.root).members.find((value) => value.name === targetName && value.phase === "active");
				if (!member) throw new TeamError("exact active member is missing", "TEAM_MEMBER_NOT_FOUND");
				const agent = await this.roster.recoverMember(membership.root, member.id, combined);
				this.bindExecution(agent, request);
				await this.activateMember(agent, combined);
				return agent;
			});
		}
		/**
		* Report a safe authority diagnostic for tools without exposing lease fields.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @returns the denial reason, or undefined when the exact current scope is authorized.
		*/
		executionDiagnostic(caller) {
			try {
				this.assertExecution(caller);
				return;
			} catch (error) {
				return errorMessage(error);
			}
		}
		/**
		* Resolve one exact live Agent's Team role.
		* @param agent - exact live Agent used as the authority credential.
		* @returns its root, Team identity, role, and model-facing name.
		*/
		membership(agent) {
			return this.roster.membership(agent);
		}
		/**
		* List the runtime-enriched roster visible to one Team member.
		* @param agent - exact live Team member.
		* @returns Lead and teammate rows in creation order.
		*/
		listMembers(agent) {
			return this.roster.list(this.roster.membership(agent));
		}
		memberAddDigest(request) {
			return payloadSha256(JSON.parse(canonicalJson({
				name: request.name,
				description: request.description,
				prompt: request.prompt,
				context: request.context,
				provider: request.provider,
				...request.agentOptions === void 0 ? {} : { agentOptions: request.agentOptions },
				attachments: request.attachments ?? []
			})));
		}
		grantMemberAdd(caller, request) {
			const grants = this.memberAddGrants.get(caller) ?? /* @__PURE__ */ new Set();
			grants.add(this.memberAddDigest(request));
			this.memberAddGrants.set(caller, grants);
		}
		consumeMemberAdd(caller, request) {
			this.journal.assertCommitted(this.roster.membership(caller).root);
			const digest = this.memberAddDigest(request);
			if (!this.memberAddGrants.get(caller)?.delete(digest)) throw new TeamError("exact host-attested HUMAN member-add approval required", "TEAM_MEMBER_ADD_APPROVAL_REQUIRED");
		}
		/**
		* Approve one exact immutable member specification; the one-use grant permits quarantine only.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @param request - exact immutable member specification covered by the one-use authenticated control receipt.
		* @returns confirmation after durable approval; the grant permits quarantine only.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		async approveMemberAdd(caller, request) {
			const membership = this.roster.membership(caller);
			if (membership.role !== "lead") throw new TeamError("only Lead control may add a member", "TEAM_LEAD_REQUIRED");
			return this.lifecycle.admitMutation(() => this.journal.transact(membership.root.id, async () => {
				let receipt;
				try {
					receipt = consumeHumanControl("agentTeams/approveMemberAdd", caller, request);
				} catch (cause) {
					throw new TeamError("exact HUMAN member-add control receipt required", "TEAM_HUMAN_CONTROL_REQUIRED", { cause });
				}
				await this.journal.appendAndFlush(membership.root, "team/member-add-approved", {
					version: 1,
					teamId: membership.id,
					receiptId: receipt.id,
					digest: receipt.digest,
					specDigest: this.memberAddDigest(request),
					name: request.name
				});
				this.grantMemberAdd(caller, request);
				return { approved: true };
			}));
		}
		/**
		* Host-attested HUMAN member-add action; arbitrary model specs cannot mint grants.
		* @param agent - exact live Agent resolved by the host or Gateway.
		* @param request - exact immutable member specification covered by the authenticated HTTP action.
		* @returns durable approval confirmation; child activation requires its separate exact lease.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		remoteApproveMemberAdd(agent, request) {
			return this.approveMemberAdd(agent, request);
		}
		/**
		* Create one named, continuable direct child of the Team Lead.
		* @param caller - exact live Lead Agent.
		* @param request - immutable name, description, prompt, context mode, provider, and cancellation.
		* @returns the active roster row.
		*/
		async spawnTeammate(caller, request) {
			return await this.roster.spawn(caller, request);
		}
		/**
		* Queue one durable peer message, then attempt immediate delivery.
		* @param caller - exact live sending Team member.
		* @param request - target name, content, and pre-queue cancellation.
		* @returns durable message identity and immediate-delivery observation.
		*/
		async sendMessage(caller, request) {
			return await this.mailbox.send(caller, request);
		}
		/**
		* Create one independently governed durable mission.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @param request - mission title/objective and empty canonical task-reference plan.
		* @returns the new durable draft mission without executable approval.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		async createMission(caller, request) {
			return await this.lifecycle.admitMutation(async () => this.missions.create(this.roster.membership(caller), request));
		}
		/**
		* Return one mission including its mission-local task set.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @param id - explicit mission identity in this Team.
		* @returns a detached mission view containing canonical task references.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		getMission(caller, id) {
			return this.missions.get(this.roster.membership(caller), id);
		}
		/**
		* List the Team's independently governed missions.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @returns detached mission views for this exact Team.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		listMissions(caller) {
			return this.missions.list(this.roster.membership(caller));
		}
		/**
		* Approve exactly the current revision of one mission.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
		* @returns the durably approved exact revision with authenticated provenance.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		async approveMission(caller, request) {
			return await this.lifecycle.admitMutation(async () => this.missions.approve(caller, this.roster.membership(caller), request));
		}
		/**
		* Close one exact mission revision using authenticated HUMAN control.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
		* @returns the durably closed mission with previous leases invalidated.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		async closeMission(caller, request) {
			return this.lifecycle.admitMutation(() => this.missions.end(caller, this.roster.membership(caller), request, "closeMission"));
		}
		/**
		* Revoke one exact mission revision using authenticated HUMAN control.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
		* @returns the durably revoked mission with previous leases invalidated.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		async revokeMission(caller, request) {
			return this.lifecycle.admitMutation(() => this.missions.end(caller, this.roster.membership(caller), request, "revokeMission"));
		}
		/**
		* Create one unowned pending task in the Team Lead log.
		* @param caller - exact live Team member creating the task.
		* @param request - explicit mission association, task text, blockers, and advisory write scopes.
		* @returns the revision-one task view.
		*/
		async createTask(caller, request) {
			return await this.lifecycle.admitMutation(() => this.tasks.create(this.roster.membership(caller), request));
		}
		/**
		* Return one task, including a deleted tombstone.
		* @param caller - exact live Team member reading the task.
		* @param id - Team-local task identity.
		* @returns the latest task value and derived readiness diagnostics.
		*/
		getTask(caller, id) {
			return this.tasks.get(this.roster.membership(caller), id);
		}
		/**
		* List current non-deleted tasks in numeric creation order.
		* @param caller - exact live Team member reading the board.
		* @returns detached current task views.
		*/
		listTasks(caller) {
			return this.tasks.list(this.roster.membership(caller));
		}
		/**
		* Compare-and-set one authorized task transition.
		* @param caller - exact live Team member authorizing the mutation.
		* @param request - task identity, expected revision, action, and action fields.
		* @returns the committed next task revision.
		*/
		async updateTask(caller, request) {
			return await this.lifecycle.admitMutation(() => this.tasks.update(caller, this.roster.membership(caller), request));
		}
		/**
		* Commit HUMAN approval of the exact current non-empty structural plan revision.
		* @param caller - exact live Lead Agent selected by the Web Remote authority.
		* @param request - revision displayed to the approving HUMAN.
		* @returns the committed approval snapshot.
		*/
		async approvePlan(caller, request) {
			return await this.lifecycle.admitMutation(async () => {
				const membership = this.roster.membership(caller);
				if (membership.role !== "lead") throw new TeamError("only the Team Lead can approve a plan", "TEAM_LEAD_REQUIRED");
				return await this.journal.transact(membership.root.id, async () => {
					const state = this.journal.state(membership.root);
					if (!state.tasks.some((task) => task.status !== "deleted")) throw new TeamError("an empty Team plan cannot be approved", "TEAM_PLAN_EMPTY");
					if (!Number.isSafeInteger(request.approvedRevision) || request.approvedRevision < 0) throw new TeamError("approvedRevision must be a non-negative safe integer", "TEAM_INVALID_ARGUMENT");
					if (request.approvedRevision !== state.planRevision || state.planApproval !== void 0 && request.approvedRevision <= state.planApproval.approvedRevision) throw new TeamError(`stale Team plan revision ${request.approvedRevision}; current revision is ${state.planRevision}`, "TEAM_PLAN_STALE_REVISION");
					const diagnostics = [...this.approvalPreflights].flatMap((preflight) => [...preflight(caller, this.remoteView(caller))]);
					if (diagnostics.length > 0) throw new TeamError(`Team plan preflight failed: ${diagnostics.join("; ")}`, "TEAM_PLAN_PREFLIGHT_FAILED");
					let receipt;
					try {
						receipt = consumeHumanControl("agentTeams/approvePlan", caller, request);
					} catch (cause) {
						throw new TeamError("exact HUMAN plan control receipt required", "TEAM_HUMAN_CONTROL_REQUIRED", { cause });
					}
					const approval = {
						approvedRevision: request.approvedRevision,
						eventId: receipt.id,
						digest: receipt.digest,
						humanSessionId: receipt.sessionId
					};
					await this.journal.appendAndFlush(membership.root, "team/plan-approved", {
						version: 3,
						teamId: TeamId(membership.root.id),
						approval
					});
					return approval;
				});
			});
		}
		/**
		* * Import the latest successful HUMAN-approved DSH plan and approve its exact
		* post-import revision in one serialized Lead-log batch.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @param request - explicit target mission identity for canonical imported task association.
		* @returns the approval of the exact post-import canonical plan revision.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		async importApprovedPlanAndApprove(caller, request) {
			return this.lifecycle.admitMutation(async () => {
				const membership = this.roster.membership(caller);
				if (membership.role !== "lead") throw new TeamError("only the Team Lead can approve a plan", "TEAM_LEAD_REQUIRED");
				return this.journal.transact(membership.root.id, async () => {
					const state = this.journal.state(membership.root);
					const mission = state.missions.find((value) => value.id === request.missionId);
					if (!mission || mission.status === "closed" || mission.status === "revoked") throw new TeamError("import requires an explicit live canonical mission", "TEAM_TASK_MISSION_REQUIRED");
					const subjects = approvedPlanTaskSubjects(membership.root.session.snapshotEvents());
					const imported = this.tasks.prepareApprovedPlanImport(state, subjects, mission.id);
					const postRevision = state.planRevision + imported.length;
					if (!Number.isSafeInteger(postRevision)) throw new TeamError("Team plan revision space exhausted", "TEAM_PLAN_IMPORT_INVALID");
					const postState = {
						...state,
						planRevision: postRevision,
						planPhase: imported.length ? "draft" : state.planPhase,
						tasks: [...state.tasks, ...imported]
					};
					if (!postState.tasks.some((task) => task.status !== "deleted")) throw new TeamError("an empty Team plan cannot be approved", "TEAM_PLAN_EMPTY");
					if (state.planApproval && postRevision <= state.planApproval.approvedRevision) throw new TeamError("Team plan approval is stale", "TEAM_PLAN_STALE_REVISION");
					const diagnostics = [...this.approvalPreflights].flatMap((preflight) => [...preflight(caller, this.teamView(membership, postState))]);
					if (diagnostics.length) throw new TeamError(`Team plan preflight failed: ${diagnostics.join("; ")}`, "TEAM_PLAN_PREFLIGHT_FAILED");
					let receipt;
					try {
						receipt = consumeHumanControl("agentTeams/importApprovedPlan", caller, request);
					} catch (cause) {
						throw new TeamError("exact HUMAN import control receipt required", "TEAM_HUMAN_CONTROL_REQUIRED", { cause });
					}
					const approval = {
						approvedRevision: postRevision,
						eventId: receipt.id,
						digest: receipt.digest,
						humanSessionId: receipt.sessionId
					};
					await this.journal.appendManyAndFlush(membership.root, [...imported.map((task) => ({
						type: "team/task",
						data: {
							version: 3,
							teamId: TeamId(membership.root.id),
							task
						}
					})), {
						type: "team/plan-approved",
						data: {
							version: 3,
							teamId: TeamId(membership.root.id),
							approval
						}
					}]);
					return approval;
				});
			});
		}
		/**
		* Register one live capability-envelope check at the HUMAN approval boundary.
		* @param preflight - synchronous check over the exact caller and current Team view.
		* @returns disposer that removes this approval check.
		*/
		registerApprovalPreflight(preflight) {
			this.approvalPreflights.add(preflight);
			return () => {
				this.approvalPreflights.delete(preflight);
			};
		}
		/**
		* Register the host initializer used by the session-scoped Enable action.
		* @param initializer - trusted default-roster producer evaluated before any member creation.
		* @returns an unregister function for this exact initializer.
		*/
		registerInitializer(initializer) {
			if (this.initializers.size > 0) throw new Error("an Agent Team initializer is already registered");
			this.initializers.add(initializer);
			return () => {
				this.initializers.delete(initializer);
			};
		}
		/**
		* Enable this Lead Session's Team once, provisioning its configured members.
		* @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
		* @param signal - cancellation checked before admission and during host preparation.
		* @returns the provisioned default roster; children remain gated until exact execution authorization.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		async enable(caller, signal) {
			this.lifecycle.assertOpen();
			const membership = this.roster.membership(caller);
			if (membership.role !== "lead") throw new TeamError("only the Team Lead can enable Agent Team", "TEAM_LEAD_REQUIRED");
			signal.throwIfAborted();
			const inFlight = this.enabling.get(membership.root);
			if (inFlight !== void 0) return await inFlight;
			const existing = this.roster.list(membership).filter((member) => member.role === "teammate");
			if (existing.length > 0) return {
				enabled: true,
				alreadyEnabled: true,
				source: "existing",
				diagnostics: [],
				members: existing
			};
			const [initializer] = this.initializers;
			if (initializer === void 0) throw new TeamError("Agent Team initializer is unavailable", "TEAM_INVALID_CONFIG");
			try {
				consumeHumanControl("agentTeams/enable", caller, void 0);
			} catch (cause) {
				throw new TeamError("authenticated HUMAN Enable control required", "TEAM_HUMAN_CONTROL_REQUIRED", { cause });
			}
			const operation = this.lifecycle.admitMutation(async () => {
				const combined = AbortSignal.any([signal, this.lifecycle.signal]);
				const initialized = await initializer(membership.root, combined);
				const prepared = await this.validateInitialization(membership.root, initialized, combined);
				const members = [];
				for (const spec of prepared.members) {
					combined.throwIfAborted();
					const spawnRequest = {
						name: spec.name,
						description: spec.description,
						prompt: spec.initialTask,
						context: spec.context,
						provider: spec.continuationProvider,
						...spec.agentOptions === void 0 ? {} : { agentOptions: spec.agentOptions },
						attachments: spec.attachments ?? [],
						signal: combined
					};
					this.grantMemberAdd(membership.root, spawnRequest);
					const spawned = await this.roster.spawn(membership.root, spawnRequest);
					members.push(spawned.member);
				}
				return {
					enabled: true,
					alreadyEnabled: false,
					source: prepared.source,
					diagnostics: prepared.diagnostics,
					members
				};
			});
			this.enabling.set(membership.root, operation);
			operation.then(() => {
				this.enabling.delete(membership.root);
			}, () => {
				this.enabling.delete(membership.root);
			});
			return await operation;
		}
		/** Fully preflight normalized specs before any row/child, preserving default adapter behavior. */
		async validateInitialization(lead, input, signal) {
			if (!input || !Array.isArray(input.members) || input.members.length < 1 || input.members.length > this.config.maxMembers) throw new TeamError("invalid normalized Team roster", "TEAM_INVALID_CONFIG");
			const source = requiredText(input.source, "initializer source", 200);
			if (!Array.isArray(input.diagnostics) || input.diagnostics.length > 64 || input.diagnostics.some((value) => typeof value !== "string" || value.length > 4096)) throw new TeamError("invalid initializer diagnostics", "TEAM_INVALID_CONFIG");
			const diagnostics = [...input.diagnostics];
			const names = /* @__PURE__ */ new Set();
			const specs = input.members.map((spec) => {
				if (!spec || typeof spec.name !== "string" || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(spec.name) || spec.name.length > 64 || spec.name === "lead" || names.has(spec.name)) throw new TeamError("invalid or duplicate normalized member name", "TEAM_INVALID_MEMBER_NAME");
				names.add(spec.name);
				const description = requiredText(spec.description, "description", 200);
				const continuationProvider = requiredText(spec.continuationProvider, "continuation provider", 200);
				if (spec.context !== "fresh" && spec.context !== "fork" || !Array.isArray(spec.initialTask) || spec.initialTask.length === 0) throw new TeamError("invalid normalized member context/task", "TEAM_INVALID_CONFIG");
				let initialTask;
				try {
					initialTask = validateInitialTask(structuredClone(spec.initialTask));
				} catch {
					throw new TeamError("invalid normalized member initial task", "TEAM_INVALID_CONFIG");
				}
				if (Buffer.byteLength(JSON.stringify(initialTask), "utf8") > this.config.maxMessageBytes) throw new TeamError("initial member task exceeds byte limit", "TEAM_INVALID_CONFIG");
				const attachments = validateAttachmentRequests(spec.attachments ?? []);
				if (attachments.length > 0) throw new TeamError("required attachments need a qualified reserved-child host", "TEAM_BINDER_UNAVAILABLE");
				if (this.ctx.subagents.getProvider(continuationProvider) === void 0) throw new TeamError("normalized continuation provider unavailable", "TEAM_INVALID_CONFIG");
				return {
					...spec,
					description,
					continuationProvider,
					initialTask,
					attachments,
					...spec.agentOptions === void 0 ? {} : { agentOptions: structuredClone(spec.agentOptions) }
				};
			});
			for (const spec of specs) {
				signal.throwIfAborted();
				const provider = spec.agentOptions?.provider ?? lead.options.provider;
				const model = spec.agentOptions?.model ?? lead.options.model;
				if (provider === void 0 || model === void 0) throw new TeamError("normalized model route unavailable", "TEAM_INVALID_CONFIG");
				await this.ctx.llm.resolveCallConfig({
					provider,
					model,
					...spec.agentOptions?.reasoningEffort === void 0 ? {} : { reasoningEffort: spec.agentOptions.reasoningEffort }
				}, signal);
			}
			return {
				source,
				diagnostics,
				members: specs
			};
		}
		/**
		* Report the exact caller's latest durable work state.
		* @param caller - exact live Team member reporting current work.
		* @param request - durable state, summary, optional reason/task, and affected files.
		* @returns the committed authoritative work view.
		*/
		async reportWork(caller, request) {
			return await this.lifecycle.admitMutation(async () => {
				return await this.work.report(caller, this.roster.membership(caller), request);
			});
		}
		/**
		* Wait for the next Team-domain or member-status change.
		* @param caller - exact live Team member waiting for activity.
		* @param timeoutMs - bounded wait duration from ten seconds through one hour.
		* @param signal - caller cancellation for the wait only.
		* @returns one observed change or a timeout result.
		*/
		async waitForChange(caller, timeoutMs, signal) {
			const membership = this.roster.membership(caller);
			return await this.activity.wait(membership.id, timeoutMs, signal);
		}
		/**
		* Interrupt one live teammate turn without clearing its pending inbox.
		* @param caller - exact live Lead Agent.
		* @param targetName - durable teammate name.
		* @returns the target status sampled before cancellation.
		*/
		interrupt(caller, targetName) {
			return this.roster.interrupt(caller, targetName);
		}
		/**
		* Resolve a caller without throwing, used by scoped-tool installation and observers.
		* @param agent - candidate exact live Agent.
		* @returns Team membership, or undefined for non-Team subagents and stale identities.
		*/
		tryMembership(agent) {
			return this.roster.tryMembership(agent);
		}
		/** Build a Team view from either committed or fully prepared transactional state. */
		teamView(membership, state) {
			return {
				enabled: state.members.length > 0,
				planRevision: state.planRevision,
				planPhase: state.planPhase,
				...state.planApproval === void 0 ? {} : { planApproval: structuredClone(state.planApproval) },
				...state.missions.length === 0 ? {} : { missions: this.missions.list(membership) },
				work: state.work.map((item) => ({
					...item,
					files: [...item.files]
				})),
				members: this.roster.list(membership),
				tasks: this.tasks.views(membership.root, state)
			};
		}
		/**
		* Read the current roster and non-deleted task board through the generated Remote API.
		* @param agent - exact live Team member used as the authority credential.
		* @returns detached current roster and task views.
		*/
		remoteView(agent) {
			const membership = this.roster.membership(agent);
			return this.teamView(membership, this.journal.state(membership.root));
		}
		/**
		* Enable and provision this Lead Session's Agent Team through the generated Web Remote API.
		* @param agent - exact live Agent resolved by the host or Gateway.
		* @param signal - cancellation checked before admission and during host preparation.
		* @returns the default-roster provisioning result; child model admission remains separately gated.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		remoteEnable(agent, signal) {
			return this.enable(agent, signal);
		}
		/**
		* Create one mission through the generated Web Remote API.
		* @param agent - exact live Agent resolved by the host or Gateway.
		* @param request - mission title/objective and empty canonical task-reference plan.
		* @returns the draft mission or a typed business rejection.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		remoteCreateMission(agent, request) {
			return this.missionMutationResult(this.createMission(agent, request));
		}
		/**
		* List independently governed missions through the generated Web Remote API.
		* @param agent - exact live Agent resolved by the host or Gateway.
		* @returns detached mission views for this Team.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		remoteListMissions(agent) {
			return this.listMissions(agent);
		}
		/**
		* Get one mission through the generated Web Remote API.
		* @param agent - exact live Agent resolved by the host or Gateway.
		* @param id - explicit mission identity in this Team.
		* @returns the detached explicitly requested mission.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		remoteGetMission(agent, id) {
			return this.getMission(agent, id);
		}
		/**
		* Approve one exact mission revision through the generated Web Remote API.
		* @param agent - exact live Agent resolved by the host or Gateway.
		* @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
		* @returns the committed approval or a typed business rejection.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		remoteApproveMission(agent, request) {
			return this.missionMutationResult(this.approveMission(agent, request));
		}
		/**
		* Close one exact mission revision through authenticated Web control.
		* @param agent - exact live Agent resolved by the host or Gateway.
		* @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
		* @returns the committed closure or a typed business rejection.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		remoteCloseMission(agent, request) {
			return this.missionMutationResult(this.closeMission(agent, request));
		}
		/**
		* Revoke one exact mission revision through authenticated Web control.
		* @param agent - exact live Agent resolved by the host or Gateway.
		* @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
		* @returns the committed revocation or a typed business rejection.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		remoteRevokeMission(agent, request) {
			return this.missionMutationResult(this.revokeMission(agent, request));
		}
		/**
		* Create one shared task through the generated Remote API.
		* @param agent - exact live Team member creating the task.
		* @param request - explicit mission association, task text, blockers, and advisory write scopes.
		* @returns the revision-one task or a typed Team rejection.
		*/
		remoteCreateTask(agent, request) {
			return this.taskMutationResult(this.createTask(agent, request));
		}
		/**
		* Apply one task mutation and preserve Team rejections as business results.
		* @param agent - exact live Team member authorizing the mutation.
		* @param request - task identity, expected revision, action, and action fields.
		* @returns the committed task or a typed Team rejection.
		*/
		remoteUpdateTask(agent, request) {
			return this.taskMutationResult(this.updateTask(agent, request));
		}
		/**
		* Approve one exact displayed plan revision through the generated Web Remote API.
		* @param agent - exact live Lead Agent used as the authority credential.
		* @param request - revision displayed to the approving HUMAN.
		* @returns the committed approval or a typed plan conflict/rejection.
		*/
		async remoteApprovePlan(agent, request) {
			try {
				return {
					ok: true,
					value: await this.approvePlan(agent, request)
				};
			} catch (error) {
				if (!(error instanceof TeamError)) throw error;
				return {
					ok: false,
					error: {
						code: error.code === "TEAM_PLAN_STALE_REVISION" ? "team-plan-conflict" : error.code === "TEAM_PLAN_PREFLIGHT_FAILED" ? "team-preflight-rejected" : "team-rejected",
						message: error.message
					}
				};
			}
		}
		/**
		* Import the latest approved DSH plan and approve it through one Web Remote action.
		* @param agent - exact live Agent resolved by the host or Gateway.
		* @param request - explicit target mission identity reviewed by HUMAN control.
		* @returns the committed plan approval or a typed import/preflight rejection.
		* @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
		*/
		async remoteImportApprovedPlan(agent, request) {
			try {
				return {
					ok: true,
					value: await this.importApprovedPlanAndApprove(agent, request)
				};
			} catch (error) {
				if (!(error instanceof TeamError)) throw error;
				return {
					ok: false,
					error: {
						code: error.code === "TEAM_PLAN_STALE_REVISION" ? "team-plan-conflict" : error.code === "TEAM_PLAN_IMPORT_INVALID" ? "team-plan-import-rejected" : error.code === "TEAM_PLAN_PREFLIGHT_FAILED" ? "team-preflight-rejected" : "team-rejected",
						message: error.message
					}
				};
			}
		}
		/**
		* Report caller-bound member work through the generated Web Remote API.
		* @param agent - exact live Team member reporting current work.
		* @param request - durable state, summary, optional reason/task, and affected files.
		* @returns the committed report or a typed Team rejection.
		*/
		async remoteReportWork(agent, request) {
			try {
				return {
					ok: true,
					value: await this.reportWork(agent, request)
				};
			} catch (error) {
				if (!(error instanceof TeamError)) throw error;
				return {
					ok: false,
					error: {
						code: "team-rejected",
						message: error.message
					}
				};
			}
		}
		/** Preserve mission stale revisions while allowing unexpected failures to reject the Remote call. */
		async missionMutationResult(operation) {
			try {
				return {
					ok: true,
					value: await operation
				};
			} catch (error) {
				if (!(error instanceof TeamError)) throw error;
				return {
					ok: false,
					error: {
						code: error.code === "TEAM_MISSION_STALE_REVISION" ? "team-mission-conflict" : "team-rejected",
						message: error.message
					}
				};
			}
		}
		/** Preserve Team task rejections while allowing unexpected failures to reject the Remote call. */
		async taskMutationResult(operation) {
			try {
				return {
					ok: true,
					value: await operation
				};
			} catch (error) {
				if (!(error instanceof TeamError)) throw error;
				return {
					ok: false,
					error: {
						code: error.code === "TEAM_TASK_STALE_REVISION" ? "team-task-conflict" : "team-rejected",
						message: error.message
					}
				};
			}
		}
		/** Queue one contained recovery pass after publication has unwound. */
		scheduleRecovery(agent) {
			queueMicrotask(() => {
				if (this.lifecycle.disposed) return;
				this.recoverFor(agent).catch((error) => {
					if (this.lifecycle.disposed) return;
					this.ctx.logger.warn(`Agent Teams recovery for "${agent.id}" failed: ${errorMessage(error)}`);
				});
			});
		}
		/** Reconcile roster provisioning before retrying that member's pending mailbox. */
		async recoverFor(agent) {
			await this.roster.recoverFor(agent, this.lifecycle.signal);
			await this.mailbox.recoverFor(agent, this.lifecycle.signal);
		}
		/** Stop Team-owned live branches and release every waiter before service disposal completes. */
		runtimeDisposal;
		/** Retain guard lifetime through one shared physical runtime drain. */
		disposeRuntime() {
			return this.runtimeDisposal ??= this.disposeRuntimeOnce();
		}
		/** Close admission before awaiting all Team-owned operations. */
		async disposeRuntimeOnce() {
			this.lifecycle.close();
			this.activity.close();
			const failures = [];
			try {
				this.roster.cutoffRuntime();
			} catch (error) {
				failures.push(error);
			}
			await this.lifecycle.settleMutations(failures);
			await this.lifecycle.settle(this.roster.pendingCreations(), failures);
			await this.lifecycle.settle(this.mailbox.pendingDispatches(), failures);
			for (const [root, childIds] of this.roster.liveChildrenByRoot()) try {
				await this.roster.stopTeammates(root, childIds);
			} catch (error) {
				failures.push(error);
			}
			failures.push(...this.roster.takeCleanupFailures());
			if (failures.length > 0) throw new AggregateError(failures, "Agent Teams runtime disposal failed");
		}
	};
})();
//#endregion
export { ATTACHMENT_LIMITS, BindingDeadline, BoundMemberRuntime, MemberBindingOwner, PreparedMemberAttachment, TeamError, TeamId, TeamMemberBinderRegistry, TeamMessageId, TeamMissionId, TeamService, TeamService as default, TeamTaskId, abortPrepared, attachmentRecord, canonicalJson, payloadSha256, prepareMembers, provisionPreparedMember, recoverBoundMember, scopesOverlap, validateAttachmentRecords, validateAttachmentRequests };
