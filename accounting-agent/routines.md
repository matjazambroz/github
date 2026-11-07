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

## 2. Mesečno, 2. delovni dan
> Ustvari Claude Routine, ki 2. delovni dan v mesecu ob 8:00 (Europe/Ljubljana) zaključi pretekli mesec:
> preveri, da so vsi računi v evidenci pripravljeni, sestavi paket za računovodski servis
> (CSV + PDF v Drive mapi Računi/YYYY-MM) in pripravi OSNUTEK e-pošte servisu zame v pregled.
> Ne pošiljaj.
