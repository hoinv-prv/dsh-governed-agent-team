/** Register the strict WK initializer and binder in an explicitly selected host. */
import { realpath } from 'node:fs/promises';
import { symbols } from '@deepseek-ai/cordis';
import z from '@deepseek-ai/schemastery';
import { ReasoningEffortId } from '@deepseek-ai/dsh-llm';
import { SessionId } from '@deepseek-ai/dsh-session';
import { TeamError } from '@vuhoi/gat-core';
import { createDurableAgentBinder } from "./binder.js";
import { loadDurableTeamMembers } from "./initializer.js";
function isTrue(value) { return value === true; }
function isV1(value) { return value === 1; }
/** Cordis composition name. */
export const name = 'gat-durable-agent';
/** Services required before the initializer may be registered. */
export const inject = ['agentTeams', 'agents', 'llm', 'subagents', 'durableAgent'];
/** Loader validation for host-owned configuration. */
export const Config = z.object({
    serviceBindingKey: z.string().min(1),
    dedicatedProvider: z.boolean(),
    singleHostWorkspace: z.boolean(),
    continuationProvider: z.string().min(1).default('spawn'),
    maxMembers: z.natural().min(1).default(4),
    maxBytes: z.natural().min(1).default(65_536),
});
/**
 * Install one strict initializer and the required v1 binder through owned effects.
 * @param ctx Host scope containing the exact selected services.
 * @param config Explicit dedicated-provider and single-host assertions and limits.
 */
export function apply(ctx, config) {
    if (!config.dedicatedProvider || !config.singleHostWorkspace
        || !config.serviceBindingKey || config.serviceBindingKey.trim() !== config.serviceBindingKey) {
        throw new TeamError('Durable composition requires explicit trusted topology', 'TEAM_INVALID_CONFIG');
    }
    const maxMembers = config.maxMembers ?? 4;
    const maxBytes = config.maxBytes ?? 65_536;
    for (const value of [maxMembers, maxBytes]) {
        if (!Number.isSafeInteger(value) || value < 1)
            throw new TeamError('invalid Durable roster limit', 'TEAM_INVALID_CONFIG');
    }
    const continuationProvider = config.continuationProvider ?? 'spawn';
    if (ctx.subagents.getProvider(continuationProvider) === undefined) {
        throw new TeamError('Durable continuation provider is unavailable', 'TEAM_BINDING_UNAVAILABLE');
    }
    const resolveProvider = () => {
        const current = ctx.get('durableAgent');
        if (!current)
            return undefined;
        return (Reflect.get(current, symbols.original) ?? current);
    };
    const service = resolveProvider();
    if (!service)
        throw new TeamError('Durable service is unavailable', 'TEAM_BINDING_UNAVAILABLE');
    if (!isV1(service.apiVersion) || !isTrue(service.features.selectiveMemoryRead) || !isTrue(service.features.memoryCandidateSubmission)) {
        throw new TeamError('Durable service is incompatible', 'TEAM_BINDING_UNAVAILABLE');
    }
    const binder = createDurableAgentBinder({
        service,
        serviceBindingKey: config.serviceBindingKey,
        dedicatedProvider: true,
        singleHostWorkspace: true,
        resolveService: key => key === config.serviceBindingKey ? resolveProvider() : undefined,
        resolveWorkspace: async (identity) => {
            const lead = ctx.agents.get(SessionId(identity.teamId));
            const membership = lead === undefined ? undefined : ctx.agentTeams.tryMembership(lead);
            if (!lead || membership?.role !== 'lead' || String(membership.id) !== identity.teamId) {
                throw new TeamError('Durable workspace owner is unavailable', 'TEAM_BINDING_UNAVAILABLE');
            }
            const cwd = lead.session.header.cwd;
            if (!cwd)
                throw new TeamError('Durable workspace is unavailable', 'TEAM_BINDING_UNAVAILABLE');
            return await realpath(cwd);
        },
    });
    ctx.effect(() => ctx.agentTeams.registerMemberBinder(binder), 'gatDurable.binder()');
    ctx.effect(() => ctx.agentTeams.registerInitializer(async (lead, signal) => {
        const cwd = lead.session.header.cwd;
        if (!cwd)
            throw new TeamError('Durable workspace is unavailable', 'TEAM_BINDING_UNAVAILABLE');
        const workspaceRealpath = await realpath(cwd);
        signal.throwIfAborted();
        return await loadDurableTeamMembers({
            workspaceRealpath,
            serviceBindingKey: config.serviceBindingKey,
            continuationProvider,
            maxMembers,
            maxBytes,
            signal,
            routePreflight: async (route, routeSignal) => {
                const reasoningEffort = route.reasoningEffort === undefined ? undefined : ReasoningEffortId(route.reasoningEffort);
                const options = { provider: route.provider, model: route.model,
                    ...(reasoningEffort === undefined ? {} : { reasoningEffort }) };
                await ctx.llm.resolveCallConfig(options, routeSignal);
                return options;
            },
        });
    }), 'gatDurable.initializer()');
}
//# sourceMappingURL=composition.js.map