# Standalone toolchain correction for WBS revision 14

## Observed facts

From `/home/hoinv/work/dsh-governed-agent-team`:

- `node_modules/.bin/vitest`: absent (`test -e` exit 1; `readlink -f` exit 1).
- `node_modules/.bin/tsc`: absent (`test -e` exit 1; `readlink -f` exit 1).
- `node_modules/.bin/tsdown`: absent (`test -e` exit 1; `readlink -f` exit 1).
- Earlier successful `pnpm exec` version probes resolved through ambient PATH state associated with the DSH checkout and therefore are not valid standalone toolchain evidence.

## Revision-14 planning correction

Before implementation, a bounded toolchain task will:

1. create the local workspace/package scaffold;
2. run one exact `pnpm add --save-dev --save-exact --offline typescript@6.0.3 vitest@4.1.8 tsdown@0.22.2` in this repository;
3. write only this repository's `package.json`, `pnpm-lock.yaml`, and `node_modules`, while reading the external pnpm content-addressed store without network;
4. verify the three local executable links exist and resolve below this workspace before any coding task is released.

If the offline store lacks any package or the command needs network/DSH bytes, the branch stops and requires a reviewed revision. No DSH checkout read/write is authorized.
