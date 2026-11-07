# Rutine (korak 6: autopilot)

Rutino ustvarite v Claude Code (Routines, v Anthropicovem oblaku, ne na laptopu).
Ker je izbrana samo priprava, rutine NE pošiljajo ničesar: samo pripravijo osnutke in poročilo.

## Obseg in strošek
30 do 100 računov na mesec = 2 do 5 na delovni dan. Dnevna rutina obdela samo nove račune (en paket, en
QA krog), zato je strošek majhen. Če ni novih računov, rutina konča brez ukrepanja in brez osnutka.
Mesečna rutina ne analizira znova, ampak sestavi paket iz že preverjenih vrstic (status PRIPRAVLJENO).

## 1. Dnevno, delovni dnevi ob 8:00 (Europe/Ljubljana)
Prilepi v Claude Code:

> Ustvari Claude Routine, ki vsak delovni dan ob 8:00 (Europe/Ljubljana) zažene skill /prejeti-racuni
> za nove račune od zadnjega zagona. Zaženi v Anthropicovem oblaku, ne na mojem laptopu.
> Rezultat (povzetek + zastavice) naj pripravi kot osnutek e-pošte meni (matjaz.ambroz@amidas.si);
> ničesar ne pošilja nikomur drugemu.

## 2. Opomnik pred rokom: 12. v mesecu ob 8:00 (Europe/Ljubljana)
Servis prejema račune sproti, končni rok za mesec je 18. Če 18. pade na vikend, je rok prejšnji delovnik.

> Ustvari Claude Routine, ki 12. v mesecu ob 8:00 (Europe/Ljubljana) preveri evidenco prejetih računov
> za tekoči in pretekli mesec: kateri računi imajo status PRIPRAVLJENO, a jih še nisem poslal servisu
> (status ni POSLANO SERVISU), kateri imajo odprte zastavice in kateri izvajalci še niso oddali računa.
> Pripravi OSNUTEK e-pošte servisu z manjkajočimi računi in meni kratek opomnik. Ne pošiljaj.

## 3. Rok servisa: 16. v mesecu ob 8:00 (Europe/Ljubljana)
Dva dni rezerve pred rokom 18.

> Ustvari Claude Routine, ki 16. v mesecu ob 8:00 (Europe/Ljubljana) preveri, da je vse za pretekli mesec
> poslano servisu. Če kaj manjka, pripravi osnutek e-pošte z zadnjimi računi in meni označi, kaj je
> še nerešeno (zastavice). Ne pošiljaj.
