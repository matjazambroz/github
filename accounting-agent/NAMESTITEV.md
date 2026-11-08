# Zagon računovodskega agenta v Claude Code (po korakih)

Agent je del repozitorija: agenti, skilli in strežnik XTRF so v projektni konfiguraciji, zato **namestitve ni**.
Claude Code vse naloži sam, ko v repozitoriju zaženete `claude`. Čas: ~20 minut, večinoma konektorji.

## Kje je kaj
| Kaj | Mesto v repozitoriju |
|---|---|
| Agenti (Strateg, Graditelj, QA) | `.claude/agents/` |
| Ukaza `/prejeti-racuni`, `/preizkus-racunov` | `.claude/skills/` |
| Strežnik XTRF (samo branje) | `.mcp.json` (koren) + `mcp-xtrf/` |
| Dovoljenja za skripte | `.claude/settings.json` |
| Pravila podjetja, spomin, kontni načrt, eSLOG, testi | `accounting-agent/` |

## 0. Predpogoji
- Claude Code (`npm i -g @anthropic-ai/claude-code`), prijava s paketom Pro, `xmllint` (paket `libxml2-utils`), Python 3, Node.js.
- Repozitorij na računalniku (`git clone`/`git pull`, veja `claude/kind-galileo-3u6834` ali po združitvi `main`).
- `claude` zaženite v **korenu repozitorija** (ne v podmapi), da naloži `.claude/` in `.mcp.json`.
- `/model`: preverjeno, da je Opus 5.5 na voljo (8. 11. 2026).

## 1. Preveri, da je agent naložen
V Claude Code: `/agents` (morajo biti `racuni-strateg`, `racuni-graditelj`, `racuni-qa`) in vpiši `/prejeti-racuni` (ukaz mora biti na seznamu).
Ob prvem zagonu vas Claude Code vpraša za odobritev projektnega strežnika MCP `xtrf` iz `.mcp.json`.

## 2. Poveži službeni Gmail
V claude.ai -> Nastavitve -> Konektorji poveži **matjaz.ambroz@amidas.si** (ne zasebnega gmail.com), nato nova seja (konektorji se preberejo ob zagonu).
Preizkus: "kdo je pošiljatelj zadnjega e-sporočila v mojem predalu", prejemnik mora biti amidas.si. Do tega koraka je agent bral napačen predal.
V Claude Code se orodja konektorjev imenujejo `mcp__claude_ai_<strežnik>__<orodje>`; prepovedi v agentih so zapisane z vzorci, ki pokrijejo to imenovanje.

## 3. Google Drive in Sheets
1. Uvozi `accounting-agent/evidenca-prejeti-racuni.csv` v novo preglednico **Prejeti računi**, list **Racuni** (glej `evidenca-navodilo.md`).
2. V Drive ustvari mapo **Računi**.
3. ID preglednice in mape vpiši v `accounting-agent/memory/reference_viri.md`.
4. Poveži konektorja Google Drive in Google Sheets z istim Google računom, kot za Gmail.

## 4. XTRF (strežnik MCP, samo branje)
```bash
cd mcp-xtrf && npm install && npm run build
export XTRF_API_KEY=...      # ključa ne commitaj; npr. v ~/.zshrc ali ~/.bashrc
```
`.mcp.json` prebere ključ iz spremenljivke okolja `XTRF_API_KEY` in ga ne vsebuje. Ključ naj bo samo za branje, če ga XTRF tako podpira.
Agenti imajo prepovedano splošno orodje `xtrf_request` (ki bi lahko pisalo); uporabljajo samo bralna orodja (`xtrf_get_project`, `xtrf_get_job` ...).
Brez nastavljenega ključa ali brez `npm run build` strežnik `xtrf` ne bo deloval (natančnega sporočila napake nisem preveril); stanje vidiš z `/mcp`.

## 5. Shema in vzorec XML (eSLOG 2.0)
`eslog.xsd`, `vzorec.xml`, `xmldsig-core-schema.xsd` in `kupec.json` (podatki Amidas) so že v `accounting-agent/eslog/`.
Preverjeno: `accounting-agent/eslog/validate.sh accounting-agent/eslog/vzorec.xml` vrne 0.
Preizkus skripte: `python3 accounting-agent/eslog/ustvari_xml.py accounting-agent/eslog/primer-racun.json /tmp/test.xml` izpiše "VELJAVEN proti eslog.xsd".
Redno: `accounting-agent/eslog/preveri-verzijo.sh` sporoči, ali je ePOS izdal drug paket. Ob izhodu 1 prenesi nov paket ročno v brskalniku
(https://epos.si/eslog; strežnik ima zaščito pred boti) in zamenjaj datoteke v `accounting-agent/eslog/`.

## 6a. Preizkus na izmišljenih računih (brez Gmaila)
`/preizkus-racunov` ali ročno po `accounting-agent/testni-podatki/NAVODILO.md`. Naredi pred pravim zagonom.

## 6. Prvi zagon (en račun)
1. `/prejeti-racuni` (obdobje: zadnjih 7 dni).
2. Preveri, česa se agent loti: ali najde obvestilo XTRF, ali vpiše vrstico v Sheets, ali ustvari **osnutek** (ne pošlje).
3. Odpri osnutek v Gmailu: prejemnik 50375431@e-racuni.com, CC invoices@amidas.si, priponki PDF in XML.
   Če priponk ni, ima zadevo `[PRILOGE ROČNO]`: znana omejitev (agent morda ne dobi bajtov datotek).
4. Osnutek pošlji **ti**, nato v Sheets ročno nastavi status `POSLANO SERVISU`.
5. Popravke, ki jih zahtevaš, agent zapiše v `accounting-agent/memory/feedback_*.md` (to so datoteke v repozitoriju; commitaj jih).

## 7. Rutine (šele po uspešnem prvem zagonu)
Ukazi so v `accounting-agent/routines.md` (dnevna ob 8:00, opomnik 12., kontrola 16.). Ali Pro omogoča Claude Routines v oblaku in koliko jih dovoli,
ne vem zanesljivo. Rutine v oblaku delajo v klonu repozitorija, zato morata biti tam tudi `.mcp.json` in ključ XTRF (okolje seje). Rutine ne pošiljajo ničesar.

## Če kaj ne dela
| Težava | Ukrep |
|---|---|
| `/prejeti-racuni` ni na seznamu | `claude` zaženi v korenu repozitorija; preveri `.claude/skills/prejeti-racuni/SKILL.md` |
| Agent ne najde računov | preveri, kateri Gmail je povezan (korak 2); obvestila XTRF morajo biti v tem predalu |
| Strateg ne vidi XTRF | `/mcp`: strežnik `xtrf` mora biti povezan; preveri `npm run build` in `XTRF_API_KEY` |
| Opus 5.5 ni na voljo / poraba omejitve | `model:` v `.claude/agents/racuni-strateg.md` in `racuni-qa.md` zamenjaj na `claude-sonnet-5-5` |
| XML je označen kot nepreverjen | manjka `xmllint` ali `eslog.xsd` (korak 5) |
| Preglednica ne sprejme številk | glej opombe v `evidenca-navodilo.md` |
