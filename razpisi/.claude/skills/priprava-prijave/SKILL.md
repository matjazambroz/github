---
name: priprava-prijave
description: Orkestrira pripravo prijave na razpis: analiza, osnutek, ponudba, pregled. Uporabi, ko uporabnik želi pripraviti prijavo za razpis v mapi vhod/.
---
Argument: ime mape razpisa v `razpisi/vhod/`.

0. Priprava datotek (agenti Read ne bere ZIP, DOCX in XLSX). Za `vhod/<razpis>/` in `viri/`:
   - razpakiraj vse ZIP-e v `razpakirano/<ime-arhiva>/` (podmapa ob datoteki, ena mapa na arhiv; razpakiraj tudi ZIP-e znotraj ZIP-ov);
   - pretvori vse DOCX in XLSX (tudi tiste iz `razpakirano/`) v besedilne datoteke `.md` v `besedilo/`. Pri XLSX zapiši vrednosti in formule celic po listih; oblikovanje se izgubi;
   - PDF in XML pustita kot sta, Read ju bere neposredno;
   - uporabi orodja, ki so na voljo (PowerShell `Expand-Archive`, Python z `python-docx`/`openpyxl`, `pandoc`); če nobeno ne deluje, to sporoči in vprašaj uporabnika;
   - preskoči datoteke, ki so že pretvorjene in novejše od izvirnika;
   - na koncu izpiši seznam pretvorjenih datotek in tistih, ki jih ni bilo mogoče pretvoriti.
1. Zaženi samo agenta `analitik-razpisa` in počakaj, da se konča. Preveri, da `izhod/<razpis>/zahteve.md` obstaja in ni prazen. Do takrat NE zaženi nobenega drugega agenta.
2. Šele ko `zahteve.md` obstaja, zaženi `pisec-prijave` in `kalkulant` vzporedno (v enem sporočilu).
3. Zaženi `pregledovalec` (poročilo shrani v `izhod/<razpis>/pregled.md`); povzemi vrzeli uporabniku.
4. Če so vrzeli, vprašaj uporabnika po manjkajočih podatkih (eno vprašanje naenkrat) in ponovi korak 2 samo za prizadete dele.
5. Na koncu (ko so vrzeli obravnavane ali uporabnik reče, da je dovolj) izvozi dokumente: zaženi `python orodja/izvozi.py <razpis>` v mapi `razpisi` (če manjka `python-docx`, ga namesti z `pip install python-docx`). Ukaz iz `izhod/<razpis>/*.md` ustvari `.docx` in, če je na voljo Word ali LibreOffice, tudi `.pdf`. Sporoči uporabniku, katere datoteke so nastale in ali PDF manjka.
