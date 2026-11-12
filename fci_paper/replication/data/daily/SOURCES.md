# Daily series for step 20 (downloaded once; no network access at run time)

Downloaded 2026-11-12 with `curl -sS --http1.1 -m 90 -o f.csv 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=ID'`. FRED, Federal Reserve Bank of St. Louis [secondhand: not compared with another source].

| file | series | URL | use |
|---|---|---|---|
| `DGS10.csv` | 10-year Treasury constant-maturity yield, percent, daily | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10 | daily change in pp |
| `DTWEXBGS.csv` | nominal broad dollar index (goods and services), daily, from 2006 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS | 100 ln change from 2006 |
| `DTWEXB.csv` | nominal broad dollar index (goods only, discontinued Dec 2019), daily, from 1995 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXB | 100 ln change before 2006 (spliced on changes) |
| `SP500.csv` | S&P 500, daily, only from 2016 (FRED licence limit); NOT used (daily CAPE in `../gs_daily.csv` is used instead) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500 | not used |
