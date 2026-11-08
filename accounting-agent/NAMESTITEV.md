# Namestitev računovodskega agenta (po korakih)

Čas: ~30 minut, večinoma konektorji. Vse spodaj delate na svojem računalniku, ne v oblaku.

## 0. Predpogoji
- Claude Code (`npm i -g @anthropic-ai/claude-code`) in prijava s paketom Pro.
- Ta repozitorij na računalniku (`git clone`, veja `claude/kind-galileo-3u6834`, ali po združitvi `main`).
- Ukaz `/model` v Claude Code: preverjeno, da je na voljo Opus 5.5 (potrjeno 8. 11. 2026).

## 1. Kopiraj agenta v ~/.claude
```bash
./accounting-agent/install.sh
```
Skripta kopira agente, skill `/prejeti-racuni`, kontni načrt, predlogo evidence, `eslog/` in spomin.
`~/CLAUDE.md` ne prepiše: če že obstaja, doda vsebino ročno (`cat accounting-agent/CLAUDE.md >> ~/CLAUDE.md`).
Znova zaženi `claude`, nato vpiši `/prejeti-racuni`: ukaz mora biti na seznamu (do zdaj ga seja ni poznala).

## 2. Poveži službeni Gmail
V claude.ai -> Nastavitve -> Konektorji poveži **matjaz.ambroz@amidas.si** (ne zasebnega gmail.com).
Preizkus: v Claude Code vprašaj "kdo je pošiljatelj zadnjega e-sporočila v mojem predalu" in preveri, da je prejemnik amidas.si.
Do tega koraka je agent bral napačen predal.

## 3. Google Drive in Sheets
1. Uvozi `evidenca-prejeti-racuni.csv` v novo preglednico **Prejeti računi**, list **Racuni** (glej `evidenca-navodilo.md`).
2. V Drive ustvari mapo **Računi**.
3. ID preglednice in mape vpiši v `~/.claude/projects/amidas-racunovodstvo/memory/reference_viri.md`.
4. Poveži konektorja Google Drive in Google Sheets z istim Google računom, ki si ga izbral za službo.

## 4. XTRF (MCP strežnik, samo branje)
```bash
cd mcp-xtrf && npm install && cp .env.example .env   # vpiši XTRF_API_KEY
npm run build
```
Registracija v Claude Code: po navodilu v `mcp-xtrf/README.md` (razdelek z `claude mcp add` ali `.mcp.json`; pot do
`dist/index.js` je pri tebi). Ključ naj bo samo za branje, če ga XTRF tako podpira.

## 5. Shema in vzorec XML od servisa
Pošlji servisu besedilo iz `eslog/vprasanje-servisu.md`. Prejeta `eslog.xsd` in `vzorec.xml` gresta v `~/.claude/eslog/`.
Do takrat so osnutki označeni `[XML NEPREVERJEN]` (to je pričakovano).

## 6. Prvi zagon (en račun)
1. V Claude Code: `/prejeti-racuni` (obdobje: zadnjih 7 dni).
2. Preveri, česa se agent loti: ali najde obvestilo XTRF, ali vpiše vrstico v Sheets, ali ustvari **osnutek** (ne pošlje).
3. Odpri osnutek v Gmailu: prejemnik 50375431@e-racuni.com, CC invoices@amidas.si, priponki PDF in XML.
   Če priponk ni, ima zadevo `[PRILOGE ROČNO]`: to ni napaka, ampak znana omejitev (agent morda ne dobi bajtov datotek).
4. Osnutek pošlji **ti**, nato v Sheets ročno nastavi status `POSLANO SERVISU`.
5. Popravke, ki jih zahtevaš, agent zapiše v `memory/feedback_*.md`.

## 7. Rutine (šele po uspešnem prvem zagonu)
Prilepi ukaze iz `routines.md` (dnevna ob 8:00, opomnik 12., kontrola 16.). Preveri, ali Pro omogoča Claude Routines v oblaku in koliko jih
dovoli; ne vem tega zanesljivo. Rutine ne pošiljajo ničesar, samo pripravijo osnutke.

## Če kaj ne dela
| Težava | Ukrep |
|---|---|
| `/prejeti-racuni` ni na seznamu | ponovno zaženi `install.sh` in `claude`; preveri `~/.claude/skills/prejeti-racuni/SKILL.md` |
| Agent ne najde računov | preveri, kateri Gmail je povezan (korak 2); obvestila XTRF morajo biti v tem predalu |
| Opus 5.5 ni na voljo / poraba omejitve | `model:` v `agents/racuni-strateg.md` in `racuni-qa.md` zamenjaj na `claude-sonnet-5-5` |
| XML je označen kot nepreverjen | manjka `eslog.xsd` (korak 5) |
| Preglednica ne sprejme številk | glej opombe v `evidenca-navodilo.md` |
