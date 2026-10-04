import { createTaskPacket } from './task-contract.js';
import { reviewContribution as createReviewContribution } from './review-packet.js';
const TOOL_READ = Object.freeze({ name: 'durable_agent_read_memory', description: 'Read one catalog item owned by this bound Durable Agent reference.', result: 'Returns the selected owned memory item only.' });
const TOOL_CANDIDATE = Object.freeze({ name: 'durable_agent_submit_candidate', description: 'Submit a reviewable memory candidate for this bound Durable Agent reference.', result: 'Returns an unconfirmed, non-canonical candidate; independent approval is required before confirmed memory.' });
/** A Consumer owns exactly one opaque service-issued reference. */
export class DurableAgentConsumer {
    #service;
    #ref;
    constructor(service, ref) { this.#service = service; this.#ref = ref; }
    async snapshot() {
        const value = await this.#service.openTaskContext(this.#ref);
        const catalog = [...value.memoryCatalog].map(item => Object.freeze({ id: item.id, title: item.title, retrievalCondition: item.retrievalCondition })).sort((left, right) => left.id < right.id ? -1 : left.id > right.id ? 1 : 0);
        return Object.freeze({ version: 1, member: Object.freeze({ name: value.member.name, description: value.member.description }), guidance: value.guidance, catalog: Object.freeze(catalog), provenance: Object.freeze({ scope: value.provenance.scope, provider: value.provenance.provider, generation: value.provenance.generation }), revision: value.revision });
    }
    async modelContribution() {
        const snapshot = await this.snapshot();
        const prompt = JSON.stringify({ version: snapshot.version, member: snapshot.member, guidance: snapshot.guidance, catalog: snapshot.catalog, provenance: snapshot.provenance, revision: snapshot.revision });
        return Object.freeze({ prompt, tools: Object.freeze([TOOL_READ, TOOL_CANDIDATE]) });
    }
    /** Explicit host-supplied task contract; existing memory-only contribution stays unchanged. */
    async taskContribution(contractInput, role) {
        const task = createTaskPacket(contractInput, role);
        const contribution = await this.modelContribution();
        return Object.freeze({ prompt: JSON.stringify({ durableAgent: JSON.parse(contribution.prompt), task }), tools: contribution.tools });
    }
    /** Explicit reviewer mode: authorize this reference, but never include its memory, catalog or guidance.
     * This contribution alone cannot enforce transport isolation; use runFreshReview for host dispatch. */
    async reviewContribution(packetInput) {
        await this.snapshot();
        return createReviewContribution(packetInput);
    }
    async readMemory(itemId) { return await this.#service.readMemoryItem(this.#ref, itemId); }
    /** Submits an explicitly unconfirmed candidate; it never confirms canonical memory. */
    async submitUnconfirmedCandidate(input) { return await this.#service.submitMemoryCandidate(this.#ref, input); }
}
/** No bound reference means no Consumer and no model-visible contribution. */
export function bindDurableAgentConsumer(service, ref) { return ref === undefined ? undefined : new DurableAgentConsumer(service, ref); }
//# sourceMappingURL=consumer.js.map