#!/usr/bin/env python3
"""Preveri IZVIRNI eSLOG XML, ki ga je račun priložil izvajalec (npr. iz e-računov), preden ga priložimo osnutku za servis.

Uporaba:  ./preveri_izvirni_xml.py izvirnik.xml racun.json [--kupec kupec.json]
  racun.json = `podatki` iz Strategovega izhoda (podatki, razbrani iz PDF-ja), vključno s `skupaj`.

Preveri: (1) datoteka je varna in veljavna po eslog.xsd, (2) XML je notranje skladen (vsote postavk = skupni zneski),
(3) XML se ujema s PDF-jem (št. računa, datum, valuta, dobavitelj, IBAN, neto/DDV/bruto), (4) kupec v XML je Amidas.
Izvirnika ne spreminja; če je vse v redu, se ga priloži takšnega, kot je.

Izhodne kode: 0 = v redu, uporabi izvirnik
              1 = neskladje med XML in PDF/podatki (ZASTAVICA; izvirnika ne prilagajaj, račun potrdi uporabnik)
              2 = datoteka je neveljavna po shemi ali nevarna/pokvarjena (ZASTAVICA)
              3 = ni mogoče preveriti (manjka xmllint ali eslog.xsd): izvirnik je NEPREVERJEN
Samo standardna knjižnica Pythona; podatkov z interneta ne prenaša.
"""
import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = {"e": "urn:eslog:2.00"}
MAX_BYTES = 5 * 1024 * 1024
TOL = Decimal("0.005")


def t(el, path):
    e = el.find(path, NS)
    return e.text.strip() if e is not None and e.text and e.text.strip() else None


