# Pseudo real time: what can be built, and does the stance/flow result survive?

**Availability, input by input [verified by download]**

| Input | Real time? | Earliest vintage | Done |
|---|---|---|---|
| UNRATE, PAYEMS | yes | ALFRED 1962, 1956 | vintages 1977-2026; information = vintage 2 months after origin |
| PCEPILFE (core PCE) | yes, from 2001 | Oct 2000 | vintages 2001-2026; no pre-2001 origins, so no 1995 OOS |
| NROU (CBO natural rate) | partly | Mar 2011 | origins from 2011 only; earlier gap uses ex-post NROU |
| r* Laubach-Williams | partly | NY Fed real-time file, 2005Q1 | final point of each vintage; none Aug 2020 to May 2023; 3 mistyped release dates fixed |
| Cleveland Fed expected inflation | no | none (current file only; ALFRED has none) | revised series kept |
| Weights; Kiley r*; CAPE earnings (Shiller); FRB/US | no | none | unchanged |

**Design (fixed before estimation; `04_run.py`).** Market index; stance design of `../../followup2/stance` and level-flow design of `../../followup/levelflow`. Versions on identical origins: revised; rt1 (vintage u, payrolls, core PCE; outcomes as first reported, vintage 14 months after the origin; ex-post NROU); rt2 (rt1 plus vintage NROU). Blocks: A 1976-2025, HAC 18, recursive OOS from 1995; B real-time r* (2007-25, n=166); C vintage NROU (2011-25, n=137); D core PCE (2002-25); B-D in sample. 135 specifications, descriptive; primary family: 6 Clark-West tests (du, pay x 3 forms), Holm.

**Results [verified, `out/`]**
- *Revisions are small for unemployment, larger for payrolls and inflation.* Correlation with revised outcome 0.997 (du), 0.989 (pay), 0.91 (core PCE); real-time r* is 0.55 below the full-sample series on average (correlation 0.79).
- *A. Unemployment, r* step, Market, revised vs real time:* flow t 5.50 vs 5.49; mixed 6.24 vs 6.35; adjusted-R2 gain 0.119 vs 0.123; recursive Clark-West 1.96 vs 1.97 (flow) and 2.38 vs 2.39 (mixed); RMSE ratio 0.952/0.921 vs 0.947/0.916. Level-and-flow regression: flow t 5.18 vs 5.26, level 0.51 vs 0.48. UNRATE is barely revised and rt1 keeps the ex-post NROU.
- *Payrolls* get stronger on first-release data: r* flow t -2.2 to -4.2, CW 1.84 to 2.73; Holm p 0.133 to 0.019.
- *C. Vintage NROU (2011-25):* r* flow t 2.62 (revised), 2.64 (rt1), 3.10 (rt2); gain 0.019, 0.020, 0.036.
- *B. Real-time r* (2007-25):* unemployment flow t 3.17 with full-sample r*, 2.23 with real-time r* (2.43 with real-time data too); gain 0.065 to 0.019-0.023; mixed form 2.16 to 1.05-1.25. The revised version is already weaker in this sample, so part is sample. No OOS possible.
- *D. Core PCE:* revised data show nothing; first-release inflation gives a negative index coefficient (t -1.7 to -3.6). Descriptive; not claimed.

**Verdict: yes where it can be built, cannot say for r* and weights.** The unemployment stance and flow results are unchanged with vintage unemployment data (t, gain, Clark-West identical to two decimals) and payrolls improve; vintage NROU (2011+) does not weaken them. With real-time r* the r*-step flow result survives in sign and at the 10 percent level but shrinks by two thirds in gain, and the mixed form does not.

**Sentence for the paper.** "I rebuild the activity and unemployment-gap inputs from ALFRED vintages (unemployment and payrolls from 1977, core PCE from 2001, the CBO natural rate from 2011) and the r* input from the New York Fed's real-time Laubach-Williams estimates (from 2005); this is pseudo real time in the macro variables, not in the market weights, the Kiley r*, the CAPE earnings or the inflation expectations."
**Avoid:** "real time" in any title or abstract; "out of sample" for the weights; any claim that the r*-step index is real time before 2005.

**Recommendation.** One paragraph in robustness plus one table: rows revised, vintage data, vintage NROU (2011+), real-time r* (2007+); columns flow t, adjusted-R2 gain, Clark-West (long sample only). Report the r* row as smaller; omit core PCE.

**Limits.** Conservative information lag; real-time r* is a step series, timing differs from the interpolated package series; blocks B-D are in sample.
