#!/usr/bin/env bash
set -e
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
SRC="$(pwd -W 2>/dev/null || pwd)/sv660n.html"
OUT="$(pwd -W 2>/dev/null || pwd)/SV660N-Guia-Tecnico-MVP.pdf"
rm -f "$OUT"
"$CHROME" --headless=new --disable-gpu --no-sandbox --no-first-run \
  --allow-file-access-from-files --font-render-hinting=none \
  --run-all-compositor-stages-before-draw --virtual-time-budget=12000 \
  --print-to-pdf-no-header --print-to-pdf="$OUT" "file:///$SRC" 2>&1 | grep -vi "devtools\|bluetooth\|Fontconfig\|voice" || true
ls -la "SV660N-Guia-Tecnico-MVP.pdf"
