#!/usr/bin/env python3
"""Ustvari IZMIŠLJENE račune (PDF), pričakovane rezultate in 'idealen' Strategov izhod za preizkus verige.
Zagon: python3 ustvari_testne_racune.py   (potreben reportlab; pisava DejaVu Sans)
Vsi podatki so izmišljeni. Računi nosijo opozorilo 'IZMIŠLJEN RAČUN, SAMO ZA PREIZKUS'."""
import json
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

KUPEC = {"naziv": "Testno podjetje d.o.o. (IZMIŠLJENO)", "naslov": "Testna cesta 5", "mesto": "Maribor",
         "posta": "2000", "drzava": "SI", "id_za_ddv": "SI87654321"}


def q2(x):
    return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)


# --- definicije računov -------------------------------------------------------------------------------------------
RACUNI = [
    dict(
        datoteka="racun-1-domaci-ddv22.pdf", naslov_dok="RAČUN", st="2026-014", datum="2026-11-05", storitev="2026-10-31",
        zapadlost="2026-12-05", sklic="SI00 2026-014", xtrf="86652",
        izd=dict(naziv="Primer Prevajalec s.p.", naslov="Testna ulica 1", mesto="Ljubljana", posta="1000", drzava="SI",
                 id_za_ddv="SI12345678", iban="SI56 0000 0000 0000 000", bic="TESTSI2X"),
        postavke=[("Prevod SL-EN, 1500 besed (XTRF 86652)", D("1500"), "C62", D("0.06"), D("22")),
                  ("Lektoriranje", D("2"), "HUR", D("30.00"), D("22"))],
        opomba_pdf="Plačilo v 30 dneh.", tiskan_bruto=None,
        pricakovano=dict(konto="4100", zastavice_prazne=True, xml_koda=0, podatki={"dobavitelj.id_za_ddv": "SI12345678"}),
    ),
    dict(
        datoteka="racun-2-sp-brez-ddv.pdf", naslov_dok="RAČUN", st="L-2026/07", datum="2026-11-03", storitev="2026-10-31",
        zapadlost="2026-11-18", sklic="SI00 07-2026", xtrf="86701",
        izd=dict(naziv="Testna Lektorica s.p.", naslov="Izmišljena pot 12", mesto="Celje", posta="3000", drzava="SI",
                 id_za_ddv=None, iban="SI56 1111 1111 1111 111", bic=None),
        postavke=[("Lektoriranje slovenskega besedila (XTRF 86701)", D("8"), "HUR", D("30.00"), D("0"))],
        opomba_pdf="Izdajatelj ni zavezanec za DDV (oprostitev za male davčne zavezance). DDV ni obračunan.", tiskan_bruto=None,
        pricakovano=dict(konto="4100", zastavice_prazne=True, xml_koda=0, podatki={"postavke.0.stopnja_ddv": 0}),
    ),
    dict(
        datoteka="racun-3-tuj-izvajalec.pdf", naslov_dok="RECHNUNG / INVOICE", st="RE-2026-0391", datum="2026-11-02",
        storitev="2026-10-30", zapadlost="2026-12-02", sklic="RE-2026-0391", xtrf="86733",
        izd=dict(naziv="Beispiel Übersetzungen GmbH", naslov="Musterstraße 7", mesto="Berlin", posta="10115", drzava="DE",
                 id_za_ddv="DE123456789", iban="DE89 3704 0044 0532 0130 00", bic="COBADEFFXXX"),
        postavke=[("Übersetzung DE-SL, 3000 Wörter (XTRF 86733)", D("3000"), "C62", D("0.08"), D("0")),
                  ("Projektmanagement", D("1"), "C62", D("60.00"), D("0"))],
        opomba_pdf="Steuerschuldnerschaft des Leistungsempfängers (Reverse Charge). Keine Umsatzsteuer ausgewiesen.",
        tiskan_bruto=None,
        pricakovano=dict(konto="4102", zastavice_vsebuje=["reverse", "tuj", "obrnjen"], xml_koda=None, podatki={"dobavitelj.drzava": "DE"}),
    ),
    dict(
        datoteka="racun-4-racunska-napaka.pdf", naslov_dok="RAČUN", st="2026-099", datum="2026-11-04", storitev="2026-10-31",
        zapadlost="2026-12-04", sklic="SI00 2026-099", xtrf="86750",
        izd=dict(naziv="Računski Test s.p.", naslov="Napačna ulica 3", mesto="Koper", posta="6000", drzava="SI",
                 id_za_ddv="SI55555555", iban="SI56 2222 2222 2222 222", bic=None),
        postavke=[("Prevod EN-SL, 100 besed (XTRF 86750)", D("100"), "C62", D("0.50"), D("22"))],
        opomba_pdf="Plačilo v 30 dneh.", tiskan_bruto=D("71.00"),
        pricakovano=dict(konto="4100", zastavice_vsebuje=["matemat", "znesek", "bruto"], matematika="napaka", xml_koda=1,
                         podatki={"skupaj.bruto": "71.00"}),
    ),
]


