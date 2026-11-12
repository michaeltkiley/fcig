# Check of step 27 (four calibrations on other input series)

Deterministic (two runs, identical checksums) [verified]. Weights identical to step 26 (same estimation code and draws); the r* column reproduces step 26's distances (F-G 0.068, F-B 0.256, F-Y 0.282, B-G 0.281) [verified by comparison of the printed values].
- Input sets from `lib/cases.inputs`: 'real' gives the real 10-year yield, 100 ln CAPE and the real dollar; 'nominal' gives the nominal 10-year yield, 100 ln CAPE and (column dollar_gs) the nominal broad dollar [verified in the code].
- [inference] '100 ln CAPE' is the documented GS equity concept (prices over a 10-year average of earnings, Caballero-Simsek p. 6); GS's own series and transformations are not reproduced.
