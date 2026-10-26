"""Lokalni OCR prek Tesseracta (priložen v Windows paketu, sicer iz PATH)."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Optional

_NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _candidates() -> list[Path]:
    base = [Path(getattr(sys, "_MEIPASS", "")), Path(sys.executable).parent, Path(__file__).resolve().parent.parent]
    out = [b / "tesseract" / ("tesseract.exe" if os.name == "nt" else "tesseract") for b in base if str(b)]
    if os.name == "nt":
        for pf in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
            if pf:
                out.append(Path(pf) / "Tesseract-OCR" / "tesseract.exe")
    return out


@lru_cache(maxsize=1)
def tesseract_path() -> Optional[str]:
    for c in _candidates():
        if c.is_file():
            return str(c)
    return shutil.which("tesseract")


def _env() -> dict:
    env = dict(os.environ)
    exe = tesseract_path()
    if exe:
        td = Path(exe).parent / "tessdata"
        if td.is_dir():
            env["TESSDATA_PREFIX"] = str(td)
    return env


@lru_cache(maxsize=1)
def languages() -> str:
    """Najboljša razpoložljiva kombinacija jezikov (slovenščina + angleščina)."""
    exe = tesseract_path()
    if not exe:
        return ""
    try:
        r = subprocess.run([exe, "--list-langs"], capture_output=True, text=True, env=_env(),
                           creationflags=_NOWIN, timeout=30)
        have = set(r.stdout.split())
    except Exception:
        return "eng"
    wanted = [l for l in ("slv", "eng") if l in have]
    return "+".join(wanted) or "eng"


def available() -> bool:
    return tesseract_path() is not None


def ocr_image(path: str) -> str:
    exe = tesseract_path()
    if not exe:
        raise RuntimeError("Tesseract OCR ni na voljo.")
    r = subprocess.run([exe, path, "stdout", "-l", languages() or "eng", "--psm", "3"],
                       capture_output=True, env=_env(), creationflags=_NOWIN, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "replace")[:300])
    return r.stdout.decode("utf-8", "replace")


def ocr_bytes(png: bytes) -> str:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "page.png"
        p.write_bytes(png)
        return ocr_image(str(p))
