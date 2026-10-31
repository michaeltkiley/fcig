# Financial shocks and activity, separate from monetary policy: proposals for a short investigation

31 Oct 2026. **Proposals only; nothing here has been run.** Decisions will be logged one at a time in `FS_QA.md` (to be created when you choose). Context: `experimental/mp_var_fci/SUMMARY_REPORT.md` (why the monetary-shock line was stopped).

## 1. Why this is a natural next step
- The market index moves for reasons other than monetary policy. In monthly data the Nakamura-Steinsson policy news correlates only 0.03 (same month) and 0.11 (next month) with changes in the r*-gap index, 1994-2026 (`mp_var_fci/01_data.log`): policy news explains roughly 0.1% to 1% of monthly index changes. So the existing two-variable VAR's shock to the index (`market_macro/`, unemployment first) is already, in practice, a **financial-conditions shock**, not a monetary one.
- Two facts from the monetary work frame the question: (i) credit spreads (EBP, NFCI), not the broad index, remove the wrong-signed post-1994 unemployment response; (ii) the policy rate reacts within the month to the EBP and not detectably to the index (`SUMMARY_REPORT.md` section 3).
- The unemployment gap responds to the index in the existing VAR (Granger M -> u, p about 0.0001 to 0.002; r* version F 9.3 vs 4.5 for real; `PROJECT_MEMORY.md` 3f, 3g). What is not known: does that survive controlling for credit and for the policy rate, and is it a *shock* effect or news about future activity?

## 2. What the literature offers (tags: [abstract] = checked against the abstract or summary page; [recall] = from memory, not checked)
- **Gilchrist and Zakrajsek (2012, AER)** [abstract]: split corporate spreads into a default-risk part and the excess bond premium (EBP); EBP innovations orthogonal to the current state of the economy lower activity and equity prices; most of the spreads' forecasting power is the EBP. The recursive "orthogonal to the macro state" identification.
- **Caldara, Fuentes-Albero, Gilchrist and Zakrajsek (2016, EER)** [abstract]: financial and uncertainty shocks separated with a penalty-function sign-restriction VAR; financial shocks a major source of fluctuations since the mid-1980s; hard to separate from uncertainty.
- **Furlanetto, Ravazzolo and Sarferaz (2019, EJ)** [abstract]: demand, supply, monetary, investment and financial shocks with a minimal set of sign restrictions; financial shocks matter for output, stock prices and investment, little for inflation; housing shocks large and persistent.
- **Stock and Watson (2012, Brookings)** [abstract]: dynamic factor model; the 2007-09 recession is explained by the same factors as earlier recessions, with no separate financial factor: a warning that "financial shocks" may be reflections of other shocks.
- **Jarocinski and Karadi (2020)** [recall]: separate monetary from central-bank-information shocks by the sign of the stock-yield co-movement. **Adrian, Boyarchenko and Giannone (2019)** [recall]: financial conditions and the lower quantiles of GDP growth. **Hatzius et al. (2010)** [recall]: financial conditions indexes and activity. **Gambetti and Musso (2017)** [recall]: loan supply shocks.
- The central difficulty in all of them: financial variables are forward-looking, so their innovations contain news about future activity; identification works only by (a) timing (financial block after the macro state), (b) sign restrictions, or (c) outside information (instruments, narrative events, heteroskedasticity).

## 3. Assets already in hand
Monthly data 1973-2026: unemployment gap, core PCE, funds rate, 2-year, three index cases (nominal, real, r*-gap), GS, FCI-G, EBP, NFCI/ANFCI (`mp_var_fci/data/mp_monthly.csv` and scripts); daily index and component series (1990-2026); FOMC event windows; the existing two-variable VAR code (`fci_note/replication/fci/var.py`, `market_macro/`); the Bayesian proxy-SVAR and AR-set machinery (`mp_var_fci/mpcommon.py`, `09_bayes_proxy.py`); the quarterly unemployment-risk data and models (`michaeltkiley/output_gap/unemployment_risk`, `resource_utilization`).

