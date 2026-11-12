# Round 4 results: buttressing the foundation of Note B (11 Nov 2026)

Four independent analyses (no FOMC-window surprises; design fixed before estimation; each folder has code and `RESULT.md`; I have not re-run them). Question: can Note B treat the market index, measured relative to r*, as a channel?

| Folder | Question | Verdict | Key numbers [as reported by the agent] |
|---|---|---|---|
| `purge/` | Is the flow just activity reflected back (Hatzius et al. / ANFCI purge)? | **Partly buttresses** | Phi(12) market r*: 0.57 [0.22, 0.84] unpurged, 0.32 [0.10, 0.51] full-sample purge, 0.19 [0.11, 0.33] recursive purge (all 30 intervals exclude zero); a third to a half of in-sample content is activity; payroll result does not survive a full purge. |
| `nfci/` | Does the market flow complement the NFCI/ANFCI? | **Complements** | Both keep coefficients at 6 and 12 months for unemployment (market flow t 4.3 and 3.1; NFCI 3.1 and 3.6); at 24 months and for recessions the NFCI carries it (recession t 4.2 vs 1.3). NFCI is a level index, the market index a flow index. NFCI is explained 36% (levels) by the three variables, 51% adding the Baa-10y spread. |
| `rstar_basis/` | Does the r* basis stabilize the index-unemployment relationship and its level? | **Cannot say; weakly buttresses neutrality only** | Level at a zero gap, 2009-19 minus 1990-2007: nominal -2.13, real -1.44, r* (LW) +0.88, r* (Kiley) +0.03; the 12-month response falls from about 0.65 to about 0 after 1989 at every basis; the unit restriction on r* (coefficient -1.52 on r*) is neither rejected nor distinguishable from no adjustment (power). |
| `stance/` | Does the index add to the funds-rate gap in explaining the economy ahead? | **Buttresses (flow form, activity, not inflation)** | Unemployment: index given funds-rate gap adds 0.105-0.119 adjusted R2 (t 5.5-6.2), the gap adds nothing given the index; out of sample RMSE 5-8% lower, 1 of 9 primary tests survives Holm; equities carry the increment, not a rates summary; episodes 2004-06 -1.29 [-1.86, -0.65] and 2022-24 -1.40 [-2.22, -0.39] (index minus funds-rate gap), ordinary in size. |

## What this means for the foundation
- **Buttressed:** the index is not a rates summary and not only activity reflected back (a purged flow still predicts unemployment and keeps a positive response); it is a complement to, not a rival of, the NFCI; it carries stance information beyond the funds-rate gap for activity.
- **Not buttressed, and Note B should not claim it:** that the r* basis stabilizes the unemployment response (it does not; the response falls after 1989 in every basis); payrolls; inflation; recession risk (NFCI carries it); a unit-restriction test of r* (no power).
- **Caveat for Note B:** the index carries both a channel and an anticipation component; the unemployment response is the claim.
