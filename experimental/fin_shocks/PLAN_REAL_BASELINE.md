# Plan: Note B with the real version as the baseline (decisions FS_QA FS-A85, 18 Nov 2026)

## The decisions (all by the author, one at a time)
| | Decision |
|---|---|
| D1 | Baseline model: real version, 2-year yield and federal funds rate in the daily block, with the FCI |
| D2 | Two steps in the main text: nominal and real (each without and with the FCI); the r* step moves to the final section (D11); one sentence on the departure from Note A's three steps |
| D3 | Two baselines: monthly equations from 1996 (first) and from 1973 (second); 1985 start as a robustness test |
| D4 | Fix the spline knots (first knot = first estimation month); the corrected cubic spline is the only trend test |
| D5 | r* robustness = the LW r*-gap step only |
| D6 | Six core robustness tests (revised twice: components test dropped, D10 for Note A; LW r*-gap and spline moved to the final section, D11): 2020 left in; EBP and IP added together; Bauer-Swanson surprise; 6 lags; without the funds rate; monthly equations from 1985 |
| D7 | Rebuild every exhibit on the new baseline; by-version exhibits show nominal and real; monthly VAR benchmarks with the funds rate; simulation's true process = new baseline |
| D8 | New package folder; `fin_shocks/baseline/` frozen as the r*-gap record |
| D10 | Drop the FCI components and weights analysis (Section 4 Tables 7-8) from Note B; left to Note A |
| D11 | A final section before the conclusion, "Slow-Moving Rates and Financial Conditions": the variance shares a spline trend fits (FCI, 2-year, u, inflation), the LW r*-gap step and the spline in the baseline model (nominal and real beside), and one paragraph framing trends and r* as further work; LW and the spline only |
| D9 | Folder `fin_shocks/baseline_real/`; text as a new copy plus a changes file; sign-off on results before text; 3 lags dropped everywhere |

## Phase 0. Housekeeping (needs the author's go-ahead)
* Merge `claude/dazzling-franklin-vcd359` (the exploration, `explore_rstar/`, FS-A83 to FS-A85) into `main`; start a short branch from `main` for the new package.

## Phase 1. The package `fin_shocks/baseline_real/`
1. Copy `fin_shocks/baseline/` (code, `data/`, `lib/`, `cases.py`, step and report scripts); `data/` stays self-contained (no new inputs needed).
2. `lib/model.py`:
   * the funds rate (variant "ff") becomes the default; the 2-year-only model becomes a case option (for robustness test 8);
   * spline knots: first knot at the first estimation month (`trend_cols` called with the first period of the sample; tested as `spl74` in `explore_rstar/real_trends.py`);
   * allow the funds rate with the 1-year yield (variant combination "1y" + "ff") if that appendix test survives (the components are out of Note B, D10, so no extension for them);
   * lags (6, 12) only.
3. `cases.py`: baselines B and B73 = nominal and real, each without and with the FCI, in the new model; robustness panels for the six tests, and panels for the final section (LW r*-gap and spline, nominal and real), both starts (1985 only for its own test); appendix panels kept from the old list where they still apply (ends 2019, Baa spread, Jarocinski-Karadi, four calibrations, 1-year yield), all in the new model; the r*-gap step as a panel.
4. Steps 01-13 unchanged in logic; step 04 (monthly VARs) and step 06 (simulation) with the funds rate in the VAR and the new baseline as the true process; step 13 (decompositions) on the new baseline.
5. Reports 07, 07b, 07c, 07d: two versions (nominal, real) in the by-version exhibits; the robustness summary with the six tests; the final section's two tables (variance shares fitted by the spline; LW r*-gap and spline responses); every claim check rewritten from the new results (no claim carried over); `CLAIMS_REPORT=1` to list failures while rewriting.
6. Full rebuild from raw data in strict mode (about 2-3 hours with 4 cores; fewer lags than before), then `check_paper.py` on a skeleton.
7. README for the new package (steps, exhibits, conventions), and a short note in `baseline/README.md` that it is frozen as the r*-gap record.

**Sign-off point:** the author reads the new results (a results document like `report/baseline_robustness.pdf`, plus a one-page summary of what moved relative to the r*-gap version) before any text is written.

## Phase 2. The text
1. New copy `fin_shocks/paper/mp_transmission_real.tex` from the author's current `mp_transmission.tex` (or from the integration copy if not yet merged: to confirm at the time); `mp_transmission.tex` untouched.
2. Rewrite, in the house style (`experimental/WRITING_GUIDE.md`, CLAUDE.md working preferences): abstract and introduction (question, result, approach; two steps; the funds rate in the model), Section 2 (model with the funds rate; two steps), Section 3 (results: Figure 1, standard methods, matched comparison, monthly VARs, sacrifice ratio, Section 3.5), Section 4 (mechanisms: persistence, timing, credit; components and weights removed, D10), Section 5 (robustness: six tests reported plainly), Section 6 (slow-moving rates and financial conditions: r* and trends, D11), conclusion, appendices.
3. `paper/CHANGES_FOR_MERGE_REAL.md`: section by section, old to new, with numbers.
4. Compile (pdflatex + bibtex), `check_paper.py`, no undefined references or overfull boxes.

## Phase 3. Close
* Update `experimental/PROJECT_MEMORY.md` section 9, `experimental/README.md` (new folder), CLAUDE.md's Note B status line; merge the branch to `main`.

## Open points to settle when reached
* The zero lower bound (2009-15, 2020-21) for the funds rate: say how the model treats it (it does not: the funds rate's daily equation is linear) and whether a test is wanted.
* Whether the funds rate's window impact (current-month futures move, 0.72) is stated as an assumption in Section 2.
* Which old appendix tests survive (ends 2019, Baa, JK, calibrations, 1-year yield, NFCI not in).
