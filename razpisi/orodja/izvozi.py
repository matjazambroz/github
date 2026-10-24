#!/usr/bin/env python3
"""Pretvori izhodne .md datoteke razpisa v Word (.docx) in PDF.

Zagon (v mapi razpisi):   python orodja/izvozi.py <ime-razpisa>
Vhod:   izhod/<razpis>/*.md
Izhod:  izhod/<razpis>/*.docx in *.pdf (PDF samo, če je na voljo Word, LibreOffice ali pandoc)

Potrebuje: pip install python-docx
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt
except ImportError:
    sys.exit("Manjka python-docx. Namesti ga z:  pip install python-docx")

ROOT = Path(__file__).resolve().parent.parent
INLINE = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*\s][^*]*\*)")


def add_runs(par, text):
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            par.add_run(part[2:-2]).bold = True
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            r = par.add_run(part[1:-1])
            r.font.name = "Consolas"
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            par.add_run(part[1:-1]).italic = True
        else:
            par.add_run(part)


def is_table_sep(line):
    return bool(re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$", line))


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def md_to_docx(md, out):
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)
    lines = md.splitlines()
    i, in_code = 0, False
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            p = doc.add_paragraph()
            r = p.add_run(line)
            r.font.name = "Consolas"
            r.font.size = Pt(9)
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            doc.add_heading(m.group(2).strip(), level=min(len(m.group(1)), 4))
        elif "|" in line and i + 1 < len(lines) and is_table_sep(lines[i + 1]):
            head = split_row(line)
            rows = []
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(split_row(lines[i]))
                i += 1
            table = doc.add_table(rows=1, cols=len(head))
            table.style = "Table Grid"
            for c, h in enumerate(head):
                cell = table.rows[0].cells[c]
                cell.text = ""
                add_runs(cell.paragraphs[0], h)
                for r in cell.paragraphs[0].runs:
                    r.bold = True
            for row in rows:
                cells = table.add_row().cells
                for c in range(len(head)):
                    cells[c].text = ""
                    add_runs(cells[c].paragraphs[0], row[c] if c < len(row) else "")
            doc.add_paragraph()
            continue
        elif re.match(r"^\s*([-*+])\s+", line):
            level = (len(line) - len(line.lstrip())) // 2
            style = "List Bullet" if level == 0 else "List Bullet 2"
            add_runs(doc.add_paragraph(style=style), re.sub(r"^\s*[-*+]\s+", "", line))
        elif re.match(r"^\s*\d+[.)]\s+", line):
            add_runs(doc.add_paragraph(style="List Number"), re.sub(r"^\s*\d+[.)]\s+", "", line))
        elif re.match(r"^\s*>\s?", line):
            p = doc.add_paragraph(style="Intense Quote")
            add_runs(p, re.sub(r"^\s*>\s?", "", line))
        elif re.match(r"^\s*(---+|\*\*\*+)\s*$", line):
            doc.add_paragraph("_" * 60).alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.strip():
            add_runs(doc.add_paragraph(), line.strip())
        i += 1
    doc.save(out)


def to_pdf(docx_path):
    """Poskusi Word (docx2pdf), LibreOffice, nato pandoc. Vrne pot do PDF ali None."""
    pdf = docx_path.with_suffix(".pdf")
    try:
        from docx2pdf import convert  # zahteva nameščen Microsoft Word
        convert(str(docx_path), str(pdf))
        if pdf.exists():
            return pdf
    except Exception:
        pass
    for exe in ("soffice", "libreoffice", r"C:\Program Files\LibreOffice\program\soffice.exe"):
        path = shutil.which(exe) or (exe if Path(exe).exists() else None)
        if path:
            subprocess.run([path, "--headless", "--convert-to", "pdf", "--outdir", str(docx_path.parent), str(docx_path)],
                           capture_output=True, timeout=180)
            if pdf.exists():
                return pdf
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit("Uporaba: python orodja/izvozi.py <ime-razpisa>")
    folder = ROOT / "izhod" / sys.argv[1]
    mds = sorted(folder.glob("*.md"))
    if not mds:
        sys.exit(f"V {folder} ni .md datotek.")
    no_pdf = []
    for md in mds:
        out = md.with_suffix(".docx")
        md_to_docx(md.read_text(encoding="utf-8"), out)
        pdf = to_pdf(out)
        print(f"{md.name} -> {out.name}" + (f", {pdf.name}" if pdf else ""))
        if not pdf:
            no_pdf.append(md.name)
    if no_pdf:
        print("\nPDF ni bil ustvarjen (ni Worda ali LibreOffice). Odpri .docx v Wordu in shrani kot PDF.")


if __name__ == "__main__":
    main()
