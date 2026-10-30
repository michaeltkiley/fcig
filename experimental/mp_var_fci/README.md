# EXPERIMENTAL: monetary policy shocks and the market index

Status: design stage, no code yet. Parallel project to `fci_note/` (the market-index note). **Everything it builds on is on branch `ccr-3a1fbe39-so6omu`** (`experimental/PROJECT_MEMORY.md` section 9, `INDEX_QA.md`, `lp_weights/`, `market_macro/`, `fci_note/`);
this branch holds only this folder. Not used by the daily workflow.

## Question
Add core PCE inflation and the policy rate to the two-variable VAR (unemployment gap, market index) and identify monetary policy shocks by Cholesky ordering, a Nakamura-Steinsson external instrument and a Bauer-Swanson external instrument.
Does the market index make the responses more robust to identification, larger, less subsample-dependent, and less dependent on the information effect? Compare with Gertler-Karadi (2015) and Caldara-Herbst (2019).

## Files
| File | Purpose |
|---|---|
| `CONTEXT.md` | What the market index is, what the project has already found that bears on MP shocks, comparison with GK and CH |
| `MP_QA.md` | Proposed tests and the decisions to be taken one at a time (answers recorded there) |
