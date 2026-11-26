#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Build style.json, sprite, glyphs and preview page into dist/.
# Needs python3, spreet and build_pbf_glyphs.
# Usage: ./build.sh [base-url]   (default: http://localhost:8765)

set -euo pipefail
cd "$(dirname "$0")"

BASE_URL="${1:-http://localhost:8765}"
WEIGHTS=(Regular Medium Bold)

rm -rf dist build
mkdir -p dist/font build/icons

echo "Sprite"
# Leaves out the Inkscape sources (_*.svg) in place/ and natural/.
cp -r icons/poi icons/pattern icons/*.svg build/icons/
spreet --recursive --minify-index-file build/icons dist/sprite
spreet --recursive --minify-index-file --retina build/icons dist/sprite@2x

echo "Glyphs"
fonts/fetch.sh
# Merge all families into one font per weight, so every script renders.
families=$(grep -v '^#' fonts/fonts.txt | awk 'NF { print $1 }')
for weight in "${WEIGHTS[@]}"; do
    faces=$(printf '"%s-'"$weight"'",' $families)
    printf '"Noto Sans %s": [%s]\n' "$weight" "${faces%,}"
done | paste -sd, | sed 's/^/{/; s/$/}/' > build/combine.json
build_pbf_glyphs -c build/combine.json fonts/ttf build/glyphs > /dev/null
for weight in "${WEIGHTS[@]}"; do
    cp -r "build/glyphs/Noto Sans $weight" dist/font/
done

echo "Style"
python3 style.py "$BASE_URL" > dist/style.json
cp index.html dist/

echo "Done: $(du -sh dist | cut -f1) in dist/"
