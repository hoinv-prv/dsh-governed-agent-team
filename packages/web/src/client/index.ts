/** Browser entry binding the generated Team Remote artifact to its Client UI. */

import agentTeamsRemote from '@deepseek-ai/dsh-experimental-agent-team/remote'
import type { Context as ClientContext } from '@deepseek-ai/cordis'
import { DEFAULT_CONFIG, mountAgentTeamUi, type Config as AgentTeamUiConfig } from './mount.ts'

export { Config, inject } from './mount.ts'
export type { TeamActionInjected, TeamActionProps, TeamActionResult } from './TeamAction.tsx'
export type { TeamKey } from './locales.ts'

/** Mount the generated Team Remote contribution and its browser UI. */
export async function apply(
  ctx: ClientContext,
  config: AgentTeamUiConfig = DEFAULT_CONFIG,
): Promise<() => Promise<void>> {
  return await mountAgentTeamUi(ctx, agentTeamsRemote, config)
}
