# Moji slovenski ukazi za Claude Code

Ukazi so v `.claude/commands/`. V Claude Code vpišite `/` za seznam ali `/ukazi` za pregled po kategorijah.

## Write & Edit

| Ukaz | Pomen | Primer |
|---|---|---|
| `/proof [besedilo]` | popravi tipkarske in slovnične napake | `/proof Sestanek je bil prestavlen na torek` |
| `/rewrites [stavek]` | 5 različic enega stavka | `/rewrites Hvala za hiter odgovor` |
| `/clarify [besedilo]` | skrajša in razjasni besedilo | `/clarify <dolgo besedilo>` |
| `/openers [besedilo]` | 5 močnejših uvodnih stavkov | `/openers <osnutek članka>` |
| `/filler [besedilo]` | označi šibke in zapolnilne besede | `/filler <besedilo>` |
| `/active [besedilo]` | pasivne stavke naredi aktivne | `/active Poročilo je bilo oddano` |
| `/human [besedilo]` | besedilo zveni naravno in človeško | `/human <besedilo>` |
| `/examples [besedilo]` | doda konkretne primere | `/examples <besedilo>` |
| `/simplify [besedilo]` | prepiše na raven 12. razreda | `/simplify <strokovno besedilo>` |
| `/title [besedilo]` | 10 predlogov naslova | `/title <besedilo>` |
| `/tone [ton: besedilo]` | prepiše v želenem tonu | `/tone formalen: Hej, pošlji mi to do petka` |

## Email & Messages

| Ukaz | Pomen | Primer |
|---|---|---|
| `/decline [e-pošta]` | vljuden odklonilni odgovor | `/decline <prejeta e-pošta>` |
| `/shorten [e-pošta]` | skrajša e-pošto na polovico | `/shorten <e-pošta>` |
| `/warmer [e-pošta]` | manj toga, bolj topla e-pošta | `/warmer <e-pošta>` |
| `/followup [tema]` | opomnik za odgovor | `/followup ponudba za prevod` |
| `/answer [zahteva]` | jasen odgovor na zahtevo | `/answer <vprašanje>` |
| `/bulletproof [osnutek]` | e-pošta brez dvoumnosti | `/bulletproof <osnutek>` |
| `/thanks [oseba + razlog]` | zahvalno sporočilo | `/thanks Peter, pomagal pri selitvi` |
| `/comfort [sporočilo]` | sočuten, podporen odgovor | `/comfort <sporočilo>` |
| `/odo [datumi + nadomestna oseba]` | sporočilo o odsotnosti | `/odo 1.–15. 8., nadomešča Ana` |
| `/hardsig [tema]` | 5 močnih zaključkov e-pošte | `/hardsig ponudba` |
| `/intro [oseba A + oseba B]` | predstavitev dveh oseb | `/intro Ana in Boris, oba prevajalca` |

## Pravilo

Ukazi `/proof`, `/clarify` in `/human` dajejo prednost slovenskemu pravopisu (SSKJ, Slovenski pravopis).

## Dodajanje novega ukaza

Naredite datoteko `.claude/commands/ime.md` z glavo `description` in `argument-hint`, nato navodilom in `$ARGUMENTS`. Dodajte ga še v to tabelo.
