import { TeamError } from '@vuhoi/gat-core'

/** Host-wide coordinator for a dedicated provider. This is not a cross-process storage lock. */
export class DurableOwnershipCoordinator {
  private readonly owners = new Map<string, object>()
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
export function coordinatorFor(service: object): DurableOwnershipCoordinator {
  let coordinator = coordinators.get(service)
  if (!coordinator) { coordinator = new DurableOwnershipCoordinator(); coordinators.set(service, coordinator) }
  return coordinator
}
