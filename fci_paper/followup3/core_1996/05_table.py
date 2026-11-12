"""One checks table: rows a-e, identical statistics. Writes out/checks_market.csv (all series long) and out/CHECKS.md."""
from common import *
V = pd.read_csv(OUT / "var.csv"); L = pd.read_csv(OUT / "levelflow.csv"); S = pd.read_csv(OUT / "stance.csv"); LD = pd.read_csv(OUT / "ladder.csv")
V.loc[V.row.eq("a") & V.lags.eq(12), "tag"] = "a"
# row e's VAR = row a's VAR
Ve = V[(V.row == "a")].copy(); Ve["row"] = "e"; V = pd.concat([V, Ve])
def lab(r, p=None): return r if p is None else f"{r}{p}"
out = []
for row in ["a", "b", "c", "d", "e"]:
    for lags in ([12, 4] if row == "b" else [12]):
        for key, nm in SERIES:
            if row == "d" and key != "market": continue
            for step in STEPS:
                v = V[(V.row == row) & (V.lags == lags) & (V.series == key) & (V.step == step)].iloc[0]
                l = L[(L.row == row) & (L.series == key) & (L.step == step)]; ld = l[l.outcome == "du"].iloc[0]; lp = l[l.outcome == "pay"].iloc[0]
                s = S[(S.row == row) & (S.series == key) & (S.step == step) & (S.outcome == "du")]
                sf = s[s.form == "flow"].iloc[0]; sm_ = s[s.form == "mixed"].iloc[0]
                sp = S[(S.row == row) & (S.series == key) & (S.step == step) & (S.outcome == "pay") & (S.form == "flow")].iloc[0]
                out.append(dict(row=row, lags=lags, series=nm, step=step, var_n=v.n, phi12=v.phi12, phi12_lo90=v.lo90, phi12_hi90=v.hi90, granger_p=v.granger_p,
                                lf_n=ld.n, du_t_flow=ld.t_flw, du_t_level=ld.t_lvl, du_gain_flow=ld.gain_flw, pay_t_flow=lp.t_flw, pay_gain_flow=lp.gain_flw,
                                st_du_flow_gain=sf.gain_idx_given_ff, st_du_flow_t=sf.t_idx_both, st_du_mixed_gain=sm_.gain_idx_given_ff, st_du_mixed_t=sm_.t_idx_both,
                                oos_first=sf.first_oos, oos_n=sf.n_oos, oos_rec=sf.n_rec_oos, cw_du_flow=sf.cw, rmse_du_flow=sf.rmse_ratio, cw_du_mixed=sm_.cw, rmse_du_mixed=sm_.rmse_ratio,
                                st_pay_flow_gain=sp.gain_idx_given_ff, st_pay_flow_t=sp.t_idx_both, cw_pay_flow=sp.cw))
T = pd.DataFrame(out); T.to_csv(OUT / "checks_all.csv", index=False)
def md(df, cols, hdr):
    s = "| " + " | ".join(hdr) + " |\n|" + "---|" * len(hdr) + "\n"
    for _, r in df.iterrows():
        s += "| " + " | ".join((f"{r[c]:.2f}" if isinstance(r[c], float) else str(r[c])) for c in cols) + " |\n"
    return s
T["row_l"] = T.row + T.lags.map(lambda p: f"({p}L)" if p else "")
T["phi"] = T.apply(lambda r: f"{r.phi12:.2f} [{r.phi12_lo90:.2f}, {r.phi12_hi90:.2f}]", axis=1)
T["oos"] = T.apply(lambda r: f"{r.oos_first} n={r.oos_n} rec={r.oos_rec}", axis=1)
text = ""
for ser in ("Market", "GS", "FRB/US"):
    t = T[T.series == ser]
    text += f"\n### {ser}\n" + md(t, ["row_l", "step", "var_n", "phi", "granger_p", "du_t_flow", "du_gain_flow", "pay_t_flow", "st_du_flow_gain", "st_du_flow_t", "st_du_mixed_gain", "st_du_mixed_t", "cw_du_flow", "cw_du_mixed", "oos"],
                                    ["row", "step", "VAR n", "Phi(12) [90%]", "Granger p", "du t flow", "du gain flow", "pay t flow", "stance gain flow", "t", "stance gain mixed", "t", "CW flow", "CW mixed", "OOS"])
open(OUT / "CHECKS.md", "w").write(text); print(text[:6000])
