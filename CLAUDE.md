# fcig: financial conditions indexes (live page + experimental research)

Two things live here. Do not confuse them.
1. **The live page and daily workflow** (repo root): `fcig_replicate.py`, `fcig_gs.py`, `index.html`, `data.json`, `.github/workflows/update.yml`. Replicates the Fed's FCI-G and a Goldman-style FCI daily. See `README.md`. Do not touch for research work.
2. **The research project** (`experimental/`, `fci_note/`): financial conditions indexes in funds-rate / 2-year-yield equivalents, a new "market index", and two draft notes that use it. This is where almost all current work is.
   - **Note A, the FCI note:** `fci_note/paper/fci_note.tex` + replication package `fci_note/replication/` (the market index, nominal -> real -> r* steps, comparisons with FCI-G, FRB/US, GS, ANFCI).
   - **Note B, the transmission note:** `experimental/fin_shocks/paper/mp_transmission.tex` (high-frequency policy surprises traced through the market index and r*; uses Note A's three indexes unchanged). Code: clean replication package `experimental/fin_shocks/baseline/` (scripts `01_` to `07_`, self-contained; older experimental code in `experimental/fin_shocks/legacy/`), draft-note tables `paper/make_tables.py`, decisions `experimental/fin_shocks/FS_QA.md`.

## Start here in a new session (research work)
0. Read `experimental/PROJECT_MEMORY.md`, **section 9 first** ("Where we are"), then sections 2-3 for decisions and results. Then `experimental/README.md` (folder index).
1. For definitions and the reasoning behind choices: `experimental/INDEX_QA.md` (answers 1-56). Open decisions are taken one at a time in the `*_QA.md` files (`INDEX_QA`, `real_case/REAL_QA`, `rstar_case/RSTAR_QA`, `mp_var_fci/MP_QA`).
2. Before concluding that something is missing or unknown, search all of `experimental/` and `fci_note/` and `git log --all`. Do not guess the user's specification; read it.

## Glossary (use these names exactly)
- **Market index (MKT):** the main index of the note. Weights on the 10-year yield, equity valuation (CAPE) and real broad dollar come from their responses to Nakamura-Steinsson policy news in FOMC event windows (USMPD); unit = a policy move raising the 2-year yield 1 pp. Dynamics: two-variable VAR in the unemployment gap and the index (unemployment first, 1973-2026, 2020 dummied, 12 lags main). Has a **level** and a **flow** (forward impetus, FCI-G form). Baseline is the **r*-gap** case (nominal -> real -> r*). Code: `fci_note/replication/`, `experimental/path_fci/`, `experimental/market_macro/`.
- **Macro-model levels index (EP_4, FRB/US):** weighted with FRB/US funds-rate equivalents (formerly "MS-style"/"five-variable"; oil dropped; with and without house prices). Our own construction; **not** the market index. Code: `experimental/ms_fci/`. The Morgan Stanley index itself is unverified.
- **GS:** a replication of Goldman's index with published weights, not the proprietary series. **FCI-G:** the Fed's growth-impulse measure (a flow; built from past changes). **NFCI/ANFCI:** Chicago Fed.
- **Forward impetus:** the FCI-G-form flow of the market index; **current pressure** is appendix only.
- **Transmission note (Note B):** window-identified NS surprises traced through a daily block (2-year yield and FCI) into monthly unemployment gap and core PCE (3/6/12 lags, quadratic trend); steps nominal -> real -> r*-gap identical to Note A. Not the same as the market-index VAR of Note A.

## Working preferences (from the user)
- Go slowly, one decision at a time. Propose, then ask; no consequential choices without the user's guidance. Record answers in the relevant `*_QA.md`.
- Style guide for Note B (confirmed 11 Nov 2026): first person singular ("I"); abstract without results numbers, short declaratives, one claim per sentence; introduction states the question, then the result, then the approach as First/Second/Finally features, and puts the literature after; robustness is a section reported as tests with outcomes in plain sentences, no apology; verdicts in words, intervals in tables; conclusion short. Evidence and quotes in `experimental/fin_shocks/paper/STYLE_GUIDE_DRAFT.md` and `style_evidence/`.
- Writing (Note B and drafts): write forward and for the big picture: the question, the approach, the core results, then 'generally robust'. Do not mention future or earlier results to set up the next point; no hand-wringing about sensitivity, no 'in some cases but not others' in the abstract, introduction or conclusion; robustness checks that broadly confirm the core are reported in the robustness section only, plainly and briefly. Nothing is robust to everything; do not add complications where none are needed.
- Tone for Note B (11 Nov 2026): analytical and dispassionate; state results plainly; significance at the 10 percent level (90 percent interval excludes zero) is the convention; no hedging, no apology, no 'borderline'; report intervals as facts. The results are strong and intuitive; say so directly where the evidence supports it (state limits only as facts in the robustness section).
- Compare like for like at each step (our nominal vs existing nominal, real vs real, r* vs r*-adjusted). Treat information effects as acknowledged and set aside in the note, examined in `mp_var_fci/`.
- Tag claims [verified] / [secondhand] / [inference]; flag unverified citations; say plainly what could not be checked.

## Repo hygiene
- Work on a short branch from `main` and merge back at the end of each block of work. Long-lived side branches are how work got hidden (main was 206 commits behind in Oct 2026).
- **Before ending a session, update `experimental/PROJECT_MEMORY.md` section 9** (status, decisions, open items) and the folder index in `experimental/README.md` if a folder was added.
- Large inputs in `raw/` are gitignored; see `fci_note/replication/README.md` for data and `run_all.py`. A TeX engine is not preinstalled; see section 9 of the memory file.
- The daily workflow commits data to `main`; research folders do not feed it.
