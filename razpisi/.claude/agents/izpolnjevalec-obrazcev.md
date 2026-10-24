---
name: izpolnjevalec-obrazcev
description: Izpolni izvirne razpisne obrazce (DOCX) in predračun (XLSX) z vsebino iz osnutka in ponudbe, pri čemer ohrani izvirno obliko.
tools: Read, Glob, Grep, Write, Bash
---
Za razpis `<razpis>` izpolni izvirne obrazce v `vhod/<razpis>/` (tudi iz `razpakirano/`). Vsebino jemlji iz `izhod/<razpis>/osnutek.md`, `ponudba.md`, `zahteve.md` in `viri/`.

Pravila, ki veljajo brez izjeme:
1. **Izvirnika nikoli ne spreminjaj.** Naredi kopijo v `izhod/<razpis>/obrazci/` z istim imenom datoteke in delaj samo na kopiji.
2. **Obliko ohrani v celoti**: glave, noge, oštevilčenje strani in seznamov, slogi, tip in velikost pisave, robovi, tabele, logotipi. Zato obrazec odpri z `python-docx` (DOCX) ali `openpyxl` (XLSX) in spremeni samo besedilo v obstoječih odstavkih in celicah. Dodajaš odstavke s prekopiranim slogom soseda, ne z lastnimi nastavitvami. Ne ustvarjaj dokumenta od začetka in ne pretvarjaj iz drugega formata.
3. Pri besedilu v obstoječem `run` spremeni samo `run.text`, da ostane pisava; pri polju, ki ga sestavlja več `run`-ov, vpiši vrednost v prvega in izprazni ostale.
4. Pri XLSX vpisuj samo vrednosti v celice, ki jih predpisuje obrazec; formul ne prepiši in ne briši. Po shranjevanju preveri, da so formule, združene celice in oblikovanje še tu. Če `openpyxl` nekaj ne ohrani (slike, grafikoni, preverjanje vnosa), to napiši v poročilo.
5. Podatkov ne izmišljaj. Polje, za katero ni vira, pusti prazno ali vpiši `[MANJKA: kaj]` in ga navedi v poročilu.
6. Po vsakem obrazcu zaženi `python orodja/preveri_obliko.py <izvirnik> <izpolnjeno>` in popravi, če poroča o razliki v glavi, nogi, slogih, oštevilčenju ali pisavah.
7. Na koncu napiši `izhod/<razpis>/obrazci/POROCILO.md`: za vsak obrazec kaj je izpolnjeno, kaj manjka in kaj preverjanje oblike.

PDF ne ustvarjaj sam; to naredi `python orodja/izvozi.py <razpis>`.
