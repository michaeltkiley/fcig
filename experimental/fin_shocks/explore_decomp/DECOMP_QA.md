# Historical and variance decompositions for Note B: decisions (exploratory)

Exploratory work, separate from Note B's package (`../baseline/`, read only) and the paper. Branch `claude/sharp-goodall-wffoqw`, which contains the FS-A75 weights branch (`claude/fci-note-b-weights-dcfgbi`). Results: `REPORT.md`.

**D-A1 (17 Nov 2026, user).** Explore whether historical and variance decompositions are possible given window-identified surprises. Two routes explained: Route 1, the measured surprises are the shock (1996 on only); Route 2, the shock is recovered from VAR innovations, e_t = b' Sigma^-1 u_t / (b' Sigma^-1 b), under invertibility (can reach 1973). **User: Route 2.** Keep it apart from Note B's scripts.

**D-A2 (17 Nov 2026, user).** Data for the 1973 VAR: the end-of-month series of Note B's monthly VARs start in 1990 (the daily FCI and daily r*-gap yield start in 1990; `cases.py` already says a 1973 start is not offered for the monthly VARs). **User: monthly averages from 1973 (Note B's own monthly-equation series, as in R1a) as the main version; end of month from 1990 as the check.** Added by me: both data versions also from 1996 (Note B's sample), for like-for-like comparisons.

**D-A3 (17 Nov 2026, user).** Impact column: **window column (Note B's restriction: macro entries zero; yield and FCI = Note B's response in the month of the announcement) as the main version; the monthly proxy column (P1) as the comparison.**

**D-A4 (17 Nov 2026, my choice; user asked me to choose and report).** Cases: the three steps (nominal, real, r*-gap), each without and with the FCI in the same step (Note B's baseline panel), 3/6/12 lags (12 main), 2020 in (Note B's baseline; `lib/monthly.py` also keeps 2020), and March-December 2020 removed (= monthly dummies) as a check at 12 lags. System as Note B's monthly benchmarks: u gap, core PCE inflation, 2-year yield, FCI.

**D-A5 (my choice).** The window column in monthly averages is Note B's model's response of the month's average yield and FCI in the month of the announcement, weighted over the announcement's position in the month (`model.estimate`, `f0[0]`; r*-gap with FCI: 0.465 and 0.489 per +1 pp in the window). End of month: `e0[0]` (1.013, 1.056). It depends only on the daily block, so it is the same for the 1973 and 1996 samples. The P1 column is rescaled so that its yield entry equals the window column's; the scale does not affect the decompositions, only the units of the shock.

**D-A6 (my choice).** Time aggregation in monthly averages: a late-month announcement moves this month's average only in part and next month's fully (Note B: 0.465 in the month, 1.005 the next), which a one-period impact column cannot represent. Added variant **WE2**: the shock moves month t by b0 and month t+1 by b1 = Note B's month-1 response minus Theta_1 b0, and is recovered by GLS from (u_t, u_{t+1}). Its variance "shares" exceed 1 for the yield, so the representation is not consistent with the VAR's innovation covariance; **WE2 is shown for the historical decomposition only, not for variance shares.**

**D-A7 (my choice).** Bootstrap: 500 draws, moving blocks of 12 months of VAR residuals, pre-1996 and post-1996 rows drawn separately (as in Note B), the VAR rebuilt recursively and re-estimated; post-1996 blocks carry their months' surprises, so P1 is re-estimated in each draw. The window column is held at its point value (its sampling error comes from the daily block; Note B's own bootstrap shows it is small relative to the VAR's). Bands for the historical decomposition: each draw's parameters applied to the actual data.

**D-A8 (my choice).** Variance shares are reported as **bounds**. Upper: shock variance 1/(b' Sigma^-1 b) (what invertibility implies; without invertibility it is an upper bound on the variance of the shock with column b [inference]). Lower: the shock is the measured surprise and nothing else, variance = mean squared monthly sum of policy news 1996-2026 (Route 1 in the monthly VAR). Both on the 1996-2026 innovation covariance for like-for-like; the full-sample upper bound too. Also the lower bound with Note B's own responses (`06_noteb_shares.py`).

**D-A9 (my choice).** Route 1 with Note B's own model as the lower-bound historical decomposition (1996 on): Note B's responses (h = 0..36, so contributions of surprises more than 36 months old are dropped) times the monthly sums of the surprises; bands from Note B's own bootstrap (500 draws, block bootstrap), surprises held fixed.

**D-A10 (my choice).** Simulation with Note B's estimated model as the true process (`../baseline/lib/simulate.py`, 200 samples, 1996-2026): Route 2 applied exactly as to the data, to see whether the data's diagnostics are what Note B's own model predicts.

## Findings on alignment of intention and execution (for the user)

* `lib_r2.note_b()` reproduces Note B's stored baseline responses exactly (r*-gap with FCI, 1996, 12 lags: u +0.335/+0.493/+0.431 at 12/24/36 months, price level -0.805 at 24) [verified].
* The monthly VAR with the window column does not reproduce Note B's responses (`REPORT.md` T4): the monthly-average VAR's yield path decays faster (0.60 in month 1 against Note B's 1.00), and responses differ by up to half. So a Route 2 decomposition uses dynamics that are not the paper's.
* The FS-A43 addendum (10 Nov) reported monthly VARs "from 1973". The end-of-month series behind them start in 1990, so those runs most likely started in 1990 [inference from the code at commit 8e9433b^]. They are not in the paper now, and `cases.py` already states that a 1973 start is not offered.
* Stale text (not changed): the CLAUDE.md glossary describes Note B's monthly block with a "quadratic trend", whereas the package has no trend (spline only as a robustness check). PROJECT_MEMORY section 9 says the Note A quarterly-VAR branch is not merged; it is on `main`.
* Nothing in the Note B draft (`paper/mp_transmission.tex`) mentions invertibility or decompositions, so nothing in the paper conflicts with these results. Note B's identification (the window surprise as the shock, as in Route 1) does not need invertibility; that is a strength worth a sentence (see REPORT.md).
