#!/usr/bin/env bash
# Download the Noto faces in fonts.txt. Fonts are unmodified upstream binaries,
# so we fetch at build time and commit only the generated glyphs.
#
# Usage: ./fetch.sh [output-dir]   (default: ./ttf)

set -euo pipefail

NOTO_REF="3a06b1c521155492df224d33464b3c7b2852d861"  # pinned; bump deliberately
BASE="https://raw.githubusercontent.com/notofonts/notofonts.github.io/${NOTO_REF}/fonts"
WEIGHTS=(Regular Medium Bold)

DIR="${1:-$(dirname "$0")/ttf}"
MANIFEST="$(dirname "$0")/fonts.txt"
mkdir -p "$DIR"

while read -r family _; do
    [[ -z "$family" || "$family" == \#* ]] && continue
    for weight in "${WEIGHTS[@]}"; do
        file="${family}-${weight}.ttf"
        [[ -f "$DIR/$file" ]] && continue
        echo "Fetching $file"
        curl -sfL "$BASE/${family}/hinted/ttf/${file}" -o "$DIR/$file"
    done
done < "$MANIFEST"

echo "Done. $(find "$DIR" -name '*.ttf' | wc -l) faces in $DIR"
