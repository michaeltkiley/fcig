# Review: index construction in Note A vs Note B, and the order of work (subagent, 17 Nov 2026)

Read-only review commissioned by the author's request (17 Nov 2026) on the MFCI framing. Saved verbatim in substance; tags as given by the reviewer. Not decisions.

## 1. Index construction: Note A vs Note B

**Same method, two differences** [verified]. Both: NS policy news = first PC of MP1, MP2, ED2, ED3, ED4 in USMPD monetary-event windows; window changes of 10-year, S&P 500, DXY regressed on it; one-factor GLS weights w = S^-1 psi / psi'S^-1 psi. Note B's `baseline/lib/noteA.py` is vendored from `fci_note/replication/fci/*` (superseded Note A code; functionally identical to `fci_paper/replication/lib/indexes.py`, `lib/cases.py`). Note B's `lib/events.py` (FS-A75, branch `origin/claude/serene-cori-2oapbc`) differs in:

| | Note A | Note B |
|---|---|---|
| Sample | 253 events, 31 Jan 1996 - 16 Sep 2026 | 252: also needs 63 trading days after, drops 16 Sep 2026 |
| Factor scaling | through the origin | OLS with intercept |
| Weight regressions | constant | constant |
| Index window loading on factor | 0.994 | exactly 1 (asserted) |

Weights: Note A 0.6089 / -0.0512 / 0.0654; Note B 0.6156 / -0.0517 / 0.0656. Responses 0.53/-7.78/4.22 vs 0.53/-7.71/4.18. Indexes: correlation 0.999999; Note B about 1 percent larger sd; largest monthly gap 0.11-0.12 at extremes; latest r* -0.932 vs -0.945. A scale change, not a direction change [verified].

**Note B does better** (mostly presentation): one sample and specification for every window regression, exact unit; step-by-step exposition (why windows, scaling equation, window equation, hawkish worked example, channel sentences, share of a policy move 0.33/0.40/0.27, the monthly-application assumption stated and tested); three steps motivated by trend variance shares; FCI* identity; ordinary-day vs announcement-day loading (0.28 vs 1, ratio 3.6; `fig_ordinary`), R2 of the surprise per asset; JK subset (record only, FS-A72); monthly averages (FS-A76).

**Note A has, Note B lacks:** weight intervals from 5,000 announcement-bootstrap draws (10-year [0.15, 1.11], equities [-0.068, -0.030], dollar [0.021, 0.112]); alternative news measures and samples (2-year, Bauer-Swanson raw/orthogonalized, to 2019, no ZLB); weight drift (step 16); held-out readings and the agreement condition (Appendix A); FRB/US and GS on the common scale (step 26); GS/NFCI/ANFCI conversions (step 02).

**Neither has:** a figure of window moves against policy news with fitted slopes; an interval on the shares w.psi (the equity share 0.40), computable at no cost from `weights_boot.csv`.

**Recommendation.** Adopt Note B's specification (intercept; exact unit). Freeze one event list both packages read (e.g. `data/mfci_events.csv`): (a) Note B's 252 (recommended; in Note A "announcements through July 2026") or (b) all complete windows with Note B dropping late events only in its daily model. Note A canonical: port the ~10-line `events.py` logic into `fci_paper/replication/lib/indexes.py`; re-vendor Note B's `lib/noteA.py` from `fci_paper`; Note B asserts equality with Note A's weights. Consequences: policy-unit numbers scale about 1 percent; bootstrap intervals move by Monte Carlo noise; full rerun (sync about 3 hours); correlations and ratios essentially unchanged.

## 2. Sequence (three gates: N1 headline and stage-1 construction first; then stages 2, 3, 6 in parallel; 4 and 5 after 2; writing last)

- **Stage 0, housekeeping (small):** finish NFCI/ANFCI rerun, FP-A62; merge Note B's branch to main first; sync check.
- **Stage 1, the MFCI (medium code, large rerun).** Decisions: D0 = N1 and the name; D1 sample rule; D2 intercept everywhere (yes); D3 canonical code in `fci_paper` (yes); D4 baseline news measure and robustness set (2-year, Bauer-Swanson orthogonalized; JK appendix); D5 ordinary-day vs window comparison (cite Note B's 3.6, or compute in Note A building on step 20). Build: scaling/sample change; share intervals; three-panel window figure; R2 per asset; one weights table (response, weight, interval, share, share interval); robustness table. Checks: slopes = 1; Note A = Note B weights; common scale w'psi_F = 1; full sync.
- **Stage 2, history (medium).** Decisions: comparison set and step (FCI-G nominal main); GS step; episode rule. Build: one history figure in policy units; co-movement table, levels and 12-month changes, 1973-95 and 1996-2026, block-bootstrap intervals; asset variance decomposition (MFCI level variance: equities 0.71, 10-year 0.10, dollar 0.05, rest covariance [verified]; script `experimental/fci_compare/variance_by_group.py`); episode notes.
- **Stage 3, PC comparison (small-medium).** Decision: published NFCI/ANFCI only, or also own PC1 on a panel (three assets + Baa and mortgage spreads, perhaps VIX). Exists: `10_nfci_on_variables.csv` (levels R2 0.36 -> 0.51 with Baa; 12-month 0.20 -> 0.51, spread t = 5.9; market flow 0.68). Build: optional PC script; loadings exhibit.
- **Stage 4, VAR and FRB/US matched path (medium).** Decisions N5-N7. Build `32_qvar.py` (CBO data with SOURCES), `33_frbus_match.py`, FRB/US hike reading at the r* step, report exhibits. Check: reproduce `qvar_full` before the switch (expect about 1 percent smaller per-point responses after).
- **Stage 5, level vs change (medium).** Decision: (a) level vs 12-month change of the same index; (b) FCI-G form with MFCI weights vs MFCI level; (c) both. Exists: `09_levelflow.py`, `15_level_vs_change.csv`, `fcig_*`, `frbus_gi`. Step 9 was designed with "read as a pattern" caveats.
- **Stage 6, equity channel (small).** Share intervals from bootstrap; FRB/US shares at 1/4/8 quarters at r* step; one table.
- **Stage 7, writing (large).** N2, N3, N9, N10, N11; Section 2 rewritten as the MFCI section in Note B's style; keep a condensed agreement condition (market direction S^-1 psi vs the model's g_h).

## 3. Risks

1. **"Direction" needs a metric.** On the common scale FRB/US gives the dollar 2.5 times the relative importance vs equities (Y 2.1, GS 0.96) [verified, step 26]; FRB/US equity weight 0.60 of the market's, dollar 1.51 times. Reviewer's computation with inputs standardized by r*-step sd: cosine MFCI vs FRB/US weights 0.95; window response psi vs FRB/US hike response 0.85 [verified computation; metric is the reviewer's]. Choose the metric before writing "very similar".
2. **About 1 percent of every policy-unit macro moves** with the construction change; threshold counts in the four-calibration results are most fragile; run stage 1 as one commit and diff the macros.
3. **Keep the notes identical:** one events file, one function, Note B asserts equality; update Note B's footnote and citation together.
4. **Bootstrap draws change** with the sample; do not compare old and new intervals in the text.
5. **One intercept convention everywhere,** including steps 21 and 28 (Bauer-Swanson scaling).
6. **Branch hygiene:** merge Note B first; Note A stage 1 on a short branch.
