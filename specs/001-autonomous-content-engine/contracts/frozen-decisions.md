# Frozen Decisions — Autonomous Content Engine

> Architectural and strategic decisions that are locked. Changes require a formal change request.
> Source: [theme.md](../theme.md) § Frozen Decisions

| # | Decision | Rationale | Date | Reversible? |
|---|----------|-----------|------|-------------|
| 1 | L3 Business Module in PROD-004 | Pluggable business feature, not foundation | 2026-03-15 | No |
| 2 | Dual-mode: standalone CLI + platform web | Prove value standalone, integrate later | 2026-03-15 | No |
| 3 | Five-Port adapter pattern | Same interfaces, swap adapters for platform | 2026-03-15 | No |
| 4 | TypeScript for engine | Five-Port chain is TS-native, PROD-004 is TS | 2026-03-15 | No |
| 5 | Business Process decomposition | Pipeline stages = natural epic boundaries | 2026-03-15 | No |
| 6 | Shopify-first CMS adapter | Hairgenetix is the R1 validation target | 2026-03-15 | Yes |
| 7 | Dual-model validation (ChatGPT + Gemini) | Self-scoring overestimates by 25-40% (BA §3.4) | 2026-03-15 | No |
