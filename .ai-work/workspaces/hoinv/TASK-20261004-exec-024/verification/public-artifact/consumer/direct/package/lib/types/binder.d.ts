import type { DurableAgentDeclaration, DurableAgentService } from '@deepseek-ai/dsh-durable-agent/service';
import type { BinderBindInput, BindingIdentity, DisposableBinding, TeamMemberBinder } from '@vuhoi/gat-core';
/** Persist the strict declaration and trusted selectors without runtime references. */
export interface DurableAttachmentV1 {
    readonly schemaVersion: 1;
    readonly serviceBindingKey: string;
    readonly workspaceRealpath: string;
    readonly declaration: DurableAgentDeclaration & {
        readonly context: 'fresh';
        readonly scope: 'workspace';
    };
}
/** Trusted composition assertions must be established by the host deployment owner. */
export interface DurableBinderComposition {
    readonly serviceBindingKey: string;
    readonly service: DurableAgentService;
    readonly dedicatedProvider: true;
    readonly singleHostWorkspace: true;
    resolveService(key: string): DurableAgentService | undefined;
    resolveWorkspace(identity: BindingIdentity): Promise<string>;
}
declare class DurableLease implements DisposableBinding {
    readonly attachment: DurableAttachmentV1;
    readonly identity: BindingIdentity;
    private readonly composition;
    private readonly releaseOwner;
    private ref?;
    private provision?;
    private cleanup?;
    private readonly operations;
    private readonly removers;
    private closed;
    private transferred;
    private installed;
    constructor(attachment: DurableAttachmentV1, identity: BindingIdentity, composition: DurableBinderComposition, releaseOwner: () => void);
    private check;
    private track;
    bind(input: BinderBindInput, signal: AbortSignal): Promise<DisposableBinding>;
    closeAdmission(): void;
    settle(_signal: AbortSignal): Promise<void>;
    release(_signal: AbortSignal): Promise<void>;
    abort(signal: AbortSignal): Promise<void>;
}
/**
 * Create a WK v1 binder for the selected trusted host topology.
 * @param composition Exact provider identity, topology assertions and independent resolvers.
 * @returns Required member binder with exclusive ownership and bounded scoped contributions.
 */
export declare function createDurableAgentBinder(composition: DurableBinderComposition): TeamMemberBinder<DurableLease>;
export {};
//# sourceMappingURL=binder.d.ts.map