# Check of step 00 (FRB/US inputs regenerated from the Board's public package)

Run: `python3 00_frbus.py` (about 40 s). It downloads pyfrbus.zip and data_only_package.zip from federalreserve.gov to `raw/frbus/` (gitignored) and, because the default interpreter cannot import pyfrbus (pandas 3, sympy), creates `raw/frbus_venv` (Python 3.11; `requirements_frbus.txt`; uv or `python3.11 -m venv`) and re-runs itself there (`lib/frbus_env.py`). Under `run_all.py` and the sync check it runs as a subprocess.

Vintage [verified]: LONGBASE.TXT dated 2026-10-06, sha256 c023c739f4179a70ca0ede84996539f8d2bf72170b9cc301afc89b95d2271a9e (`results/00_frbus_vintage.csv`).

Set-up [verified, copied from experimental/ms_fci/frbus_paths.py]: steady-state baseline from 2040Q1, fiscal settings as in the Board's demos, VAR expectations, 32 quarters; the experiments rshort, rg10, rme, rbbbp, req, fpxr, phouse in the two designs (z-expectations free or fixed), persistent and temporary; the yardstick is the +1 pp funds-rate hike with full transmission.

Outputs: `results/00_frbus_paths.csv`, `00_frbus_hike_paths.csv` (identical in format to `data/frbus_paths.csv`, `data/frbus_hike_paths.csv`). In a normal run the data/ copies are replaced and the previous files are kept as `data/*_oldvintage.csv`; under the sync check data/ is left alone and the fresh results are compared with the stored results (185 files compared, in sync).

Old versus new vintage, GDP per unit, persistent, zfree [verified]: relative difference at quarter 4 max 4.6 percent (rshort), mean 1.4 percent; at quarter 8 max 6.9 percent, mean 1.8 percent. The hike at quarter 4: -0.4616 against -0.4525. The experiments that enter the paper's weights differ by 0.1 to 1.5 percent (fpxr 0.06, rme 0.2, rg10 0.8, req 1.5 percent at quarter 4).

Downstream with the new vintage everywhere [verified]: b4'psi 0.954 [0.85, 1.07] (was 0.975 [0.87, 1.09]); ratio of ratios 2.53 [1.04, 6.91] (was 2.49 [1.02, 6.81]); FRB/US effects of the Figure 1 movements 0.153 and 0.384 funds-rate points (were 0.158 and 0.392); all asserted claims in 07_report.py hold with no threshold change.
