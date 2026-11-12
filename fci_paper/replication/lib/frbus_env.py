"""Environment for the FRB/US steps (00_frbus, 22_*): download the Board's pyfrbus package and the LONGBASE data to raw/frbus (gitignored), and make sure the
running interpreter can import pyfrbus (it pins old libraries: pandas<3, sympy==1.3). If not, create raw/frbus_venv (Python 3.11, requirements_frbus.txt) and re-run the
calling script inside it. Usage at the top of a script:   from lib.frbus_env import ensure_runtime; ensure_runtime()   (then import pyfrbus)."""
import os, sys, io, time, shutil, hashlib, zipfile, subprocess, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]                  # fci_paper/replication
ROOT = HERE.parents[1]
RAW = ROOT / "raw" / "frbus"
VENV = ROOT / "raw" / "frbus_venv"
BASE_URL = "https://www.federalreserve.gov/econres/files/"
LONGBASE = RAW / "data_only_package" / "LONGBASE.TXT"
MODEL = RAW / "pyfrbus" / "models" / "model.xml"


def ensure_package():
    RAW.mkdir(parents=True, exist_ok=True)
    for z, marker in (("pyfrbus.zip", "pyfrbus"), ("data_only_package.zip", "data_only_package")):
        if not (RAW / marker).exists():
            req = urllib.request.Request(BASE_URL + z, headers={"User-Agent": "Mozilla/5.0"})
            zf = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(req, timeout=180).read())); zf.extractall(RAW)
            for zi in zf.infolist():                      # keep the archive's file dates, so that the recorded LONGBASE date is the vintage date, not the download date
                ts = time.mktime(zi.date_time + (0, 0, -1)); os.utime(RAW / zi.filename, (ts, ts))
    sys.path.insert(0, str(RAW / "pyfrbus"))


def longbase_info():
    """(file date, sha256 of LONGBASE.TXT) for the record."""
    import datetime
    st = LONGBASE.stat()
    return datetime.date.fromtimestamp(st.st_mtime).isoformat(), hashlib.sha256(LONGBASE.read_bytes()).hexdigest()


def _importable():
    try:
        import pandas, sympy
        if int(pandas.__version__.split(".")[0]) >= 3 or sympy.__version__ != "1.3":
            return False
        from pyfrbus.frbus import Frbus  # noqa: F401
        return True
    except Exception:
        return False


def _make_venv():
    py = VENV / "bin" / "python"
    if py.exists():
        return py
    req = HERE / "requirements_frbus.txt"
    if shutil.which("uv"):
        subprocess.run(["uv", "venv", "--python", "3.11", str(VENV)], check=True)
        subprocess.run(["uv", "pip", "install", "--python", str(py), "-r", str(req)], check=True)
    else:
        subprocess.run(["python3.11", "-m", "venv", str(VENV)], check=True)
        subprocess.run([str(py), "-m", "pip", "install", "-r", str(req)], check=True)
    return py


def ensure_runtime():
    """Download the package if needed; if this interpreter cannot import pyfrbus, re-run the calling script in the isolated environment (does not return)."""
    ensure_package()
    if _importable():
        return
    if os.environ.get("FCI_FRBUS_INNER"):
        raise SystemExit("pyfrbus cannot be imported in the isolated environment either")
    py = _make_venv()
    os.environ["FCI_FRBUS_INNER"] = "1"
    os.execv(str(py), [str(py)] + sys.argv)
