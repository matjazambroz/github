#!/usr/bin/env python3
"""Ustvari eSLOG 2.0 INVOIC XML za PREJETI račun (dobavitelj = prodajalec SE, Amidas = kupec BY).

Uporaba:
    ./ustvari_xml.py racun.json izhod.xml [--kupec kupec.json]

Vhod (JSON, glej primer-racun.json): podatki, ki jih je razpoznal Strateg. Zneske računa izračuna skripta iz postavk;
če JSON vsebuje "skupaj" (neto, ddv, bruto s PDF-ja), se morajo ujemati z izračunom; DDV se računa na vsoti osnov po stopnji
(ne po postavkah). Razlika v DDV do 0,02 pri eni sami stopnji (drugačno zaokroževanje dobavitelja) se razreši v korist PDF-ja; večja je napaka.

Izhodne kode: 0 = XML ustvarjen in veljaven proti eslog.xsd
              1 = napaka v vhodnih podatkih (nič ni zapisano)
              2 = XML zapisan, a NEPREVERJEN (manjka xmllint ali eslog.xsd)
              3 = XML zapisan, a validacija proti XSD pade
              4 = podatki kupca še niso izpolnjeni (kupec.json vsebuje VPISI...)
Samo standardna knjižnica Pythona. Struktura sledi vzorcu eslog/vzorec.xml; kode (npr. kategorija DDV) so predlog,
ki ga potrdi računovodski servis.
"""
import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = "urn:eslog:2.00"
TOL = Decimal("0.02")
CENT = Decimal("0.01")


class Napaka(Exception):
    pass


def q2(x):
    return Decimal(x).quantize(CENT, rounding=ROUND_HALF_UP)


def dec(v, polje):
    try:
        return Decimal(str(v).replace(",", "."))
    except Exception:
        raise Napaka(f"{polje}: ni število ({v!r})")


def fmt(d):
    return format(q2(d), "f")


def fmt_free(d):
    s = format(Decimal(d).normalize(), "f")
    return s


def datum(v, polje):
    try:
        return date.fromisoformat(str(v)).isoformat()
    except Exception:
        raise Napaka(f"{polje}: pričakujem LLLL-MM-DD ({v!r})")


def chunks(text, n, k):
    """Razreže besedilo na do k kosov po n znakov (eSLOG ima D_xxxx, D_xxxx_2 ...)."""
    text = (text or "").strip()
    if len(text) > n * k:
        raise Napaka(f"besedilo je predolgo (največ {n * k} znakov): {text[:30]}...")
    return [text[i:i + n] for i in range(0, len(text), n)] or [""]


class B:
    """Pomočnik za gradnjo elementov v imenskem prostoru eSLOG."""

    @staticmethod
    def el(parent, tag, text=None):
        e = ET.SubElement(parent, f"{{{NS}}}{tag}")
        if text is not None:
            e.text = str(text)
        return e


def dtm(parent, koda, d=None):
    s = B.el(parent, "S_DTM")
    c = B.el(s, "C_C507")
    B.el(c, "D_2005", koda)
    if d:
        B.el(c, "D_2380", d)


def rff(parent, koda, vrednost):
    s = B.el(parent, "S_RFF")
    c = B.el(s, "C_C506")
    B.el(c, "D_1153", koda)
    B.el(c, "D_1154", vrednost)


def moa(parent, koda, znesek):
    s = B.el(parent, "S_MOA")
    c = B.el(s, "C_C516")
    B.el(c, "D_5025", koda)
    B.el(c, "D_5004", fmt(znesek))


def tax(parent, kat, stopnja):
    s = B.el(parent, "S_TAX")
    B.el(s, "D_5283", "7")
    c = B.el(s, "C_C241")
    B.el(c, "D_5153", "VAT")
    c2 = B.el(s, "C_C243")
    B.el(c2, "D_5278", fmt_free(stopnja))
    B.el(s, "D_5305", kat)


