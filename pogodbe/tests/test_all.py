import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pregled_pogodb import extract, importer, ocr  # noqa: E402
from pregled_pogodb.db import Store  # noqa: E402
import sample  # noqa: E402


def test_extract_sample():
    ex = extract.extract(sample.SAMPLE)
    assert ex.title.startswith("POGODBA O OPRAVLJANJU")
    assert ex.number == "2024/015"
    assert [p.name for p in ex.parties] == ["ACME PODJETJE d.o.o.", "Storitve Novak d.o.o."]
    assert ex.parties[0].role == "Naročnik" and ex.parties[0].vat_id == "SI12345678"
    assert ex.sign_date == date(2024, 1, 15)
    assert ex.start_date == date(2024, 2, 1) and ex.end_date == date(2026, 1, 31)
    assert ex.value == 24000.0 and ex.currency == "EUR" and ex.vat_note == "brez DDV"
    assert ex.payment_term_days == 30 and ex.auto_renew and ex.notice_period == "3 mesecev"
    assert [a.num for a in ex.articles if a.kind == "člen"] == [1, 2, 3, 4]
    assert ex.articles[1].title == "predmet pogodbe"
    assert "svetovanja" in ex.subject


def test_duration_and_amounts():
    t = "Pogodba začne veljati 1. 3. 2024 in velja za dobo dveh let. Mesečna cena znaša 1.250,50 EUR."
    ex = extract.extract(t)
    assert ex.end_date == date(2026, 2, 28)
    assert ex.value == 1250.5 and ex.value_period == "mesečno"
    assert extract.parse_amount("1,234.56") == 1234.56 and extract.parse_amount("12 000,5") == 12000.5
    assert extract.extract("Pogodba velja za nedoločen čas.").indefinite


def test_status():
    today = date(2026, 1, 1)
    assert extract.status_of(date(2025, 12, 31), False, today) == "Pretečena"
    assert extract.status_of(date(2026, 2, 1), False, today) == "Poteče kmalu"
    assert extract.status_of(date(2027, 1, 1), False, today) == "Veljavna"
    assert extract.status_of(None, True, today) == "Nedoločen čas"


def test_import_text_pdf(tmp_path):
    p = tmp_path / "a.pdf"
    sample.make_text_pdf(p)
    store = Store(str(tmp_path / "t.db"))
    st, cid = importer.import_file(store, str(p))
    assert st.startswith("dodano") and cid
    assert importer.import_file(store, str(p))[0].startswith("preskočeno")
    assert store.get(cid)["value"] == 24000.0
    assert len(store.list("svetovanja")) == 1 and len(store.list("nepoznano")) == 0
    assert len(store.list("novak")) == 1
    assert store.summary()["skupaj"] == 1


@pytest.mark.skipif(not ocr.available(), reason="Tesseract ni nameščen")
def test_import_scan_pdf(tmp_path):
    p = tmp_path / "scan.pdf"
    sample.make_scan_pdf(p)
    store = Store(str(tmp_path / "t.db"))
    st, cid = importer.import_file(store, str(p))
    assert st.startswith("dodano"), st
    r = store.get(cid)
    assert r["ocr_pages"] == 1
    assert r["value"] == 24000.0
    assert r["end_date"] == "2026-01-31"
