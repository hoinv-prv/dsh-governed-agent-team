# Final P2 HUMAN decision package — revision 36

## Decision requested

Choose exactly one:

- **ACCEPT**
- **DEFER**
- **REJECT**

The reviewed integration recommends proceeding to this HUMAN decision. This report does not choose or record the decision.

## Approved plan and current package

- Plan revision: `36`
- Plan SHA-256: `8b9fba4125348be85d9bbaaa94e54f68f069dafc5c1757e44f17059586bb8fba`
- Integration attempt: `p2_integration-a02-r36`
- Coverage: `28` unique work-task IDs and exactly `8` requirements
- Final requirement state: `p2-final-decision = awaiting_human`

## Exact foundation and delta receipt chain

1. Composite baseline artifact: `977c1cf0fc9e43ae477cc7ee2c9b1f8837984ccae4b86d42be6e5eba0134a003`
   - Composite identity: `62aa45f83251c8c45c25ecce99722049e23b8cd600f947a79e5b4503f8d5fb3a`
2. Runtime approval receipt: `1c9566eae5b9ee1d334bfb00a63d33bc4eedaac3c4c6cf9fadbf11c79961fde0`
   - Runtime activation: `decision-rebaseline-r35-007`
3. Real-behavior integration evidence: `4dbd0bb30c6a003d1c18d349da5eb646c2e51502c571082f80aad3d56faf2b5c`
4. Factual decision reconciliation: `6622d10c994ee937c874274e4449fc0a6ddc0c221f13335d6bb8c56b964cf9dc`
   - Accounting projection: charged `160`, task arrays `159`, preserved difference `1`
5. Bounded contingency disposition: `94d711028bad9aafcd1a90014832823857cee1c51824d0f8539f2ce90707ab57`
   - Disposition: exactly `not_required`
6. Exact requirement mapping: `8a6ad17e7bb0ae9f86a11dbf49457f3e403299920420400e36b10f5fb2c7d7c5`

The source catalog excludes historical WBS files, raw attempt-evidence dependencies, revision-current copies of immutable foundations, and prior integration outputs.

## Bounded history

- `p2_integration-a01-r6` remains a failed, non-authoritative attempt. Its outputs were not consumed.
- `p2_integration-a02-r36` is the current reviewed package.
- Coordinator-native verification executed once and passed `8/8` tests with exit code `0`.
- Independent reviewer `sol` returned `meets_criteria` and confirmed 28-task/eight-requirement coverage, six full SHA-256 source bindings, five deterministic outputs, prior-failure isolation, and HUMAN-only disposition.

Verified integration output hashes:

- `integration-r31.md`: `8d0156b00ab14c9e262974c2b33b80e9a4b8a8aafa21115e135eccafafae62c1`
- `p2-decision-candidate-r31.json`: `df520179982f2fb9f9e9c7bfbdcc166d5ef14e2d9f8c0c417dda704e4523bd0a`
- `integration-selfcheck.test.mjs`: `d4b6b8fa5321b657ffbd02771d6ba527f0be52c083e48422f3f9898ace6cbb63`
- `source-hashes.json`: `b80e1fd10a8c0c91e97afe8e190d384ad6bddfaa72290cb1808a3145a9a2fad9`
- `learning-check.md`: `eae6dc641e2ceb99812ec8bd47a7cfc30edd14fc55611817fa4751c7a688a909`

## Evidence boundary and limitations

The evidence supports a single cooperative owner in a local namespace. It does **not** claim safety against a hostile concurrent writer, distributed or remote storage, power-loss durability, production readiness, or cross-platform operation.

## Authority boundary

Even if the HUMAN chooses **ACCEPT**, that decision grants **no** product edit, BS1 edit, FS5 edit, downstream execution, runtime effect, learning promotion, worker self-authority, or automatic acceptance of any other task. Any such action requires its own explicit authority and scope.

**HUMAN decision: ACCEPT / DEFER / REJECT**
