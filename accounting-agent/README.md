# Računovodski agent Amidas (prejeti računi)

Zgrajen po šestih korakih iz infografike "Build an AI Agent in 10 Minutes".

| Korak | Datoteka | Namen |
|---|---|---|
| 1. Claude Code | (namestitev) | `npm i -g @anthropic-ai/claude-code` |
| 2. Kontekst | `CLAUDE.md` | vloga, glas, prepovedane besede, privzete nastavitve, pravila samostojnosti |
| 3. Spomin | `memory/` | popravki -> .md datoteke, indeks `MEMORY.md` |
| 4. Skill | `skills/prejeti-racuni/SKILL.md` | ukaz `/prejeti-racuni` |
| 5. Agenti | `agents/` | Strateg (Opus) -> Graditelj (Sonnet) -> QA vrata 95/100 |
| Kontiranje | `kontni-nacrt.md` | predlog kontov in odločitveno drevo |
| 6. Autopilot | `routines.md` | dnevna rutina + opomnika 12. in 16. v mesecu (rok servisa 18.) |

## Potek
Diagram: [`DIAGRAM.md`](DIAGRAM.md).

Gmail + XTRF obvestila -> **Strateg** (analiza, zastavice) -> **Graditelj** (Sheets, oznake, paket, osnutki)
-> **QA** (>= 95/100) -> vi potrdite -> paket odide računovodskemu servisu (e-računi) z vaše strani.

## Varnost
Samo priprava: agent ne pošilja, ne briše, ne plačuje, ne piše v XTRF. IBAN, ki se razlikuje od zgodovine, je rdeča zastavica.

## Namestitev
```bash
./accounting-agent/install.sh
```
Nato ročno vpišite Sheets ID, Drive mapo in kontakt servisa v `memory/reference_viri.md`.
Povežite konektorje Gmail, Google Drive, Google Sheets in MCP `mcp-xtrf` (glej `../mcp-xtrf/README.md`).

## Odprto (dopolnimo skupaj)
- **eSlog XSD + vzorčni XML od servisa** v `eslog/` (besedilo vprašanja: `eslog/vprasanje-servisu.md`). Brez njiju so osnutki označeni `[XML NEPREVERJEN]`.
- Kontni načrt: predlog je v `kontni-nacrt.md`, potrditi ga mora servis.
- Format uvoza, ki ga želi servis (stolpci CSV).
- Obravnava izvajalcev: s.p. / d.o.o. / tujina / fizične osebe.