def dec(x):
    try:
        return Decimal(str(x).replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


def norm_iban(x):
    return re.sub(r"\s+", "", x or "").upper()


def norm_sklic(x):
    s = re.sub(r"\s+", "", x or "").upper()
    return s[2:] if s.startswith("SI") else s


def varno_nalozi(pot):
    data = Path(pot).read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError(f"datoteka je prevelika ({len(data)} bajtov, največ {MAX_BYTES})")
    if b"<!doctype" in data.lower() or b"<!entity" in data.lower():
        raise ValueError("datoteka vsebuje DOCTYPE/ENTITY (možen napad z entitetami): zavrnjeno")
    try:
        return ET.fromstring(data)
    except ET.ParseError as e:
        raise ValueError(f"XML ni berljiv: {e}")


def izlusci(root):
    m = root.find("e:M_INVOIC", NS)
    if m is None:
        raise ValueError("manjka M_INVOIC (to ni eSLOG račun)")
    r = {"st_racuna": t(m, "e:S_BGM/e:C_C106/e:D_1004"), "valuta": t(m, "e:G_SG7/e:S_CUX/e:C_C504/e:D_6345")}
    for d in m.findall("e:S_DTM", NS):
        k, v = t(d, "e:C_C507/e:D_2005"), t(d, "e:C_C507/e:D_2380")
        if k == "137":
            r["datum_racuna"] = v
    for g in m.findall("e:G_SG1", NS):
        if t(g, "e:S_RFF/e:C_C506/e:D_1153") == "PQ":
            r["sklic"] = t(g, "e:S_RFF/e:C_C506/e:D_1154")
    for g in m.findall("e:G_SG8", NS):
        for d in g.findall("e:S_DTM", NS):
            if t(d, "e:C_C507/e:D_2005") == "13":
                r["zapadlost"] = t(d, "e:C_C507/e:D_2380")
    for g in m.findall("e:G_SG2", NS):
        vloga = t(g, "e:S_NAD/e:D_3035")
        va = None
        for g3 in g.findall("e:G_SG3", NS):
            if t(g3, "e:S_RFF/e:C_C506/e:D_1153") == "VA":
                va = t(g3, "e:S_RFF/e:C_C506/e:D_1154")
        if vloga == "SE":
            r["dobavitelj_ddv"] = va
            for f in g.findall("e:S_FII", NS):
                if t(f, "e:D_3035") == "RB":
                    r["iban"] = t(f, "e:C_C078/e:D_3194")
        if vloga == "BY":
            r["kupec_ddv"] = va
    zneski = {}
    for g in m.findall("e:G_SG50", NS):
        zneski[t(g, "e:S_MOA/e:C_C516/e:D_5025")] = dec(t(g, "e:S_MOA/e:C_C516/e:D_5004"))
    r["zneski"] = zneski
    vsota = Decimal(0)
    stevilo = 0
    for g in m.findall("e:G_SG26", NS):
        for g27 in g.findall("e:G_SG27", NS):
            if t(g27, "e:S_MOA/e:C_C516/e:D_5025") == "203":
                vsota += dec(t(g27, "e:S_MOA/e:C_C516/e:D_5004")) or 0
                stevilo += 1
    r["vsota_postavk"], r["postavk"] = vsota, stevilo
    return r


def schema_koda(pot):
    p = subprocess.run([str(HERE / "validate.sh"), str(pot)], capture_output=True, text=True, timeout=60)
    return p.returncode, (p.stdout + p.stderr).strip()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("izvirnik")
    ap.add_argument("podatki")
    ap.add_argument("--kupec", default=str(HERE / "kupec.json"))
    a = ap.parse_args(argv)
    vrstice = []

    def rez(ok, ime, opis=""):
        vrstice.append((ok, ime, opis))
        print(f"  {'OK       ' if ok is True else 'NAPAKA   ' if ok is False else 'OPOZORILO'}  {ime}" + (f": {opis}" if opis and ok is not True else ""))

    try:
        podatki = json.loads(Path(a.podatki).read_text(encoding="utf-8"))
        root = varno_nalozi(a.izvirnik)
        x = izlusci(root)
    except (OSError, json.JSONDecodeError) as e:
        print(f"NAPAKA branja: {e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"NEVARNO/POKVARJENO: {e}")
        return 2

    koda, sporocilo = schema_koda(a.izvirnik)
    if koda == 2:
        print(f"NEPREVERJENO: {sporocilo}")
        return 3
    if koda != 0:
        print(f"NEVELJAVNO po eslog.xsd: {sporocilo.splitlines()[0] if sporocilo else ''}")
        return 2
    rez(True, "veljavno po eslog.xsd")

    z = x["zneski"]
    neto, ddv, bruto = z.get("389"), z.get("176"), z.get("388")
    if None in (neto, ddv, bruto):
        rez(False, "skupni zneski v XML (MOA 389, 176, 388)", f"manjkajo: {sorted(z)}")
    else:
        rez(abs(neto + ddv - bruto) <= TOL, "notranje: neto + DDV = bruto", f"{neto} + {ddv} != {bruto}")
        rez(abs(x["vsota_postavk"] - neto) <= TOL, "notranje: vsota postavk = skupni neto", f"{x['postavk']} postavk = {x['vsota_postavk']}, skupaj {neto}")

    napake_pdf = 0

    def primerjaj(ime, iz_xml, iz_pdf, norm=lambda s: s, opozorilo=False):
        nonlocal napake_pdf
        if iz_pdf in (None, ""):
            rez(None, f"PDF: {ime}", "v podatkih iz PDF-ja ni, ni mogoče primerjati")
            return
        ok = iz_xml is not None and norm(str(iz_xml)) == norm(str(iz_pdf))
        if not ok and not opozorilo:
            napake_pdf += 1
        rez(True if ok else (None if opozorilo else False), f"XML = PDF: {ime}", f"XML {iz_xml!r}, PDF {iz_pdf!r}")

    d = podatki.get("dobavitelj", {})
    primerjaj("št. računa", x.get("st_racuna"), podatki.get("st_racuna"), str.strip)
    primerjaj("datum računa", x.get("datum_racuna"), podatki.get("datum_racuna"))
    primerjaj("valuta", x.get("valuta"), podatki.get("valuta"), str.upper)
    primerjaj("ID za DDV dobavitelja", x.get("dobavitelj_ddv"), d.get("id_za_ddv"), lambda s: s.replace(" ", "").upper())
    primerjaj("IBAN dobavitelja", x.get("iban"), d.get("iban"), norm_iban)
    primerjaj("zapadlost", x.get("zapadlost"), podatki.get("zapadlost"), opozorilo=True)
    primerjaj("sklic", x.get("sklic"), podatki.get("sklic"), norm_sklic, opozorilo=True)
    sk = podatki.get("skupaj", {})
    for ime, vred in (("neto", neto), ("DDV", ddv), ("bruto", bruto)):
        pdf = dec(sk.get({"neto": "neto", "DDV": "ddv", "bruto": "bruto"}[ime]))
        if pdf is None:
            rez(None, f"PDF: skupaj {ime}", "v podatkih iz PDF-ja ni")
        else:
            ok = vred is not None and abs(vred - pdf) <= TOL
            napake_pdf += 0 if ok else 1
            rez(ok, f"XML = PDF: skupaj {ime}", f"XML {vred}, PDF {pdf}")

    kp = Path(a.kupec)
    kupec_id = None
    if kp.exists():
        try:
            kupec_id = json.loads(kp.read_text(encoding="utf-8")).get("id_za_ddv")
        except (OSError, json.JSONDecodeError):
            pass
    if not kupec_id or str(kupec_id).upper().startswith("VPISI"):
        rez(None, "kupec v XML je Amidas", "kupec.json ni izpolnjen, ni mogoče preveriti")
    else:
        ok = (x.get("kupec_ddv") or "").replace(" ", "").upper() == str(kupec_id).replace(" ", "").upper()
        napake_pdf += 0 if ok else 1
        rez(ok, "kupec v XML je Amidas (ID za DDV)", f"XML {x.get('kupec_ddv')!r}, pričakovano {kupec_id}")

    napake = sum(1 for ok, _, _ in vrstice if ok is False)
    print("REZULTAT: " + ("izvirni XML je v redu, priloži ga nespremenjenega" if napake == 0 else f"{napake} neskladij: ZASTAVICA, izvirnika ne prilagajaj"))
    return 0 if napake == 0 else (2 if any(ok is False and ime.startswith("notranje") for ok, ime, _ in vrstice) else 1)


if __name__ == "__main__":
    sys.exit(main())
