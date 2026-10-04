import { type Context } from '@deepseek-ai/cordis';
import z from '@deepseek-ai/schemastery';
/** Cordis composition name. */
export declare const name = "gat-durable-agent";
/** Services required before the initializer may be registered. */
export declare const inject: string[];
/** Trusted topology and roster limits supplied by the selected host profile. */
export interface Config {
    readonly serviceBindingKey: string;
    readonly dedicatedProvider: boolean;
    readonly singleHostWorkspace: boolean;
    readonly continuationProvider?: string;
    readonly maxMembers?: number;
    readonly maxBytes?: number;
}
/** Loader validation for host-owned configuration. */
export declare const Config: z<Config>;
/**
 * Install one strict initializer and the required v1 binder through owned effects.
 * @param ctx Host scope containing the exact selected services.
 * @param config Explicit dedicated-provider and single-host assertions and limits.
 */
export declare function apply(ctx: Context, config: Config): void;
//# sourceMappingURL=composition.d.ts.map