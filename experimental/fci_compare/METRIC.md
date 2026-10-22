# Pre-specified metric for comparing indexes in funds-rate units (written 22 Oct 2026, before computing the comparison)

Purpose: fix how agreement and disagreement are measured so that episodes are not picked after seeing the results. Experimental, part of the plan in `experimental/path_fci/NOTE_PLAN.md`.

**Indexes (first pass).** (1) Official Fed FCI-G, monthly, 3-year-lookback baseline (`raw/fed_monthly_3yr.csv`; the 1-year lookback as a check); (2) the GS replication (`fcig_gs_daily.csv`); (3) the market-based index (intraday event-window weights on the 10-year, equities and dollar; parallel unit); (4) the MS-style FRB/US-weighted index (`experimental/ms_fci`, q4 weights). NFCI, ANFCI, SF Fed proxy and OFR FSI are added later.

**Frequency and sample.** Monthly (end-of-month values for daily series), January 1990 to the latest month. Every index is demeaned over the common window 1990-01 to 2026-09 (zero = that average), in pp of funds rate; higher = tighter.

**Units.** Each index is divided by its own conversion factor (pp of the index per 1 pp parallel funds-rate move). Two conversions are reported for each index where available and the comparison is run under each: (a) output-equivalent: FCI-G only at first, by the FRB/US yardstick (GDP effect of a full-transmission funds-rate hike at 4 quarters; 8 and 12 quarters as sensitivity); the MS-style FRB/US index is native; (b) transmission-equivalent, applied uniformly to every index: the cumulative 3-month response of the index to a parallel policy surprise (MP1 and ED4 both up 1 pp), estimated by monthly local projection on USMPD surprises summed by month (h = 0 as a check).

**Metrics (all computed, none selected afterwards).**
1. Levels: pairwise correlation and the regression slope of one index on another in funds-rate units (amplitude ratio).
2. 12-month changes: correlation, slope, and the share of months in which the signs of the 12-month changes agree.
3. Gap in funds-rate units: for each month, each index minus the cross-index median; report the mean absolute gap by index and the cross-index range (max minus min) by month.
4. Episodes: defined mechanically as (i) the 24 months with the smallest cross-index range ("closest alignment") and (ii) the 24 months with the largest range ("biggest differences"), taken as non-overlapping 6-month windows ranked by the mean range; every window found is reported, whatever it contains.
5. By group (rates incl. the policy rate, corporate yields and mortgage rates; equities; dollar; other): contributions in funds-rate units to the latest level, to the change since 27 Feb 2026 and since 27 Aug 2026, and to the cross-index gap in each episode window.

**Not done:** no episodes chosen by hand; no ranking of indexes; no policy-versus-other decomposition.
