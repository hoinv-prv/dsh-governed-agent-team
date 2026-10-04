/** Real signed-cookie HTTP ingress for protected Team control tests. */
import { createServer } from 'node:http'
import type { AddressInfo } from 'node:net'
import type { Context } from '@deepseek-ai/cordis'
import { apply as applyConnection, inject as connectionInject } from '@deepseek-ai/dsh-client-connection'
import type { WebRoute, WebServer } from '@deepseek-ai/dsh-host-webserver'
import Gateway from '@deepseek-ai/dsh-api-gateway'
import TypertRegistry from '@deepseek-ai/dsh-typert-registry'
import { provideBrowserCredentials } from '../../../api/gateway/tests/browser-credentials.ts'

/** Mount the actual Connection/Gateway carrier and return exact unary control dispatch. */
export async function mountHumanControl(ctx: Context) {
  const routes: WebRoute[] = []
  provideBrowserCredentials(ctx)
  ctx.provide('webServer', { register(route: WebRoute) { routes.push(route); return () => {} }, tapIndex: () => () => {}, port: 0 } as unknown as WebServer)
  await ctx.plugin({ inject: [...connectionInject], apply: applyConnection })
  await ctx.plugin(TypertRegistry)
  await ctx.plugin(Gateway)
  const server = createServer((req, res) => { void routes.find(route => route.path === '/api')!.handler(req, res) })
  await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve))
  const origin = `http://127.0.0.1:${(server.address() as AddressInfo).port}`
  const connection = ctx.connection
  const url = new URL(connection.authenticatedUrl(origin))
  let cookie = ''
  connection.authorizeIndex({ method: 'GET', url: url.pathname + url.search, headers: { host: url.host } }, {
    writeHead(_status, headers) { cookie = headers?.['set-cookie']?.split(';', 1)[0] ?? '' }, end() {},
  })
  return {
    async call(method: string, agentId: string, request?: unknown, headers: Record<string, string> = { cookie }) {
      const response = await fetch(`${origin}/api/agentTeams/${method}`, { method: 'POST', headers: { 'content-type': 'application/json', ...headers },
        body: JSON.stringify({ type: 'client-request', rpcId: 'human-control', method: `agentTeams/${method}`, payload: { args: { agentId, ...(request === undefined ? {} : { request }) } } }) })
      if (response.status !== 200) throw new Error(`control HTTP ${response.status}`)
      return (await response.json() as { result: { ok: boolean; value?: unknown; error?: unknown } }).result
    },
    close: () => new Promise<void>((resolve, reject) => server.close((error) => { if (error) reject(error); else resolve() })),
  }
}
