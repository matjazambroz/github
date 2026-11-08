"""Testi za ustvari_xml.py. Zagon: python3 -m unittest -v test_ustvari_xml  (v mapi eslog/). Potreben xmllint."""
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import ustvari_xml as U

HERE = Path(__file__).resolve().parent
KUPEC = dict(naziv="Testno podjetje d.o.o.", naslov="Testna cesta 5", mesto="Maribor", posta="2000",
             drzava="SI", id_za_ddv="SI87654321")


def primer():
    return json.loads((HERE / "primer-racun.json").read_text(encoding="utf-8"))


@unittest.skipUnless(shutil.which("xmllint"), "xmllint ni nameščen")
class Testi(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "kupec.json").write_text(json.dumps(KUPEC), encoding="utf-8")

    def zazeni(self, racun, kupec=None):
        vhod = self.tmp / "racun.json"
        vhod.write_text(json.dumps(racun), encoding="utf-8")
        izhod = self.tmp / "izhod.xml"
        koda = U.main([str(vhod), str(izhod), "--kupec", str(kupec or self.tmp / "kupec.json")])
        return koda, izhod

    def test_osnovni_racun_je_veljaven(self):
        koda, izhod = self.zazeni(primer())
        self.assertEqual(koda, 0)
        self.assertTrue(izhod.exists())

    def test_neujemanje_skupnega_zneska_je_napaka_in_nic_ne_zapise(self):
        r = primer()
        r["skupaj"]["bruto"] = "190.00"
        koda, izhod = self.zazeni(r)
        self.assertEqual(koda, 1)
        self.assertFalse(izhod.exists())

    def test_neujemanje_neto_postavke(self):
        r = primer()
        r["postavke"][0]["neto"] = "99.00"
        self.assertEqual(self.zazeni(r)[0], 1)

    def test_manjka_obvezno_polje(self):
        r = primer()
        del r["dobavitelj"]["naziv"]
        self.assertEqual(self.zazeni(r)[0], 1)

    def test_kupec_s_placeholderji(self):
        koda, izhod = self.zazeni(primer(), kupec=HERE / "kupec.primer.json")
        self.assertEqual(koda, 4)
        self.assertFalse(izhod.exists())

    def test_posebni_znaki_in_dolga_imena(self):
        r = primer()
        r["dobavitelj"]["naziv"] = "Šumnik & Čeh <prevajanje> d.o.o. " + "x" * 80
        r["postavke"][0]["opis"] = "Prevod \"A&B\" <test> " + "č" * 300
        koda, izhod = self.zazeni(r)
        self.assertEqual(koda, 0)
        vsebina = izhod.read_text(encoding="utf-8")
        self.assertIn("Šumnik &amp; Čeh &lt;prevajanje&gt;", vsebina)
        self.assertIn("<D_3036_2>", vsebina)
        self.assertIn("<D_7008_2>", vsebina)

    def test_predolgo_ime_pade(self):
        r = primer()
        r["dobavitelj"]["naziv"] = "a" * 400
        self.assertEqual(self.zazeni(r)[0], 1)

    def test_brez_ddv_dobi_kategorijo_e(self):
        r = primer()
        for p in r["postavke"]:
            p["stopnja_ddv"] = 0
        r["skupaj"] = {"neto": "150.00", "ddv": "0.00", "bruto": "150.00"}
        r["dobavitelj"].pop("id_za_ddv")
        koda, izhod = self.zazeni(r)
        self.assertEqual(koda, 0)
        self.assertIn("<D_5305>E</D_5305>", izhod.read_text(encoding="utf-8"))

    def test_mesane_stopnje_dajo_dve_skupini(self):
        r = primer()
        r["postavke"][1]["stopnja_ddv"] = 9.5
        r.pop("skupaj")
        koda, izhod = self.zazeni(r)
        self.assertEqual(koda, 0)
        self.assertEqual(izhod.read_text(encoding="utf-8").count("<G_SG52>"), 2)

    def test_zaokrozevanje_pol_navzgor(self):
        self.assertEqual(U.q2("0.125"), U.Decimal("0.13"))
        self.assertEqual(U.q2("2.675"), U.Decimal("2.68"))

    def test_validacija_res_zavrne_pokvarjen_xml(self):
        koda, izhod = self.zazeni(primer())
        pokvarjen = izhod.read_text(encoding="utf-8").replace("<D_0065>INVOIC</D_0065>", "<D_0065>INVOIC</D_0065><NAPAKA/>")
        pot = self.tmp / "pokvarjen.xml"
        pot.write_text(pokvarjen, encoding="utf-8")
        self.assertNotEqual(subprocess.run([str(HERE / "validate.sh"), str(pot)], capture_output=True).returncode, 0)

    def test_strategov_primer_deluje_v_skripti(self):
        """Pogodba: `podatki` iz Strategovega izhoda je neposreden vhod skripte (eslog/preslikava.md)."""
        strateg = json.loads((HERE / "strateg-primer.json").read_text(encoding="utf-8"))
        for racun in strateg:
            for kljuc in ("racun_id", "prejeto", "xml_izvirnik", "podatki", "preverjanja", "konto_predlog", "zastavice", "zaupanje"):
                self.assertIn(kljuc, racun)
            koda, izhod = self.zazeni(racun["podatki"])
            self.assertEqual(koda, 0)

    def test_niz_manjka_je_zavrnjen(self):
        for polje in ("iban", "id_za_ddv", "naziv"):
            r = primer()
            r["dobavitelj"][polje] = "MANJKA"
            self.assertEqual(self.zazeni(r)[0], 1, polje)
        r = primer()
        r["sklic"] = "MANJKA"
        self.assertEqual(self.zazeni(r)[0], 1)

    # --- DDV po osnovi, ne po postavkah (napaka, najdena na pravem računu: vsota po postavkah je dala +0,02) ---
    NETO = ["15.13", "69.99", "13.12", "41.22", "12.63", "26.81", "52.44"]  # izmišljeno; vsota 231,34

    def racun_zaokrozevanje(self, ddv_pdf, bruto_pdf):
        r = primer()
        r["postavke"] = [{"opis": f"Postavka {i}", "kolicina": 1, "cena_neto": n, "stopnja_ddv": 22} for i, n in enumerate(self.NETO, 1)]
        r["skupaj"] = {"neto": "231.34", "ddv": ddv_pdf, "bruto": bruto_pdf}
        return r

    def test_ddv_je_na_vsoti_osnov_in_ne_na_vsoti_postavk(self):
        # vsota zaokroženih DDV po postavkah = 50,91; DDV od osnove 231,34 x 22 % = 50,89
        koda, izhod = self.zazeni(self.racun_zaokrozevanje("50.89", "282.23"))
        self.assertEqual(koda, 0)
        xml = izhod.read_text(encoding="utf-8")
        self.assertIn("<D_5004>50.89</D_5004>", xml)
        self.assertIn("<D_5004>282.23</D_5004>", xml)
        self.assertNotIn("<D_5004>50.91</D_5004>", xml.split("<S_UNS>")[1])

    def test_zaokrozevalna_razlika_dobavitelja_se_razresi_v_korist_pdf(self):
        # dobavitelj je DDV sešteval po postavkah (50,91): ena stopnja, razlika 0,02 -> XML ima znesek s PDF-ja
        koda, izhod = self.zazeni(self.racun_zaokrozevanje("50.91", "282.25"))
        self.assertEqual(koda, 0)
        xml = izhod.read_text(encoding="utf-8")
        self.assertIn("<D_5004>282.25</D_5004>", xml)
        self.assertIn("<D_5004>50.91</D_5004>", xml.split("<S_UNS>")[1])

    def test_vecja_razlika_ddv_je_napaka(self):
        koda, izhod = self.zazeni(self.racun_zaokrozevanje("50.92", "282.26"))
        self.assertEqual(koda, 1)
        self.assertFalse(izhod.exists())

    def test_pri_vec_stopnjah_se_razlika_ne_razresuje_samodejno(self):
        r = primer()
        r["postavke"][1]["stopnja_ddv"] = 9.5   # 90,00 x 22 % + 60,00 x 9,5 % = 19,80 + 5,70 = 25,50
        r["skupaj"] = {"neto": "150.00", "ddv": "25.51", "bruto": "175.51"}
        self.assertEqual(self.zazeni(r)[0], 1)
        r["skupaj"] = {"neto": "150.00", "ddv": "25.50", "bruto": "175.50"}
        self.assertEqual(self.zazeni(r)[0], 0)

    def test_kupec_json_je_izpolnjen(self):
        """Podatki Amidas v eslog/kupec.json morajo biti izpolnjeni (brez VPISI) in v obliki, ki jo skripta potrebuje."""
        kupec = json.loads((HERE / "kupec.json").read_text(encoding="utf-8"))
        for k in ("naziv", "naslov", "mesto", "posta", "drzava", "id_za_ddv"):
            self.assertTrue(kupec.get(k), k)
        self.assertFalse(any(str(v).upper().startswith("VPISI") for v in kupec.values()))
        import re
        self.assertRegex(kupec["id_za_ddv"], r"^SI\d{8}$")

    def test_datum_v_napacni_obliki(self):
        r = primer()
        r["datum_racuna"] = "5. 11. 2026"
        self.assertEqual(self.zazeni(r)[0], 1)


if __name__ == "__main__":
    unittest.main()
