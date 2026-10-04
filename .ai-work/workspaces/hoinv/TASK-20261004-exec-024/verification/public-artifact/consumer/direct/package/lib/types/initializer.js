import { open, realpath } from 'node:fs/promises';
import { constants } from 'node:fs';
import { join } from 'node:path';
import { TextDecoder } from 'node:util';
import { parseDocument } from 'yaml';
import { ReasoningEffortId } from '@deepseek-ai/dsh-llm/brand';
import { TeamError } from '@vuhoi/gat-core';
const FILE_NAME = 'team_members.durable.yaml';
const DOCUMENT_KEYS = new Set(['version', 'members']);
const MEMBER_KEYS = new Set([
    'name', 'description', 'prompt', 'context', 'provider', 'model', 'reasoning_effort', 'durable',
]);
const DURABLE_KEYS = new Set(['scope']);
const MEMBER_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/u;
function invalidConfiguration() {
    throw new TeamError('Durable Team configuration is missing or invalid', 'TEAM_INVALID_CONFIG');
}
function plainRecord(value) {
    if (typeof value !== 'object' || value === null || Array.isArray(value))
        return false;
    const prototype = Object.getPrototypeOf(value);
    return prototype === Object.prototype || prototype === null;
}
function closedRecord(value, keys) {
    if (!plainRecord(value) || Object.keys(value).some(key => !keys.has(key)))
        invalidConfiguration();
    return value;
}
function boundedText(value, max) {
    if (typeof value !== 'string' || value.trim().length === 0 || value !== value.trim() || value.length > max) {
        invalidConfiguration();
    }
    return value;
}
function parseDeclarations(source, maxMembers) {
    let document;
    try {
        document = parseDocument(source, { uniqueKeys: true, prettyErrors: false, version: '1.2' });
        if (document.errors.length > 0 || document.warnings.length > 0)
            invalidConfiguration();
    }
    catch {
        invalidConfiguration();
    }
    let value;
    try {
        // A zero alias budget makes YAML aliases invalid rather than expanding them.
        value = document.toJS({ maxAliasCount: 0 });
    }
    catch {
        invalidConfiguration();
    }
    const documentRecord = closedRecord(value, DOCUMENT_KEYS);
    if (documentRecord.version !== 1 || !Array.isArray(documentRecord.members)
        || documentRecord.members.length === 0 || documentRecord.members.length > maxMembers) {
        invalidConfiguration();
    }
    const names = new Set();
    return documentRecord.members.map((rawMember) => {
        const member = closedRecord(rawMember, MEMBER_KEYS);
        const name = boundedText(member.name, 64);
        if (!MEMBER_NAME.test(name) || name === 'lead' || names.has(name))
            invalidConfiguration();
        names.add(name);
        const durable = closedRecord(member.durable, DURABLE_KEYS);
        if (durable.scope !== 'workspace' || member.context !== 'fresh')
            invalidConfiguration();
        const reasoningEffort = member.reasoning_effort === undefined
            ? undefined
            : boundedText(member.reasoning_effort, 80);
        return {
            name,
            description: boundedText(member.description, 200),
            prompt: boundedText(member.prompt, 16_384),
            context: 'fresh',
            provider: boundedText(member.provider, 200),
            model: boundedText(member.model, 200),
            ...(reasoningEffort === undefined ? {} : { reasoningEffort }),
            scope: 'workspace',
        };
    });
}
async function readBoundedConfig(workspaceRealpath, maxBytes) {
    let handle;
    try {
        if (await realpath(workspaceRealpath) !== workspaceRealpath)
            invalidConfiguration();
        handle = await open(join(workspaceRealpath, FILE_NAME), constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
        const before = await handle.stat();
        if (!before.isFile() || before.size > maxBytes)
            invalidConfiguration();
        const bytes = Buffer.alloc(maxBytes + 1);
        let offset = 0;
        while (offset < bytes.length) {
            const { bytesRead } = await handle.read(bytes, offset, bytes.length - offset, offset);
            if (bytesRead === 0)
                break;
            offset += bytesRead;
        }
        if (offset > maxBytes)
            invalidConfiguration();
        const after = await handle.stat();
        if (!after.isFile() || after.size > maxBytes || after.ino !== before.ino || after.dev !== before.dev) {
            invalidConfiguration();
        }
        return new TextDecoder('utf-8', { fatal: true }).decode(bytes.subarray(0, offset));
    }
    catch {
        return invalidConfiguration();
    }
    finally {
        await handle?.close().catch(() => undefined);
    }
}
/**
 * Load the explicit Durable roster; errors fail closed and never select GAT defaults.
 * @param options Canonical workspace, trusted selectors, bounds and host route preflight.
 * @returns Normalized required member specifications with persisted declaration payloads.
 */
export async function loadDurableTeamMembers(options) {
    const { workspaceRealpath, serviceBindingKey, continuationProvider, maxMembers, maxBytes, routePreflight } = options;
    const signal = options.signal ?? new AbortController().signal;
    if (typeof workspaceRealpath !== 'string' || workspaceRealpath.length === 0
        || typeof serviceBindingKey !== 'string' || serviceBindingKey.trim() !== serviceBindingKey || serviceBindingKey.length === 0
        || typeof continuationProvider !== 'string' || continuationProvider.trim() !== continuationProvider || continuationProvider.length === 0
        || !Number.isSafeInteger(maxMembers) || maxMembers < 1
        || !Number.isSafeInteger(maxBytes) || maxBytes < 1
        || typeof routePreflight !== 'function')
        invalidConfiguration();
    signal.throwIfAborted();
    const declarations = parseDeclarations(await readBoundedConfig(workspaceRealpath, maxBytes), maxMembers);
    const members = await Promise.all(declarations.map(async (declaration) => {
        signal.throwIfAborted();
        let agentOptions;
        try {
            agentOptions = await routePreflight({
                provider: declaration.provider,
                model: declaration.model,
                ...(declaration.reasoningEffort === undefined ? {} : { reasoningEffort: declaration.reasoningEffort }),
            }, signal);
        }
        catch {
            throw new TeamError('Durable Team route preflight failed', 'TEAM_INVALID_CONFIG');
        }
        signal.throwIfAborted();
        if (agentOptions !== undefined && (agentOptions.provider !== undefined && agentOptions.provider !== declaration.provider
            || agentOptions.model !== undefined && agentOptions.model !== declaration.model
            || agentOptions.reasoningEffort !== undefined && agentOptions.reasoningEffort !== declaration.reasoningEffort)) {
            throw new TeamError('Durable Team route preflight failed', 'TEAM_INVALID_CONFIG');
        }
        const payload = {
            schemaVersion: 1,
            serviceBindingKey,
            workspaceRealpath,
            declaration: {
                name: declaration.name,
                description: declaration.description,
                prompt: declaration.prompt,
                context: declaration.context,
                provider: declaration.provider,
                model: declaration.model,
                ...(declaration.reasoningEffort === undefined ? {} : { reasoningEffort: declaration.reasoningEffort }),
                scope: declaration.scope,
            },
        };
        return {
            name: declaration.name,
            description: declaration.description,
            initialTask: [{ type: 'text', text: declaration.prompt }],
            context: 'fresh',
            continuationProvider,
            agentOptions: { provider: declaration.provider, model: declaration.model,
                ...(declaration.reasoningEffort === undefined ? {} : { reasoningEffort: ReasoningEffortId(declaration.reasoningEffort) }),
                ...agentOptions },
            attachments: [{ binderId: 'durable-agent', protocolVersion: 1, required: true, payload }],
        };
    }));
    return { source: 'durable-workspace', diagnostics: [], members };
}
//# sourceMappingURL=initializer.js.map