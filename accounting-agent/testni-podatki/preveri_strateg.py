#!/usr/bin/env python3
"""Primerja izhod agenta racuni-strateg z pričakovanimi rezultati za izmišljene račune (pricakovano.json).

Uporaba:  python3 preveri_strateg.py strateg-izhod.json [--pricakovano pricakovano.json]
Preverja podatke (zneski, številka računa, dobavitelj), konto, zastavice, matematiko in izhodno kodo skripte
eslog/ustvari_xml.py (s testnim kupcem). Izhod: 0 = vse v redu, 1 = vsaj ena napaka.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKRIPTA = HERE.parent / "eslog" / "ustvari_xml.py"


def pot_vrednost(d, pot):
    for k in pot.split("."):
        if isinstance(d, list) and k.isdigit() and int(k) < len(d):
            d = d[int(k)]
        elif isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return None
    return d


def enako(a, b):
    try:
        return abs(Decimal(str(a).replace(",", ".")) - Decimal(str(b).replace(",", "."))) <= Decimal("0.005")
    except (InvalidOperation, ValueError):
        return str(a).strip() == str(b).strip()


def xml_koda(podatki):
    with tempfile.TemporaryDirectory() as t:
        vhod, izhod = Path(t) / "racun.json", Path(t) / "izhod.xml"
        vhod.write_text(json.dumps(podatki), encoding="utf-8")
        p = subprocess.run([sys.executable, str(SKRIPTA), str(vhod), str(izhod), "--kupec", str(HERE / "kupec-testni.json")],
                           capture_output=True, text=True, timeout=60)
        return p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1:] or [""]


def preveri(racun, ocak):
    rez = []
    p = racun.get("podatki", {})
    for pot, pricakovano in ocak.get("podatki", {}).items():
        dobljeno = pot_vrednost(p, pot)
        rez.append((f"podatki.{pot}", dobljeno is not None and enako(dobljeno, pricakovano), f"pričakovano {pricakovano}, dobljeno {dobljeno}"))
    if "konto" in ocak:
        k = str(racun.get("konto_predlog", ""))
        rez.append(("konto_predlog", k.startswith(ocak["konto"]), f"pričakovano {ocak['konto']}, dobljeno {k!r}"))
    zast = [str(z) for z in racun.get("zastavice", [])]
    if ocak.get("zastavice_prazne"):
        rez.append(("zastavice prazne", not zast, f"dobljeno {zast}"))
    if ocak.get("zastavice_vsebuje"):
        zl = " ".join(zast).lower()
        rez.append(("zastavica vsebuje eno od " + "/".join(ocak["zastavice_vsebuje"]),
                    any(s in zl for s in ocak["zastavice_vsebuje"]), f"dobljeno {zast}"))
    if "matematika" in ocak:
        m = racun.get("preverjanja", {}).get("matematika")
        rez.append(("preverjanja.matematika", m == ocak["matematika"], f"pričakovano {ocak['matematika']}, dobljeno {m}"))
    if ocak.get("xml_koda") is not None:
        koda, zadnja = xml_koda(p)
        rez.append(("ustvari_xml.py izhodna koda", koda == ocak["xml_koda"], f"pričakovano {ocak['xml_koda']}, dobljeno {koda} {zadnja[0]}"))
    return rez


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("izhod")
    ap.add_argument("--pricakovano", default=str(HERE / "pricakovano.json"))
    a = ap.parse_args()
    izhod = json.loads(Path(a.izhod).read_text(encoding="utf-8"))
    if isinstance(izhod, dict):
        izhod = [izhod]
    ocakovano = json.loads(Path(a.pricakovano).read_text(encoding="utf-8"))
    po_st = {r.get("podatki", {}).get("st_racuna"): r for r in izhod}
    napak = 0
    for st, ocak in ocakovano.items():
        print(f"\n== {ocak['datoteka']} (št. {st})")
        if st not in po_st:
            print("  NAPAKA  računa ni v Strategovem izhodu")
            napak += 1
            continue
        for ime, ok, opis in preveri(po_st[st], ocak):
            print(f"  {'OK    ' if ok else 'NAPAKA'}  {ime}" + ("" if ok else f": {opis}"))
            napak += 0 if ok else 1
    nepricakovani = [s for s in po_st if s not in ocakovano]
    if nepricakovani:
        print(f"\nOpozorilo: v izhodu so računi, ki jih preizkus ne pozna: {nepricakovani}")
    print(f"\nSKUPAJ: {'VSE V REDU' if napak == 0 else str(napak) + ' napak'}")
    return 0 if napak == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
