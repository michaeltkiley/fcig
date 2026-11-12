# Check of step 26 (four calibrations on common assets and units)

Deterministic (two runs, identical checksums) [verified]; first 500 F draws equal the stored `weights_boot.csv` draws (asserted) [verified]; F weights equal `market_weights.csv` (asserted) [verified].
- GS weights are `lib/indexes.GS_W` (0.451, -0.049, 0.060 on the 10-year, equities, dollar), the published U.S. weights (Caballero-Simsek 2026, Table 1, US row 4.4/45.1/39.6/4.9/6.0) [verified against the PDF, p. 6]. The published-weight arithmetic (0.060 x 3.9)/(0.049 x 5) = 0.955 is reproduced (`gs_ratio_raw`) [verified].
- Y normalized on the factor response reads 0.999 on psi_F, so the common and own normalizations give the same distances to three decimals [verified].
- [inference] G applies the GS weights to this package's r*-step series (earnings-yield gap in CAPE log points; real broad dollar), not to GS's own variable definitions (prices over 10-year average earnings; nominal trade-weighted dollar); the GS policy-rate and BBB-spread terms are held fixed. G is a published benchmark applied here, not the GS index.
- Not independently re-derived: the pairwise distances and the judgment counts.
