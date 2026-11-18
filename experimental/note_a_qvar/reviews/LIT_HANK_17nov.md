# Literature deep dive 1: HANK and risk-premium NK models (subagent, 17 Nov 2026)

Reviewer read every PDF cited (working-paper versions; saved in the session scratchpad). Page numbers are of the versions read; "e" = eyeballed from a figure; conversions to a 1 pp basis are the reviewer's [inference].

**Citation corrections:** NBER WP 28869 is Kekre-Lenel (not Caramp-Silva; Caramp-Silva is UC Davis WP 341 / CESifo WP 11049, read 20 June 2023 draft). Kekre-Lenel journal details (Econometrica 90(5), 2022) [secondhand]; read NBER revision May 2022.

## Short answer
Two models come close to the high-frequency equity response: Kekre-Lenel and Pflueger-Rinaldi. Both have transitory shocks and front-loaded output, no hump at 4-8 quarters. The humped, persistent HANK (Auclert-Rognlie-Straub) has equity responses 3-5 times smaller and equities about a quarter of consumption or less. Melcangi-Sterk has a strong stock channel through investment flows, with a model stock price that barely moves. No model delivers both an equity response near 7.7 percent per pp and an output effect still near 1 percent at 8 quarters (as FRB/US does).

## Papers
1. **Kekre-Lenel** (NBER WP 28869 rev. May 2022). Heterogeneous risk aversion; easing redistributes to risk-tolerant households, lowers risk premia, raises investment and wealth. Data (GK SVAR-IV): 0.2 pp fall in 1-year yield -> real S&P 500 +1.92 pp [1.54, 2.59], 59 percent excess-return news (pp. 2, 18-19, Table I) [verified] (~9.6 percent per pp of 1-year yield [inference]). Model: excess equity return 1.2 pp on impact (p. 36) [verified] (~6 percent per pp); excess-return news 32 percent vs 59 in data (Table VII p. 37). Shock iid (rho_m = 0). Output peaks 0.7 pp on impact (RANK 0.5), ~0.1 by q4-5, ~0 by q8 (e). Amplification 1.3-1.4x (p. 2, 36) -> ~25-30 percent via risk premia [inference]. Claims match to SVAR-IV evidence.
2. **Caramp-Silva** (draft 20 June 2023). Rare disasters, heterogeneous beliefs, risky government debt; neutrality if consumption = dividends. 100 bp rise, half-life 3.5 months: stocks -2.15 percent ("smaller than Bernanke-Kuttner but within their confidence interval", p. 32) [verified]; output -1.05 on impact (RANK -0.14), back near zero by t 3-4 (e); time-varying risk 39 percent of output response, outside wealth 47, intertemporal substitution 6.5 (pp. 33-34) [verified].
3. **Melcangi-Sterk** (REStud 92(4), 2025). Participation ~25 percent (1989); stock investment channel (flows into mutual funds finance investment), not a consumption wealth effect. Own VAR (MAR, +100 bp FFR): S&P 500 trough about -10 to -12 percent (Fig. 2 p. 8, e). Model: output -1.6 first quarter (calibrated), consumption -0.75, investment -6.3, price level -0.26 (pp. 25-26, Table 5) [verified]; back to zero by q3-4 (e); "Stock prices fall much less in the model than in the data" (p. 26), about -0.4 percent (e). Shutting stock investment makes output response much smaller and less persistent (p. 27).
4. **Kaplan-Moll-Violante** (AER 2018). Equity in the illiquid asset; profits fall in an easing under sticky prices, so equity tends to fall; neutralized by reinvesting profits. Indirect effect via r^a and q: -2 percent of consumption response (Table 7, p. 727) [verified]; share price response near zero (e). ARS (p. 33): many leading models "do not even get the stock market response to go in the right direction".
5. **Pflueger-Rinaldi** (NBER WP 27856, 2020; JFE 2022 [secondhand]). NK with habits; no investment; no feedback from stocks to spending [inference]. HF data: S&P 500 -4.11 per pp of 1-hour fed funds surprise (2001-2019); model -5.27 per pp, of which risk premium -2.54 (Table 4 p. 34; pp. 23-24) [verified]. Output gap per pp ~-0.2 at 4q, ~0 at 8q; inflation ~-0.5 pp (Fig. 3, e).
6. **Caballero-Simsek** (WP 30132 rev. 2023; JF 79(3) 2024; Caballero-Caravello-Simsek WP 33206 rev. 2026). MPC out of wealth 0.04, half adjust per year, multiplier 1.5 -> ~3 cents of next-year spending per dollar (JF pp. 1747-48) [verified]. Equity ~40 percent of the average annual absolute change in the GS FCI ex housing (WP 30132 fn. 1, p. 2, citing Hatzius et al. 2017) [verified]. FCT: a 1.9 percent equity flow shock -> ~0.08 percent output at ~2 years (pp. 15-17) [verified]. Scaling [inference]: a 7.7 percent equity move -> ~0.3 percent output at 1-2 years; 14.5 percent -> ~0.6.
7. **Bianchi-Lettau-Ludvigson** (JF 2022): regime shifts in policy move valuations; no shock-level elasticity [verified by text search].
8. **Added: Auclert-Rognlie-Straub** "Micro Jumps, Macro Humps" (NBER WP 26647, 2020). Estimated HANK, sticky expectations, equity in the illiquid account, matches Romer-Romer. 25 bp cut: stocks +0.4 percent (~1.6 per pp), "somewhat smaller" than Bernanke-Kuttner (no risk premia, p. 33); output hump peak ~0.11 at ~6 quarters (~0.4-0.45 per pp at 4-8q) (Figs. 3, 9, e); stock returns ~25 percent of consumption response (Fig. 9 p. 34, App. A.3) [verified]. Footnote 27: average Coenen et al. (2012) DSGE ~0.5 percent output per pp at 4 quarters [verified].

