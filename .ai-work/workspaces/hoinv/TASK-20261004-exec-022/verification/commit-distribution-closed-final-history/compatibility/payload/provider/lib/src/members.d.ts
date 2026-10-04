import { type DurableMember, type MembersOptions } from './standalone-adapter.js';
declare const MANIFEST_VERSION: 1;
export { loadDurableMembersManifest } from './standalone-adapter.js';
export type { DurableMember, DurableMembersManifest, DurableMemberStorageScope, MembersOptions } from './standalone-adapter.js';
export interface DurableMemberProfile extends DurableMember {
    readonly version: typeof MANIFEST_VERSION;
    /** Present only for workspace-scoped members and bound to the canonical workspace directory. */
    readonly workspace_path?: string;
}
export interface DurableMemoryIndexItem {
    readonly id: string;
    readonly title: string;
    /** Short retrieval hint loaded before a task so the agent can decide whether to open the item. */
    readonly when_to_use: string;
    readonly file: string;
}
export interface DurableMemoryIndex {
    readonly version: 1;
    readonly items: readonly DurableMemoryIndexItem[];
}
export interface WriteDurableMemoryItemInput {
    readonly id: string;
    readonly title: string;
    readonly when_to_use: string;
    readonly content: string;
}
export interface DurableMemberTaskContext {
    readonly profile: DurableMemberProfile;
    /** Persistent behavioral guidance. Inject immediately after host system commands. */
    readonly soul: string;
    /** Bounded catalog loaded each task; open matching memory items separately. */
    readonly memoryIndex: DurableMemoryIndex;
}
/** Idempotently provisions one member after authorization by the current workspace manifest. */
export declare function ensureDurableMember(workspaceRoot: string, name: string, options?: MembersOptions): Promise<DurableMemberProfile>;
/** Lists and provisions all members authorized by the current workspace manifest. */
export declare function listDurableMembers(workspaceRoot: string, options?: MembersOptions): Promise<readonly DurableMemberProfile[]>;
/** Reads persistent behavioral guidance for injection immediately after host system commands. */
export declare function readDurableMemberSoul(workspaceRoot: string, name: string, options?: MembersOptions): Promise<string>;
/**
 * Loads the persistent context required for one task. The host must inject `soul`
 * immediately after its system commands, then use the memory index for selective retrieval.
 * Call this for every task so edits to SOUL.md and the memory index take effect.
 */
export declare function loadDurableMemberTaskContext(workspaceRoot: string, name: string, options?: MembersOptions): Promise<DurableMemberTaskContext>;
/** Loads the bounded memory catalog intended to be added to the agent context before each task. */
export declare function readDurableMemberMemoryIndex(workspaceRoot: string, name: string, options?: MembersOptions): Promise<DurableMemoryIndex>;
/** Opens one memory item selected from the task-time index. */
export declare function readDurableMemberMemoryItem(workspaceRoot: string, name: string, id: string, options?: MembersOptions): Promise<string>;
/** Creates or replaces one memory item and atomically publishes its retrieval metadata in the index. */
export declare function writeDurableMemberMemoryItem(workspaceRoot: string, name: string, input: WriteDurableMemoryItemInput, options?: MembersOptions): Promise<void>;
/** @deprecated Compatibility adapter for the former single MEMORY.md API. */
export declare function readDurableMemberMemory(workspaceRoot: string, name: string, options?: MembersOptions): Promise<string>;
/** @deprecated Writes the compatibility legacy-memory item; new callers should write named items. */
export declare function writeDurableMemberMemory(workspaceRoot: string, name: string, content: string, options?: MembersOptions): Promise<void>;
//# sourceMappingURL=members.d.ts.map