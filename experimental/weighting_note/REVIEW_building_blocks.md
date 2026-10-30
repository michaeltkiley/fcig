# Review: "Measuring Financial Conditions: when do market, macroeconomic, and principal-component methods agree?" (tutorial dated 24 Oct 2026)

Reviewed 27 Oct 2026 against the weighting note in this folder (`weighting_note.tex`) and the project's empirical work. The PDF itself is not in the repo; its companion script and "theory memorandum" are not in the repo either.

## What it does
- Single target: the GDP effect of current financial conditions, scaled by the GDP effect of a 1 pp *immediate* policy move, F = θ'x/θ'b. Funds rate kept out of the index.
- Two-step test for any weights m with m'b = 1: bias (right on average for every state of the economy) first, then precision (noise variance m'Rm, with R the covariance of iid measurement error in x).
- Economy 1 (fixed proportions, x = b s): market, macro and normalized-PC weights are all unbiased; they differ only in precision; the BLUE is R⁻¹b/(b'R⁻¹b).
- Economy 2 (non-policy shocks C ν move x differently): market weights unbiased iff (m_W − θ/D)'C = 0; with full rank, iff θ ∝ W b. MSE splits into wrong-weight error plus noise.
- Economy 3 (one shock, different speeds, MA(1)): unbiased requires m'b₀ = 1 and m'b₁ = θ'b₁/θ'b₀; market weights fail unless b₁ ∝ b₀.
- General MA: unbiased iff (m − θ/D)'B_j = 0 for all lags and shocks; sufficient condition B_j = b h_j' (fixed proportions). Forecasting h ahead needs ψ_{h+j} = ψ_h ψ_j (geometric decay) even with fixed proportions.
- Estimation: local projections for B_h and g_h; θ from B_h'θ = g_h by GLS/minimum distance; weight uncertainty; reverse regression = shrunk market index; OLS of GDP on noisy x is attenuated; direct funds-rate effect.

## Assessment
**Strong and correct.** I checked the algebra (BLUE derivation and the no-cross-term decomposition, the constrained minimum-variance formula m_U, the reverse-regression shrinkage, the MA(1) conditions, the geometric-decay condition): all correct. The bias-then-precision ordering is the right discipline, and the point in 3.2 (covariance weighting by event-window residuals can downweight economically important risk-appetite moves) is important for our market index.

**It reaches the same core results as our note.** Mapping: their measurement error e (covariance R) = our noise component u^n (Σ_n); their non-policy shocks Cν = our causal component u^c (Σ_c); their F = our output equivalent O; their condition θ ∝ Wb = our equivalence condition g ∝ Σ⁻¹ψ; their fixed-proportions economy = our policy ray / common dynamics. The two documents are consistent.

**Where it differs from, or is narrower than, what the project needs.**
1. *One target only.* It treats the output effect as the only object, so the market index is "biased" whenever non-policy shocks have output effects. The project's market lens is deliberately a transmission (policy-equivalent) measure; under that target the market weights are BLUE without a GDP model. Our note keeps both targets and shows the gap between indexes is always (s − w)'u, i.e. only non-policy movements. Recommend the note keep the two-target framing; the tutorial's framing should be cited as the output-target special case.
2. *Normalization.* It uses an immediate policy move and a static GDP equation (y = θ'x). The project's yardstick is a persistent 1 pp hike evaluated at four quarters with GDP responding with lags (FRB/US). Section 6.3 flags this but does not carry it through; our note's levels result (horizon-k cumulative responses are right for levels only if the configuration has persisted k periods and effects have built up) and the FCI-G growth-impulse identity fill that gap.
3. *"Measurement error" in prices.* Financial prices are observed almost without error; what the market method treats as noise is non-policy news. Their iid assumption on e fits event windows but not levels, where non-policy deviations are persistent. This is the Ψ_E (window) vs R (levels) issue they note in 2.5; for our indexes it is first order and should be stated as such.
4. *Complete transmission.* The tutorial assumes policy works only through the included x (until 7.3). In FRB/US it does not: the partials sum to about 80% of the full q4 hike effect (expectations channel). Worth stating the check s'ψ explicitly as we do.
5. *PCA.* Useful and not in our note: NFCI-style indexes are in scope, and the result that a normalized first PC is unbiased only if v'C/v'b = θ'C/D (and in the dynamic case v'b₁/v'b₀ = λ) gives the NFCI a place in the same framework. Recommend adding a short PCA paragraph to the note when the NFCI conversion is done.
6. *Identification of θ.* Section 6.2 (θ from multiple shocks/horizons via B'θ = g) is a genuinely new idea relative to the project: impulse responses to a single policy shock at several horizons can identify θ when the number of horizons is at least the number of variables and the financial responses are not proportional. It is a possible empirical extension (LP of financial variables and GDP on NS/GSS surprises), though power will be low.

**Minor.**
- Title page says "prepared for Michael T. Kiley"; the closing sentence refers to an accompanying script and a "separate theory memorandum and repository": neither is in this repo.
- Units: the reference policy change is an immediate funds-rate move; the project's unit is a parallel, persistent path shift. The equations are unchanged but the numbers are not; state the unit when quoting.
- No numerical illustration with the project's estimates; our note's last section supplies one (IR weights price the observed market response vector as about 1.00 funds-rate unit; s/w ratios 0.95 / 0.64 / 1.57 for 10-year / equities / dollar).

## Suggested use
Treat the tutorial as the appendix-level derivation for the output target (bias/precision, PCA, MA dynamics, identification of θ); keep the weighting note as the main text with the two-target framing, the mixed-case formula and the levels/FCI-G results. Add PCA to the note when NFCI is brought in.