def izracun(r):
    vrst = []
    for opis, kol, enota, cena, stopnja in r["postavke"]:
        neto = q2(kol * cena)
        vrst.append((opis, kol, enota, cena, stopnja, neto, q2(neto * stopnja / 100)))
    neto = sum(v[5] for v in vrst)
    ddv = sum(v[6] for v in vrst)
    return vrst, neto, ddv, neto + ddv


def narisi(r):
    vrst, neto, ddv, bruto = izracun(r)
    c = canvas.Canvas(str(HERE / r["datoteka"]), pagesize=A4, invariant=1)
    w, h = A4
    c.setFillColorRGB(0.75, 0.1, 0.1)
    c.setFont("DVB", 9)
    c.drawString(40, h - 30, "IZMIŠLJEN RAČUN, SAMO ZA PREIZKUS. Podatki ne obstajajo.")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("DVB", 18)
    c.drawString(40, h - 70, r["naslov_dok"])
    c.setFont("DV", 10)
    y = h - 95
    for vr in (f"Št. računa: {r['st']}", f"Datum računa: {r['datum']}", f"Datum storitve: {r['storitev']}",
               f"Zapadlost: {r['zapadlost']}", f"Sklic: {r['sklic']}"):
        c.drawString(40, y, vr)
        y -= 14
    i = r["izd"]
    c.setFont("DVB", 10)
    c.drawString(330, h - 95, "Izdajatelj")
    c.setFont("DV", 10)
    yy = h - 109
    for vr in (i["naziv"], i["naslov"], f"{i['posta']} {i['mesto']}", f"Država: {i['drzava']}",
               f"ID za DDV: {i['id_za_ddv']}" if i["id_za_ddv"] else "Ni zavezanec za DDV",
               f"IBAN: {i['iban']}", f"BIC: {i['bic']}" if i["bic"] else ""):
        if vr:
            c.drawString(330, yy, vr)
            yy -= 14
    y = min(y, yy) - 16
    c.setFont("DVB", 10)
    c.drawString(40, y, "Kupec")
    c.setFont("DV", 10)
    for vr in (KUPEC["naziv"], KUPEC["naslov"], f"{KUPEC['posta']} {KUPEC['mesto']}", f"ID za DDV: {KUPEC['id_za_ddv']}"):
        y -= 14
        c.drawString(40, y, vr)
    y -= 30
    c.setFont("DVB", 9)
    for x, t in ((40, "Opis"), (300, "Količina"), (355, "Enota"), (400, "Cena"), (455, "DDV %"), (500, "Neto")):
        c.drawString(x, y, t)
    c.line(40, y - 4, 555, y - 4)
    c.setFont("DV", 9)
    for opis, kol, enota, cena, stopnja, neto_v, _ in vrst:
        y -= 16
        c.drawString(40, y, opis[:52])
        c.drawRightString(345, y, format(kol.normalize(), "f"))
        c.drawString(355, y, enota)
        c.drawRightString(440, y, format(cena, "f"))
        c.drawRightString(485, y, format(stopnja.normalize(), "f"))
        c.drawRightString(555, y, format(neto_v, "f"))
    y -= 30
    c.line(330, y + 16, 555, y + 16)
    tisk_bruto = r["tiskan_bruto"] if r["tiskan_bruto"] is not None else bruto
    for t, v in (("Skupaj neto", neto), ("DDV", ddv), ("SKUPAJ ZA PLAČILO (EUR)", tisk_bruto)):
        c.setFont("DVB" if t.startswith("SKUPAJ") else "DV", 10)
        c.drawString(330, y, t)
        c.drawRightString(555, y, format(v, "f"))
        y -= 16
    y -= 14
    c.setFont("DV", 9)
    c.drawString(40, y, r["opomba_pdf"])
    c.showPage()
    c.save()


