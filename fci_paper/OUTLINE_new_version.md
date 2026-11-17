# Outline of the new version of Note A (draft for the author, 17 Nov 2026)

Decisions behind it: FP-A63 to FP-A71 (`FP_QA.md`); writing in Note B's manner, `experimental/WRITING_GUIDE.md` (section 1: economic intuition, method built on it, tangible results; each construction step developed as reason, approach and equation, shift or result, in the main text). Numbers in brackets are current package values [verified], for orientation only; the text will read them from macros. Exhibits marked **exists** (file) or **to build**.

## Title options
1. Financial Conditions in Units of Monetary Policy: What Policy News Says About the Weights
2. A Monetary Conditions Financial Conditions Index
3. Monetary Policy News and Macro Models Agree on How to Weigh Financial Conditions
4. What Monetary Policy Moves: Financial Conditions, Equities and Macro Models

## Abstract (sketch, no numbers)
Financial conditions indexes weight asset prices by the effects in a macroeconomic model or by their common statistical variation. I take the weights from monetary policy itself. Around FOMC announcements, policy news moves the 10-year yield, stock prices and the dollar in a characteristic pattern; weights that recover that news define a monetary conditions financial conditions index (MCFCI) in units of policy. Measured relative to the neutral real rate, its level says whether conditions are tight or loose. The MCFCI's weights are close to those of the FRB/US model and of the Goldman Sachs index, and over five decades it moves with them and has a similar reduced-form relation to subsequent output. Statistical indexes built around credit spreads and stress measures behave differently. Policy news and the macro models agree because both act heavily through equity prices, a channel absent from most models used for policy analysis.

## 1. Introduction
- **Question.** How much is a movement in financial conditions worth in units of monetary policy, and which asset prices should carry it? Existing indexes answer with model multipliers (FRB/US, GS, FCI-G) or principal components (NFCI). Policy itself offers a third answer.
- **Result.** The policy-news weights land where the macro-model weights do; the MCFCI's history and its reduced-form relation to output match the macro indexes; equities are the reason; statistical stress indexes differ.
- **Figure 1** (to build): the weights side by side on one scale: MCFCI with 90 percent intervals, GS, FRB/US (10-year, equities, dollar); a second panel with each asset's share of a policy move in the windows and in FRB/US's reading of a hike.
- **Approach.** First, the MCFCI: weights from asset co-movement with policy news in announcement windows, in units of a policy move, measured relative to r*. Second, the comparison with macro-model weights: when the two must coincide, and whether they do. Finally, history and activity: co-movement, tight versus tightening, statistical indexes, and a reduced-form VAR benchmarked against FRB/US.
- **Literature** (after): FCIs and their weights (Hatzius et al. 2010; Ajello et al. 2023; Brave-Butters 2011; Arnaut-Bauer 2024; Sack-Swanson 2023; Bletzinger et al. 2026); MCIs (Eika et al. 1996; Batini-Turnbull 2002) and the MFCI names; equity responses to policy (Bernanke-Kuttner 2005; Bauer-Swanson 2023); FCI* (Caballero-Caravello-Simsek 2026). What differs: weights estimated from policy news, a unit tied to a policy move, a level relative to neutral.

## 2. A Financial Conditions Index from Monetary Policy News (the method)
Each subsection: economic reason, approach and equation, shift or result.
- **2.1 Why announcement windows.** Reason: in a 30-minute window around an FOMC statement, policy news dominates other news, so co-movement reveals what policy moves. Approach: the Nakamura-Steinsson factor from futures surprises, scaled so one unit raises the 2-year yield 1 pp (OLS with intercept; exact unit). Result: window responses [10-year +0.53, stocks -7.7 percent, dollar +4.2 percent per point]; policy news explains [80] percent of the 2-year move and about a third of each asset's [0.32, 0.31, 0.34]. **Figure 2** exists: `report/fig_window.pdf`. Connection: Bauer-Swanson's same-window estimate [7.4 percent, R2 0.30].
- **2.2 From responses to weights.** Reason: an index should read a policy move as one point and be as little disturbed as possible by other news. Approach: one-factor GLS, w = S^-1 psi / psi'S^-1 psi. Result: weights [0.62, -0.052, 0.066] with announcement-bootstrap intervals; shares of a policy move [0.33 / 0.40 / 0.27] with intervals [equities 0.19-0.58]. **Table 1** exists in part (`tab_weights`; add shares and intervals).
- **2.3 Measured relative to what? Nominal, real, relative to r*.** For each step: the reason, the equation, the shift.
  - Nominal: rates as published; the trend problem (a 10-year yield of 8 percent in 1981 and 2000).
  - Real: less expected inflation at matched horizons; result: the trend falls [1980 vs 2023: 9.4 -> 4.7 points].
  - Relative to r*: yields less r*; equity valuation as the earnings-yield gap to r*; result: the level reads tight or loose relative to neutral [1980 vs 2023: 3.3]; 2008-09 [r* adds 0.93-1.22 points]. The FCI* link: relative to r*, the index tracks its own neutral level up to a constant when neutral premiums are constant; correlation with FCI* changes [0.64-0.69].
  - **Figure 3** exists in part (`fig_market_steps`, `fig_inflation_rstar`).
- **2.4 Reading one announcement.** Worked example: 28 January 2004 (window moves and the reading, by asset). Exists (`31_examples`).

