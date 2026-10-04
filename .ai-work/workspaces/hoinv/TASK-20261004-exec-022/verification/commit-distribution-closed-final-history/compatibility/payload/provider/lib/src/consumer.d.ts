import { type TaskPacket } from './task-contract.js';
import type { DurableAgentMemoryCandidate, DurableAgentMemoryCandidateInput, DurableAgentMemoryItem, DurableAgentRef, DurableAgentService } from './service.js';
export interface DurableAgentConsumerSnapshot {
    readonly version: 1;
    readonly member: Readonly<{
        readonly name: string;
        readonly description: string;
    }>;
    readonly guidance: string;
    readonly catalog: readonly Readonly<{
        readonly id: string;
        readonly title: string;
        readonly retrievalCondition: string;
    }>[];
    readonly provenance: Readonly<{
        readonly scope: 'workspace' | 'global';
        readonly provider: string;
        readonly generation: string;
    }>;
    readonly revision: number;
}
export interface DurableAgentModelContribution {
    readonly prompt: string;
    readonly tools: readonly Readonly<{
        readonly name: string;
        readonly description: string;
        readonly result: string;
    }>[];
}
/** A Consumer owns exactly one opaque service-issued reference. */
export declare class DurableAgentConsumer {
    #private;
    constructor(service: DurableAgentService, ref: DurableAgentRef);
    snapshot(): Promise<Readonly<DurableAgentConsumerSnapshot>>;
    modelContribution(): Promise<Readonly<DurableAgentModelContribution>>;
    /** Explicit host-supplied task contract; existing memory-only contribution stays unchanged. */
    taskContribution(contractInput: unknown, role: TaskPacket['role']): Promise<Readonly<DurableAgentModelContribution>>;
    /** Explicit reviewer mode: authorize this reference, but never include its memory, catalog or guidance.
     * This contribution alone cannot enforce transport isolation; use runFreshReview for host dispatch. */
    reviewContribution(packetInput: unknown): Promise<Readonly<DurableAgentModelContribution>>;
    readMemory(itemId: string): Promise<Readonly<DurableAgentMemoryItem>>;
    /** Submits an explicitly unconfirmed candidate; it never confirms canonical memory. */
    submitUnconfirmedCandidate(input: DurableAgentMemoryCandidateInput): Promise<Readonly<DurableAgentMemoryCandidate>>;
}
/** No bound reference means no Consumer and no model-visible contribution. */
export declare function bindDurableAgentConsumer(service: DurableAgentService, ref: DurableAgentRef | undefined): DurableAgentConsumer | undefined;
//# sourceMappingURL=consumer.d.ts.map