"""Run the weights analysis (about 1 minute): forecasts, activity-fitted weights, summary."""
import subprocess, sys
for s in ("01_forecast.py", "02_weights.py", "03_summary.py"):
    subprocess.run([sys.executable, s], check=True, cwd=__file__.rsplit("/", 1)[0] or ".")
