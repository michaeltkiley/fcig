# Literature check for the new version (first pass, 17 Nov 2026; N10)

Web searches run 17 Nov 2026. Tags: [search] = from search-result summaries, primary source not opened; [bib] = already in `fci_paper/paper/references.bib`; [repo] = recorded as read in an earlier session's notes (`experimental/path_fci/lit/`). Nothing here is cleared for citation until the primary source is read (CLAUDE.md).

## 1. Equities respond strongly to policy news (supports the window evidence)
- **Bernanke and Kuttner (2005, JF 60(3), 1221-57)** [bib: bernanke2005; search]: an unanticipated 25 bp cut in the funds-rate target is associated with about a 1 percent rise in broad stock indexes (June 1989-Dec 2002; CRSP value-weighted). Most of the effect works through forecast equity risk premiums, little through real rates. Per pp: about 4 percent; ours: 7.7 percent per pp of the 2-year yield (a different unit: path news, 2-year).
- **Arnaut and Bauer (2024, FRBSF Economic Letter 2024-07)** [bib: arnaut2024; search]: a surprise tightening tightens financial conditions significantly and persistently; 0.1 pp surprise raises the GS FCI about 0.07 on the day and more over two weeks; consistent with Sack and Swanson (2023, FCI-G). The nearest existing work: it measures the FCI's response to surprises; it does not build an index from the responses.
- To add: Rigobon and Sack (2004), Gurkaynak-Sack-Swanson (2005) [bib: gurkaynak2005], Bauer-Swanson (2023) [bib].

## 2. Stock wealth moves spending (supports the spending side)
- **Chodorow-Reich, Nenov and Simsek (2021, AER 111(5), 1613-57)** [search]: higher local stock wealth raises nontradable and total employment, not tradable; implied MPC 3.2 cents per year per dollar of stock wealth; with passive policy a 20 percent rise in valuations raises the labor bill at least 1.7 percent and hours 0.7 percent after two years. For scale: a 20 percent rise in valuations is about 18 log points, about 0.9 point of easing on the market index at its equity weight of 0.0517 per log point [inference, arithmetic; units of their experiment to be checked].
- **Caballero and Simsek** (2026) [bib: caballero2026b; repo]: transmission "primarily through financial market conditions"; GS weights (Table 1).
- To add: Di Maggio, Kermani and Majlesi (2020, JF) [secondhand].

## 3. The models used for policy and the equity channel (the "blind spot" claim)
- **Castelnuovo and Nistico (2010, JEDC 34(9), 1700-31)** [search]: in the standard New Keynesian framework stock prices are redundant for inflation, output and the policy rate (infinitely lived agents smooth wealth); adding agents who enter with no wealth makes stock prices affect demand; estimated on U.S. data, stock prices have a significant effect on activity and the Fed responds to them. The cleanest citation for "standard models omit the equity channel".
- **Smets and Wouters (2007); Christiano, Eichenbaum and Evans (2005)** [secondhand]: Tobin's q is the value of installed capital, not a stock-market wealth effect on consumption. NOT CONFIRMED by search; read the papers before citing.
- **Bank of England, Bernanke review (April 2024)** [search, news coverage]: the BoE's main model lacked a detailed financial sector; the review recommended replacing or revamping it and building financial-sector models. A second central-bank example of the gap (UK).
- **FRB/US de-emphasis at the Fed (author's view)** [search: NOT FOUND]: searches found no source documenting a decline in FRB/US use. Board materials in 2025-26 still list FRB/US among the staff's models (a 2026 Board ASSA presentation; FEDS 2025-069 on staff inflation forecast errors suggests nonlinear frameworks and alternative slack measures). Until a source is found, the text should not assert de-emphasis; it can say that FRB/US is one of several models and that the DSGE models in use treat equities as in point 3.
- To check: the Board's EDO/SIGMA/GEMUS models and the NY Fed DSGE for a household stock-wealth channel.

## 4. Principal-component indexes, stress and asymmetry
- **Adrian, Boyarchenko and Giannone (2019, AER, "Vulnerable Growth")** [bib: adrian2019; search]: with the NFCI as the conditioning variable, upside risks to growth are low and stable while downside risks rise as conditions tighten; the NFCI moves the lower quantiles, not the median. Consistent with the NFCI as a stress measure.
- **Brave and Butters (2011)** [bib: brave2011; repo]: NFCI construction (dynamic factor on 100+ indicators; risk, credit, leverage).
- Our numbers [verified, FP-A64]: 1990-2026 level skewness NFCI 3.55 vs market 0.00.
- To search: direct work on NFCI skewness or nonlinearity; Hatzius et al. (2010) [bib] on FCI construction.

## 5. Novelty: an FCI built from high-frequency policy surprises
- Searches found **no index whose weights come from asset-price responses to policy surprises** [search]. Nearest: Arnaut-Bauer (2024) and Sack-Swanson (2023) estimate FCI responses to surprises; FCI-G weights come from FRB/US multipliers [search: FRBSF letter]; Jarocinski-Karadi use rate-stock co-movement to separate policy and information shocks (identification, not an index).
- To search further: "policy-equivalent" or "rate-equivalent" FCIs with market-based weights; the ECB MF-FCI (Bletzinger et al. 2026) [bib; repo: policy-rate units, model-based].

## 6. Names
- "MCFCI" not found in use; nearby: BoE "Monetary and Financial Conditions Index (MFCI)" (since 2019), Beaton-Lalonde-Luu (2009) MFCI, Bank of Canada MCI [search; FP-A64].

## Gaps to close before writing
1. A source for FRB/US de-emphasis, or drop that sentence.
2. Read Smets-Wouters (2007) and CEE (2005) on equities (or cite Castelnuovo-Nistico for the general point).
3. Read Chodorow-Reich-Nenov-Simsek and redo the mapping to index points.
4. Novelty: one more targeted search; ask colleagues.

Sources (search results): econpapers.repec.org/RePEc:bla:jfinan:v:60:y:2005:i:3:p:1221-1257; nber.org/system/files/working_papers/w10402/w10402.pdf; frbsf.org/research-and-insights/publications/economic-letter/2024/03/monetary-policy-and-financial-conditions/; aeaweb.org/doi/10.1257/aer.20200208; econpapers.repec.org/RePEc:eee:dyncon:v:34:y:2010:i:9:p:1700-1731; newyorkfed.org/research/staff_reports/sr794.html; federalreserve.gov/econres/feds/files/2025069pap.pdf; aeaweb.org/aea/2026conference/program/powerpoint/114934_ASSA_Presentation.pdf; richmondfed.org/publications/research/econ_focus/2018/q2/federal_reserve; cityam.com/beneath-the-jargon-bernanke-delivers-devastating-critique-of-the-bank-of-england/; bankofengland.co.uk/bank-overground/2021/how-do-we-monitor-uk-financial-conditions.
