import { Service } from '@deepseek-ai/cordis';
export const DURABLE_AGENT_SERVICE_NAME = 'durableAgent';
export const DURABLE_AGENT_API_VERSION = 1;
export const DURABLE_AGENT_FEATURE_NAMES = Object.freeze([
    'selectiveMemoryRead',
    'memoryCandidateSubmission',
    'approvedMemoryCommit',
    'workingArtifacts',
]);
/**
 * Provider-neutral Cordis port. Every operation after declaration validation
 * requires a service-issued reference. A reference grants only these Durable
 * Agent operations; it grants no filesystem, Team, Session, budget, approval,
 * tool, or delegation authority.
 */
export class DurableAgentService extends Service {
    apiVersion = DURABLE_AGENT_API_VERSION;
    features;
    constructor(ctx, features) {
        super(ctx, DURABLE_AGENT_SERVICE_NAME);
        this.features = Object.freeze({
            selectiveMemoryRead: features.selectiveMemoryRead,
            memoryCandidateSubmission: features.memoryCandidateSubmission,
            approvedMemoryCommit: features.approvedMemoryCommit,
            workingArtifacts: features.workingArtifacts,
        });
    }
}
//# sourceMappingURL=service.js.map