## Comparison table (conversions rough)

| Paper | Equity per 1 pp | Output ~4q per 1 pp | Output ~8q | Inflation | Share via equity / risk premia | Matches HF equity? |
|---|---|---|---|---|---|---|
| This paper (HF windows; VAR) | -7.7 (2-year yield) | -0.75 to -1.1 per FCI point | -0.4 to -0.5 | - | ~40 percent of reading | data |
| FRB/US | -14.5 (persistent FFR) | -0.46 | -0.96 | - | 53-60 percent of reading | - |
| Kekre-Lenel | model ~6, data ~9.6 (1-year yield; iid) | ~0.5 e | <=0.2 e | price level jump | ~25-30 percent | yes (SVAR-IV) |
| Caramp-Silva | -2.15 (policy rate) | ~0 e | ~0 | n/a | 39-52 percent risk | partly |
| Melcangi-Sterk | model ~-0.4 e (VAR ~-12) | ~0 e | ~0 | -0.26 price level | stock investment channel | no |
| KMV 2018 | ~0 (sign problem) | ~0 e | 0 | +1.3 pp | -2 percent | no |
| Pflueger-Rinaldi | -5.3 (FFR; data -4.1) | ~-0.2 e | ~0 | ~-0.5 pp | none (no feedback) | yes (1-hour) |
| Auclert-Rognlie-Straub | ~+1.6 e | ~0.4 e | ~0.4 e | small | ~25 percent of consumption | no |
| Caballero-Simsek (arithmetic) | data | - | ~0.3 at 1-2 years for 7.7 percent | - | equity ~40 percent of GS FCI moves | n/a |

## Assessment (reviewer)
1. Only risk-premium models reach the paper's equity magnitude; HANK without risk premia is 3-20 times too small or wrong-signed; FRB/US's 14.5 is larger than any structural model here.
2. Models that match equity have front-loaded output; none reproduces FRB/US's building path; ARS's hump (~0.4 per pp) is close to FRB/US at 4q and the VAR at 8q but with a small equity response.
3. Shares through equities 25-50 percent where the mechanism exists; ~0 in KMV and Pflueger-Rinaldi. The paper's 40 percent and FRB/US's 53-60 are within or above the risk-premium HANK range.
4. For the argument [inference]: "research models have an equity channel" is accurate but each has only part of it; no single model combines a HF-sized equity response, feedback from equity to spending, and persistent humped output.

Not checked: journal page numbers for Kekre-Lenel and Pflueger-Rinaldi; Caramp-Silva time unit; Melcangi-Sterk Q_w definition; KMV share-price magnitude; exact 4q/8q numbers (none tabulated).
