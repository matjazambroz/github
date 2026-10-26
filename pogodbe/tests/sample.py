"""Ustvari vzorčne pogodbe za preizkus (besedilni PDF, skeniran PDF, DOCX)."""
from pathlib import Path

import pymupdf as fitz

FONT = next((f for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf") if Path(f).exists()), None)
SAMPLE = """POGODBA O OPRAVLJANJU STORITEV
št. 2024/015

Pogodbeni stranki:

Naročnik: ACME PODJETJE d.o.o., Dunajska cesta 1, 1000 Ljubljana, matična številka: 1234567000,
ID za DDV: SI12345678 (v nadaljevanju: naročnik)

in

Izvajalec: Storitve Novak d.o.o., Celovška 22, 1000 Ljubljana, matična številka: 7654321000,
ID za DDV: SI87654321 (v nadaljevanju: izvajalec)

sklenita dne 15. 1. 2024 naslednjo

1. člen
(predmet pogodbe)
Izvajalec se zavezuje za naročnika opravljati storitve svetovanja.

2. člen
(vrednost)
Skupna vrednost pogodbe znaša 24.000,00 EUR brez DDV. Pogodbena kazen znaša 500,00 EUR.

3. člen
(plačilo)
Plačilni rok je 30 dni od prejema računa.

4. člen
(veljavnost)
Pogodba velja od 1. 2. 2024 do 31. 1. 2026. Pogodba se samodejno podaljša za eno leto,
če je ena stranka ne odpove. Odpovedni rok je 3 mesece.

V Ljubljani, dne 15. 1. 2024
"""


def make_text_pdf(path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_textbox(fitz.Rect(50, 50, 550, 800), SAMPLE, fontsize=10, fontname="f0", fontfile=FONT)
    doc.save(str(path))


def make_scan_pdf(path: Path) -> None:
    """PDF samo s sliko (brez besedilnega sloja) - posnema sken."""
    src = fitz.open()
    p = src.new_page()
    p.insert_textbox(fitz.Rect(50, 50, 550, 800), SAMPLE, fontsize=11, fontname="f0", fontfile=FONT)
    pix = p.get_pixmap(matrix=fitz.Matrix(3, 3), colorspace=fitz.csGRAY)
    out = fitz.open()
    pg = out.new_page()
    pg.insert_image(pg.rect, stream=pix.tobytes("png"))
    out.save(str(path))
