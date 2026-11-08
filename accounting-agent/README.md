# Računovodski agent Amidas (prejeti računi)

Zgrajen po šestih korakih iz infografike "Build an AI Agent in 10 Minutes".

| Korak | Datoteka | Namen |
|---|---|---|
| 1. Claude Code | (namestitev) | `npm i -g @anthropic-ai/claude-code` |
| 2. Kontekst | `CLAUDE.md` | vloga, glas, prepovedane besede, privzete nastavitve, pravila samostojnosti |
| 3. Spomin | `memory/` | popravki -> .md datoteke, indeks `MEMORY.md` |
| 4. Skill | `../.claude/skills/prejeti-racuni/SKILL.md` | ukaz `/prejeti-racuni` |
| 5. Agenti | `../.claude/agents/` | Strateg (`claude-opus-5-5`) -> Graditelj (`claude-sonnet-5-5`) -> QA vrata 95/100 (`claude-opus-5-5`) |
| Evidenca | `evidenca-prejeti-racuni.csv`, `evidenca-navodilo.md` | predloga za Google Sheets (glava, stolpci, statusi) |
| Preizkus | `testni-podatki/`, `../.claude/skills/preizkus-racunov/` | 4 izmišljeni računi, preverjalnik Strategovega izhoda, ukaz `/preizkus-racunov` |
| Kontiranje | `kontni-nacrt.md` | predlog kontov in odločitveno drevo |
| 6. Autopilot | `routines.md` | dnevna rutina + opomnika 12. in 16. v mesecu (rok servisa 18.) |

## Potek
Diagram: [`DIAGRAM.md`](DIAGRAM.md).

Gmail + XTRF obvestila -> **Strateg** (analiza, zastavice) -> **Graditelj** (Sheets, oznake, paket, osnutki)
-> **QA** (>= 95/100) -> vi potrdite -> paket odide računovodskemu servisu (e-računi) z vaše strani.

## Varnost
Samo priprava: agent ne pošilja, ne briše, ne plačuje, ne piše v XTRF. IBAN, ki se razlikuje od zgodovine, je rdeča zastavica.

## Zagon v Claude Code
Agenti (`.claude/agents/`), skilli (`.claude/skills/`) in strežnik XTRF (`.mcp.json`) so v **korenu repozitorija**: namestitve ni, `claude` zaženete
v korenu repozitorija. Koraki (konektorji, ključ XTRF, evidenca): [`NAMESTITEV.md`](NAMESTITEV.md).
Pravila podjetja so v `accounting-agent/CLAUDE.md`; agenti jih preberejo ob zagonu (v podmapi je `CLAUDE.md` naložen šele na zahtevo, zato to piše tudi v agentih).

## Odprto (dopolnimo skupaj)
- **eSlog XSD + vzorčni XML od servisa** v `eslog/` (besedilo vprašanja: `eslog/vprasanje-servisu.md`). XSD in vzorec sta v mapi; XML ustvari `eslog/ustvari_xml.py` in ga validira (glej `eslog/README.md`).
- Kontni načrt: predlog je v `kontni-nacrt.md`, potrditi ga mora servis.
- Format uvoza, ki ga želi servis (stolpci CSV).
- Obravnava izvajalcev: s.p. / d.o.o. / tujina / fizične osebe.
