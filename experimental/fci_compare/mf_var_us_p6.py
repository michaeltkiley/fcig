"""ECB-method VAR (mf_var_us.py) with 6 lags, main version (core PCE, no house prices): alpha, yardstick paths, partial responses (answer 36). Usage: python experimental/fci_compare/mf_var_us_p6.py"""
import sys, numpy as np
sys.path.insert(0, "experimental/fci_compare"); sys.path.insert(0, "experimental/ms_fci")
import mf_var_us as V, macro_model_dl as DL
x, _ = DL.levels_data()
M = V.macro_data(False); Z = x[V.FIN0]
s0 = np.array([0.009, 0.57, 0.42, 0.13, -0.032, 0.10]); s0 /= np.linalg.norm(s0)
starts = [s0, np.r_[1.0, np.zeros(5)] + 0.05, np.array([0.1, 0.1, 0.85, 0.5, -0.02, 0.0])]
v = V.MFVAR(M, Z, 6, first="1990-07").fit(starts)
se = v.alpha_se()
ui = v.names.index("unemployment gap"); nm = v.nm
print("p=6 T", v.T, "logL", round(v.ll, 1))
print("alpha:", ", ".join(f"{n} {a:+.3f} ({s:.3f})" for n, a, s in zip(Z.columns, v.alpha, se)))
y = v.yardstick(H=36)
print("yardstick u path m1,3,6,12,18,24,36:", np.round(y[[0, 2, 5, 11, 17, 23, 35], ui], 3))
print("   F path m1,6,12,24:", np.round(y[[0, 5, 11, 23], nm:] @ v.alpha, 3))
print("   financial paths m12:", dict(zip(v.names[nm:], np.round(y[11, nm:], 3))))
for j, n in enumerate(Z.columns):
    pj = v.partial(j, H=36)
    print(f"   partial {n:16s} +1 for 12m: u m12 {pj[11,1]:+.3f}, m24 {pj[23,1]:+.3f}")
du = y[11, ui]
print("weights (if yardstick usable):", {n: round(float(v.partial(j)[11, 1] / du), 3) for j, n in enumerate(Z.columns)}, "yardstick output eq", round(-2 * du, 3))
