/** Register a dedicated WK local provider through the provider's public API. */
import type { Context } from '@deepseek-ai/cordis';
/** Cordis provider plugin name. */
export declare const name = "gat-durable-provider";
/** The dedicated provider creates its own service. */
export declare const inject: string[];
/**
 * Register the provider without sharing an existing capability service.
 * @param ctx The selected provider's host scope.
 */
export declare function apply(ctx: Context): void;
//# sourceMappingURL=provider.d.ts.map