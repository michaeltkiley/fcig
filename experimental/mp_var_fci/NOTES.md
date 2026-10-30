# Market FCI and monetary-policy shock identification: research design

Draft v2, 30 Oct 2026. Replaces the first draft, which was written before I had read the market FCI work and wrongly used the Fed FCI-G / Goldman-style indexes as the baseline.
Read `INDEX_AND_LITERATURE.md` first: it describes the index (funds-rate-equivalent, five variables, FRB/US weights) and compares it with Gertler-Karadi and Caldara-Herbst.

## 1. Question
Starting from the two-variable VAR in unemployment and the market FCI, add core PCE inflation and the federal funds rate, and identify monetary policy shocks by (a) Cholesky ordering, (b) Nakamura-Steinsson (NS) external instrument,
(c) Bauer-Swanson (BS) external instrument. Does including the market FCI make the impulse responses more robust to identification, larger, less subsample-dependent, and less dependent on the Fed information effect?

## 2. Why this index and not a credit spread
It is in the same units as the instrument (pp of funds rate), has a model-implied transmission benchmark (about 1), carries no funds-rate term, keeps moving at the ZLB, maps to GDP through FRB/US,
and has an r*-gap variant. Credit spreads (GK, CH) are about 2% of its monthly variance; equities, the dollar and the 10-year carry the rest. Details and caveats: `INDEX_AND_LITERATURE.md`.

## 3. Specifications
System: (unemployment, core PCE, policy indicator, market FCI). Policy indicator: the funds rate, and the one-year yield (GK) for the ZLB-spanning sample.
Index variants: nominal q4 (baseline), r*-gap q4 (subsample), q8 and q12 (horizon), without oil, and the Fed FCI-G and Goldman-style indexes from the main repo as outside comparisons.
Identification: Cholesky with the index ordered before and after the policy indicator; proxy-SVAR with NS; proxy-SVAR with BS; each with and without the index in the VAR.

## 4. Hypotheses and tests
| Claim | Test |
|---|---|
| Transmission is as the model implies | Cumulative index IRF to a 1 pp policy shock vs the FRB/US benchmark (about 1 at q4); by component |
| Policy reacts to market tightening (CH, in policy units) | Systematic-response coefficient of the policy indicator on the index; effect of omitting the index on IRFs (toward zero?) |
| More robust to identification | Distance between unemployment/PCE IRFs across Cholesky/NS/BS, with vs without the index |
| Larger | Peak and cumulative responses per 25 bp; and implied-GDP check: index IRF x 0.45% per pp (q4) against the VAR's response |
| Less subsample dependent | Pre-2008 / ZLB / post-2015 / ex-2020 splits, nominal vs r*-gap index; recursive windows |
| Less information-effect dependent | Sign of index response to raw vs orthogonalised instruments; JK-style check with equity and dollar components; first-stage strength with and without the index; invertibility (instrument Granger-causality on residuals) |

Guard: "larger" is not "better"; if the index only raises the estimate by absorbing the information effect, the last row should show it.

## 5. Data
Index: `ms5_level_daily_rstar.csv` and the nominal variant (1990-01-02 to 2026-10-20, daily), aggregated to month averages (also month-end for event windows). Outcomes: UNRATE, core PCE (PCEPILFE), funds rate, one-year yield (FRED).
Instruments: NS and BS surprises; the SF Fed USMPD workbook (1994 on) and `michaeltkiley/monetary_policy_surprises` are the likely sources; check which shocks that repo already builds before rebuilding.
Instrument sample ends well before 2026; the identification sample is about 1994-2019, with 2020+ and the 2026 episode as out-of-sample.

## 6. Risks
1. **Circularity**: the weights are FRB/US-implied, so the index embeds the Fed model's transmission view; a ratio near 1 is partly by construction (the partials sum to the full hike within 4-11%). Report the component IRFs, not only the total.
2. **Weak sensitivities and data links**: 2040 steady-state start, VAR expectations, 10-year as the long end, linear extrapolation, r* filter artifacts (NOTES in `ms_fci`).
3. **Pre-2008 validation is weak** (+0.17 with the funds rate); the index is conditions relative to the sample mean, not a policy-rate proxy.
4. **Instrument strength**: earlier LP-IV on a related index had first-stage F of 6-12; use robust inference.
5. **Novelty** until a literature search is done.

## 7. Next steps
1. Confirm the specification of the existing two-variable VAR (section 4 of `INDEX_AND_LITERATURE.md`).
2. Build the monthly dataset (index variants, outcomes, NS/BS instruments).
3. Cholesky baseline with and without the index, then the proxy-SVARs and the tests above.
