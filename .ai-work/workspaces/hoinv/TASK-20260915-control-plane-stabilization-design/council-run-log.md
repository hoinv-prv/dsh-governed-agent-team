# Council run log

## Run 001

- Review ID: `control-plane-stabilization-v1-council-001`
- Design SHA-256: `5deeaba1e8210ca4a78eafa747a2e7eb5caca21ebbc55a8ed13a482118eb746f`
- Result: terminal failure at review stage.
- Evidence: schema-constrained workflow returned null for all three initial lanes without typed per-invocation failures.
- Disposition: `ledger_integrity_failed`, not retryable within this run; no review verdict.

## Run 002

- Review ID: `control-plane-stabilization-v1-council-002`
- Same design SHA-256.
- Artifact manifest SHA-256: `dabaafcdcddd8fecf0f547a2e8c84eb6a0dbbd6ab4850f0d231ab29752ac0edb`.
- Internal authority packet: `616099d6cd531f3efd4af95b881a2bf371aea8cf6ddff34894e8c82b37fa5361`.
- Internal adversarial packet: `c9889f1a9daaf524c576e22abf3b1994662204a07f10dc216c255476b306413a`.
- Outside-view packet: `987cc50e090dadaac3aa1c47ce13b0d19b72d3d2437f95539dfade5c24674883`.
- Routes: DeepSeek V4.1 Flash authority lane; OpenAI GPT-5.6 Sol adversarial lane; OpenAI GPT-5.6 Luna outside-view lane.
- State: initial lanes dispatched; no peer findings shared.
