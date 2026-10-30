# EXPERIMENTAL: monetary policy shocks and the market index

Status: design stage, no code yet. Parallel project to `fci_note/` (the market-index note). Everything it builds on is in `experimental/PROJECT_MEMORY.md` (section 9), `INDEX_QA.md`, `lp_weights/`, `market_macro/` and `../../fci_note/`. Not used by the daily workflow.

## Question
Add core PCE inflation and the policy rate to the two-variable VAR (unemployment gap, market index) and identify monetary policy shocks by Cholesky ordering, a Nakamura-Steinsson external instrument and a Bauer-Swanson external instrument.
Does the market index make the responses more robust to identification, larger, less subsample-dependent, and less dependent on the information effect? Compare with Gertler-Karadi (2015) and Caldara-Herbst (2019).

## Files
| File | Purpose |
|---|---|
| `CONTEXT.md` | What the market index is, what the project has already found that bears on MP shocks, comparison with GK and CH |
| `01_data.py`, `01_data.log`, `data/` | Step 1: monthly data set (`data/mp_monthly.csv`) and the FRED inputs |
| `02a_lags.py`, `02_cholesky.py`, `02c_report.py`, `irf_cholesky*.csv`, `cholesky_*.png`, `02*.log` | Step 2: lag choice, Cholesky baseline and report |
| `02d_exzlb.py`, `03_instruments.py`, logs, `data/mp_instruments.csv` | Steps 2d and 3: ex-ZLB check; NS and own-purge instruments and first stages |
| `02e_cholesky_gs2.py`, `04_proxy.py`, `04b_why_weak.py`, `mpcommon.py`, `irf_*.csv`, `*_u.png` | 2-year Cholesky; proxy-SVAR with Anderson-Rubin sets; why first stages differ across conventions |
| `MP_QA.md` | Proposed tests and the decisions to be taken one at a time (answers recorded there) |