def nad(parent, vloga, o, z_ddv_in_banka):
    g = B.el(parent, "G_SG2")
    s = B.el(g, "S_NAD")
    B.el(s, "D_3035", vloga)
    c80 = B.el(s, "C_C080")
    for i, kos in enumerate(chunks(o["naziv"], 70, 5)):
        B.el(c80, "D_3036" if i == 0 else f"D_3036_{i + 1}", kos)
    c59 = B.el(s, "C_C059")
    for i, kos in enumerate(chunks(o["naslov"], 35, 3)):
        B.el(c59, "D_3042" if i == 0 else f"D_3042_{i + 1}", kos)
    B.el(s, "D_3164", o["mesto"][:35])
    B.el(s, "D_3251", str(o["posta"])[:17])
    B.el(s, "D_3207", o.get("drzava", "SI"))
    if z_ddv_in_banka:
        if o.get("iban"):
            f = B.el(g, "S_FII")
            B.el(f, "D_3035", "RB")
            c78 = B.el(f, "C_C078")
            B.el(c78, "D_3194", o["iban"].replace(" ", "")[:35])
            B.el(c78, "D_3192", o["naziv"][:35])
            if o.get("bic"):
                c88 = B.el(f, "C_C088")
                B.el(c88, "D_3433", o["bic"][:11])
    if o.get("id_za_ddv"):
        g3 = B.el(g, "G_SG3")
        rff(g3, "VA", o["id_za_ddv"])


def poisci_manjka(v, pot=""):
    """Vrne pot prve vrednosti 'MANJKA' (Strateg tako označi podatek, ki ga ni); ta beseda ne sme v XML."""
    if isinstance(v, str):
        return pot if v.strip().upper().startswith("MANJKA") else None
    if isinstance(v, dict):
        items = v.items()
    elif isinstance(v, list):
        items = enumerate(v)
    else:
        return None
    for k, x in items:
        r = poisci_manjka(x, f"{pot}.{k}" if pot else str(k))
        if r:
            return r
    return None


def preveri_vhod(r):
    m = poisci_manjka(r)
    if m:
        raise Napaka(f"'{m}' je MANJKA: neobvezno polje izpusti iz JSON-a, pri obveznem računa ne pretvarjaj (ZASTAVICA)")
    for k in ("st_racuna", "datum_racuna", "valuta", "dobavitelj", "postavke"):
        if k not in r or r[k] in (None, "", []):
            raise Napaka(f"manjka polje '{k}'")
    d = r["dobavitelj"]
    for k in ("naziv", "naslov", "mesto", "posta"):
        if not d.get(k):
            raise Napaka(f"dobavitelj.{k} manjka")
    if len(r["valuta"]) != 3:
        raise Napaka("valuta mora biti 3-črkovna koda (EUR)")


