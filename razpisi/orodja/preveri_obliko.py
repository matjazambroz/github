#!/usr/bin/env python3
"""Preveri, da izpolnjen DOCX/XLSX ohranja obliko izvirnika.

Uporaba:  python orodja/preveri_obliko.py <izvirnik> <izpolnjeno>
DOCX: primerja glave, noge, sloge, oštevilčenje, teme, nastavitve strani in uporabljene pisave.
XLSX: primerja sloge, širine stolpcev, združene celice in formule.
Izhod: 0 = enako, 1 = razlike, 2 = napaka v uporabi.
"""
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

PARTS_DOCX = re.compile(r"^word/(header\d*|footer\d*|styles|numbering|theme/theme\d*|fontTable|settings)\.xml$")
FONT_RE = re.compile(rb'w:(?:ascii|hAnsi|cs|eastAsia)="([^"]+)"')
SIZE_RE = re.compile(rb'<w:sz w:val="(\d+)"')
SECT_RE = re.compile(rb"<w:sectPr.*?</w:sectPr>", re.S)


def read(zf, name):
    return zf.read(name) if name in zf.namelist() else b""


def check_package(a, b):
    """Preveri, da je izpolnjen DOCX veljaven paket, ki ga Word lahko odpre."""
    diffs = []
    with zipfile.ZipFile(a) as za, zipfile.ZipFile(b) as zb:
        try:
            bad = zb.testzip()
        except Exception as e:  # poškodovan ZIP
            return [f"ZIP je poškodovan: {e}"]
        if bad:
            diffs.append(f"ZIP: poškodovan zapis {bad}")
        names_a, names_b = set(za.namelist()), set(zb.namelist())
        for n in sorted(names_a - names_b):
            diffs.append(f"manjka del paketa, ki je v izvirniku: {n}")
        for n in sorted(names_b - names_a):
            diffs.append(f"dodan del paketa, ki ga izvirnik nima: {n}")
        if "[Content_Types].xml" not in names_b:
            diffs.append("manjka [Content_Types].xml")
        trees = {}
        for n in zb.namelist():
            if n.endswith((".xml", ".rels")):
                try:
                    trees[n] = ET.fromstring(zb.read(n))
                except ET.ParseError as e:
                    diffs.append(f"{n}: neveljaven XML ({e})")
        # cilji povezav (relationships) morajo obstajati
        for n, tree in trees.items():
            if not n.endswith(".rels"):
                continue
            base = posixpath.dirname(posixpath.dirname(n))
            for rel in tree:
                if rel.get("TargetMode") == "External":
                    continue
                target = rel.get("Target", "")
                full = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join(base, target))
                if full not in names_b:
                    diffs.append(f"{n}: povezava kaže na manjkajoči del {full}")
        # sprotne in končne opombe: vsaka referenca mora imeti zapis
        doc = zb.read("word/document.xml").decode("utf-8", "ignore") if "word/document.xml" in names_b else ""
        for kind, part in (("footnote", "word/footnotes.xml"), ("endnote", "word/endnotes.xml")):
            refs = set(re.findall(rf'<w:{kind}Reference[^>]*w:id="(-?\d+)"', doc))
            if not refs:
                continue
            if part not in names_b:
                diffs.append(f"dokument sklicuje {kind}-e ({len(refs)}), a {part} manjka (Word: »footnotes are missing or corrupt«)")
                continue
            have = set(re.findall(rf'<w:{kind}[^>]*w:id="(-?\d+)"', zb.read(part).decode("utf-8", "ignore")))
            missing = refs - have
            if missing:
                diffs.append(f"{part}: manjkajo zapisi za reference {sorted(missing)}")
        # vsak del mora imeti vrsto vsebine
        ct = trees.get("[Content_Types].xml")
        if ct is not None:
            defaults = {d.get("Extension", "").lower() for d in ct if d.tag.endswith("Default")}
            overrides = {o.get("PartName", "") for o in ct if o.tag.endswith("Override")}
            for n in names_b:
                if n == "[Content_Types].xml" or n.endswith("/"):
                    continue
                if "/" + n not in overrides and n.rsplit(".", 1)[-1].lower() not in defaults:
                    diffs.append(f"[Content_Types].xml ne pozna vrste za {n}")
    return diffs


def check_docx(a, b):
    diffs = check_package(a, b)
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
