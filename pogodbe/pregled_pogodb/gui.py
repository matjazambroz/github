"""Namizni vmesnik (PySide6)."""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate, QObject, Qt, QThread, Signal
from PySide6.QtGui import QAction, QBrush, QColor, QDesktopServices, QTextCursor, QTextDocument
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox, QDateEdit, QDoubleSpinBox,
                               QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
                               QPlainTextEdit, QProgressDialog, QPushButton, QSplitter, QTableWidget,
                               QTableWidgetItem, QTabWidget, QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                               QWidget)

from . import APP_NAME, __version__, importer, ocr, reader
from .db import Store
from .export import export_xlsx
from .extract import status_of

COLORS = {"Pretečena": "#f8d7da", "Poteče kmalu": "#fff3cd", "Veljavna": "#d4edda",
          "Nedoločen čas": "#d1ecf1", "Neznano": "#eeeeee"}
COLS = ["Naslov", "Št.", "Stranka 1", "Stranka 2", "Vrsta", "Sklenjena", "Velja do", "Vrednost", "Status"]
CONF_COLOR = {"visoka": "#198754", "srednja": "#b58105", "nizka": "#dc3545"}


def fmt_date(s):
    return date.fromisoformat(s).strftime("%d.%m.%Y") if s else ""


def fmt_value(v, cur, period=""):
    if v is None:
        return ""
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} {cur or ''}".strip() + (f" ({period})" if period else "")


class ImportWorker(QObject):
    progress = Signal(int, int, str)
    done = Signal(list)

    def __init__(self, store_path: str, files: list[str]):
        super().__init__()
        self.store_path, self.files, self.cancel = store_path, files, False

    def run(self):
        store = Store(self.store_path)  # povezava mora nastati v niti, ki jo uporablja
        results = []
        for i, f in enumerate(self.files):
            if self.cancel:
                break
            self.progress.emit(i, len(self.files), Path(f).name)
            st, _ = importer.import_file(store, f, lambda m, n=Path(f).name: self.progress.emit(i, len(self.files), f"{n} – {m}"))
            results.append((f, st))
        self.done.emit(results)


