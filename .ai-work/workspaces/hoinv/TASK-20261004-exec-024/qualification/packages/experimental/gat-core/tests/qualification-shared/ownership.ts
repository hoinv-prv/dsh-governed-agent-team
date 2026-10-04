import { TeamError } from '@vuhoi/gat-core'

/** Host-wide coordinator for a dedicated provider. This is not a cross-process storage lock. */
export class DurableOwnershipCoordinator {
  private readonly owners = new Map<string, object>()
  /**
   * Reserve one canonical workspace and member identity until physical cleanup succeeds.
   * @param workspaceRealpath Canonical workspace path selected by the host.
   * @param name Explicit durable member name.
   * @returns Idempotent release callback owned by the bound resource.
   */
  reserve(workspaceRealpath: string, name: string): () => void {
    const key = JSON.stringify([workspaceRealpath, name])
    if (this.owners.has(key)) throw new TeamError('Durable identity already has an owner or pending cleanup', 'TEAM_BINDING_CONFLICT')
    const owner = {}
    this.owners.set(key, owner)
    let released = false
    return () => {
      if (released) return
      released = true
      if (this.owners.get(key) === owner) this.owners.delete(key)
    }
  }
}

const coordinators = new WeakMap<object, DurableOwnershipCoordinator>()
/**
 * Resolve the exclusive coordinator shared by binders on one exact provider.
 * @param service Underlying registered provider identity.
 * @returns The process-local ownership coordinator for that provider.
 */
export function coordinatorFor(service: object): DurableOwnershipCoordinator {
  let coordinator = coordinators.get(service)
  if (!coordinator) { coordinator = new DurableOwnershipCoordinator(); coordinators.set(service, coordinator) }
  return coordinator
}