def izracun(r):
    vrstice = []
    for i, p in enumerate(r["postavke"], 1):
        kol = dec(p["kolicina"], f"postavke[{i}].kolicina")
        cena = dec(p["cena_neto"], f"postavke[{i}].cena_neto")
        stopnja = dec(p.get("stopnja_ddv", 0), f"postavke[{i}].stopnja_ddv")
        neto = q2(kol * cena)
        if "neto" in p:
            dan = q2(dec(p["neto"], f"postavke[{i}].neto"))
            if abs(dan - neto) > TOL:
                raise Napaka(f"postavke[{i}]: neto {dan} se ne ujema s količina x cena = {neto}")
            neto = dan
        kat = p.get("kategorija") or ("S" if stopnja > 0 else "E")
        ddv = q2(neto * stopnja / 100)
        vrstice.append(dict(opis=p["opis"], kol=kol, cena=cena, enota=p.get("enota", "C62"),
                            neto=neto, ddv=ddv, stopnja=stopnja, kat=kat))
    # Pravilo DDV: ddv se računa na VSOTI osnov po stopnji (kategoriji), ne kot vsota zaokroženih DDV po postavkah.
    # (Vsota po postavkah se lahko razlikuje za nekaj centov; račun in XML morata imeti DDV od osnove.)
    # Zneski DDV pri postavkah (MOA 124/38) so informativni in se lahko razlikujejo od deleža v skupini.
    osnove = {}
    for v in vrstice:
        osnove[(v["kat"], v["stopnja"])] = osnove.get((v["kat"], v["stopnja"]), Decimal(0)) + v["neto"]
    skupine = {k: [osn, q2(osn * k[1] / 100)] for k, osn in osnove.items()}
    neto = sum((v["neto"] for v in vrstice), Decimal(0))
    ddv = sum((s[1] for s in skupine.values()), Decimal(0))
    sk = r.get("skupaj")
    # Dobavitelj lahko DDV zaokroži drugače (npr. po postavkah). Če je razlika samo zaokroževalna (do 0,02) in je ena sama
    # skupina, v XML prepišemo DDV s PDF-ja: XML mora ustrezati računu. Pri večji razliki je to napaka (možna napaka pri branju).
    if sk and "ddv" in sk:
        pdf_ddv = q2(dec(sk["ddv"], "skupaj.ddv"))
        if pdf_ddv != ddv and abs(pdf_ddv - ddv) <= TOL and len(skupine) == 1:
            kljuc = next(iter(skupine))
            skupine[kljuc][1] = pdf_ddv
            ddv = pdf_ddv
    bruto = neto + ddv
    if sk:
        for ime, izr in (("neto", neto), ("ddv", ddv), ("bruto", bruto)):
            if ime in sk and abs(q2(dec(sk[ime], f"skupaj.{ime}")) - izr) > Decimal("0.005"):
                raise Napaka(f"skupaj.{ime} s PDF ({sk[ime]}) se ne ujema z izračunom ({izr})")
    return vrstice, skupine, neto, ddv, bruto


def zgradi(r, kupec):
    vrstice, skupine, neto, ddv, bruto = izracun(r)
    st = str(r["st_racuna"])
    d_rac = datum(r["datum_racuna"], "datum_racuna")

    root = ET.Element(f"{{{NS}}}Invoice")
    m = B.el(root, "M_INVOIC")
    m.set("Id", "data")

    unh = B.el(m, "S_UNH")
    B.el(unh, "D_0062", st[:14])
    c9 = B.el(unh, "C_S009")
    for t, v in (("D_0065", "INVOIC"), ("D_0052", "D"), ("D_0054", "01B"), ("D_0051", "UN")):
        B.el(c9, t, v)

    bgm = B.el(m, "S_BGM")
    B.el(B.el(bgm, "C_C002"), "D_1001", "380")
    B.el(B.el(bgm, "C_C106"), "D_1004", st[:70])

    dtm(m, "137", d_rac)
    if r.get("datum_storitve"):
        dtm(m, "35", datum(r["datum_storitve"], "datum_storitve"))

    if r.get("opomba"):
        f = B.el(m, "S_FTX")
        B.el(f, "D_4451", "AAI")
        c108 = B.el(f, "C_C108")
        for i, kos in enumerate(chunks(r["opomba"], 512, 5)):
            B.el(c108, "D_4440" if i == 0 else f"D_4440_{i + 1}", kos)

    if r.get("sklic"):
        rff(B.el(m, "G_SG1"), "PQ", str(r["sklic"])[:70])

    nad(m, "BY", kupec, z_ddv_in_banka=False)
    nad(m, "SE", r["dobavitelj"], z_ddv_in_banka=True)

    cux = B.el(B.el(m, "G_SG7"), "S_CUX")
    c504 = B.el(cux, "C_C504")
    B.el(c504, "D_6347", "2")
    B.el(c504, "D_6345", r["valuta"].upper())

    if r.get("zapadlost"):
        g8 = B.el(m, "G_SG8")
        B.el(B.el(g8, "S_PAT"), "D_4279", "1")
        dtm(g8, "13", datum(r["zapadlost"], "zapadlost"))

    for i, v in enumerate(vrstice, 1):
        g26 = B.el(m, "G_SG26")
        B.el(B.el(g26, "S_LIN"), "D_1082", str(i))
        imd = B.el(g26, "S_IMD")
        B.el(imd, "D_7077", "F")
        c273 = B.el(imd, "C_C273")
        for j, kos in enumerate(chunks(v["opis"], 256, 2)):
            B.el(c273, "D_7008" if j == 0 else "D_7008_2", kos)
        qc = B.el(B.el(g26, "S_QTY"), "C_C186")
        B.el(qc, "D_6063", "47")
        B.el(qc, "D_6060", fmt_free(v["kol"]))
        B.el(qc, "D_6411", v["enota"])
        moa(B.el(g26, "G_SG27"), "203", v["neto"])
        moa(B.el(g26, "G_SG27"), "38", v["neto"] + v["ddv"])
        pri = B.el(B.el(g26, "G_SG29"), "S_PRI")
        pc = B.el(pri, "C_C509")
        B.el(pc, "D_5125", "AAA")
        B.el(pc, "D_5118", fmt_free(v["cena"]))
        g34 = B.el(g26, "G_SG34")
        tax(g34, v["kat"], v["stopnja"])
        moa(g34, "125", v["neto"])
        moa(g34, "124", v["ddv"])

    B.el(B.el(m, "S_UNS"), "D_0081", "D")
    for koda, znesek in (("79", neto), ("389", neto), ("388", bruto), ("9", bruto), ("176", ddv)):
        moa(B.el(m, "G_SG50"), koda, znesek)
    for (kat, stopnja), (osnova, dv) in skupine.items():
        g52 = B.el(m, "G_SG52")
        tax(g52, kat, stopnja)
        moa(g52, "125", osnova)
        moa(g52, "124", dv)

    ET.register_namespace("", NS)
    ET.indent(root, space="\t")
    return ET.ElementTree(root), (neto, ddv, bruto)


