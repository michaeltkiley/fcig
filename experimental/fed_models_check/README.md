# Which staff models drive the alternative scenarios? Greenbooks 2006-2010 vs Tealbooks 2016-2020 (17 Nov 2026)

Purpose: document the author's point (FP-A63, Note A new version) that the Board staff moved from an FRB/US-centred set of alternative scenarios to a mix
of models. All scheduled FOMC meetings, not a sample: Greenbook Part 1 (Jan 2006-Apr 2010, 35) and Tealbook A (Jun-Dec 2010, 5; 2016-2020, 40),
downloaded from the Board's historical-materials pages (`docs.csv`; PDFs and text in `../../raw/fed_docs`, `../../raw/fed_txt`, gitignored).

Run: `python3 fetch.py` (download), `pdftotext -layout` each PDF into `raw/fed_txt`, then `python3 analyze.py`, `python3 model_sets.py`, `python3 scenario_tags.py`.

## Result [verified, `summary.txt`, `model_sets.csv`, `tealbook_scenarios_2016_2020.csv`]

| | Greenbooks 2006-Apr 2010 | Tealbooks Jun-Dec 2010 | Tealbooks 2016-2020 |
|---|---|---|---|
| Documents | 35 | 5 | 40 |
| Models used in the alternative scenarios (mean per document) | 1.0 | 2.0 | 3.05 |
| FRB/US the only model | 100% | 0% | 0% |
| Uses FRB/US / SIGMA / EDO | 100% / 0 / 0 | 100% / 100% / 0 | 92% / 98% / 38% |
| Uses another DSGE (NY Fed DSGE, Gertler-Sala-Trigari, Smets-Wouters, Gertler-Karadi, US-FLM, ...) | 0 | 0 | 70% (incl. EDO) |

- Every Greenbook from January 2006 to April 2010 opens the section with "...using simulations of the FRB/US model" (`model_mentions.csv`, column `intro_sentence`).
- From June 2010 the Tealbook says "...using simulations of staff models"; in 2016-2020 the scenario headings name the model. Of 176 tagged scenarios in 31 Tealbooks, 47 percent are run in FRB/US alone and 55 percent involve FRB/US; SIGMA (multicountry DSGE) 60, NY Fed DSGE 8, Gertler-Sala-Trigari 7, GEMUS 7, EDO 6.
- Two 2016-2020 Tealbooks use no FRB/US at all in the scenarios (Jan 2016, Jul 2016) and one more (Jan 2019).

## Caveats
- Model sets are coded automatically from scenario headings and from sentences that tie a scenario to a model; one hand code (Jan 2008, the wording "alternative simulations of the FRB/US model"; `hand_codes.json`). Spot checks against the text: Jan 2016, Jul 2016, Sep 2016, Mar/May/Jun 2019, Nov 2018, May 2017.
- FRB/US remains in use for the confidence intervals (stochastic simulations) and r* estimates throughout; the measure here is the alternative scenarios only.
- The measure counts models named, not how much weight the staff put on each in its judgment.
