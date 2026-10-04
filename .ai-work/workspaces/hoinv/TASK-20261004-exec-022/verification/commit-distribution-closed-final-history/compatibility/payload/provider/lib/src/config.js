export const ACCEPTED_CONTEXT_DELEGATION_SKILL_SHA256 = 'd19885139f8bbee3e9dcc792e903bde672cc575b6066db957214cbb2d40b541b';
export const DURABLE_ROLE_IDS = ['worker', 'triage', 'verify'];
function isRecord(value) {
    return typeof value === 'object' && value !== null && !Array.isArray(value);
}
export function validateSkillBinding(value, role) {
    if (!isRecord(value) || value.role !== role || !isRecord(value.skill)) {
        throw new TypeError(`DURABLE_AGENT_INVALID_ROLE_BINDING:${role}`);
    }
    if (value.skill.name !== 'context-delegation') {
        throw new TypeError(`DURABLE_AGENT_SKILL_NAME_MISMATCH:${role}`);
    }
    if (value.skill.sha256 !== ACCEPTED_CONTEXT_DELEGATION_SKILL_SHA256) {
        throw new TypeError(`DURABLE_AGENT_SKILL_HASH_MISMATCH:${role}`);
    }
    return Object.freeze({
        role,
        skill: Object.freeze({ name: 'context-delegation', sha256: ACCEPTED_CONTEXT_DELEGATION_SKILL_SHA256 }),
    });
}
export function validateDurableAgentConfig(value) {
    if (!isRecord(value) || value.schemaVersion !== 1 || !isRecord(value.roles)) {
        throw new TypeError('DURABLE_AGENT_INVALID_CONFIG');
    }
    const roleInputs = value.roles;
    const keys = Object.keys(roleInputs).sort();
    if (keys.join(',') !== [...DURABLE_ROLE_IDS].sort().join(',')) {
        throw new TypeError('DURABLE_AGENT_ROLE_SET_MISMATCH');
    }
    const roles = Object.fromEntries(DURABLE_ROLE_IDS.map(role => [role, validateSkillBinding(roleInputs[role], role)]));
    return Object.freeze({ schemaVersion: 1, roles: Object.freeze(roles) });
}
export function validateDurableAgentClientConfig(value) {
    if (!isRecord(value) || value.schemaVersion !== 1 || value.hostBinding !== '@deepseek-ai/dsh-durable-agent' || Object.keys(value).sort().join(',') !== 'hostBinding,schemaVersion') {
        throw new TypeError('DURABLE_AGENT_CLIENT_HOST_BINDING_REQUIRED');
    }
    return Object.freeze({ schemaVersion: 1, hostBinding: '@deepseek-ai/dsh-durable-agent' });
}
//# sourceMappingURL=config.js.map