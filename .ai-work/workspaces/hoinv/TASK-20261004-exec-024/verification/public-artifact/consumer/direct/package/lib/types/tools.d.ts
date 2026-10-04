import type { DurableAgentConsumer } from '@deepseek-ai/dsh-durable-agent/consumer';
/** JSON schema data without a dependency on the direct-member capability interface. */
export type DurableJsonValue = string | number | boolean | null | DurableJsonValue[] | {
    [key: string]: DurableJsonValue;
};
type JsonValue = DurableJsonValue;
/** Closed executable model tool with immutable dispatch classification. */
export interface DurableToolDescriptor {
    readonly name: string;
    /** Captured host dispatch classification, independent of the tool name. */
    readonly capability: 'read' | 'effect';
    readonly schema: JsonValue;
    readonly invoke: (args: unknown) => Promise<unknown>;
}
/**
 * Build the selective-read and unconfirmed-candidate model tools.
 * @param consumer Public WK Consumer bound to the exact opaque provider reference.
 * @param authorize Current authority check performed before and after each operation.
 * @returns Two closed tool descriptors without confirmed-memory authority.
 */
export declare function createDurableTools(consumer: DurableAgentConsumer, authorize: (capability: 'read' | 'effect') => void): readonly DurableToolDescriptor[];
export {};
//# sourceMappingURL=tools.d.ts.map