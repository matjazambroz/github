"""Testi za preveri_izvirni_xml.py in pripravi_xml.py (izvirni XML izvajalca ali generiran). Zagon: python3 -m unittest -v test_preveri_izvirni_xml"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import pripravi_xml as P
import preveri_izvirni_xml as V

HERE = Path(__file__).resolve().parent
FX = HERE / "fixtures"
KUPEC_TEST = dict(naziv="Testno podjetje d.o.o. (IZMIŠLJENO)", naslov="Testna cesta 5", mesto="Maribor", posta="2000",
                  drzava="SI", id_za_ddv="SI87654321")


def podatki():
    return json.loads((FX / "izvirnik-eracuni-podatki.json").read_text(encoding="utf-8"))


@unittest.skipUnless(shutil.which("xmllint"), "xmllint ni nameščen")
class Testi(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.kupec = self.tmp / "kupec.json"
        self.kupec.write_text(json.dumps(KUPEC_TEST), encoding="utf-8")
        self.xml = (FX / "izvirnik-eracuni.xml").read_text(encoding="utf-8")

    def preveri(self, p=None, xml=None, kupec=None):
        pp = self.tmp / "podatki.json"
        pp.write_text(json.dumps(p or podatki()), encoding="utf-8")
        xx = self.tmp / "izvirnik.xml"
        if isinstance(xml, bytes):
            xx.write_bytes(xml)
        else:
            xx.write_text(xml if xml is not None else self.xml, encoding="utf-8")
        return V.main([str(xx), str(pp), "--kupec", str(kupec or self.kupec)])

    def test_pravi_izvirnik_je_v_redu(self):
        self.assertEqual(self.preveri(), 0)

    def test_neskladen_znesek_s_pdf(self):
        p = podatki()
        p["skupaj"]["bruto"] = "176.73"
        self.assertEqual(self.preveri(p), 1)

    def test_neskladen_iban(self):
        p = podatki()
        p["dobavitelj"]["iban"] = "SI56 1111 1111 1111 111"
        self.assertEqual(self.preveri(p), 1)

    def test_neskladna_stevilka_racuna(self):
        p = podatki()
        p["st_racuna"] = "2026-00008"
        self.assertEqual(self.preveri(p), 1)

    def test_racun_naslovljen_na_drugega_kupca(self):
        self.kupec.write_text(json.dumps({"id_za_ddv": "SI11111111"}), encoding="utf-8")
        self.assertEqual(self.preveri(), 1)

    def test_manjkajoci_neobvezni_podatki_iz_pdf_niso_napaka(self):
        p = podatki()
        for k in ("zapadlost", "sklic"):
            p.pop(k)
        self.assertEqual(self.preveri(p), 0)

    def test_notranje_neskladen_xml(self):
        # skupni bruto (MOA 388) ne ustreza neto + DDV
        import re
        xml, n = re.subn(r"(<D_5025>388</D_5025>\s*<D_5004>)176\.72(</D_5004>)", r"\g<1>176.99\g<2>", self.xml)
        self.assertEqual(n, 1, "test mora spremeniti natanko skupni bruto (MOA 388)")
        self.assertEqual(self.preveri(xml=xml), 2)

    def test_neveljavno_po_shemi(self):
        xml = self.xml.replace("<D_0065>INVOIC</D_0065>", "<D_0065>INVOIC</D_0065><NAPAKA/>", 1)
        self.assertEqual(self.preveri(xml=xml), 2)

    def test_entitete_so_zavrnjene_brez_razsiritve(self):
        bomba = ('<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY a "aaaaaaaaaa"><!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;">]>'
                 '<Invoice xmlns="urn:eslog:2.00"><M_INVOIC>&b;</M_INVOIC></Invoice>')
        self.assertEqual(self.preveri(xml=bomba), 2)

    def test_ni_eslog_racun(self):
        self.assertEqual(self.preveri(xml='<?xml version="1.0"?><nekaj><drugega/></nekaj>'), 2)

    def test_prevelika_datoteka(self):
        self.assertEqual(self.preveri(xml=self.xml.encode("utf-8") + b" " * (V.MAX_BYTES + 1)), 2)

    def test_nebranljiv_xml(self):
        self.assertEqual(self.preveri(xml="<Invoice><nezaprt>"), 2)

    # --- pripravi_xml.py: izvirnik ali generiran ---
    def pripravi(self, izvirnik=True, p=None, xml=None):
        pp = self.tmp / "podatki.json"
        pp.write_text(json.dumps(p or podatki()), encoding="utf-8")
        args = [str(pp), str(self.tmp / "izhod.xml"), "--kupec", str(self.kupec)]
        if izvirnik:
            xx = self.tmp / "izvirnik.xml"
            xx.write_text(xml if xml is not None else self.xml, encoding="utf-8")
            args += ["--izvirnik", str(xx)]
        return P.main(args), self.tmp / "izhod.xml"

    def test_izvirnik_se_prekopira_nespremenjen(self):
        koda, izhod = self.pripravi()
        self.assertEqual(koda, 0)
        self.assertEqual(izhod.read_bytes(), (FX / "izvirnik-eracuni.xml").read_bytes())

    def test_brez_izvirnika_se_generira(self):
        koda, izhod = self.pripravi(izvirnik=False)
        self.assertEqual(koda, 0)
        self.assertIn("<D_1004>2026-00007</D_1004>", izhod.read_text(encoding="utf-8"))

    def test_neskladen_izvirnik_se_ne_zamenja_tiho_z_generiranim(self):
        p = podatki()
        p["skupaj"]["bruto"] = "999.99"
        koda, izhod = self.pripravi(p=p)
        self.assertEqual(koda, 10)
        self.assertFalse(izhod.exists())

    def test_neveljaven_izvirnik_ni_zapisan(self):
        koda, izhod = self.pripravi(xml=self.xml.replace("<D_0065>INVOIC</D_0065>", "<D_0065>INVOIC</D_0065><NAPAKA/>", 1))
        self.assertEqual(koda, 11)
        self.assertFalse(izhod.exists())

    def test_napaka_vhoda_pri_generiranju(self):
        p = podatki()
        p["skupaj"]["bruto"] = "1.00"
        koda, _ = self.pripravi(izvirnik=False, p=p)
        self.assertEqual(koda, 20)

    def test_kupec_ni_izpolnjen(self):
        self.kupec.write_text(json.dumps({"naziv": "VPISI ime", "naslov": "VPISI", "mesto": "VPISI", "posta": "VPISI", "id_za_ddv": "VPISI"}), encoding="utf-8")
        koda, _ = self.pripravi(izvirnik=False)
        self.assertEqual(koda, 30)

    def test_fixture_vsebuje_samo_izmisljene_podatke(self):
        """Preverjanje po vzorcih (brez pravih vrednosti): vsi e-nasloviji, ID-ji za DDV, IBAN-i in telefoni morajo biti izmišljeni."""
        import re
        self.assertTrue(all(e.endswith("@example.si") for e in re.findall(r"[\w.+-]+@[\w.-]+", self.xml)))
        self.assertEqual(set(re.findall(r"\bSI\d{8}\b", self.xml)), {"SI12345678", "SI87654321"})
        self.assertEqual(set(re.findall(r"\bSI56\d{15}\b", self.xml)), {"SI56000000000000099"})
        self.assertEqual(set(re.findall(r"<D_3148>(\d{9})</D_3148>", self.xml)), {"040000000"})
        self.assertIn("IZMIŠLJENO", self.xml)


if __name__ == "__main__":
    unittest.main()
