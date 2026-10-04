import type { Context } from '@deepseek-ai/cordis';
import { DurableAgentService, type DurableAgentApprovedMemoryInput, type DurableAgentCommittedMemoryItem, type DurableAgentDeclaration, type DurableAgentMemoryCandidate, type DurableAgentMemoryCandidateInput, type DurableAgentMemoryItem, type DurableAgentRef, type DurableAgentTaskContext, type DurableAgentWorkingLocation } from './service.js';
export interface LocalDurableAgentProviderOptions {
    readonly homeDirectory?: string;
    readonly providerName?: string;
}
export declare class LocalDurableAgentProvider extends DurableAgentService {
    #private;
    readonly providerName: string;
    constructor(ctx: Context, options?: LocalDurableAgentProviderOptions);
    validateDeclaration(workspace: string, declaration: DurableAgentDeclaration): Promise<void>;
    provision(workspaceInput: string, declarationInput: DurableAgentDeclaration): Promise<DurableAgentRef>;
    openTaskContext(memberRef: DurableAgentRef): Promise<Readonly<DurableAgentTaskContext>>;
    readMemoryItem(memberRef: DurableAgentRef, itemId: string): Promise<Readonly<DurableAgentMemoryItem>>;
    submitMemoryCandidate(memberRef: DurableAgentRef, candidateInput: DurableAgentMemoryCandidateInput): Promise<Readonly<DurableAgentMemoryCandidate>>;
    commitMemoryItem(memberRef: DurableAgentRef, approvedInput: DurableAgentApprovedMemoryInput): Promise<Readonly<DurableAgentCommittedMemoryItem>>;
    workingLocation(memberRef: DurableAgentRef): Promise<DurableAgentWorkingLocation>;
    release(memberRef: DurableAgentRef): Promise<void>;
}
//# sourceMappingURL=local-provider.d.ts.map