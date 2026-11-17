"""Variance share of the measured window surprises with Note B's own responses (the lower bound computed with the model of the paper rather than the VAR's dynamics):
   share_k(h) = sigma_z^2 sum_{j<h} r_k(j)^2 / [forecast-error variance of k at h in the VAR in monthly averages, 1996-2026 innovations],
   r = Note B's responses per +1 pp window surprise (h = 0..36), sigma_z^2 = mean squared monthly sum of policy news, 1996-2026.
   python3 06_noteb_shares.py  -> results/noteb_shares.csv"""
import numpy as np, pandas as pd
import lib_r2 as R
OUT = R.Path(__file__).resolve().parent / "results"; rows = []
for step, fci in (("nom", 0), ("nom", "nom"), ("real", 0), ("real", "real"), ("rstar", 0), ("rstar", "rstar")):
    for start in ("1996-01", "1973-01"):
        if start == "1973-01" and (step, fci) not in (("rstar", "rstar"),): continue
        c = R.run(step, fci, "avg", start, 12, "WE", "in"); post = c["per"] >= pd.Period("1996-01", "M")
        Sp = np.cov(c["U"][post].T); den = np.cumsum(np.einsum("hij,jk,hik->hi", c["T"][:37], Sp, c["T"][:37]), axis=0)
        r = np.array([R.path_vector(step, fci, "avg", h, start)[:c["K"]] for h in range(37)]); s2 = float((R.ZFULL ** 2).mean())
        num = np.cumsum(r ** 2, axis=0) * s2
        for h in (12, 24, 36):
            rows.append(dict(step=step, fci=fci, start=start, h=h, **{n: num[h - 1, i] / den[h - 1, i] for i, n in enumerate(c["names"])}))
D = pd.DataFrame(rows); D.to_csv(OUT / "noteb_shares.csv", index=False, float_format="%.5f"); print(D.round(4).to_string())