class DetailPanel(QTabWidget):
    saved = Signal()

    def __init__(self, store: Store):
        super().__init__()
        self.store, self.cid = store, None
        # --- podatki
        form_w = QWidget()
        form = QFormLayout(form_w)
        self.f = {}
        for key, label in [("title", "Naslov"), ("number", "Št. pogodbe"), ("doc_type", "Vrsta"),
                           ("party1", "Stranka 1"), ("party1_role", "Vloga 1"), ("party2", "Stranka 2"),
                           ("party2_role", "Vloga 2"), ("notice_period", "Odpovedni rok"), ("duration", "Trajanje"),
                           ("currency", "Valuta"), ("vat_note", "DDV"), ("value_period", "Obdobje vrednosti")]:
            self.f[key] = QLineEdit()
            form.addRow(label, self.f[key])
        for key, label in [("sign_date", "Sklenjena"), ("start_date", "Velja od"), ("end_date", "Velja do")]:
            w = QDateEdit()
            w.setCalendarPopup(True)
            w.setDisplayFormat("dd.MM.yyyy")
            w.setSpecialValueText("—")
            w.setMinimumDate(QDate(1990, 1, 1))
            self.f[key] = w
            form.addRow(label, w)
        self.f["value"] = QDoubleSpinBox()
        self.f["value"].setRange(0, 1e12)
        self.f["value"].setDecimals(2)
        self.f["value"].setGroupSeparatorShown(True)
        self.f["value"].setSpecialValueText("—")
        form.addRow("Vrednost", self.f["value"])
        self.f["payment_term_days"] = QLineEdit()
        form.addRow("Plačilni rok (dni)", self.f["payment_term_days"])
        self.f["indefinite"] = QCheckBox("Za nedoločen čas")
        self.f["auto_renew"] = QCheckBox("Samodejno podaljšanje")
        form.addRow(self.f["indefinite"])
        form.addRow(self.f["auto_renew"])
        self.f["subject"] = QPlainTextEdit()
        self.f["subject"].setFixedHeight(70)
        form.addRow("Predmet", self.f["subject"])
        self.f["notes"] = QPlainTextEdit()
        self.f["notes"].setFixedHeight(60)
        form.addRow("Opombe", self.f["notes"])
        self.evidence = QTextEdit()
        self.evidence.setReadOnly(True)
        self.evidence.setFixedHeight(130)
        form.addRow("Od kod podatek", self.evidence)
        btns = QHBoxLayout()
        self.save_btn = QPushButton("Shrani popravke")
        self.save_btn.clicked.connect(self.save)
        self.open_btn = QPushButton("Odpri izvirnik")
        self.open_btn.clicked.connect(lambda: self.cid and QDesktopServices.openUrl(
            QUrl.fromLocalFile(self.store.get(self.cid)["file_path"])))
        self.folder_btn = QPushButton("Odpri mapo")
        self.folder_btn.clicked.connect(lambda: self.cid and QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(Path(self.store.get(self.cid)["file_path"]).parent))))
        for b in (self.save_btn, self.open_btn, self.folder_btn):
            btns.addWidget(b)
        form.addRow(btns)
        from PySide6.QtWidgets import QScrollArea
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setWidget(form_w)
        self.addTab(sc, "Podatki")
        # --- struktura
        st = QSplitter(Qt.Horizontal)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Struktura pogodbe"])
        self.tree.currentItemChanged.connect(self._show_article)
        self.art_view = QTextEdit()
        self.art_view.setReadOnly(True)
        st.addWidget(self.tree)
        st.addWidget(self.art_view)
        st.setSizes([280, 500])
        self.addTab(st, "Struktura")
        # --- besedilo
        tw = QWidget()
        tl = QVBoxLayout(tw)
        self.find = QLineEdit()
        self.find.setPlaceholderText("Poišči v besedilu…")
        self.find.returnPressed.connect(self._find_next)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        tl.addWidget(self.find)
        tl.addWidget(self.text)
        self.addTab(tw, "Besedilo")
        self.setEnabled(False)

    def load(self, cid):
        self.cid = cid
        r = self.store.get(cid) if cid else None
        self.setEnabled(r is not None)
        if r is None:
            return
        for k, w in self.f.items():
            v = r[k]
            if isinstance(w, QLineEdit):
                w.setText("" if v is None else str(v))
            elif isinstance(w, QDateEdit):
                w.setDate(QDate.fromString(v, Qt.ISODate) if v else w.minimumDate())
            elif isinstance(w, QDoubleSpinBox):
                w.setValue(v or 0)
            elif isinstance(w, QCheckBox):
                w.setChecked(bool(v))
            elif isinstance(w, QPlainTextEdit):
                w.setPlainText(v or "")
        ev = json.loads(r["evidence_json"] or "{}")
        names = {"sign_date": "Sklenjena", "start_date": "Velja od", "end_date": "Velja do", "value": "Vrednost",
                 "duration": "Trajanje", "notice_period": "Odpovedni rok", "auto_renew": "Podaljšanje",
                 "indefinite": "Nedoločen čas", "payment_term_days": "Plačilni rok"}
        html = "".join(f"<p><b>{names.get(k, k)}</b> <span style='color:{CONF_COLOR.get(v['confidence'], '#000')}'>"
                       f"[{v['confidence']}]</span><br><i>{v['text']}</i></p>" for k, v in ev.items())
        self.evidence.setHtml(html or "<i>Podatki niso bili samodejno najdeni – vnesite jih ročno.</i>")
        self.tree.clear()
        for a in self.store.articles(cid):
            label = (f"{a['num']}. člen – " if a["kind"] == "člen" else "") + (a["title"] or "")
            it = QTreeWidgetItem([label.strip(" –") or "(brez naslova)"])
            it.setData(0, Qt.UserRole, a["body"])
            self.tree.addTopLevelItem(it)
        self.art_view.clear()
        self.text.setPlainText((r["full_text"] or "").replace("\f", "\n\n──────── nova stran ────────\n\n"))

    def _show_article(self, cur, _prev):
        self.art_view.setPlainText(cur.data(0, Qt.UserRole) if cur else "")

    def _find_next(self):
        if not self.text.find(self.find.text()):
            self.text.moveCursor(QTextCursor.Start)
            self.text.find(self.find.text())

    def save(self):
        if not self.cid:
            return
        v = {}
        for k, w in self.f.items():
            if isinstance(w, QLineEdit):
                v[k] = w.text().strip()
            elif isinstance(w, QDateEdit):
                v[k] = None if w.date() == w.minimumDate() else w.date().toString(Qt.ISODate)
            elif isinstance(w, QDoubleSpinBox):
                v[k] = w.value() or None
            elif isinstance(w, QCheckBox):
                v[k] = int(w.isChecked())
            elif isinstance(w, QPlainTextEdit):
                v[k] = w.toPlainText()
        v["payment_term_days"] = int(v["payment_term_days"]) if str(v["payment_term_days"]).isdigit() else None
        self.store.update(self.cid, v)
        self.saved.emit()


