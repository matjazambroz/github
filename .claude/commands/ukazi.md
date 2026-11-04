---
description: Izpiše vse moje ukaze po kategorijah s pomenom in primerom
argument-hint: [kategorija ali iskana beseda, neobvezno]
---
Preberi vse datoteke z ukazi iz obeh mest: `.claude/commands/*.md` v trenutnem projektu in `~/.claude/commands/*.md` (osebni ukazi). Če se ime ukaza pojavi na obeh mestih, upoštevaj projektno različico in ukaza ne podvajaj. Če mapa ne obstaja, jo preskoči. Iz glave vsake datoteke vzemi `description` in `argument-hint`.

Ukaze razvrsti v kategorije:
- **Write & Edit**: proof, rewrites, clarify, openers, filler, active, human, examples, simplify, title, tone
- **Email & Messages**: decline, shorten, warmer, followup, answer, bulletproof, thanks, comfort, odo, hardsig, intro
- **Work & Career**: interviewq, resumebullet, askinterviewer, negotiate, reconnect, gap, wins, oneonone, selfreview, idiomtov, raise
- **Learn & Understand**: eli10, primer, myths, analogy, quiz, compare, proscons, sums, glossary, askbetter, mentalmodel
- **Plan & Organize**: week, milestones, pack, schedule, routine, prioritize, meals, agenda, prepare, order, checklist
- **Content & Social**: hook, caption, thread, caro, repurpose, cta, bio, subject, contrarian, shortpost, comment
- **Think & Decide**: choose, realpc, blindspot, steelman, devil, skeptic, steps, ripple, premortem, minetest
- **Brainstorm**: ideas20, gifts, names, unusual, angle, combine, metaphor, starters, journal10, as, child
- **Drugo**: vsi ostali ukazi, ki niso v zgornjih kategorijah

Za vsak ukaz izpiši eno vrstico: `/ukaz [argument]` – pomen (iz `description`). Pod vsako kategorijo dodaj en kratek primer uporabe. Če je spodaj naveden filter, pokaži samo ustrezno kategorijo ali ukaze, katerih ime ali opis vsebuje to besedo. Odgovori v slovenščini, brez uvoda.

Filter: $ARGUMENTS
