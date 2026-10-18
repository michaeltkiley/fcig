"""
Extract Goldman Sachs' monthly U.S. FCI from the chart in the New York Fed's Investor Advisory Committee on
Financial Markets presentation (July 13, 2022), slide 18 / PDF page 19 ("Financial Conditions indices").

The chart is vector art, so the data are read from the line's vertices, not traced from pixels. Axes are
calibrated from the 100.0 reference line and the plot frame (97.0 to 104.0) and from the 1990 and 2020 labels.
The 391 vertices are monthly, January 1990 to July 2022. Resolution is about 0.01 index points.

    curl -L -o q3.pdf https://www.newyorkfed.org/medialibrary/media/aboutthefed/pdf/2022/iacfm-q3-2022
    pdftocairo -svg -f 19 -l 19 q3.pdf p19.svg          # poppler-utils
    python tools/digitize_nyfed.py p19.svg history/gs_nyfed_digitized.csv
"""
import re, sys
import numpy as np, pandas as pd

svg, out = sys.argv[1], sys.argv[2]
t = open(svg).read()
line = next(re.search(r' d="([^"]*)"', p).group(1) for p in re.findall(r"<path ([^>]*?)/>", t)
            if "stroke=\"rgb(37.29" in p and "stroke-width=\"2.03" in p)  # the grey Goldman line
pts = np.array([[float(a), float(b)] for a, b in re.findall(r"[ML]\s*([-\d.]+)\s+([-\d.]+)", line)])
# Plot frame in the line's coordinate system: bottom (97.0) and top (104.0); the dashed 100 line is at 148.6115.
frame = next(re.search(r' d="([^"]*)"', p).group(1) for p in re.findall(r"<path ([^>]*?)/>", t)
             if "rgb(75.29" in p and re.search(r' d="M 23\.87', p))
ys = [float(v) for v in re.findall(r"[ML]\s*[-\d.]+\s+([-\d.]+)", frame)]
y_lo, y_hi = min(ys), max(ys)
per = (y_hi - y_lo) / 7.0
y100 = y_lo + 3 * per
val = 97.0 + (pts[:, 1] - y_lo) / per
idx = pd.period_range("1990-01", periods=len(pts), freq="M")
assert len(pts) == 391 and abs(y100 - 148.61) < 0.3, (len(pts), y100)
pd.Series(val.round(3), index=idx, name="gs_fci_digitized").rename_axis("month").to_csv(out)
print(f"{len(pts)} months, {idx[0]} to {idx[-1]}; min {val.min():.2f} ({idx[val.argmin()]}), max {val.max():.2f} ({idx[val.argmax()]})")
