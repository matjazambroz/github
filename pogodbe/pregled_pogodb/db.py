"""SQLite zbirka pogodb (z iskanjem po celotnem besedilu)."""
from __future__ import annotations

import json
import os
import sqlite3
import time
from datetime import date
from pathlib import Path
from typing import Optional

from .extract import Extracted, status_of

FIELDS = ["title", "number", "doc_type", "party1", "party1_role", "party2", "party2_role", "parties_json",
          "sign_date", "start_date", "end_date", "indefinite", "auto_renew", "notice_period", "duration",
          "value", "currency", "value_period", "vat_note", "payment_term_days", "subject", "notes"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS contracts(
  id INTEGER PRIMARY KEY, file_path TEXT, file_name TEXT, file_hash TEXT UNIQUE, imported_at TEXT,
  title TEXT, number TEXT, doc_type TEXT, party1 TEXT, party1_role TEXT, party2 TEXT, party2_role TEXT,
  parties_json TEXT, sign_date TEXT, start_date TEXT, end_date TEXT, indefinite INTEGER DEFAULT 0,
  auto_renew INTEGER DEFAULT 0, notice_period TEXT, duration TEXT, value REAL, currency TEXT,
  value_period TEXT, vat_note TEXT, payment_term_days INTEGER, subject TEXT, notes TEXT,
  full_text TEXT, pages INTEGER, ocr_pages INTEGER, evidence_json TEXT, edited INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS articles(
  id INTEGER PRIMARY KEY, contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
  ordinal INTEGER, num INTEGER, title TEXT, body TEXT, kind TEXT);
CREATE INDEX IF NOT EXISTS ix_art ON articles(contract_id);
"""


def data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    p = Path(base) / "PregledPogodb"
    p.mkdir(parents=True, exist_ok=True)
    return p


class Store:
    def __init__(self, path: Optional[str] = None):
        self.path = path or str(data_dir() / "pogodbe.db")
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript(SCHEMA)
        try:
            self.conn.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(title, parties, body, tokenize='unicode61 remove_diacritics 2')")
            self.fts = True
        except sqlite3.OperationalError:
            self.fts = False

    # ---- zapis
    def exists(self, h: str) -> bool:
        return self.conn.execute("SELECT 1 FROM contracts WHERE file_hash=?", (h,)).fetchone() is not None

    def add(self, file_path: str, file_hash: str, text: str, pages: int, ocr_pages: int, ex: Extracted) -> int:
        p1 = ex.parties[0] if ex.parties else None
        p2 = ex.parties[1] if len(ex.parties) > 1 else None
        iso = lambda d: d.isoformat() if d else None
        cur = self.conn.execute(
            """INSERT INTO contracts(file_path,file_name,file_hash,imported_at,title,number,doc_type,party1,party1_role,
            party2,party2_role,parties_json,sign_date,start_date,end_date,indefinite,auto_renew,notice_period,duration,
            value,currency,value_period,vat_note,payment_term_days,subject,notes,full_text,pages,ocr_pages,evidence_json)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (file_path, Path(file_path).name, file_hash, time.strftime("%Y-%m-%d %H:%M:%S"),
             ex.title or Path(file_path).stem, ex.number, ex.doc_type,
             p1.name if p1 else "", p1.role if p1 else "", p2.name if p2 else "", p2.role if p2 else "",
             json.dumps([p.__dict__ for p in ex.parties], ensure_ascii=False),
             iso(ex.sign_date), iso(ex.start_date), iso(ex.end_date), int(ex.indefinite), int(ex.auto_renew),
             ex.notice_period, ex.duration, ex.value, ex.currency, ex.value_period, ex.vat_note,
             ex.payment_term_days, ex.subject, "", text, pages, ocr_pages,
             json.dumps({k: v.__dict__ for k, v in ex.evidence.items()}, ensure_ascii=False)))
        cid = cur.lastrowid
        self.conn.executemany(
            "INSERT INTO articles(contract_id,ordinal,num,title,body,kind) VALUES(?,?,?,?,?,?)",
            [(cid, i, a.num, a.title, a.body, a.kind) for i, a in enumerate(ex.articles)])
        self._index(cid)
        self.conn.commit()
        return cid

    def _index(self, cid: int) -> None:
        if not self.fts:
            return
        r = self.conn.execute("SELECT title,party1,party2,number,full_text FROM contracts WHERE id=?", (cid,)).fetchone()
        self.conn.execute("DELETE FROM fts WHERE rowid=?", (cid,))
        self.conn.execute("INSERT INTO fts(rowid,title,parties,body) VALUES(?,?,?,?)",
                          (cid, f"{r['title']} {r['number']}", f"{r['party1']} {r['party2']}", r["full_text"]))

    def update(self, cid: int, values: dict) -> None:
        keys = [k for k in values if k in FIELDS]
        if not keys:
            return
        self.conn.execute(f"UPDATE contracts SET {','.join(k + '=?' for k in keys)}, edited=1 WHERE id=?",
                          [values[k] for k in keys] + [cid])
        self._index(cid)
        self.conn.commit()

    def delete(self, cid: int) -> None:
        self.conn.execute("DELETE FROM contracts WHERE id=?", (cid,))
        if self.fts:
            self.conn.execute("DELETE FROM fts WHERE rowid=?", (cid,))
        self.conn.commit()

    # ---- branje
    def list(self, query: str = "") -> list[sqlite3.Row]:
        cols = ("id,file_name,title,number,doc_type,party1,party2,sign_date,start_date,end_date,indefinite,"
                "auto_renew,value,currency,value_period,vat_note,edited,pages,ocr_pages")
        q = query.strip()
        if not q:
            return self.conn.execute(f"SELECT {cols} FROM contracts ORDER BY id DESC").fetchall()
        if self.fts:
            tokens = " ".join(f'"{t}"*' for t in q.replace('"', " ").split())
            try:
                return self.conn.execute(
                    f"SELECT {cols} FROM contracts WHERE id IN (SELECT rowid FROM fts WHERE fts MATCH ?) ORDER BY id DESC",
                    (tokens,)).fetchall()
            except sqlite3.OperationalError:
                pass
        like = f"%{q}%"
        return self.conn.execute(
            f"SELECT {cols} FROM contracts WHERE title LIKE ? OR party1 LIKE ? OR party2 LIKE ? OR full_text LIKE ? "
            "ORDER BY id DESC", (like,) * 4).fetchall()

    def get(self, cid: int) -> Optional[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM contracts WHERE id=?", (cid,)).fetchone()

    def articles(self, cid: int) -> list[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM articles WHERE contract_id=? ORDER BY ordinal", (cid,)).fetchall()

    def summary(self, today: Optional[date] = None) -> dict:
        today = today or date.today()
        s = {"skupaj": 0, "veljavne": 0, "kmalu": 0, "pretecene": 0, "vrednost_veljavnih": {}}
        for r in self.conn.execute("SELECT end_date,indefinite,value,currency FROM contracts"):
            end = date.fromisoformat(r["end_date"]) if r["end_date"] else None
            st = status_of(end, bool(r["indefinite"]), today)
            s["skupaj"] += 1
            if st in ("Veljavna", "Poteče kmalu", "Nedoločen čas"):
                s["veljavne"] += 1
                if r["value"]:
                    cur = r["currency"] or "EUR"
                    s["vrednost_veljavnih"][cur] = s["vrednost_veljavnih"].get(cur, 0) + r["value"]
            if st == "Poteče kmalu":
                s["kmalu"] += 1
            if st == "Pretečena":
                s["pretecene"] += 1
        return s
