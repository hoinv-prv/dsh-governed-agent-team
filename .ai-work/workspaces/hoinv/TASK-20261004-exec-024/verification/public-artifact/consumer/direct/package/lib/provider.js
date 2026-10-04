import { LocalDurableAgentProvider } from "@deepseek-ai/dsh-durable-agent";
//#region lib/types/provider.js
/** Cordis provider plugin name. */
const name = "gat-durable-provider";
/** The dedicated provider creates its own service. */
const inject = [];
/**
* Register the provider without sharing an existing capability service.
* @param ctx The selected provider's host scope.
*/
function apply(ctx) {
	if (ctx.get("durableAgent") !== void 0) throw new Error("a Durable provider is already registered");
	new LocalDurableAgentProvider(ctx);
}
//#endregion
export { apply, inject, name };
