#!/usr/bin/env python3
"""Enotna vstopna točka za XML računa: uporabi IZVIRNI XML izvajalca, če ga je priložil; sicer ga ustvari (ustvari_xml.py).

Uporaba:  ./pripravi_xml.py racun.json izhod.xml [--izvirnik izvirnik.xml] [--kupec kupec.json]
  racun.json = `podatki` iz Strategovega izhoda (podatki iz PDF-ja)
  --izvirnik = XML, ki ga je izvajalec priložil (če ga ni, parametra ne podaj)

Pravilo: obstaja izvirnik -> preveri ga (preveri_izvirni_xml.py) in, če je v redu, ga prekopiraj NESPREMENJENEGA.
         Neskladen/neveljaven izvirnik se NE zamenja tiho z generiranim: račun gre z zastavico, odloči uporabnik.
         Izvirnika ni -> ustvari ga ustvari_xml.py.
Izpiše vrstico `VIR=IZVIRNIK|GENERIRAN|NI`. Izhodne kode:
   0  XML pripravljen in veljaven proti shemi
  10  izvirnik se ne ujema s PDF/podatki (ZASTAVICA, izhod ni zapisan)
  11  izvirnik je neveljaven po shemi, pokvarjen ali nevaren (ZASTAVICA, izhod ni zapisan)
  12  XML zapisan, a NEPREVERJEN (manjka xmllint ali eslog.xsd): osnutek z zadevo [XML NEPREVERJEN]
  20  napaka v vhodnih podatkih (generiranje; ZASTAVICA)
  21  generirani XML ni veljaven proti shemi (ZASTAVICA)
  30  podatki kupca (kupec.json) še niso izpolnjeni: ustavi in obvesti uporabnika
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def poganjaj(skripta, *args):
    p = subprocess.run([sys.executable, str(HERE / skripta), *map(str, args)], capture_output=True, text=True, timeout=120)
    return p.returncode, (p.stdout + p.stderr).rstrip()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("podatki")
    ap.add_argument("izhod")
    ap.add_argument("--izvirnik")
    ap.add_argument("--kupec", default=str(HERE / "kupec.json"))
    a = ap.parse_args(argv)

    if a.izvirnik:
        koda, besedilo = poganjaj("preveri_izvirni_xml.py", a.izvirnik, a.podatki, "--kupec", a.kupec)
        print(besedilo)
        if koda == 1:
            print("VIR=IZVIRNIK (zavrnjen: neskladje s PDF)")
            return 10
        if koda == 2:
            print("VIR=IZVIRNIK (zavrnjen: neveljaven/nevaren)")
            return 11
        if koda in (0, 3):
            shutil.copyfile(a.izvirnik, a.izhod)  # nespremenjen izvirnik (bajt za bajtom)
            print("VIR=IZVIRNIK")
            return 0 if koda == 0 else 12
        print(f"NEPRICAKOVANA koda preverjalnika izvirnika: {koda}")
        return 11

    koda, besedilo = poganjaj("ustvari_xml.py", a.podatki, a.izhod, "--kupec", a.kupec)
    print(besedilo)
    print("VIR=" + ("GENERIRAN" if koda in (0, 2, 3) else "NI"))
    return {0: 0, 1: 20, 2: 12, 3: 21, 4: 30}.get(koda, 20)


if __name__ == "__main__":
    sys.exit(main())
