---
name: En osnutek na račun, PDF + XML
description: Za servis (e-računi) vsak račun v svojem osnutku z obema prilogama
type: feedback
---
Pravilo: en osnutek (draft) na en račun; v prilogi OBVEZNO obe datoteki: PDF in XML (eSlog).
**Why:** odločitev uporabnika 7. 11. 2026; aplikacija e-računov prejme račun prek e-pošte.
**How to apply:** nekateri izvajalci (npr. z e-računi) priložijo PDF in XML, drugi samo PDF; XTRF XML ne ustvari (potrjeno 7. in 8. 11. 2026).
Odločitev uporabnika 8. 11. 2026: **če izvajalec priloži XML, uporabi izvirnik nespremenjen** (po preverjanju: shema, notranja skladnost,
ujemanje s PDF, kupec = Amidas); **svoj XML generiraj samo, če izvirnika ni**. Vse prek `eslog/pripravi_xml.py`.
Neskladen/neveljaven izvirnik se ne zamenja tiho z generiranim: ZASTAVICA, odloči uporabnik.
Manjkajoč XML v prejemu je NORMALEN, ni zastavica. Zastavica je le: XML ni skladen s PDF ali ni preverjen proti XSD
(zadeva osnutka `[XML NEPREVERJEN]`). Če priponk ni mogoče pripeti: `[PRILOGE ROČNO]`.
