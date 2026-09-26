# Package scaffold correction — attempt-gat-scaffold-002

Plan revision 18; cumulative charge 26. STEP-07 ASC remained fresh.

Bounded changes:

- Added exact `packages/gat/scripts/freeze.mjs --output <path> --handoff <path>` surface used by the approved future command.
- Parser requires each option exactly once, rejects unknown/missing/duplicate options, and accepts only the exact approved output/handoff paths. It requires a non-symlinked canonical mission root, captures its device/inode/realpath, creates no directories, rejects existing leaf symlinks/non-files/multiply-linked files, checks distinct PID-scoped exclusive temporary paths, revalidates the captured parent identity before each write/rename, then atomically renames; manifest traversal also rejects symlink/file anomalies.
- Freeze deterministically hashes sorted fixed design inputs plus package files, writes the JSON manifest and Markdown handoff, and emits the literal `.artifacts/gat-conformance/<implementation-hash>/` path without executing it.
- Root `freeze.mjs` is a compatibility entry importing the exact scripts implementation; package script points directly to `scripts/freeze.mjs`.
- Built smoke now spawns a clean Node child with empty environment, imports the built file URL directly, and asserts exit code, empty stderr, and exact inactive/not-integrated status output.

No package build/test/freeze command was authorized or executed in this task; only the approved STEP-07 transition had run previously. No DSH, dependency, network, conformance, Web, close, or activation effect occurred.

Changed hashes:

- `packages/gat/package.json`: `83700ebfcc15fe42d7ed2a27ea8b4d38aefe70f358c1f4fbc82d415b5b3353c5`
- `packages/gat/freeze.mjs`: `6554a8d8bca977bbdd3c8993a6a19b271f91bfaee7a46eb44eaf8c96c310e9f0`
- `packages/gat/scripts/freeze.mjs`: `ddf5494e6746fe86cae14344d5dca07b0b67012569caf9beadfccc284d9991b2`
- `packages/gat/tests/built-package.test.mjs`: `7faa771568f9ceb8e10fc1363307b129d5c60203f09ed4b1cfa8466f872df940`
