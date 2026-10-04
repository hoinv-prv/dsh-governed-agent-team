export declare const ACCEPTED_CONTEXT_DELEGATION_SKILL_SHA256: "d19885139f8bbee3e9dcc792e903bde672cc575b6066db957214cbb2d40b541b";
export declare const DURABLE_ROLE_IDS: readonly ["worker", "triage", "verify"];
export type DurableRoleId = typeof DURABLE_ROLE_IDS[number];
export interface SkillBinding {
    name: 'context-delegation';
    sha256: string;
}
export interface DurableRoleBinding {
    role: DurableRoleId;
    skill: SkillBinding;
}
export interface DurableAgentConfig {
    schemaVersion: 1;
    roles: Record<DurableRoleId, DurableRoleBinding>;
}
export interface DurableAgentClientConfig {
    schemaVersion: 1;
    hostBinding: '@deepseek-ai/dsh-durable-agent';
}
export declare function validateSkillBinding(value: unknown, role: DurableRoleId): DurableRoleBinding;
export declare function validateDurableAgentConfig(value: unknown): Readonly<DurableAgentConfig>;
export declare function validateDurableAgentClientConfig(value: unknown): Readonly<DurableAgentClientConfig>;
//# sourceMappingURL=config.d.ts.map