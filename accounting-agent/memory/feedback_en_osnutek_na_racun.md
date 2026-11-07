---
name: En osnutek na račun, PDF + XML
description: Za servis (e-računi) vsak račun v svojem osnutku z obema prilogama
type: feedback
---
Pravilo: en osnutek (draft) na en račun; v prilogi OBVEZNO obe datoteki: PDF in XML (eSlog).
**Why:** odločitev uporabnika 7. 11. 2026; aplikacija e-računov prejme račun prek e-pošte.
**How to apply:** izvajalci naložijo SAMO PDF; XTRF XML ne ustvari (potrjeno 7. 11. 2026).
XML (eSlog) ustvari Graditelj iz podatkov Stratega, po eslog/README.md, in ga preveri z eslog/validate.sh.
Manjkajoč XML v prejemu je NORMALEN, ni zastavica. Zastavica je le: XML ni skladen s PDF ali ni preverjen proti XSD
(zadeva osnutka `[XML NEPREVERJEN]`). Če priponk ni mogoče pripeti: `[PRILOGE ROČNO]`.
