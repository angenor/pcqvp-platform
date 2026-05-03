#!/usr/bin/env bash
# Garde CI : MadagascarMap.vue doit rester sous 320 lignes (cf. spec 019, T064).
set -euo pipefail

FILE="frontend/app/components/MadagascarMap.vue"
LIMIT=320

if [[ ! -f "$FILE" ]]; then
  echo "ERREUR: $FILE introuvable" >&2
  exit 1
fi

LINES=$(wc -l < "$FILE")
if (( LINES >= LIMIT )); then
  echo "ERREUR: $FILE = $LINES lignes (limite stricte: $LIMIT)" >&2
  exit 1
fi
echo "OK: $FILE = $LINES lignes (< $LIMIT)"
