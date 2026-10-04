import type { AgentId, MissionId } from '../identity.js';
export interface EvidenceScope {
    readonly missionId: MissionId;
    readonly projectId: string;
}
export interface ArtifactRef extends EvidenceScope {
    readonly artifactId: string;
    readonly revision: number;
    readonly sha256: string;
    readonly sourceHashes: readonly string[];
    readonly contributorIds: readonly AgentId[];
}
export interface EvidenceRef extends EvidenceScope {
    readonly evidenceId: string;
    readonly revision: number;
    readonly artifactRefs: readonly {
        artifactId: string;
        revision: number;
        sha256: string;
    }[];
    readonly sourceHashes: readonly string[];
}
export interface GateDecision extends EvidenceScope {
    readonly gateId: string;
    readonly revision: number;
    readonly reviewerId: AgentId;
    readonly contributorIds: readonly AgentId[];
    readonly verdict: 'PASS' | 'HOLD' | 'REJECT';
    readonly evidenceIds: readonly string[];
    readonly evidenceHashes: readonly string[];
}
export interface Handoff extends EvidenceScope {
    readonly senderId: AgentId;
    readonly receiverId: AgentId;
    readonly scope: readonly string[];
    readonly artifactHashes: readonly string[];
    readonly gateIds: readonly string[];
    readonly gateHashes: readonly string[];
    readonly revision: number;
    readonly nextAction: string;
    readonly completionClaim?: string;
}
export declare function artifact(v: ArtifactRef, e: EvidenceScope): Readonly<ArtifactRef>;
export declare function evidence(v: EvidenceRef, e: EvidenceScope): Readonly<EvidenceRef>;
export declare function gate(v: GateDecision, e: EvidenceScope): Readonly<GateDecision>;
export declare function handoff(v: Handoff, e: EvidenceScope, supportedCompletion: boolean): Readonly<Handoff>;
export interface EvidenceGraph {
    readonly artifacts: readonly ArtifactRef[];
    readonly evidence: readonly EvidenceRef[];
    readonly gates: readonly GateDecision[];
    readonly handoff: Handoff;
}
export declare function evidenceGraph(v: EvidenceGraph, e: EvidenceScope, supportedCompletion: boolean): Readonly<EvidenceGraph>;
//# sourceMappingURL=evidence.d.ts.map