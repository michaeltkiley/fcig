# fin_shocks: window-identified mixed-frequency transmission (Note B)

**Main output:** the transmission note `paper/mp_transmission.tex` (PDF alongside): "Financial Conditions, r*, and the Transmission of Monetary Policy Surprises". It uses the market index (FCI) of the FCI note (`../../fci_note/`, Note A) with identical nominal/real/r* steps. Start with `../PROJECT_MEMORY.md` section 9 ("START HERE").

| File | What |
|---|---|
| `paper/mp_transmission.tex`, `.pdf` | The note (plain language). Tables `paper/tables/`, figures `paper/figures/`, built by `paper/make_tables.py` |
| `paper/REVIEW_*.md`, `paper/REFERENCE_CHECK.md` | Colleague reviews, plain-language review, reference check |
| `midas_core.py` | Model used by the note: daily HAR block (2-year, FCI) + monthly VAR rows (u gap, core PCE [, IP]); options for rate/FCI forms, trend, samples, shocks, bootstrap |
| `mf_common.py`, `route_a_pos.py`, `midas_var.py`, `midas_bs.py` | Shared data, events, shocks (NS, MP1, NS-GB, BS-ORTH, NS-JK), window responses; helpers |
| `data/` | GSW 9-10y forward rate; Bauer-Swanson posted surprises |
| `FS_QA.md` | Decisions FS-A1..A28 |
| `MF_REPORT.md` | Older markdown version of the note (superseded) |
| `MF_DEVELOPMENT.md`, `MF_PLAN.md`, `MIXED_FREQUENCY_NOTES.md`, `LITERATURE_MIDAS.md`, `PROPOSALS.md` | Exploratory history, literature notes, original proposals |
| other `*.py`, `*.log`, `*.csv`, `runs68/` | Exploratory routes (stage 0, routes A/B, MIDAS variants, direct regressions) and run logs |

Not used by the daily workflow.
