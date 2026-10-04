import { r as coordinatorFor, t as createDurableTools } from "./tools-BVkFAKbd.js";
import { open, realpath } from "node:fs/promises";
import { DurableAgentConsumer } from "@deepseek-ai/dsh-durable-agent/consumer";
import { TeamError, validateAttachmentRequests } from "@vuhoi/gat-core";
import { constants } from "node:fs";
import { join } from "node:path";
import { TextDecoder } from "node:util";
import { parseDocument } from "yaml";
import { ReasoningEffortId } from "@deepseek-ai/dsh-llm/brand";
//#region lib/types/binder.js
function isTrue(value) {
	return value === true;
}
function isV1(value) {
	return value === 1;
}
function unavailable() {
	throw new TeamError("required Durable binding unavailable", "TEAM_BINDING_UNAVAILABLE");
}
function closed(value, keys, optional = []) {
	if (!value || typeof value !== "object" || Array.isArray(value)) unavailable();
	const record = value;
	if (keys.some((key) => !(key in record)) || Object.keys(record).some((key) => !keys.includes(key) && !optional.includes(key))) unavailable();
	return record;
}
function text(value, max) {
	return typeof value === "string" && value.length > 0 && value === value.trim() && value.length <= max && !value.includes("\0");
}
function payload(value, input, composition) {
	const validated = validateAttachmentRequests([{
		binderId: "durable-agent",
		protocolVersion: 1,
		required: true,
		payload: value
	}])[0];
	if (!validated) unavailable();
	const detached = validated.payload;
	const root = closed(detached, [
		"schemaVersion",
		"serviceBindingKey",
		"workspaceRealpath",
		"declaration"
	]);
	const d = closed(root.declaration, [
		"name",
		"description",
		"prompt",
		"context",
		"provider",
		"model",
		"scope"
	], ["reasoningEffort"]);
	if (root.schemaVersion !== 1 || root.serviceBindingKey !== composition.serviceBindingKey || !text(root.workspaceRealpath, 16384) || d.name !== input.memberName || !text(d.name, 64) || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(d.name) || !text(d.description, 200) || !text(d.prompt, 16384) || !text(d.provider, 200) || !text(d.model, 200) || d.context !== "fresh" || d.scope !== "workspace" || d.reasoningEffort !== void 0 && !text(d.reasoningEffort, 80)) unavailable();
	return detached;
}
var DurableLease = class {
	attachment;
	identity;
	composition;
	releaseOwner;
	ref;
	provision;
	cleanup;
	operations = /* @__PURE__ */ new Set();
	removers = [];
	closed = false;
	transferred = false;
	installed = false;
	constructor(attachment, identity, composition, releaseOwner) {
		this.attachment = attachment;
		this.identity = identity;
		this.composition = composition;
		this.releaseOwner = releaseOwner;
	}
	check(scope, action) {
		try {
			if (this.closed || !scope.isCurrent() || this.composition.resolveService(this.attachment.serviceBindingKey) !== this.composition.service) unavailable();
			if (action) scope.authorize(action);
		} catch (error) {
			try {
				this.closeAdmission();
			} catch {}
			queueMicrotask(() => {
				this.release(new AbortController().signal).catch(() => void 0);
			});
			throw error;
		}
	}
	async track(operation) {
		const pending = Promise.resolve().then(operation);
		this.operations.add(pending);
		try {
			return await pending;
		} finally {
			this.operations.delete(pending);
		}
	}
	async bind(input, signal) {
		signal.throwIfAborted();
		if (input.workspaceRealpath !== this.attachment.workspaceRealpath) unavailable();
		this.check(input.scope);
		if (this.transferred || this.closed || JSON.stringify(this.identity) !== JSON.stringify({
			teamId: input.teamId,
			memberId: input.memberId,
			memberName: input.memberName,
			generation: input.generation
		})) unavailable();
		this.transferred = true;
		const onAbort = () => {
			try {
				this.closeAdmission();
			} catch {}
			queueMicrotask(() => {
				this.release(new AbortController().signal).catch(() => void 0);
			});
		};
		signal.addEventListener("abort", onAbort, { once: true });
		this.removers.push(() => {
			signal.removeEventListener("abort", onAbort);
		});
		const service = this.composition.service;
		this.provision = (async () => {
			this.ref = await service.provision(this.attachment.workspaceRealpath, this.attachment.declaration);
		})();
		try {
			await this.provision;
			signal.throwIfAborted();
			this.check(input.scope);
			const ref = this.ref;
			if (!ref) unavailable();
			const consumer = new DurableAgentConsumer(service, ref);
			const key = `gat:durable-agent:${input.teamId}:${input.memberId}:${input.generation}`;
			const refresh = async (authorize) => {
				await this.track(async () => {
					this.check(input.scope, authorize ? "request" : void 0);
					const contribution = await consumer.modelContribution();
					signal.throwIfAborted();
					this.check(input.scope, authorize ? "request" : void 0);
					if (typeof contribution.prompt !== "string" || Buffer.byteLength(contribution.prompt, "utf8") > 1048576) unavailable();
					if (!this.installed) {
						const tools = createDurableTools(consumer, (action) => {
							this.check(input.scope, action);
						}).map((tool) => ({
							...tool,
							invoke: (args) => this.track(() => tool.invoke(args))
						}));
						this.removers.push(input.scope.install({
							key,
							prompt: contribution.prompt,
							tools
						}));
						this.installed = true;
					} else input.scope.replacePrompt(key, contribution.prompt);
				});
			};
			await refresh(false);
			this.removers.push(input.scope.beforeRequest(() => refresh(true)));
			signal.throwIfAborted();
			this.check(input.scope);
			return this;
		} catch (error) {
			const failures = [error];
			try {
				this.closeAdmission();
			} catch (cleanup) {
				failures.push(cleanup);
			}
			try {
				await this.release(new AbortController().signal);
			} catch (cleanup) {
				failures.push(cleanup);
			}
			if (failures.length > 1) throw new AggregateError(failures, "Durable binding acquisition and cleanup failed");
			throw error;
		}
	}
	closeAdmission() {
		if (this.closed) return;
		this.closed = true;
		const failures = [];
		for (const remove of this.removers.splice(0).reverse()) try {
			remove();
		} catch (error) {
			failures.push(error);
		}
		if (failures.length) throw new AggregateError(failures, "Durable contribution removal failed");
	}
	async settle(_signal) {
		await Promise.allSettled([...this.operations]);
	}
	release(_signal) {
		if (this.cleanup) return this.cleanup;
		try {
			this.closeAdmission();
		} catch {}
		this.cleanup = (async () => {
			await this.provision?.catch(() => void 0);
			await this.settle(_signal);
			if (this.ref) await this.composition.service.release(this.ref);
			this.releaseOwner();
		})();
		this.cleanup.catch(() => void 0);
		return this.cleanup;
	}
	abort(signal) {
		return this.release(signal);
	}
};
/**
* Create a WK v1 binder for the selected trusted host topology.
* @param composition Exact provider identity, topology assertions and independent resolvers.
* @returns Required member binder with exclusive ownership and bounded scoped contributions.
*/
function createDurableAgentBinder(composition) {
	if (!isTrue(composition.dedicatedProvider) || !isTrue(composition.singleHostWorkspace) || !text(composition.serviceBindingKey, 200)) unavailable();
	const service = composition.service;
	const coordinator = coordinatorFor(service);
	const validate = async (input, value, signal) => {
		signal.throwIfAborted();
		if (composition.resolveService(composition.serviceBindingKey) !== service || !isV1(service.apiVersion) || !isTrue(service.features.selectiveMemoryRead) || !isTrue(service.features.memoryCandidateSubmission)) unavailable();
		const attachment = payload(value, input, composition);
		const workspace = await composition.resolveWorkspace(input);
		if (workspace !== attachment.workspaceRealpath || workspace !== input.workspaceRealpath || await realpath(workspace) !== workspace) unavailable();
		await service.validateDeclaration(workspace, attachment.declaration);
		signal.throwIfAborted();
		if (composition.resolveService(composition.serviceBindingKey) !== service) unavailable();
		return attachment;
	};
	return {
		id: "durable-agent",
		protocolVersion: 1,
		async prepare(input, signal) {
			const attachment = await validate(input, input.payload, signal);
			const d = attachment.declaration;
			const route = input.spec.agentOptions;
			if (route === void 0 || input.spec.name !== d.name || input.spec.context !== "fresh" || input.spec.description !== d.description || route.provider !== d.provider || route.model !== d.model || route.reasoningEffort !== d.reasoningEffort || input.spec.initialTask.length !== 1 || input.spec.initialTask[0]?.type !== "text" || input.spec.initialTask[0].text !== d.prompt) unavailable();
			const releaseOwner = coordinator.reserve(attachment.workspaceRealpath, d.name);
			const value = new DurableLease(attachment, {
				teamId: input.teamId,
				memberId: input.memberId,
				memberName: input.memberName,
				generation: input.generation
			}, composition, releaseOwner);
			return {
				attachment,
				value,
				abort: (signal) => value.abort(signal)
			};
		},
		async bind(input, value, prepared, signal) {
			if (!(prepared instanceof DurableLease) || JSON.stringify(prepared.attachment) !== JSON.stringify(payload(value, input, composition))) unavailable();
			await validate(input, value, signal);
			return await prepared.bind(input, signal);
		},
		async recover(input, value, signal) {
			const attachment = await validate(input, value, signal);
			const releaseOwner = coordinator.reserve(attachment.workspaceRealpath, attachment.declaration.name);
			const lease = new DurableLease(attachment, {
				teamId: input.teamId,
				memberId: input.memberId,
				memberName: input.memberName,
				generation: input.generation
			}, composition, releaseOwner);
			try {
				return await lease.bind(input, signal);
			} catch (error) {
				try {
					await lease.abort(new AbortController().signal);
				} catch (cleanup) {
					throw new AggregateError([error, cleanup], "Durable recovery and cleanup failed");
				}
				throw error;
			}
		}
	};
}
//#endregion
//#region lib/types/initializer.js
const FILE_NAME = "team_members.durable.yaml";
const DOCUMENT_KEYS = new Set(["version", "members"]);
const MEMBER_KEYS = new Set([
	"name",
	"description",
	"prompt",
	"context",
	"provider",
	"model",
	"reasoning_effort",
	"durable"
]);
const DURABLE_KEYS = new Set(["scope"]);
const MEMBER_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/u;
function invalidConfiguration() {
	throw new TeamError("Durable Team configuration is missing or invalid", "TEAM_INVALID_CONFIG");
}
function plainRecord(value) {
	if (typeof value !== "object" || value === null || Array.isArray(value)) return false;
	const prototype = Object.getPrototypeOf(value);
	return prototype === Object.prototype || prototype === null;
}
function closedRecord(value, keys) {
	if (!plainRecord(value) || Object.keys(value).some((key) => !keys.has(key))) invalidConfiguration();
	return value;
}
function boundedText(value, max) {
	if (typeof value !== "string" || value.trim().length === 0 || value !== value.trim() || value.length > max) invalidConfiguration();
	return value;
}
function parseDeclarations(source, maxMembers) {
	let document;
	try {
		document = parseDocument(source, {
			uniqueKeys: true,
			prettyErrors: false,
			version: "1.2"
		});
		if (document.errors.length > 0 || document.warnings.length > 0) invalidConfiguration();
	} catch {
		invalidConfiguration();
	}
	let value;
	try {
		value = document.toJS({ maxAliasCount: 0 });
	} catch {
		invalidConfiguration();
	}
	const documentRecord = closedRecord(value, DOCUMENT_KEYS);
	if (documentRecord.version !== 1 || !Array.isArray(documentRecord.members) || documentRecord.members.length === 0 || documentRecord.members.length > maxMembers) invalidConfiguration();
	const names = /* @__PURE__ */ new Set();
	return documentRecord.members.map((rawMember) => {
		const member = closedRecord(rawMember, MEMBER_KEYS);
		const name = boundedText(member.name, 64);
		if (!MEMBER_NAME.test(name) || name === "lead" || names.has(name)) invalidConfiguration();
		names.add(name);
		if (closedRecord(member.durable, DURABLE_KEYS).scope !== "workspace" || member.context !== "fresh") invalidConfiguration();
		const reasoningEffort = member.reasoning_effort === void 0 ? void 0 : boundedText(member.reasoning_effort, 80);
		return {
			name,
			description: boundedText(member.description, 200),
			prompt: boundedText(member.prompt, 16384),
			context: "fresh",
			provider: boundedText(member.provider, 200),
			model: boundedText(member.model, 200),
			...reasoningEffort === void 0 ? {} : { reasoningEffort },
			scope: "workspace"
		};
	});
}
async function readBoundedConfig(workspaceRealpath, maxBytes) {
	let handle;
	try {
		if (await realpath(workspaceRealpath) !== workspaceRealpath) invalidConfiguration();
		handle = await open(join(workspaceRealpath, FILE_NAME), constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
		const before = await handle.stat();
		if (!before.isFile() || before.size > maxBytes) invalidConfiguration();
		const bytes = Buffer.alloc(maxBytes + 1);
		let offset = 0;
		while (offset < bytes.length) {
			const { bytesRead } = await handle.read(bytes, offset, bytes.length - offset, offset);
			if (bytesRead === 0) break;
			offset += bytesRead;
		}
		if (offset > maxBytes) invalidConfiguration();
		const after = await handle.stat();
		if (!after.isFile() || after.size > maxBytes || after.ino !== before.ino || after.dev !== before.dev) invalidConfiguration();
		return new TextDecoder("utf-8", { fatal: true }).decode(bytes.subarray(0, offset));
	} catch {
		return invalidConfiguration();
	} finally {
		await handle?.close().catch(() => void 0);
	}
}
/**
* Load the explicit Durable roster; errors fail closed and never select GAT defaults.
* @param options Canonical workspace, trusted selectors, bounds and host route preflight.
* @returns Normalized required member specifications with persisted declaration payloads.
*/
async function loadDurableTeamMembers(options) {
	const { workspaceRealpath, serviceBindingKey, continuationProvider, maxMembers, maxBytes, routePreflight } = options;
	const signal = options.signal ?? new AbortController().signal;
	if (typeof workspaceRealpath !== "string" || workspaceRealpath.length === 0 || typeof serviceBindingKey !== "string" || serviceBindingKey.trim() !== serviceBindingKey || serviceBindingKey.length === 0 || typeof continuationProvider !== "string" || continuationProvider.trim() !== continuationProvider || continuationProvider.length === 0 || !Number.isSafeInteger(maxMembers) || maxMembers < 1 || !Number.isSafeInteger(maxBytes) || maxBytes < 1 || typeof routePreflight !== "function") invalidConfiguration();
	signal.throwIfAborted();
	const declarations = parseDeclarations(await readBoundedConfig(workspaceRealpath, maxBytes), maxMembers);
	return {
		source: "durable-workspace",
		diagnostics: [],
		members: await Promise.all(declarations.map(async (declaration) => {
			signal.throwIfAborted();
			let agentOptions;
			try {
				agentOptions = await routePreflight({
					provider: declaration.provider,
					model: declaration.model,
					...declaration.reasoningEffort === void 0 ? {} : { reasoningEffort: declaration.reasoningEffort }
				}, signal);
			} catch {
				throw new TeamError("Durable Team route preflight failed", "TEAM_INVALID_CONFIG");
			}
			signal.throwIfAborted();
			if (agentOptions !== void 0 && (agentOptions.provider !== void 0 && agentOptions.provider !== declaration.provider || agentOptions.model !== void 0 && agentOptions.model !== declaration.model || agentOptions.reasoningEffort !== void 0 && agentOptions.reasoningEffort !== declaration.reasoningEffort)) throw new TeamError("Durable Team route preflight failed", "TEAM_INVALID_CONFIG");
			const payload = {
				schemaVersion: 1,
				serviceBindingKey,
				workspaceRealpath,
				declaration: {
					name: declaration.name,
					description: declaration.description,
					prompt: declaration.prompt,
					context: declaration.context,
					provider: declaration.provider,
					model: declaration.model,
					...declaration.reasoningEffort === void 0 ? {} : { reasoningEffort: declaration.reasoningEffort },
					scope: declaration.scope
				}
			};
			return {
				name: declaration.name,
				description: declaration.description,
				initialTask: [{
					type: "text",
					text: declaration.prompt
				}],
				context: "fresh",
				continuationProvider,
				agentOptions: {
					provider: declaration.provider,
					model: declaration.model,
					...declaration.reasoningEffort === void 0 ? {} : { reasoningEffort: ReasoningEffortId(declaration.reasoningEffort) },
					...agentOptions
				},
				attachments: [{
					binderId: "durable-agent",
					protocolVersion: 1,
					required: true,
					payload
				}]
			};
		}))
	};
}
//#endregion
export { createDurableAgentBinder as n, loadDurableTeamMembers as t };
