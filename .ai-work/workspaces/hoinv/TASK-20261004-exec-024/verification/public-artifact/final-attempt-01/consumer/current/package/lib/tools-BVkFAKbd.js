import { TeamError } from "@vuhoi/gat-core";
//#region lib/types/ownership.js
/** Host-wide coordinator for a dedicated provider. This is not a cross-process storage lock. */
var DurableOwnershipCoordinator = class {
	owners = /* @__PURE__ */ new Map();
	/**
	* Reserve one canonical workspace and member identity until physical cleanup succeeds.
	* @param workspaceRealpath Canonical workspace path selected by the host.
	* @param name Explicit durable member name.
	* @returns Idempotent release callback owned by the bound resource.
	*/
	reserve(workspaceRealpath, name) {
		const key = JSON.stringify([workspaceRealpath, name]);
		if (this.owners.has(key)) throw new TeamError("Durable identity already has an owner or pending cleanup", "TEAM_BINDING_CONFLICT");
		const owner = {};
		this.owners.set(key, owner);
		let released = false;
		return () => {
			if (released) return;
			released = true;
			if (this.owners.get(key) === owner) this.owners.delete(key);
		};
	}
};
const coordinators = /* @__PURE__ */ new WeakMap();
/**
* Resolve the exclusive coordinator shared by binders on one exact provider.
* @param service Underlying registered provider identity.
* @returns The process-local ownership coordinator for that provider.
*/
function coordinatorFor(service) {
	let coordinator = coordinators.get(service);
	if (!coordinator) {
		coordinator = new DurableOwnershipCoordinator();
		coordinators.set(service, coordinator);
	}
	return coordinator;
}
//#endregion
//#region lib/types/tools.js
const MAX_METADATA_BYTES = 16 * 1024;
const MAX_MEMORY_ITEM_BYTES = 1024 * 1024;
const MAX_PROVENANCE_BYTES = 64 * 1024;
const MAX_CANDIDATE_BYTES = 2 * 1024 * 1024;
const MAX_READ_RESULT_BYTES = 2 * 1024 * 1024;
const MAX_CANDIDATE_RESULT_BYTES = 128 * 1024;
const MAX_LIMITATIONS = 64;
const MEMORY_ID = /^[a-z0-9]+(?:-[a-z0-9]+)*$/u;
const CANDIDATE_KEYS = [
	"title",
	"retrievalCondition",
	"content",
	"provenance",
	"confidence",
	"limitations"
];
function rejected() {
	throw new TeamError("invalid Durable Agent tool arguments", "TEAM_INVALID_ARGUMENT");
}
function unavailable() {
	throw new TeamError("Durable Agent operation failed", "TEAM_BINDING_UNAVAILABLE");
}
function utf8Bytes(value) {
	return Buffer.byteLength(value, "utf8");
}
function text(value, maximum) {
	return typeof value === "string" && value.length > 0 && value.trim() === value && !value.includes("\0") && utf8Bytes(value) <= maximum;
}
function contentText(value, maximum) {
	return typeof value === "string" && !value.includes("\0") && utf8Bytes(value) <= maximum;
}
function closedDataArray(value) {
	if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype) rejected();
	const keys = Reflect.ownKeys(value);
	if (keys.some((key) => typeof key !== "string" || key !== "length" && !/^(?:0|[1-9][0-9]*)$/u.test(key))) rejected();
	if (keys.length !== value.length + 1) rejected();
	const copy = [];
	for (let index = 0; index < value.length; index += 1) {
		const descriptor = Object.getOwnPropertyDescriptor(value, String(index));
		if (descriptor === void 0 || !("value" in descriptor) || descriptor.get !== void 0 || descriptor.set !== void 0) rejected();
		copy.push(descriptor.value);
	}
	return copy;
}
function closedDataRecord(value, expectedKeys) {
	if (typeof value !== "object" || value === null || Array.isArray(value)) rejected();
	const prototype = Object.getPrototypeOf(value);
	if (prototype !== Object.prototype && prototype !== null) rejected();
	const keys = Reflect.ownKeys(value);
	if (keys.some((key) => typeof key !== "string") || keys.length !== expectedKeys.length || expectedKeys.some((key) => !keys.includes(key))) rejected();
	const result = Object.create(null);
	for (const key of expectedKeys) {
		const descriptor = Object.getOwnPropertyDescriptor(value, key);
		if (descriptor === void 0 || !("value" in descriptor) || descriptor.get !== void 0 || descriptor.set !== void 0) rejected();
		result[key] = descriptor.value;
	}
	return result;
}
function candidateInput(args) {
	const input = closedDataRecord(args, CANDIDATE_KEYS);
	const limitations = closedDataArray(input.limitations);
	if (!text(input.title, MAX_METADATA_BYTES) || !text(input.retrievalCondition, MAX_METADATA_BYTES) || !contentText(input.content, MAX_MEMORY_ITEM_BYTES) || !text(input.provenance, MAX_PROVENANCE_BYTES) || ![
		"low",
		"medium",
		"high"
	].includes(input.confidence) || limitations.length > MAX_LIMITATIONS || limitations.some((item) => !text(item, MAX_METADATA_BYTES))) rejected();
	const normalized = {
		title: input.title,
		retrievalCondition: input.retrievalCondition,
		content: input.content,
		provenance: input.provenance,
		confidence: input.confidence,
		limitations
	};
	if (utf8Bytes(JSON.stringify(normalized)) > MAX_CANDIDATE_BYTES) rejected();
	return normalized;
}
function safeReadResult(value) {
	try {
		const item = closedDataRecord(value, [
			"id",
			"title",
			"retrievalCondition",
			"content",
			"revision"
		]);
		const result = {
			id: item.id,
			title: item.title,
			retrievalCondition: item.retrievalCondition,
			content: item.content,
			revision: item.revision
		};
		if (!text(result.id, MAX_METADATA_BYTES) || !MEMORY_ID.test(result.id) || !text(result.title, MAX_METADATA_BYTES) || !text(result.retrievalCondition, MAX_METADATA_BYTES) || !contentText(result.content, MAX_MEMORY_ITEM_BYTES) || !Number.isSafeInteger(result.revision) || result.revision < 0 || utf8Bytes(JSON.stringify(result)) > MAX_READ_RESULT_BYTES) unavailable();
		return result;
	} catch {
		unavailable();
	}
}
function safeCandidateResult(value) {
	try {
		const candidate = closedDataRecord(value, [
			"candidateId",
			"status",
			"title",
			"retrievalCondition",
			"provenance",
			"confidence",
			"limitations"
		]);
		const limitations = closedDataArray(candidate.limitations);
		const result = {
			candidateId: candidate.candidateId,
			status: candidate.status,
			title: candidate.title,
			retrievalCondition: candidate.retrievalCondition,
			provenance: candidate.provenance,
			confidence: candidate.confidence,
			limitations
		};
		if (candidate.status !== "unconfirmed" || !text(result.candidateId, MAX_METADATA_BYTES) || !text(result.title, MAX_METADATA_BYTES) || !text(result.retrievalCondition, MAX_METADATA_BYTES) || !text(result.provenance, MAX_PROVENANCE_BYTES) || ![
			"low",
			"medium",
			"high"
		].includes(result.confidence) || result.limitations.length > MAX_LIMITATIONS || result.limitations.some((item) => !text(item, MAX_METADATA_BYTES)) || utf8Bytes(JSON.stringify(result)) > MAX_CANDIDATE_RESULT_BYTES) unavailable();
		return result;
	} catch {
		unavailable();
	}
}
const readSchema = {
	type: "object",
	properties: { itemId: {
		type: "string",
		pattern: "^[a-z0-9]+(?:-[a-z0-9]+)*$",
		maxLength: MAX_METADATA_BYTES
	} },
	required: ["itemId"],
	additionalProperties: false
};
const candidateSchema = {
	type: "object",
	properties: {
		title: {
			type: "string",
			maxLength: MAX_METADATA_BYTES
		},
		retrievalCondition: {
			type: "string",
			maxLength: MAX_METADATA_BYTES
		},
		content: {
			type: "string",
			maxLength: MAX_MEMORY_ITEM_BYTES
		},
		provenance: {
			type: "string",
			maxLength: MAX_PROVENANCE_BYTES
		},
		confidence: {
			type: "string",
			enum: [
				"low",
				"medium",
				"high"
			]
		},
		limitations: {
			type: "array",
			items: {
				type: "string",
				maxLength: MAX_METADATA_BYTES
			},
			maxItems: MAX_LIMITATIONS
		}
	},
	required: [...CANDIDATE_KEYS],
	additionalProperties: false
};
/**
* Build the selective-read and unconfirmed-candidate model tools.
* @param consumer Public WK Consumer bound to the exact opaque provider reference.
* @param authorize Current authority check performed before and after each operation.
* @returns Two closed tool descriptors without confirmed-memory authority.
*/
function createDurableTools(consumer, authorize) {
	const read = {
		name: "durable_agent_read_memory",
		capability: "read",
		schema: readSchema,
		invoke: async (args) => {
			const itemId = closedDataRecord(args, ["itemId"]).itemId;
			if (!text(itemId, MAX_METADATA_BYTES) || !MEMORY_ID.test(itemId)) rejected();
			authorize("read");
			let item;
			try {
				item = await consumer.readMemory(itemId);
			} catch {
				unavailable();
			}
			authorize("read");
			return safeReadResult(item);
		}
	};
	const submit = {
		name: "durable_agent_submit_candidate",
		capability: "effect",
		schema: candidateSchema,
		invoke: async (args) => {
			const input = candidateInput(args);
			authorize("effect");
			let result;
			try {
				result = await consumer.submitUnconfirmedCandidate(input);
			} catch {
				unavailable();
			}
			authorize("effect");
			return safeCandidateResult(result);
		}
	};
	return Object.freeze([Object.freeze(read), Object.freeze(submit)]);
}
//#endregion
export { DurableOwnershipCoordinator as n, coordinatorFor as r, createDurableTools as t };
