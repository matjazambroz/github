#!/usr/bin/env bash
# Preveri XML proti eslog.xsd. Izhod 0 = veljaven; 2 = XSD manjka (NEPREVERJEN); drugo = neveljaven.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
XML="${1:?uporaba: validate.sh datoteka.xml}"
[ -f "$DIR/eslog.xsd" ] || { echo "NEPREVERJEN: eslog.xsd manjka v $DIR"; exit 2; }
command -v xmllint >/dev/null || { echo "NEPREVERJEN: xmllint ni nameščen"; exit 2; }
xmllint --noout --schema "$DIR/eslog.xsd" "$XML"
