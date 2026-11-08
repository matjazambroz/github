#!/usr/bin/env bash
# Preveri, ali je ePOS objavil drug paket eSLOG kot zapisan v VERZIJA.txt.
# Prebere samo javno stran (brez prenosa datotek). Izhod: 0 = enako, 1 = DRUGAČE ali novo, 2 = ni mogoče preveriti.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
PAGE="$(curl -sSL -m 30 https://epos.si/eslog 2>/dev/null)" || { echo "NEPREVERJENO: strani ni mogoče prebrati"; exit 2; }
NOW="$(printf '%s' "$PAGE" | grep -oE 'e-SLOG-[0-9.]+-[0-9]{2}-[0-9]{4}-SL\.zip' | sort -u | tr '\n' ' ')"
[ -n "$NOW" ] || { echo "NEPREVERJENO: na strani ni najden paket e-SLOG (stran se je morda spremenila)"; exit 2; }
KNOWN="$(grep -E '^paket_sl=' "$DIR/VERZIJA.txt" | cut -d= -f2)"
if printf '%s' "$NOW" | grep -qw "$KNOWN" && [ "$(printf '%s' "$NOW" | wc -w)" -eq 1 ]; then
  echo "OK: najnovejši paket je še vedno $KNOWN"; exit 0
fi
echo "DRUGAČE: zapisano $KNOWN, na strani: $NOW"
echo "Prenesi novi paket v brskalniku, zamenjaj eslog.xsd in vzorec.xml ter posodobi VERZIJA.txt."
exit 1
