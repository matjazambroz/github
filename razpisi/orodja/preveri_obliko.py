#!/usr/bin/env python3
"""Preveri, da izpolnjen DOCX/XLSX ohranja obliko izvirnika.

Uporaba:  python orodja/preveri_obliko.py <izvirnik> <izpolnjeno>
DOCX: primerja glave, noge, sloge, oštevilčenje, teme, nastavitve strani in uporabljene pisave.
XLSX: primerja sloge, širine stolpcev, združene celice in formule.
Izhod: 0 = enako, 1 = razlike, 2 = napaka v uporabi.
"""
import re
import sys
import zipfile
from pathlib import Path

PARTS_DOCX = re.compile(r"^word/(header\d*|footer\d*|styles|numbering|theme/theme\d*|fontTable|settings)\.xml$")
FONT_RE = re.compile(rb'w:(?:ascii|hAnsi|cs|eastAsia)="([^"]+)"')
SIZE_RE = re.compile(rb'<w:sz w:val="(\d+)"')
SECT_RE = re.compile(rb"<w:sectPr.*?</w:sectPr>", re.S)


def read(zf, name):
    return zf.read(name) if name in zf.namelist() else b""


def check_docx(a, b):
    diffs = []
    with zipfile.ZipFile(a) as za, zipfile.ZipFile(b) as zb:
        names = sorted({n for n in za.namelist() + zb.namelist() if PARTS_DOCX.match(n)})
        for n in names:
            x, y = read(za, n), read(zb, n)
            if not x:
                diffs.append(f"{n}: dodan v izpolnjenem")
            elif not y:
                diffs.append(f"{n}: manjka v izpolnjenem")
            elif n.startswith(("word/header", "word/footer")):
                # glava/noga: primerjaj brez vsebine polj, ki se lahko posodobijo
                if re.sub(rb"\s+", b"", x) != re.sub(rb"\s+", b"", y):
                    diffs.append(f"{n}: vsebina ali oblika se razlikuje")
            elif x != y:
                diffs.append(f"{n}: se razlikuje")
        da, db = read(za, "word/document.xml"), read(zb, "word/document.xml")
        if SECT_RE.findall(da) != SECT_RE.findall(db):
            diffs.append("word/document.xml: nastavitve strani/odsekov (sectPr: velikost, robovi, glava/noga) se razlikujejo")
        fonts_a, fonts_b = set(FONT_RE.findall(da)), set(FONT_RE.findall(db))
        new = fonts_b - fonts_a
        if new:
            diffs.append("v izpolnjenem so nove pisave: " + ", ".join(sorted(f.decode() for f in new)))
        sizes_a, sizes_b = set(SIZE_RE.findall(da)), set(SIZE_RE.findall(db))
        new = sizes_b - sizes_a
        if new:
            diffs.append("v izpolnjenem so nove velikosti pisave (pol-točke): " + ", ".join(sorted(s.decode() for s in new)))
    return diffs


def check_xlsx(a, b):
    from openpyxl import load_workbook
    diffs = []
    wa, wb = load_workbook(a), load_workbook(b)
    if wa.sheetnames != wb.sheetnames:
        diffs.append(f"listi se razlikujejo: {wa.sheetnames} / {wb.sheetnames}")
    for name in wa.sheetnames:
        if name not in wb.sheetnames:
            continue
        sa, sb = wa[name], wb[name]
        if {str(r) for r in sa.merged_cells.ranges} != {str(r) for r in sb.merged_cells.ranges}:
            diffs.append(f"[{name}] združene celice se razlikujejo")
        ca = {k: v.width for k, v in sa.column_dimensions.items()}
        cb = {k: v.width for k, v in sb.column_dimensions.items()}
        if ca != cb:
            diffs.append(f"[{name}] širine stolpcev se razlikujejo")
        for row in sa.iter_rows():
            for c in row:
                d = sb[c.coordinate]
                if isinstance(c.value, str) and c.value.startswith("=") and d.value != c.value:
                    diffs.append(f"[{name}] formula v {c.coordinate} je spremenjena")
                if (c.font.name, c.font.sz, c.font.b, c.number_format) != (d.font.name, d.font.sz, d.font.b, d.number_format):
                    diffs.append(f"[{name}] oblika celice {c.coordinate} se razlikuje")
                if len(diffs) > 30:
                    diffs.append("… (več razlik ni prikazanih)")
                    return diffs
    return diffs


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    a, b = Path(sys.argv[1]), Path(sys.argv[2])
    if not a.exists() or not b.exists():
        print("Datoteka ne obstaja.")
        return 2
    if a.suffix.lower() == ".docx":
        diffs = check_docx(a, b)
    elif a.suffix.lower() in (".xlsx", ".xlsm"):
        diffs = check_xlsx(a, b)
    else:
        print("Podprta sta samo DOCX in XLSX.")
        return 2
    if diffs:
        print(f"RAZLIKE ({b.name}):")
        for d in diffs:
            print(" -", d)
        return 1
    print(f"V redu: {b.name} ohranja obliko izvirnika.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
