# KF_QA: decisions for the Kalman-filter version of Note B

One decision at a time. KF-Q = question (proposal), KF-A = the user's answer.

**KF-A0 (13 Nov 2026, user instruction). [decided]** New directory for experimental work on Note B with completely separate code (no overlap with `../fin_shocks/`). First replicate Note B with a Kalman-filter (state-space) mixed-frequency model, same form and restrictions where possible; then relax the restrictions the MIDAS form needs and the state space does not.

**KF-Q1 (open). Inputs and separation.** Proposal: copy the raw inputs Note B reads (`../fin_shocks/baseline/data/`, about 2 MB) into `data/` here, and take Note A's monthly indexes, the market weights and r* as **frozen data inputs** (copied from `../fin_shocks/baseline/output/`, checksums recorded), not rebuilt. All code is new; nothing is imported from `../fin_shocks/`. Alternative: rebuild Note A's indexes with new code too (more work; no new information for this exercise).

**KF-Q2 (open). Inference in stage 1.** Proposal: the same 12-month block bootstrap as Note B (500 draws), so that the replication covers intervals as well as point estimates. KF-native inference (a posterior from a Gibbs sampler with a simulation smoother, or the inverse Hessian) would come in stage 2, where latent states make the bootstrap expensive.

**KF-Q3 (open). Stage-1 scope.** Proposal: the r*-gap case with the FCI at 12 lags first (to machine precision on point estimates), then the rest of panel B (nominal, real, r*-gap; with and without the FCI; 3/6/12 lags). Robustness panels not replicated unless asked.

**KF-Q4 (open, for stage 2). Order of relaxations and the form of K1.** See `KF_PLAN.md` section 4. To be taken up after stage 1.
