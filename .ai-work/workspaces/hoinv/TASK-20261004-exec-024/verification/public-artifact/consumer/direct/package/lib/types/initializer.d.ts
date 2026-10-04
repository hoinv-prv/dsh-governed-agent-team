import type { AgentOptions } from '@deepseek-ai/dsh-agent';
import type { TeamInitialization } from '@vuhoi/gat-core';
/** Explicit model route selected by one strict Durable declaration. */
export interface DurableRouteSelection {
    readonly provider: string;
    readonly model: string;
    readonly reasoningEffort?: string;
}
/** Host validation that resolves the declared route without changing its selection. */
export type DurableRoutePreflight = (route: DurableRouteSelection, signal: AbortSignal) => Promise<AgentOptions | undefined>;
/** Trusted host configuration for bounded workspace-only roster loading. */
export interface LoadDurableTeamMembersOptions {
    /** Canonical workspace path resolved and trusted by the host. */
    readonly workspaceRealpath: string;
    /** Trusted host registration selector; never read from YAML. */
    readonly serviceBindingKey: string;
    /** DSH continuable-child route, distinct from the member's model route. */
    readonly continuationProvider: string;
    readonly maxMembers: number;
    readonly maxBytes: number;
    readonly routePreflight: DurableRoutePreflight;
    readonly signal?: AbortSignal;
}
/**
 * Load the explicit Durable roster; errors fail closed and never select GAT defaults.
 * @param options Canonical workspace, trusted selectors, bounds and host route preflight.
 * @returns Normalized required member specifications with persisted declaration payloads.
 */
export declare function loadDurableTeamMembers(options: LoadDurableTeamMembersOptions): Promise<TeamInitialization>;
//# sourceMappingURL=initializer.d.ts.map