## 3. The MCFCI and Macro-Model Indexes
- **3.1 Weights from spending effects.** Reason: in a macro index an asset earns weight by moving spending. Approach: FRB/US weights b = Phi(4)/G(4) (GDP effect of a persistent shift per funds-rate equivalent); the published GS weights (calibrated to GDP growth; Caballero-Simsek Table 1). Result: weights on the common scale.
- **3.2 When the two must agree.** Reason and equation: a market index and a spending index coincide when the spending direction is proportional to S^-1 psi (the agreement condition, Appendix A derivation in the main text in one line). Result: similarity [cosine of sd-scaled weights: MCFCI-GS 0.997, MCFCI-FRB/US 0.950]; FRB/US reads a persistent 1 pp hike as [1.03] MCFCI points.
- **3.3 Why they agree: equities.** Policy moves equities strongly (windows; literature); equities move spending (FRB/US: stock wealth in consumption, equity cost of capital; Chodorow-Reich-Nenov-Simsek MPC 3.2 cents; Ludvigson-Steindel-Lettau 2002: 29-63 percent of the GDP effect through wealth in large models). Result: equity share of a policy move [windows 0.40; FRB/US hike 0.53-0.70]; equity share of level variance [0.77 MCFCI, 0.79 GS, 0.49 FRB/US]. **Table 2** exists (`34_equity_channel.csv`; to format).

## 4. Financial Conditions over Five Decades
- **4.1 The indexes together.** **Figure 4** to build: MCFCI, GS, FRB/US levels 1973-2026 (r* step). Co-movement with intervals [levels 0.99 / 0.94; changes 0.98 / 0.96]; variance by asset. Exists (`32_*`).
- **4.2 Tight or tightening.** Reason: a level says where conditions stand relative to neutral; a change measure (FCI-G) says whether they moved. Result: the MCFCI level against FCI-G 1-year: 2022-24 [FCI-G a drag while the level read loose in 44 percent of months], 1994, 1980-82, 1998-2001. Exists (`32_tight_vs_tightening.csv`); figure to build.
- **4.3 Where the indexes part.** The dollar against equities: January 1998 (worked accounting); one sentence of counts (recompute with three indexes: to build).
- **4.4 Statistical indexes.** NFCI and ANFCI weight credit, risk and leverage; the MCFCI correlates [0.52] with the NFCI; the NFCI is asymmetric [skew 3.6 vs 0.0, 1990-2026], a stress index that does not say whether conditions support or restrain spending. Own principal components: on the three assets the PC is close to the MCFCI [0.95]; adding spreads moves it toward spreads [0.60; skew 1.05]. Exists (`32_shape.csv`, `35_*`).

## 5. Financial Conditions and Activity
- **5.1 A reduced-form VAR.** Reason: does a point of each index go with a policy-sized change in output? Approach: two-variable quarterly VAR (CBO output gap, one index; 4 lags; 1973-2026); shock scaled to one point; GDP lagged and the generalized response as the two bounds (a mix of structural shocks: reduced form, stated once).
- **5.2 Results.** **Table 3 / Figure 5** to build from `33_irf.csv`: output gap at 4 quarters [MCFCI -0.74 to -1.03; GS -0.88 to -1.19; FRB/US -0.77 to -1.10; FCI-G -1.27 to -1.54; NFCI -0.10].
- **5.3 Against FRB/US.** Approach: the funds-rate path that makes each index follow its VAR path in FRB/US. Result: at 4 quarters the VAR matches FRB/US [MCFCI -0.74 vs -0.77; GS -0.88 vs -0.87]; after that FRB/US builds, the VAR fades. The bridge from weights to responses: beta_k = g'Omega w_k / w_k'Omega w_k.
- **5.4 Levels and changes.** Level lags act as changes in the gap equation [fit equal; sum of level coefficients near zero]; the level's role is the stance reading (4.2). Exists (`36_levelflow_q.csv`).

## 6. Equities and Macro Models
- The models used for policy have no equity price or stock-wealth effect (Smets-Wouters, CEE, EDO, SIGMA, NY Fed DSGE; FRB/US the exception): **Table 4** to build from `experimental/note_a_qvar/reviews/LIT_DSGE_17nov.md` (documentation pages).
- The staff's scenario work moved from FRB/US alone (all 35 Greenbooks 2006-2010) to about three models per Tealbook (2016-2020), most without equities: `experimental/fed_models_check/`.
- Castelnuovo-Nistico (2010) and Bernanke (2024): the gap named in the literature and at a central bank.
- Research models capture parts (risk-premium HANK and NK models match the equity response; persistent-output models have small equity responses).
- Next steps: quantitative models for policy with an equity channel whose equity response matches the windows and whose effect on spending matches the evidence.

## 7. Robustness
Each as a test with its outcome, plainly: Bauer-Swanson orthogonalized policy news (information effects); event samples (to 2019, without the lower-bound years); weights over time (drift); 2020 dummies; VAR ordering, nominal and real steps; GS conversion.

## 8. Conclusion
Short; ends on the MCFCI as a level in units of policy and on equities in models.

## Appendix
A. Derivation of the weights and the agreement condition. B. Data and construction (sources; expected inflation; r*). C. Weights: precision, variants, drift. D. Where the indexes part: full tables (three indexes) and episodes. E. VAR: full tables (steps, dummies, orderings, NFCI/ANFCI), FRB/US readings of the hike. F. Principal components (loadings). G. Coding of the Greenbooks and Tealbooks.

## Dropped from the current draft
The two-choices framing; the four-calibration headline; the two-year-yield calibration; the composition test and net-export result (FP-A71).

## To build before writing
Figure 1 (weights and shares); Figure 4 (history); tight-vs-tightening figure; month counts with three indexes; VAR table and figure with the FRB/US benchmark; Table 4 (models and equities); all as package steps with macros and claim checks in `07_report.py`.
