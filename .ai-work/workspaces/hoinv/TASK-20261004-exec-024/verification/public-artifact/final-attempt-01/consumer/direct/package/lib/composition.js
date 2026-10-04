import { n as createDurableAgentBinder, t as loadDurableTeamMembers } from "./initializer-WrA1zjHL.js";
import { realpath } from "node:fs/promises";
import { TeamError } from "@vuhoi/gat-core";
import { symbols } from "@deepseek-ai/cordis";
import z from "@deepseek-ai/schemastery";
import { ReasoningEffortId } from "@deepseek-ai/dsh-llm";
import { SessionId } from "@deepseek-ai/dsh-session";
//#region lib/types/composition.js
/** Register the strict WK initializer and binder in an explicitly selected host. */
function isTrue(value) {
	return value === true;
}
function isV1(value) {
	return value === 1;
}
/** Cordis composition name. */
const name = "gat-durable-agent";
/** Services required before the initializer may be registered. */
const inject = [
	"agentTeams",
	"agents",
	"llm",
	"subagents",
	"durableAgent"
];
/** Loader validation for host-owned configuration. */
const Config = z.object({
	serviceBindingKey: z.string().min(1),
	dedicatedProvider: z.boolean(),
	singleHostWorkspace: z.boolean(),
	continuationProvider: z.string().min(1).default("spawn"),
	maxMembers: z.natural().min(1).default(4),
	maxBytes: z.natural().min(1).default(65536)
});
/**
* Install one strict initializer and the required v1 binder through owned effects.
* @param ctx Host scope containing the exact selected services.
* @param config Explicit dedicated-provider and single-host assertions and limits.
*/
function apply(ctx, config) {
	if (!config.dedicatedProvider || !config.singleHostWorkspace || !config.serviceBindingKey || config.serviceBindingKey.trim() !== config.serviceBindingKey) throw new TeamError("Durable composition requires explicit trusted topology", "TEAM_INVALID_CONFIG");
	const maxMembers = config.maxMembers ?? 4;
	const maxBytes = config.maxBytes ?? 65536;
	for (const value of [maxMembers, maxBytes]) if (!Number.isSafeInteger(value) || value < 1) throw new TeamError("invalid Durable roster limit", "TEAM_INVALID_CONFIG");
	const continuationProvider = config.continuationProvider ?? "spawn";
	if (ctx.subagents.getProvider(continuationProvider) === void 0) throw new TeamError("Durable continuation provider is unavailable", "TEAM_BINDING_UNAVAILABLE");
	const resolveProvider = () => {
		const current = ctx.get("durableAgent");
		if (!current) return void 0;
		return Reflect.get(current, symbols.original) ?? current;
	};
	const service = resolveProvider();
	if (!service) throw new TeamError("Durable service is unavailable", "TEAM_BINDING_UNAVAILABLE");
	if (!isV1(service.apiVersion) || !isTrue(service.features.selectiveMemoryRead) || !isTrue(service.features.memoryCandidateSubmission)) throw new TeamError("Durable service is incompatible", "TEAM_BINDING_UNAVAILABLE");
	const binder = createDurableAgentBinder({
		service,
		serviceBindingKey: config.serviceBindingKey,
		dedicatedProvider: true,
		singleHostWorkspace: true,
		resolveService: (key) => key === config.serviceBindingKey ? resolveProvider() : void 0,
		resolveWorkspace: async (identity) => {
			const lead = ctx.agents.get(SessionId(identity.teamId));
			const membership = lead === void 0 ? void 0 : ctx.agentTeams.tryMembership(lead);
			if (!lead || membership?.role !== "lead" || String(membership.id) !== identity.teamId) throw new TeamError("Durable workspace owner is unavailable", "TEAM_BINDING_UNAVAILABLE");
			const cwd = lead.session.header.cwd;
			if (!cwd) throw new TeamError("Durable workspace is unavailable", "TEAM_BINDING_UNAVAILABLE");
			return await realpath(cwd);
		}
	});
	ctx.effect(() => ctx.agentTeams.registerMemberBinder(binder), "gatDurable.binder()");
	ctx.effect(() => ctx.agentTeams.registerInitializer(async (lead, signal) => {
		const cwd = lead.session.header.cwd;
		if (!cwd) throw new TeamError("Durable workspace is unavailable", "TEAM_BINDING_UNAVAILABLE");
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
				const reasoningEffort = route.reasoningEffort === void 0 ? void 0 : ReasoningEffortId(route.reasoningEffort);
				const options = {
					provider: route.provider,
					model: route.model,
					...reasoningEffort === void 0 ? {} : { reasoningEffort }
				};
				await ctx.llm.resolveCallConfig(options, routeSignal);
				return options;
			}
		});
	}), "gatDurable.initializer()");
}
//#endregion
export { Config, apply, inject, name };
