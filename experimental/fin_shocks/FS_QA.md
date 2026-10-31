# Financial shocks: decisions, one at a time (started 31 Oct 2026)

Labels: [decided] by the user; [proposal] my suggestion, not adopted until confirmed.

**FS-A1 (31 Oct 2026). [decided]** The user approved the proposals in `PROPOSALS.md` ("these are all good; let's pursue all"): P1 (recursive financial shock, index versus credit), P2 (sign restrictions), P3 (unemployment-risk model), P4 (identification through heteroskedasticity). Order [proposal]: P1, P2, P3, P4. The defaults written into the proposals stand: 12 lags (4 as a check), 2020 monthly dummies, r*-gap index baseline with nominal and real as checks, samples 1973-2026, 1990-2007, 1994-2026, EBP and NFCI as credit comparators, bootstrap bands.
**FS-A2 (31 Oct 2026). [decided]** In addition, a literature review on mixed-frequency VARs and mixed-frequency identification: `MIXED_FREQUENCY_NOTES.md`. It proposes an optional **P5** (frequency ladder and bridge), awaiting the user.
**Design choice made by me in P1 [proposal, to be confirmed]:** the policy variable is the **funds rate** (the cleanest policy instrument, not mechanically overlapping with the index's yield component); the 2-year is the check.

**FS-A3 (31 Oct 2026). [decided] Mixed-frequency idea, answers to my questions.** (1) Run the cheap go/no-go test first: yes. (2) Frequencies: minutes (sparse windows) to daily to monthly; the state-space model is the point of the exercise. (3) Samples: a long mixed-frequency VAR from 1973 and a 1994- sample to match USMPD; daily data from 1997 (credit spread) only as robustness or if needed. (4) Run the window shock three ways: NS, MP1, Greenbook-purged NS: yes. Plan for the user's return: `MF_PLAN.md`.
**FS-A4 (31 Oct 2026). Stage-0 result. [result, not a decision]** Passed the pre-registered criteria (GO); sign conventional in all three shock versions; magnitude depends on within-month timing by a factor of 2 to 3, which motivates the mixed-frequency build. Details in `MF_PLAN.md`.
