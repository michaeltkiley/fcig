# Assessment: financial conditions indexes in funds-rate-path units from FOMC surprises (22 Oct 2026)

Status: experimental, exploratory. Everything here is reproducible from the scripts in `experimental/path_fci/` (market-based indexes) and `experimental/ms_fci/`
(model-based, FRB/US). Data to 20 Oct 2026. The preferred approach is the **GSS path factor** and **Nakamura-Steinsson policy news** versions below.

## 1. The question
GS and Fed FCI-G style indexes combine financial variables with weights that come from a macro model (GS: FRB/US-based weights on a levels index; FCI-G: FRB/US
growth effects). Can the weights instead come from financial markets directly: how large are the moves in core financial variables associated with a given
monetary policy surprise? The index is then in units of a policy-rate path, a "funds-rate equivalent" without a macro model.

## 2. Preferred method (GSS and NS)
Data: SF Fed US Monetary Policy Event-Study Database (USMPD), 253 FOMC events 1994-2026 (unscheduled events with MP1 = 0 and Mar-Apr 2020 dropped); event-window surprises
in the futures and in the 10-year Treasury yield (UST10Y), S&P 500 (SP500) and the dollar index (DXY).

1. **Policy factor.** Two measures, both from the event-window surprises in MP1, MP2, ED2, ED3, ED4:
   - *GSS path factor* (Gurkaynak, Sack and Swanson 2005): first two principal components, rotated so the second has no loading on MP1; path = the second, scaled so that 1 unit = 1 pp on ED4
     (the expected 3-month rate roughly a year ahead; the current-meeting funds rate is unchanged). Correlation with the ED4-residual path surprise: 0.86.
   - *Nakamura-Steinsson policy news* (2018): first principal component, scaled so 1 unit = 1 pp on the 2-year yield (USMPD has no 1-year). It mixes target and path news (correlation with MP1: 0.62; with the GSS path: 0.98).
   No instruments and no target control: the factors are used as the policy measure.
2. **Response.** For each variable, `x_j = a_j + b_j f + e_j` in the event window: b_j = move per 1 unit of the factor.
3. **Weights without double counting.** One latent factor, three noisy indicators. Weights `w = Psi^-1 b / (b' Psi^-1 b)` (Psi = full covariance of the errors), so `w'b = 1`: a unit surprise moves the index one unit,
   and the index is the minimum-error-variance estimate of the factor. A variant uses only the error variances (diagonal Psi).
4. **Index.** `index_t = sum_j w_j (x_j,t - mean_j)` on daily levels, 1990-2026 mean: real 10-year yield, 100 ln CAPE (real valuation), 100 ln real dollar. Higher = tighter. Weights are estimated once from the event window
   (nominal 10-year) and not re-estimated for the real or r*-adjusted 10-year. Units: pp of the factor (GSS: pp on ED4; NS: pp on the 2-year).

Why preferred: no macro model; cleaner than one ED4 residual (several indicators averaged); weights are stable across variants; fit to the GS FCI is the best of the versions tried.

## 3. What it shows
Event-window responses to a 1-unit surprise (se): GSS 10-year +0.40 pp (0.03), S&P -5.2% (0.6), dollar +3.1% (0.3); NS 10-year +0.54 (0.06), S&P -7.8% (0.9), dollar +4.2% (0.5).

Weights (pp of factor per unit of variable; 90% bootstrap band) and shares of the unit response:

| | 10-year | Equities (per 1%) | Dollar (per 1%) | Shares (10y / eq / usd) |
|---|---|---|---|---|
| GSS path | 0.97 [0.35, 1.56] | -0.059 [-0.078, -0.036] | 0.098 [0.04, 0.16] | 39 / 31 / 30% |
| NS news | 0.61 [0.16, 1.10] | -0.051 [-0.066, -0.031] | 0.065 [0.02, 0.12] | 33 / 40 / 28% |
| diagonal Psi, GSS | 0.91 | -0.049 | 0.122 | 36 / 26 / 38% |
| diagonal Psi, NS | 0.61 | -0.041 | 0.085 | 32 / 32 / 36% |
| FRB/US q4 (model-based, per unit of the variable; see ms_fci) | 0.57 | -0.032 | 0.10 | |

