---
name: En osnutek na račun, PDF + XML
description: Za servis (e-računi) vsak račun v svojem osnutku z obema prilogama
type: feedback
---
Pravilo: en osnutek (draft) na en račun; v prilogi OBVEZNO obe datoteki: PDF in XML (eSlog).
**Why:** odločitev uporabnika 7. 11. 2026; aplikacija e-računov prejme račun prek e-pošte.
**How to apply:** račun brez XML ali brez PDF ne gre v osnutek za servis, ampak dobi ZASTAVICO
"MANJKA XML" ali "MANJKA PDF". Če agent vsebine priponk ne more dobiti (base64), osnutek
vseeno ustvari z oznako v zadevi "[PRILOGE ROČNO]" in v telesu navede, kaj je treba priložiti.