class MainWindow(QMainWindow):
    def __init__(self, store: Store):
        super().__init__()
        self.store = store
        self.setWindowTitle(f"{APP_NAME} {__version__}")
        self.resize(1400, 820)
        self.setAcceptDrops(True)
        self._threads = []

        bar = self.addToolBar("Orodna vrstica")
        bar.setMovable(False)
        for text, fn in [("Uvozi datoteke…", self.import_files), ("Uvozi mapo…", self.import_folder),
                         ("Izvozi v Excel…", self.export), ("Izbriši izbrano", self.delete_selected),
                         ("O programu", self.about)]:
            a = QAction(text, self)
            a.triggered.connect(fn)
            bar.addAction(a)

        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)
        self.summary = QLabel()
        self.summary.setStyleSheet("font-size:14px;padding:6px;background:#f1f3f5;border-radius:4px")
        lay.addWidget(self.summary)
        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Išči po naslovu, strankah in vsebini pogodb…")
        self.search.textChanged.connect(self.refresh)
        self.filter = QComboBox()
        self.filter.addItems(["Vse", "Veljavna", "Poteče kmalu", "Pretečena", "Nedoločen čas", "Neznano"])
        self.filter.currentTextChanged.connect(self.refresh)
        top.addWidget(self.search, 1)
        top.addWidget(QLabel("Status:"))
        top.addWidget(self.filter)
        lay.addLayout(top)

        split = QSplitter(Qt.Horizontal)
        self.table = QTableWidget(0, len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemSelectionChanged.connect(self.on_select)
        split.addWidget(self.table)
        self.detail = DetailPanel(store)
        self.detail.saved.connect(self.refresh)
        split.addWidget(self.detail)
        split.setSizes([800, 560])
        lay.addWidget(split, 1)
        self.statusBar().showMessage("Povlecite PDF, slike ali Word datoteke v okno za uvoz.")
        if not ocr.available():
            self.statusBar().showMessage("OPOZORILO: Tesseract OCR ni najden – skenirane pogodbe ne bodo prebrane.")
        self.refresh()

    # ---- seznam
    def refresh(self, *_):
        sel = self.current_id()
        rows = self.store.list(self.search.text())
        want = self.filter.currentText()
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        for r in rows:
            end = date.fromisoformat(r["end_date"]) if r["end_date"] else None
            status = status_of(end, bool(r["indefinite"]))
            if want != "Vse" and status != want:
                continue
            vals = [r["title"], r["number"], r["party1"], r["party2"], r["doc_type"], fmt_date(r["sign_date"]),
                    fmt_date(r["end_date"]) or ("nedoločen čas" if r["indefinite"] else ""),
                    fmt_value(r["value"], r["currency"], r["value_period"]), status]
            i = self.table.rowCount()
            self.table.insertRow(i)
            for c, v in enumerate(vals):
                it = QTableWidgetItem(str(v or ""))
                it.setBackground(QBrush(QColor(COLORS[status])))
                it.setForeground(QBrush(QColor("#212529")))
                if c == 0:
                    it.setData(Qt.UserRole, r["id"])
                self.table.setItem(i, c, it)
        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, min(self.table.columnWidth(0), 320))
        for i in range(self.table.rowCount()):
            if self.table.item(i, 0).data(Qt.UserRole) == sel:
                self.table.selectRow(i)
        s = self.store.summary()
        vals = " · ".join(fmt_value(v, c) for c, v in s["vrednost_veljavnih"].items()) or "—"
        self.summary.setText(f"<b>Pogodb: {s['skupaj']}</b> &nbsp;|&nbsp; veljavnih: {s['veljavne']} &nbsp;|&nbsp; "
                             f"<span style='color:#b58105'>poteče v 90 dneh: {s['kmalu']}</span> &nbsp;|&nbsp; "
                             f"<span style='color:#dc3545'>pretečenih: {s['pretecene']}</span> &nbsp;|&nbsp; "
                             f"vrednost veljavnih: {vals}")

    def current_id(self):
        rows = self.table.selectionModel().selectedRows() if self.table.selectionModel() else []
        return self.table.item(rows[0].row(), 0).data(Qt.UserRole) if rows else None

    def on_select(self):
        self.detail.load(self.current_id())

    # ---- uvoz
    def import_files(self):
        exts = " ".join("*" + e for e in sorted(reader.SUPPORTED))
        files, _ = QFileDialog.getOpenFileNames(self, "Izberite pogodbe", "", f"Pogodbe ({exts})")
        if files:
            self.run_import(files)

    def import_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Izberite mapo s pogodbami")
        if d:
            files = reader.find_files(d)
            if not files:
                QMessageBox.information(self, APP_NAME, "V mapi ni podprtih datotek (PDF, slike, DOCX).")
                return
            self.run_import(files)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        files = []
        for u in e.mimeData().urls():
            p = u.toLocalFile()
            files += reader.find_files(p) if os.path.isdir(p) else ([p] if Path(p).suffix.lower() in reader.SUPPORTED else [])
        if files:
            self.run_import(files)

    def run_import(self, files):
        dlg = QProgressDialog("Priprava…", "Prekini", 0, len(files), self)
        dlg.setWindowTitle("Uvoz pogodb")
        dlg.setMinimumDuration(0)
        dlg.setWindowModality(Qt.WindowModal)
        th = QThread(self)
        w = ImportWorker(self.store.path, files)
        w.moveToThread(th)
        th.started.connect(w.run)
        w.progress.connect(lambda i, n, name: (dlg.setValue(i), dlg.setLabelText(f"({i + 1}/{n}) {name}")))
        dlg.canceled.connect(lambda: setattr(w, "cancel", True))

        def finished(results):
            dlg.close()
            th.quit()
            th.wait()
            self.refresh()
            ok = sum(1 for _, s in results if s.startswith("dodano"))
            bad = [(f, s) for f, s in results if s.startswith("napaka") or "OCR" in s]
            msg = f"Uvoženih: {ok}, preskočenih: {sum(1 for _, s in results if s.startswith('preskočeno'))}, " \
                  f"napak: {sum(1 for _, s in results if s.startswith('napaka'))}."
            if bad:
                msg += "\n\n" + "\n".join(f"{Path(f).name}: {s}" for f, s in bad[:15])
            QMessageBox.information(self, "Uvoz končan", msg)

        w.done.connect(finished)
        self._threads.append((th, w))
        th.start()

    # ---- ostalo
    def export(self):
        p, _ = QFileDialog.getSaveFileName(self, "Izvoz v Excel", "pogodbe.xlsx", "Excel (*.xlsx)")
        if p:
            n = export_xlsx(self.store, p)
            QMessageBox.information(self, APP_NAME, f"Izvoženih pogodb: {n}")

    def delete_selected(self):
        cid = self.current_id()
        if cid and QMessageBox.question(self, APP_NAME, "Izbrišem pogodbo iz zbirke? (Izvirna datoteka ostane.)") \
                == QMessageBox.Yes:
            self.store.delete(cid)
            self.detail.load(None)
            self.refresh()

    def about(self):
        QMessageBox.about(self, APP_NAME, f"{APP_NAME} {__version__}\n\nPodatki: {self.store.path}\n"
                          f"OCR: {ocr.tesseract_path() or 'ni najden'} ({ocr.languages() or '-'})\n\n"
                          "Vse se izvaja lokalno, pogodbe ne zapustijo računalnika.")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow(Store())
    w.show()
    sys.exit(app.exec())