def strateg_izhod(r):
    """'Idealen' izhod Stratega za ta račun (po eslog/preslikava.md)."""
    vrst, neto, ddv, bruto = izracun(r)
    tisk = r["tiskan_bruto"] if r["tiskan_bruto"] is not None else bruto
    i = r["izd"]
    dob = {k: v for k, v in dict(naziv=i["naziv"], naslov=i["naslov"], mesto=i["mesto"], posta=i["posta"], drzava=i["drzava"],
                                 id_za_ddv=i["id_za_ddv"], iban=i["iban"], bic=i["bic"]).items() if v}
    p = r["pricakovano"]
    zastavice, matematika = [], "ok"
    if r["datoteka"].startswith("racun-3"):
        zastavice = ["TUJ IZVAJALEC (DE)", "REVERSE CHARGE: obravnavo potrdi servis"]
    if r["datoteka"].startswith("racun-4"):
        zastavice = ["MATEMATIKA: neto + DDV (61.00) ne ustreza skupnemu znesku na računu (71.00)"]
        matematika = "napaka"
    return {
        "racun_id": f"IZMISLJEN-{r['st']}", "prejeto": "2026-11-06", "xml_izvirnik": None,
        "podatki": {"st_racuna": r["st"], "datum_racuna": r["datum"], "datum_storitve": r["storitev"], "zapadlost": r["zapadlost"],
                    "valuta": "EUR", "sklic": r["sklic"], "dobavitelj": dob,
                    "postavke": [{"opis": o, "kolicina": format(k.normalize(), "f"), "enota": e, "cena_neto": format(c, "f"),
                                  "stopnja_ddv": int(s) if s == s.to_integral() else float(s)} for o, k, e, c, s, _, _ in vrst],
                    "skupaj": {"neto": format(neto, "f"), "ddv": format(ddv, "f"), "bruto": format(tisk, "f")},
                    "xtrf_projekt": r["xtrf"]},
        "preverjanja": {"matematika": matematika, "dvojnik": "ne", "xtrf": "ni podatka", "iban": "ok"},
        "davcno": "preslikano iz izmišljenega računa", "konto_predlog": p["konto"], "zastavice": zastavice, "zaupanje": 95,
    }


def main():
    pricak = {}
    ideal = []
    for r in RACUNI:
        narisi(r)
        vrst, neto, ddv, bruto = izracun(r)
        tisk = r["tiskan_bruto"] if r["tiskan_bruto"] is not None else bruto
        osnovni = {"st_racuna": r["st"], "datum_racuna": r["datum"], "valuta": "EUR", "dobavitelj.naziv": r["izd"]["naziv"],
                   "skupaj.neto": format(neto, "f"), "skupaj.ddv": format(ddv, "f"), "skupaj.bruto": format(tisk, "f")}
        pr = dict(r["pricakovano"])
        pr["podatki"] = osnovni | pr.get("podatki", {})
        pricak[r["st"]] = pr | {"datoteka": r["datoteka"]}
        ideal.append(strateg_izhod(r))
    (HERE / "pricakovano.json").write_text(json.dumps(pricak, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / "strateg-idealen.json").write_text(json.dumps(ideal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / "kupec-testni.json").write_text(json.dumps(KUPEC, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ustvarjeno:", ", ".join(r["datoteka"] for r in RACUNI))


if __name__ == "__main__":
    main()
