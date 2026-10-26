# Pregled pogodb

Namizna aplikacija (Windows 10/11, samostojna) za pregled pogodb s strankami: OCR skenov, izluščenje strukture,
veljavnosti in vrednosti, iskanje po vsebini, izvoz v Excel. Vse lokalno. Navodila za uporabnika: `NAVODILA.md`.

## Razvoj
```
pip install -r requirements.txt pytest
python -m pytest tests
python run.py
```
Za OCR mora biti na PATH `tesseract` (s `slv` in `eng` podatki).

## Windows paket
GitHub Actions (`.github/workflows/pogodbe-windows.yml`) ali lokalno `./build_windows.ps1` na Windows.
Rezultat: `dist/PregledPogodb-windows.zip` s priloženim Tesseractom.

## Zgradba
- `extract.py` – pravila za stranke, datume, vrednosti, člene
- `reader.py`, `ocr.py` – branje PDF/slik/DOCX, Tesseract
- `db.py` – SQLite + FTS5; `gui.py` – PySide6; `export.py` – Excel