- Each of the three variables carries roughly a third of the policy signal. Equities and the dollar get close to their FRB/US weights per unit; the 10-year weight is higher (about 0.6-1.0 vs 0.57); the 10-year weight is the least precise.
- Index fit (real 10-year version, 1990-2026): correlation with the GS FCI 0.88 (GSS) and 0.92 (NS) in levels, 0.92 and 0.96 in daily changes; with the MS-style FRB/US-weighted index 0.87 / 0.84 in levels, 0.90 / 0.87 in daily changes.
- 10-year versions (same weights): nominal / real / real gap to Kiley's r*: GSS latest -0.30 / -0.59 / -0.42; NS -0.74 / -0.92 / -0.81 (pp of factor). Daily changes are the same across versions; the real and r* adjustments lower the level standard deviation (GSS 2.29 / 1.77 / 1.52)
  and improve the level fit to the GS FCI (0.80 / 0.88 / 0.91 for GSS). The FRB/US-weighted MS index reads +0.80 / +0.62 / +0.72 on the same 10-year versions.
- Today (20 Oct 2026) the market-weighted indexes read slightly loose (equity valuations at record levels), while the FRB/US-weighted MS index reads tighter; the diagonal variants read -0.20 to +0.15.
- Changes since 27 Feb / 27 Aug 2026 (GSS nominal): +1.13 / +0.73, almost entirely the 10-year (+1.14 / +0.46) and dollar (+0.32 / +0.25), offset by equities (-0.33 / +0.02). NS nominal: +0.65 / +0.47. Real versions: GSS +0.71 / +0.54; NS +0.38 / +0.35.
  FRB/US-weighted MS: +1.18 / +0.74 nominal, +0.94 / +0.63 real. GS FCI: +0.45 / +0.43 index points.

## 4. Related work in this repo
- `experimental/ms_fci`: a five-variable Morgan Stanley-style index (10-year, BBB spread, equities, dollar, oil) in funds-rate equivalents from FRB/US (q4 weights 0.57, 0.13, -0.032 per 1%, 0.10 per 1%, 0.008 per 1%; level and change versions;
  nominal, real and r*-gap 10-year; the original MS index is unverified). Full-transmission funds-rate hike effect on GDP in FRB/US: -0.45 / -0.95 / -1.43% at 4 / 8 / 12 quarters.
- Earlier steps in `path_fci/` (kept for the record): event-day regressions on the ED4-residual path surprise with GLS weights (`path_fci.py`), robustness (LAD/Huber), the BBB IV check, reverse regressions, and IV/instrumental-PC variants.

## 5. What did not work, and why
- **BBB spread.** Event-day spreads *narrow* after hawkish path surprises (IV on the 10-year, Baa less 10-year and ICE OAS: -0.4 to -0.5 per 1 pp of 10-year, first-stage F > 50). The GLS weights net it against the 10-year, so it is dropped. No intraday BBB or oil series exists in USMPD.
- **Oil.** Not identified (t about -1), dropped.
- **IV reverse regressions** with ED1-ED4 as instruments fail the exclusion restriction (the path surprise is built from ED4); with S&P futures and FX series as instruments the dollar's instruments carry its own noise.
- **Plain reverse regression** (surprise on the three variables) gives shrunk weights (R2 about 0.5) and puts little weight on equities; its relative weights equal the factor-model weights up to the R2 scale.
- **Instrumental PC from ED1 + 2-year**, with or without MP1 control: weights similar to raw ED4; target-neutral constraint is unstable.

## 6. Caveats
Weights come from a few hundred event-window moves; the 10-year weight band is wide. Applying event-window responses to daily levels assumes level deviations map to policy tightening like surprises do. The index is in units of a futures-implied
rate path (a year-ahead 3-month rate for GSS), not an effective funds-rate-equivalent in the model sense. Weights for the real and r* versions come from nominal surprises. ED4 changed from Eurodollar to SOFR futures in 2022. Importance for output is not
identified by these regressions (they give transmission from policy to markets, not effects on growth); the FRB/US weights supply that.
Sample splits (non-ZLB only) change the weights materially (intraday GLS 10-year weight 1.1-1.4 vs 0.96).

## 7. File map (`experimental/path_fci/`)
`path_fci_gss_ns.py` (preferred; `--diag`, `--real10`), `path_fci_rates_variants.py` (nominal / real / r* versions), `path_fci_changes.py` (changes between dates), `path_fci.py` (event-day regressions, shared code),
`path_fci_raw_ed4.py`, `path_fci_ipc*.py`, `path_fci_iv*.py`, `path_fci_intraday*.py`, `path_fci_reverse*.py`, `path_fci_robust.py`, `path_fci_nobbb.py`, `path_fci_charts.py`; README.md has the full chronology. USMPD workbook path is set in `path_fci.py`.
