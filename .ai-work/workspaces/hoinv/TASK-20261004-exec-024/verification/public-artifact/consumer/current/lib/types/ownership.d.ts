/** Host-wide coordinator for a dedicated provider. This is not a cross-process storage lock. */
export declare class DurableOwnershipCoordinator {
    private readonly owners;
    /**
     * Reserve one canonical workspace and member identity until physical cleanup succeeds.
     * @param workspaceRealpath Canonical workspace path selected by the host.
     * @param name Explicit durable member name.
     * @returns Idempotent release callback owned by the bound resource.
     */
    reserve(workspaceRealpath: string, name: string): () => void;
}
/**
 * Resolve the exclusive coordinator shared by binders on one exact provider.
 * @param service Underlying registered provider identity.
 * @returns The process-local ownership coordinator for that provider.
 */
export declare function coordinatorFor(service: object): DurableOwnershipCoordinator;
//# sourceMappingURL=ownership.d.ts.map