## 4. Proposals (ordered by size)
### P1. Recursive financial shock: index versus credit (smallest; recommended first)
**Question.** Is there a financial-conditions shock to the market index, orthogonal to the macro state, with effects on unemployment that are separate from the EBP's, once the policy rate and inflation are controlled?
**Method.** VAR in (unemployment gap, core PCE, policy rate, then the financial block EBP and index in both orders), Gilchrist-Zakrajsek style: the financial innovation is the part orthogonal to contemporaneous macro variables. IRFs of unemployment and core PCE; forecast-error variance shares of unemployment due to the index shock and the EBP shock; compare with the two-variable VAR of the note. The policy rate ordered after the financial block (it reacts, per the reaction-function result) and before it (as a check).
**Data/steps (all in hand).** (1) Share of monthly index variance explained by FOMC-window policy news (1 table); (2) the VARs, 12 lags (4 as a check), 2020 dummied, r*-gap index (nominal and real as checks), samples 1973-2026, 1990-2007 and 1994-2026; (3) Cholesky bands (bootstrap) plus a long-sample/short-sample comparison; (4) a short narrative check on large index shocks (Oct 1987 excluded by sample, 1998, 2001, 2008-09, Mar 2020, Mar 2023).
**Deliverable.** A 2-3 page note and four figures. **Size.** One working session.
**Counts as a result.** The index shock has a significant unemployment effect after controlling for the EBP (or not), and a variance share that is stated. A null (all explained by credit) is also a clear result.
**Risks.** The recursive timing assumption (financial variables respond to the macro state within the month) is the standard but contestable one; equities carry news about future activity, so the "shock" may be a demand-news indicator (Stock-Watson's point).

### P2. Sign-restriction separation of financial, monetary, demand and supply shocks
**Question.** Can the index's own components separate a financial shock from a monetary shock and from demand and supply shocks, without instruments?
**Method.** Small VAR (unemployment or output proxy, core PCE, policy rate, index; components as an extension) with sign restrictions in the spirit of Furlanetto et al. and Jarocinski-Karadi, for example: financial shock = index up (tighter), activity down, policy rate down or unchanged on impact; monetary = index up, activity down, policy rate up; demand = activity up, inflation up, policy rate up; supply = activity and inflation in opposite directions. The index's equity versus 10-year components give extra restrictions (a financial shock lowers equities and the 10-year; a monetary tightening raises the 10-year and lowers equities).
**Steps.** Rubio-Ramirez-Waggoner-Zha rotation sampler, 12 lags, report the identified set and the share of draws satisfying restrictions; compare the financial shock with P1's. **Size.** Two sessions. **Counts as a result.** A financial shock whose unemployment response is robust across restriction sets, and a variance decomposition across the four shocks.
**Risks.** Identified sets are wide; restrictions drive results; same-month sign restrictions on monthly averages are blurred by the averaging.

### P3. Financial conditions and downside risk to unemployment (user's framework, predictive)
**Question.** Does the market index (and EBP, NFCI) add to the Baa spread and term spread in Kiley (2021)-style quantile and logit models of a large rise in unemployment, one and three years ahead?
**Method.** Use `unemployment_risk` (full5 and fin2 specifications, 1965-2019 replication and current sample), add the index, EBP and NFCI as predictors; compare in-sample coefficients and out-of-sample quantile scores (pinball loss, Brier score) against fin2 and full5; also the upside risk to the unemployment rate in the adrian-style "vulnerable growth" form.
**Size.** One to two sessions (data are in a sibling repo). **Counts as a result.** A gain (or none) in out-of-sample risk forecasts from the index.
**Risks.** Predictive, not structural: it answers "does the index carry information about downside risk", not "what does a financial shock do". The index starts in 1973 only through the r*-gap cases (check availability for the 1965 sample).

### P4. Identification through heteroskedasticity on daily data (ambitious; not recommended now)
**Question.** Separate policy-news movements from other financial movements in the daily index by the variance difference between FOMC days and other days (Rigobon-Sack), then use the non-policy daily shock, aggregated to months, in a local projection of unemployment.
**Risks.** Needs a defensible control-day set; estimates weak when the variance ratio is modest; aggregation to monthly loses the identification; several sessions. Listed for completeness.

## 5. Recommendation
P1 first, because everything is in hand, it uses the project's own index, it answers the open question left by the monetary line (does the index matter apart from credit?), and a null is informative. If P1 shows an index effect independent of credit, add P2 as the robustness check on identification; run P3 separately as a use of the index in the unemployment-risk framework. Defer P4.

## 6. Decisions needed (to be logged in `FS_QA.md`)
FS-Q1 which proposal(s) and order; FS-Q2 sample (1973-2026 with 2020 dummied as in the note, plus 1990-2007 and 1994-2026 as subsamples?); FS-Q3 baseline index case (r*-gap as in the note, nominal and real as checks); FS-Q4 whether to use the EBP, the NFCI, or both as the credit comparator (EBP is the literature's; NFCI fixed the sign over the full sample); FS-Q5 lags (12 main, 4 check, as in the note) and bands (bootstrap).

## 7. Caveats
[inference] The 0.1% to 1% policy-news share is a monthly-average statement, using the NS factor for 1994-2026; it is not a decomposition of daily moves. The literature list was checked against abstracts only for the four items tagged [abstract]; the rest are recalled. Financial-shock identification is contested (Stock-Watson); whatever P1 delivers should be described as "orthogonal to the macro state", not as a structural financial shock.
