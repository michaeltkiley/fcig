# Literature deep dive 3: empirical equity responses, activity effects, stock-wealth effects (subagent, 17 Nov 2026)

Reviewer read working-paper versions (PDF pages of the versions read). Tags: [verified p.X]; [fig] read off plots; [inference] unit conversions (to per pp of the 2-year yield: divide by the study's own 2-year window response, else GSS 0.47 for target surprises).

## 1. Equity responses
| Study | Per 1 pp (rate) | Per pp of 2-year [inference] | Notes |
|---|---|---|---|
| Bernanke-Kuttner 2005 (FEDS 2004-16) | -4.68 target (t 3.03, R2 0.17), -2.55 excl. outliers (Table 2 p.41) | ~-10 (-5.4 excl. outliers) | decomposition (Table 11 p.50): 53 percent risk premium, 42 dividends, 5 real rates; "very little" through real rates (p.4) |
| Rigobon-Sack 2004 (NBER w8794) | -7.70 (SE 2.75), 3-month eurodollar (Table 2 p.18) | ~-10.5 (2-year response 0.73, Table 3 p.19) | fed funds futures shocks smaller, insignificant |
| GSS 2005 (FEDS 2004-66) | target -4.26 (SE 1.11); path -0.94 (n.s.) (Table 5 p.27) | target ~-9.1; path ~-2.3 | 30-minute windows |
| Ehrmann-Fratzscher 2004 (ECB WP 354) | -5.5 target (p.14) | - | 79 FOMC meetings 1994-2003 |
| Nakamura-Steinsson 2018 (w19260) | -6.5 per pp of 2-year forward (Table 5 p.36) | ~-6.7 | 10-year 0.35 per pp of 2-year |
| **Bauer-Swanson 2023 (Macro Annual, w29939)** | -5.39 per ED4 (t -7.7, **R2 0.304**); orthogonalized -5.50 (Table 3 p.29) | **~-7.4**; 10-year ~0.56 | 322 announcements 1988-2019, 30-minute windows: closest like-for-like benchmark to this paper's -7.7, R2 0.31, 10-year 0.53 |
| Swanson 2021 (w23311) | per sd factor (Tables 4-5) | funds rate ~-8.6; forward guidance ~-3.3 (pre-ZLB), ~-5.1 (ZLB); LSAP n.s. | stock R2 0.31 |
| Jarocinski-Karadi 2020 | pure policy shock ~-8 per pp 3-month futures; standard HFI ~-3.5 (Table 2 p.13) | - | removing information effects doubles stock sensitivity |
| Paul 2020 (FRBSF WP) | stocks fall after tightenings, no systematic time pattern (p.4) | - | IP ~-2 per 100 bp (fn. 30) |

## 2. Activity and inflation
- Gertler-Karadi 2015: per pp of 1-year yield IP ~-1.2 at 1y, -1.7 at 2y [fig]; CPI ~-0.4 at 2y; EBP +0.4. Ramey standardization 2.2 percent at 18 months per 100 bp [verified Ramey p.29].
- Bauer-Swanson 2023: per pp of 2-year IP ~-1.4 (unadjusted) or ~-5.6 (orthogonalized, F 2.44) at ~1y [verified p.39, p.41; inference]; best practice: unemployment ~+0.2 per pp, CPI ~-0.8 over 5y.
- Swanson 2023 (w31603): IP ~-3 per pp of 2-year at 9 months [inference].
- Romer-Romer 2004: IP -2.1 at 12 months, -4.3 at 24, -1.7 at 48; price level 0 for 22 months, -6 at 48 [verified].
- Ramey 2016 Table 1 (p.29): trough per 100 bp funds peak 0.6 (Faust; BBE) to 5 (Barakchian-Crowe); CEE 0.7 at 8q; SW 1.8 at 4q; typical ~2 percent IP at 18 months; persistence not controlled (p.28).
- BJMW 2024 (FEDS 2024-011r1): per pp of 2-year impact IP ~-4 to -5 (NS shock), ~-13 (FF4) [fig]; 2-year yield back to zero in ~10 months (p.30), so per-impact numbers overstate a persistent 1 pp.
- GDP equivalents [inference; IP moves ~2-3x GDP]: GK ~0.5 at 1y, ~0.7 at 2y; RR ~1 and ~2; BS unadjusted ~0.5-0.7. Model simulations of a sustained 100 bp (FRB/US, DRI, WUMM; LSL 2002): GDP 0.6-0.9 at 4q, 0.8-1.8 at 8q.

## 3. Stock-wealth effects
- Chodorow-Reich-Nenov-Simsek 2021 (w25959): MPC 3.2 cents per year (p.41: 3.23); labor bill >= 8.6 percent x return, hours >= 3.73 percent x return (p.47) [verified]; a 10 percent decline lowers labor bill >= 0.86 percent, hours >= 0.37 percent at 2 years [inference].
- Di Maggio-Kermani-Majlesi 2020: MPC out of unrealized gains 23 percent bottom 50 (under 7 percent of stocks), ~3 percent top 30; dividends 40-60 [verified]; value-weighted ~3-5 cents [inference].
- Lettau-Ludvigson 2004: up to 88 percent of net-worth variation transitory and unrelated to consumption; conventional MPC 3-6 cents (Poterba) [verified p.1-2].
- Conversion [inference]: equity ~1.7-2x GDP; a 10 percent fall -> consumption ~0.55-0.65 percent of GDP at ~2 years (partial equilibrium); roughly 0.4-0.9 percent lower activity at 2 years without a policy offset.

## 4. Channel decompositions
- **Ludvigson-Steindel-Lettau 2002 (FRBNY EPR), table p.3** [verified]: 100 bp funds cut, stock market frozen vs not: GDP at 4q / 8q and wealth share at 8q: WUMM 0.9 / 1.8, 44 percent; DRI 0.6 / 0.8, 63 percent; FRB/US 0.6 / 1.7, 29 percent ("about one-fourth"); Modigliani's old FRB model about one-half (p.2). Their own VAR: wealth channel "scant" (p.1).
- No study found that decomposes output effects into channels with high-frequency identification [search; not exhaustive].

## Assessment (reviewer)
- **Equity: 7.7 per pp of the 2-year yield is in line.** Window estimates converted cluster at -6.7 to -10.5 (NS -6.7, BS -7.4, Swanson funds -8.6, GSS target -9, BK ~-10, RS ~-10.5). Bauer-Swanson (same windows, overlapping sample) gives -7.4 with R2 0.304: almost exactly the paper's -7.7 and 0.31. Path/forward-guidance news moves stocks less per unit of the 2-year; the paper sits in the middle. JK: removing information effects doubles sensitivity, so 7.7 is if anything conservative.
- **Activity: the paper's -0.75 to -1.1 at 4q is in the moderate range; the profile peaks earlier** (near 4q, fading by 8) than most studies (18-24 months). Persistence-controlled comparisons (Ramey's standardized figures; LSL model simulations) are the apt ones.
- **Wealth channel:** with the paper's 7.7 percent stock move per point, a CNS-type wealth effect gives ~0.3-0.7 percent lower activity at ~2 years, a third to two-thirds of the peak output effect, in line with the 29-63 percent equity share in LSL's large models; in tension with VAR evidence that wealth shocks are mostly transitory (LSL, Lettau-Ludvigson).

Not checked: Poterba 2000; Bernanke-Gertler 1999; Case-Quigley-Shiller; Kroner/Boehm 2025; Bauer-Swanson AER; published journal versions; Bu-Rogers-Wu magnitudes; exact [fig] values.
