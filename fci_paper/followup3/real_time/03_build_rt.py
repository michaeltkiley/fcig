"""Build real-time (vintage) inputs and outcomes for each origin month t from the ALFRED vintages in raw/.
Information set at origin t = vintage dated the 1st of month t+2 (UNRATE and PAYEMS for month t are out in t+1, core PCE by the end of t+1); conservative by up to a month.
Outcome 'first release' = value known in the vintage dated the 1st of t+14 (12-month change t -> t+12 with that vintage's own history).
NROU: CBO natural rate in ALFRED exists from the Feb 2011 vintage only; earlier origins use the ex-post series (flagged)."""
import numpy as np, pandas as pd, pathlib
HERE = pathlib.Path(__file__).resolve().parent; RAW = HERE / "raw"; OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
def vint(sid, v):
    f = RAW / f"{sid}_{v:%Y%m}.csv"
    if not f.exists(): return None
    d = pd.read_csv(f); s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()
    return s
def mid_q(q):                                  # same convention as the package: quarterly value in the middle month, interpolated
    q = q.copy(); q.index = q.index.to_period("Q")
    m = pd.Series(q.values, index=[p.asfreq("M", "s") + 1 for p in q.index]); full = pd.period_range(m.index[0], m.index[-1], freq="M")
    return m.reindex(full).interpolate(limit_area="inside")
def mser(s): s = s.copy(); s.index = s.index.to_period("M"); return s
rows = []
OFF = {"k": (2, 3), "f": (14, 15)}            # vintage offsets in months after the origin; the second is used only if the first lacks the observation
def get(sid, t, tag, fn):
    """return dict from fn(series) using the first vintage (of OFF[tag]) in which every requested obs is present"""
    for o in OFF[tag]:
        s = vint(sid, (t + o).to_timestamp())
        if s is None: continue
        r = fn(s)
        if all(pd.notna(x) for x in r.values()): return r
    return {k: np.nan for k in fn(pd.Series(dtype=float, index=pd.DatetimeIndex([])) if False else vint("UNRATE", pd.Timestamp("2026-11-01"))).keys()} if False else None
for t in pd.period_range("1976-03", "2025-09", freq="M"):
    r = dict(t=str(t))
    specs = {
        "k": {"UNRATE": lambda u: {"u_k": mser(u).get(t), "u12_k": mser(u).get(t - 12)},
              "PAYEMS": lambda p: (lambda l: {"p_k": l.get(t), "p3_k": l.get(t - 3), "p12_k": l.get(t - 12)})(np.log(mser(p)) * 100),
              "PCEPILFE": lambda c: (lambda l: {"c_k": l.get(t), "c3_k": l.get(t - 3), "c12_k": l.get(t - 12)})(np.log(mser(c)) * 100),
              "NROU": lambda n: (lambda m: {"n_k": m.get(t), "n12_k": m.get(t - 12)})(mid_q(n))},
        "f": {"UNRATE": lambda u: {"u_t_f": mser(u).get(t), "u_h_f": mser(u).get(t + 12)},
              "PAYEMS": lambda p: (lambda l: {"p_t_f": l.get(t), "p_h_f": l.get(t + 12)})(np.log(mser(p)) * 100),
              "PCEPILFE": lambda c: (lambda l: {"c_t_f": l.get(t), "c_h_f": l.get(t + 12)})(np.log(mser(c)) * 100),
              "NROU": lambda n: (lambda m: {"n_t_f": m.get(t), "n_h_f": m.get(t + 12)})(mid_q(n))}}
    for tag, d in specs.items():
        for sid, fn in d.items():
            out = get(sid, t, tag, fn)
            if out: r.update(out); r[f"vint_{sid}_{tag}"] = 1
    rows.append(r)
P = pd.DataFrame(rows).set_index("t"); P.to_csv(OUT / "rt_panel.csv"); print(P.notna().groupby(P.index.str[:4]).mean().iloc[::5].round(2).to_string())