def validiraj(pot):
    try:
        p = subprocess.run([str(HERE / "validate.sh"), str(pot)], capture_output=True, text=True, timeout=60)
    except Exception as e:  # noqa: BLE001
        return 2, str(e)
    return p.returncode, (p.stdout + p.stderr).strip()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vhod")
    ap.add_argument("izhod")
    ap.add_argument("--kupec", default=str(HERE / "kupec.json"))
    a = ap.parse_args(argv)
    try:
        r = json.loads(Path(a.vhod).read_text(encoding="utf-8"))
        kp = Path(a.kupec)
        if not kp.exists():
            raise Napaka(f"manjka {kp.name}: kopiraj kupec.primer.json v kupec.json in vpiši podatke Amidas")
        kupec = json.loads(kp.read_text(encoding="utf-8"))
        if any(str(v).upper().startswith("VPISI") for v in kupec.values()):
            print("Podatki kupca (Amidas) v kupec.json še niso izpolnjeni (VPISI...).", file=sys.stderr)
            return 4
        preveri_vhod(r)
        drevo, (neto, ddv, bruto) = zgradi(r, kupec)
    except Napaka as e:
        print(f"NAPAKA vhoda: {e}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError) as e:
        print(f"NAPAKA branja: {e}", file=sys.stderr)
        return 1
    drevo.write(a.izhod, encoding="UTF-8", xml_declaration=True)
    koda, sporocilo = validiraj(a.izhod)
    print(f"neto {fmt(neto)}  ddv {fmt(ddv)}  bruto {fmt(bruto)}  ->  {a.izhod}")
    if koda == 0:
        print("VELJAVEN proti eslog.xsd")
        return 0
    print(("NEPREVERJEN: " if koda == 2 else "NEVELJAVEN: ") + sporocilo, file=sys.stderr)
    return 2 if koda == 2 else 3


if __name__ == "__main__":
    sys.exit(main())
