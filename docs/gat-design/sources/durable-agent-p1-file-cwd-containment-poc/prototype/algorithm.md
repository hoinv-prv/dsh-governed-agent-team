# P1 strict no-symlink containment algorithm

## Binding

- Mission revision/hash: `1` / `9b7243ea15285e95e7922489113ae7b8069eb3f5893a2e8a81aa9d909921f3de`
- Task/attempt: `p1_containment_prototype` / `p1_containment_prototype-a02-r1`
- Public seam: `async applyContainedOperation({ root, action, target, data? })`
- Accepted oracle inputs are the five hashes recorded in `execution.json`.

## Algorithm

1. Reject every action except `read`, `write`, `append`, and `command_cwd`. `delete` and unknown actions return `{ok:false,code:"UNSUPPORTED_ACTION"}` before filesystem effects.
2. Require `root` to be a nonempty, NUL-free, already-normalized absolute string within the path-input ceiling. `lstat` must show that it exists, is not a symbolic link, and is a directory.
3. Require `target` to be a nonempty, NUL-free string within the action-specific UTF-8 byte ceiling. Resolve relative targets against the root and absolute targets directly.
4. Use `path.relative(root, resolvedTarget)` and component-boundary tests to reject `..`, `../...`, absolute-relative results, traversal, absolute outside paths, and prefix-collision siblings as `OUTSIDE_ROOT`.
5. Split the contained relative path into at most 64 components. Walk from the root with `lstat`, never `stat`, so every visible symlink—inside, outside, or dangling—is rejected as `SYMLINK_COMPONENT` without following it.
6. Reject a missing non-final component as `MISSING_ANCESTOR`. An absent final component is accepted only for `write` or `append`; because all preceding components were walked, its direct parent is an existing normal directory. Read/cwd absent finals return `NOT_FOUND`.
7. Require the final existing object to be a regular file for read/write/append and a directory for `command_cwd`; otherwise return `WRONG_KIND`.
8. Enforce positive safe-integer byte/depth/operation/result ceilings before effects. Write/append accept only string, Buffer, or Uint8Array data.
9. Immediately before the effect, repeat the full root and component walk. Fail closed with `REVALIDATION_MISMATCH` if classification, absence state, path, or observed file identity/mode/size differs.
10. Perform only the declared bounded effect: `readFile`, `writeFile`, or `appendFile`. `command_cwd` returns the contained absolute cwd and never spawns. Filesystem errors become typed `FILESYSTEM_ERROR` blocks.

The operation counter covers asynchronous filesystem calls made by the seam. Metadata size excludes returned read payload, which is governed independently by `file_read_bytes`.

## Generic evidence instrumentation

The module records only generic runtime facts encountered through public-seam roots. It does not inspect manifest row IDs or test names. Internally, each root observation captures device ID, raw numeric/hex `statfs.type`, and a case-variant lookup classified as measured or explicit assumption. The emitted receipt deduplicates these observations into a deterministic summary: observed-root count, the common mission `test-runtime` scope, a proof flag that every root was under that scope, unique device/type/case sets, and a proof flag that all roots shared those facts. Per-row absolute paths are not emitted. Any symlink encountered by the normal `lstat` walk positively marks symlink capability.

Once, at process `beforeExit` after fixture execution, the module emits deterministic one-line JSON receipts:

- `durable-agent-p1-environment-receipt/1` with `process.version`, platform/architecture, `os.release()`, uid/gid/sorted groups, read-only `process.umask()` observation, symlink observation, and sorted root/device/filesystem/case facts;
- `durable-agent-p1-prototype-receipt/1` mapping the exact workspace-relative paths of all five prototype outputs to SHA-256, computed using `node:crypto`.

The first probe has now settled `environment.json` to `observed`. Its `runtime` object must deep-canonically equal every freshly derived receipt or the process fails closed. Node's `process.arch` value `x64` and normalized machine architecture `x86_64` are recorded separately. Filesystem type remains raw numeric/hex evidence with no fabricated name. Instrumentation is read-only, changes no seam result, performs no spawn/network/product access, and writes no receipt file.

## Boundary and limitations

The claim is limited to Linux/POSIX, an existing local containment root, one cooperative process, and no concurrent topology mutation between classification, revalidation, and effect. This is not protection against hostile rename/symlink races, hard-link aliases, bind mounts, mount mutation, remote filesystems, ACL/quota failures, durability/crash atomicity, Windows reparse behavior, or a production sandbox. It performs no delete, rename, chmod, subprocess, shell, network, model, WBS, queue, delegation, or product operation.
