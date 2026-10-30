# Replication package: "A Simple Market-Based Financial Conditions Index"

Everything in the note (`../paper/fci_note.tex`) is produced by seven short scripts from the public data in `data/`.
Run all of them with

```
pip install -r requirements.txt
python run_all.py          # about 2 minutes; writes output/
cd ../paper && pdflatex fci_note.tex && pdflatex fci_note.tex
```

The paper reads figures (`output/figures/`), tables (`output/tables/`) and every number quoted in the text (`output/numbers_*.tex`, LaTeX macros), so
re-running the scripts updates the paper.

## Scripts (run in order)

| Script | What it does | Paper |
|---|---|---|
| `01_data.py` | Builds the monthly data set (`output/data_monthly.csv`): rates, CAPE, prices, dollar, unemployment gap, expected inflation, r* | Figure 1 |
| `02_weights.py` | Policy news (Nakamura-Steinsson factor) from USMPD announcement windows; one-factor GLS weights of the market index; conversion of GS, NFCI and ANFCI to the market index's units by their own response to policy news; FRB/US weights on the same variables | Tables 1, 3 |
| `03_indexes.py` | Every index at every step (nominal, real, r* with Laubach-Williams, r* with Kiley): market index, GS replication, FRB/US index (level and growth impetus), FCI-G replication (1- and 3-year), NFCI, ANFCI | inputs to all |
| `04_var.py` | VAR of the unemployment gap and the market index (12 lags, 4 as a check), yardstick, bootstrap bands, forward impetus (and current pressure for the appendix) | Table 2, Figures 2-3 |
| `05_compare.py` | Like-for-like comparison at each step; widest and closest episodes | Tables 4-5, Figures 4-5 |
| `06_unemployment.py` | Local projections of the unemployment gap a year ahead, out-of-sample forecasts, FCI-G's scale by horizon | Table 6, Figure 6, Appendix Table 8 |
| `07_appendix.py` | Current pressure; checks with Kiley's r* and the 4-lag VAR | Figure 7, Table 7 |

## Utilities (`fci/`)

| Module | Contents |
|---|---|
| `data.py` | Reading the source files; monthly averages; splices; unemployment gap; expected inflation (Cleveland Fed, Livingston before 1982); r* |
| `cases.py` | The index inputs at each step: nominal, real (matched-horizon expected inflation), r* (gaps to r*, earnings-yield gap for equities) |
| `indexes.py` | Policy news and GLS weights; market index; GS replication; FRB/US index; FCI-G replication |
| `var.py` | Two-variable VAR, responses, bootstrap, forward impetus, current pressure |
| `lp.py` | Local projections and out-of-sample forecasts |
| `compare.py` | Correlations, cross-index range, episode windows |
| `report.py` | Writing LaTeX numbers and tables, figure style |

## Data (`data/`, all public; snapshot of October 2026)

| File | Source |
|---|---|
| `FEDFUNDS`, `GS10`, `BAA`, `MORTGAGE30US`, `TWEXBPA`, `RTWEXBGS`, `TWEXBMTH`, `DTWEXBGS`, `CPIAUCSL`, `CUUR0000SEHA`, `CSUSHPISA`, `SP500`, `UNRATE`, `NROU`, `EXPINF1YR`, `EXPINF10YR`, `NFCI`, `ANFCI` (.csv) | FRED, Federal Reserve Bank of St. Louis |
| `shiller_cape.csv`, `shiller_sp500.csv`, `shiller_home_price.csv` | Robert Shiller's online data (ie_data.xls; U.S. home prices) |
| `gs_daily.csv` | Daily GS FCI replication and daily CAPE from this repository (`fcig_gs.py`: public FRED data, ICE BofA BBB spread, Shiller E10 via multpl.com). Used for recent CAPE and for GS's response to policy news |
| `livingston_median_growth.xlsx` | Livingston Survey, Federal Reserve Bank of Philadelphia (median CPI inflation forecasts) |
| `usmpd_monetary_events.csv` | U.S. Monetary Policy Event-Study Database (Federal Reserve Bank of San Francisco; Acosta et al. 2025), sheet "Monetary Events", columns used |
| `rstar_onesided.csv` | One-sided r* estimates from full-sample estimation: Laubach-Williams (New York Fed) and Kiley |
| `fed_monthly_1yr.csv`, `fed_monthly_3yr.csv`, `multipliers.csv` | Published FCI-G and its multipliers (Federal Reserve Board, FEDS Note data and code release) |
| `frbus_paths.csv`, `frbus_hike_paths.csv` | FRB/US simulations (this repository, `experimental/ms_fci/frbus_paths.py`): cumulative GDP responses to persistent unit shifts in each financial variable, and to a persistent 1 pp funds-rate hike |

## Choices made for simplicity (differences from the project's exploratory work in `experimental/`)

- All series are monthly averages throughout (the exploratory work used end-of-month daily data from 1990, spliced to monthly averages before).
- The BBB spread is Moody's Baa yield less the 10-year yield (public and available from 1973); FCI-G's BBB yield is the Baa yield; FCI-G's stock prices are the
  S&P 500 (Shiller, then FRED) and its house prices Case-Shiller (Shiller's index before 1987).
- The FRB/US house-price variable is detrended (deviation from its trailing 15-year average) at every step, including the nominal one.
- Each variable is demeaned over January 1973 to September 2026.
- The GS conversion is re-estimated from the daily GS replication (response over the previous business day to the day after each announcement).

These choices change the exploratory numbers only slightly (for example, the 12-lag VAR yardstick is 0.57 in the nominal case here against 0.51 there, and the
monthly FCI-G replication tracks the published series at 0.98 rather than 0.99).
