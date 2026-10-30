# Market FCI and monetary policy shock identification: research design

Draft, 30 Oct 2026 (first pass written before reading the index docs; see INDEX_AND_LITERATURE.md for corrections). Citations are from memory and **not yet checked against the papers**; verify before use. Tags: **[recall]** = my recollection of
the paper, **[design]** = proposal here.

## 1. Question and contribution
Baseline: a two-variable VAR in unemployment and the market FCI. Extension: add core PCE inflation and the federal funds rate (four variables)
and study monetary policy shocks under three identification schemes:

1. Cholesky (recursive) ordering.
2. Proxy-SVAR with Nakamura-Steinsson (NS, 2018) high-frequency surprises as external instrument.
3. Proxy-SVAR with Bauer-Swanson (BS, 2023) surprises as external instrument.

The claim to test: **adding a market-based FCI to the VAR makes monetary policy impulse responses more robust to identification, larger, and less
dependent on subsample and on the Fed information effect.** Each of the four is a separate, testable hypothesis (section 6).

## 2. Why the FCI could matter (mechanisms)
- **Information / invertibility.** Proxy-SVARs need the VAR to span the structural shock (invertibility). Four slow macro variables plus a funds rate
  probably do not; an FCI aggregates many forward-looking prices (yields, spreads, equities, dollar, house prices) and is the standard fix for
  missing information (cf. Gertler-Karadi 2015 with the excess bond premium; Caldara-Herbst 2019 with credit spreads) **[recall]**.
- **The transmission channel is measured directly.** Policy works on activity through financial conditions. With the FCI in the system you can show
  the funds-rate shock -> FCI -> unemployment/inflation path and test how much of the real response runs through it.
- **Information effect.** A surprise that raises yields and also raises equities (positive news) is not a tightening (Jarocinski-Karadi 2020 sign
  restrictions) **[recall]**. The FCI includes equities and yields, so its own response to the instrument is a diagnostic: a "tightening" instrument that
  loosens the FCI is information-contaminated. It can also be used to rotate/purge the instrument.
- **Funds rate is uninformative at the ZLB / post-2008.** The FCI (or a long-rate/proxy funds rate) carries the policy stance when the funds rate is stuck.

## 3. Literature positioning (honest overlap)
- Proxy-SVAR: Stock-Watson 2018; Gertler-Karadi 2015 (1-year rate as policy indicator, EBP); Caldara-Herbst 2019 **[recall]**.
- Instruments: Nakamura-Steinsson 2018 (information effect); Bauer-Swanson 2023 (surprises are predictable from public data; orthogonalizing to
  macro/financial news removes the apparent information effect); Miranda-Agrippino-Ricco 2021 (information-robust, Greenbook-purged); Jarocinski-
  Karadi 2020 **[recall]**.
- Method comparison: Plagborg-Moller-Wolf 2021 (LP vs VAR), Ramey 2016 handbook chapter **[recall]**.
- **Overlap risk:** adding a financial/credit variable to a proxy-SVAR is not new (GK, Caldara-Herbst). The contribution must be (a) a *composite market FCI* rather than one spread, (b) the systematic three-scheme comparison, and (c) the specific robustness/info-effect tests below. A literature search for "FCI in proxy-SVAR" and "information effect robustness" is the first task.

## 4. Which FCI
Superseded: see `INDEX_AND_LITERATURE.md` (what the index is, comparison with Gertler-Karadi and Caldara-Herbst, corrected variable choice). In short: baseline = GS-style level
and unfiltered FCI-G components; FCI-G itself as an outcome, not a lagged regressor.

## 5. Data and sample
- Outcomes: unemployment rate, core PCE price index (log), federal funds rate (effective, or shadow rate / 1-year Treasury yield after 2008), FCI. Monthly.
- Instruments: NS surprises (published on Nakamura's site) and BS surprises (published by Bauer/SF Fed) aggregated to monthly **[recall: both are public]**. Both end
  before 2026; check coverage and extend via the underlying federal funds / Eurodollar-SOFR futures if needed.
- Sample: 1990-2019 baseline (HFI data), 1990-2007 pre-crisis, 2009-2019 ZLB-era, and with/without 2020+. Each VAR: 12 lags monthly (or 6), Bayesian priors
  (Minnesota) as a robustness variant. Credible bands via wild bootstrap (proxy-SVAR, Mertens-Ravn style) **[recall]**.
- Funds rate term: ZLB makes Cholesky on the funds rate weak after 2008; use the 1-year yield as the policy indicator in the proxy schemes (as GK) and report the funds rate version where valid.

## 6. Specifications and tests
Four-variable systems: (U, PCEcore, FFR, FCI) with Cholesky orderings (FCI last = financial markets react to policy within the month; FCI first = policy
reacts to markets; both reported). Comparison grid: {Cholesky, NS-IV, BS-IV} x {with FCI, without FCI} x {full, pre-2008, post-2008} x {raw instrument,
orthogonalized instrument}. Metrics:

| Claim | Test |
|---|---|
| More robust to identification | Distance between IRFs across schemes (e.g. integrated absolute difference of unemployment/PCE IRFs at 0-48 months), with vs without FCI; bootstrap CI on the difference |
| Larger | Peak response and cumulative response of U and PCE to a shock normalized to a 25 bp rise in the policy indicator |
| Less subsample-dependent | Same IRF distance between pre-2008 and post-2008 samples, and recursive-window IRF stability |
| Less information-effect dependent | (i) Sign of the FCI response to the raw NS instrument vs BS-orthogonalized instrument; (ii) first-stage F with and without FCI; (iii) change in the unemployment response when the instrument is purged of its predictable component (BS) and when Greenbook-controlled; (iv) JK-style check: share of surprises with yield up / FCI loosening |
| Invertibility | Granger test of the instrument on VAR residuals with vs without FCI (a standard non-invertibility check) |

Interpretation guard: "larger" is not "better"; if the FCI raises the estimated effect only by absorbing information effects, that should show up in
test (iii). Report all four jointly.

## 7. Risks and open points
1. **Mechanical correlation.** The FCI is built from prices that move on FOMC days, so it reacts to the instrument by construction. That is the point (transmission) but must
   not be mistaken for identification strength; distinguish the contemporaneous FCI response from the lagged real effects.
2. **Look-ahead in the FCI.** Replication series use filled/extrapolated inputs (house prices, CAPE, dollar); restrict VAR use to the period with real observations
   (pre-2026) and prefer variables with no revisions.
3. **FCI-G uses Fed-model weights**, so its inclusion partly imports the Fed's own transmission view. Another reason for MS/GS baseline.
4. **Instrument sample ends early**, and post-2020 policy (QE, inflation surge) is outside the identification sample; the 2026 contribution is out of sample.
5. **Weak instruments**: report the Montiel Olea-Stock-Watson robust F and Anderson-Rubin bands.
6. **Novelty** (section 3) is unresolved until the literature search is done.

## 8. Next steps
1. Literature search for prior FCI-in-proxy-SVAR work; narrow the claim accordingly.
2. Build `mp_dataset.py`: monthly aggregation of the FCI variants and the NS/BS instruments.
3. Run the Cholesky baseline (2-var and 4-var), then proxy-SVARs; write `mp_irf.py` and the comparison table/plots.
