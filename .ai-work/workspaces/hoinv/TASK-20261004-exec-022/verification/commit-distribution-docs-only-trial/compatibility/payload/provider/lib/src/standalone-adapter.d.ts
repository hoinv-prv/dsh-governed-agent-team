import type { DurableAgentContextMode, DurableAgentDeclaration, DurableAgentStorageScope } from './service.js';
declare const MANIFEST_VERSION: 1;
export type { DurableAgentStorageScope as DurableMemberStorageScope };
/** Legacy team_members.yaml declaration retained only at this boundary. */
export interface DurableMember {
    readonly name: string;
    readonly description: string;
    readonly prompt: string;
    readonly context: DurableAgentContextMode;
    readonly provider: string;
    readonly model: string;
    readonly reasoning_effort?: string;
    readonly storage_scope: DurableAgentStorageScope;
}
export interface DurableMembersManifest {
    readonly version: typeof MANIFEST_VERSION;
    readonly members: readonly DurableMember[];
}
export interface MembersOptions {
    /** A workspace-root manifest file name; nested paths are rejected. Defaults to team_members.yaml. */
    readonly manifestPath?: string;
    /** Trusted host/test seam for global members; consumed by storage, not this adapter. */
    readonly homeDirectory?: string;
}
/** The sole parser/default resolver for legacy team_members.yaml. */
export declare function loadDurableMembersManifest(workspaceRoot: string, options?: MembersOptions): Promise<DurableMembersManifest>;
/** Converts legacy declarations to the explicit service contract. */
export declare function loadDurableAgentDeclarations(workspaceRoot: string, options?: MembersOptions): Promise<readonly DurableAgentDeclaration[]>;
/** Compatibility resolver; authorization happens only in the manifest adapter. */
export declare function resolveLegacyDurableMember(workspaceRoot: string, name: string, options?: MembersOptions): Promise<{
    readonly workspace: string;
    readonly member: DurableMember;
    readonly declaration: DurableAgentDeclaration;
}>;
//# sourceMappingURL=standalone-adapter.d.ts.map