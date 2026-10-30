# EXPERIMENTAL: does a market-based FCI make monetary policy IRFs more robust?

Status: design stage, no code yet. Not used by the daily update workflow. Like `experimental/ms_fci/`, it may read the main repo's outputs
(`fcig_gs_daily.csv`, `fcig_replication_daily.csv`, `history/`) and writes only inside this folder. Full design: `NOTES.md`.

## Question
Take the unemployment + market-FCI VAR and add core PCE inflation and the federal funds rate (four variables). Estimate monetary policy shock
responses under three identification schemes (Cholesky, Nakamura-Steinsson external instrument, Bauer-Swanson external instrument). Does
including the market FCI make the responses (a) more robust to the identification scheme, (b) larger / more precisely estimated, (c) less
sensitive to subsample, (d) less dependent on the Fed information effect?

## Files
| File | Purpose |
|---|---|
| `NOTES.md` | Research design, literature positioning, specifications, tests, data needs, risks |

## Planned next steps
1. Build the monthly FCI series (see NOTES.md section 4) and the instrument/outcome dataset.
2. Cholesky baseline with and without the FCI.
3. Proxy-SVAR with NS and BS instruments; first-stage strength for each.
4. Robustness grid and summary table (NOTES.md section 6).
