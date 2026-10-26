"""Uvoz datotek: branje/OCR -> izluščenje -> shranjevanje."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from . import extract, reader
from .db import Store


def import_file(store: Store, path: str, progress: Optional[Callable[[str], None]] = None) -> tuple[str, Optional[int]]:
    """Vrne (stanje, id): 'dodano' | 'preskočeno' | 'napaka: ...'."""
    try:
        h = reader.file_hash(path)
        if store.exists(h):
            return "preskočeno (že uvoženo)", None
        res = reader.read_file(path, progress)
        if not res.text.strip():
            return f"napaka: ni mogoče prebrati besedila. {res.warning}".strip(), None
        ex = extract.extract(res.text)
        cid = store.add(path, h, res.text, res.pages, res.ocr_pages, ex)
        return ("dodano" + (f" ({res.warning})" if res.warning else "")), cid
    except Exception as e:  # ena slaba datoteka ne sme ustaviti uvoza
        return f"napaka: {e}", None
