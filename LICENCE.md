# Licence

| What | Licence |
| --- | --- |
| Style and documentation | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| Code | [GPL-3.0-or-later](./COPYING) |
| `icons/` | CC0 1.0 |
| Noto fonts and the glyphs built from them | [SIL OFL 1.1](https://openfontlicense.org/) |
| Map data in any tiles produced | [ODbL](https://www.openstreetmap.org/copyright) |

**Style and documentation.** `style.json`, the sprite, and `docs/`. Credit the
Humanitarian OpenStreetMap Team. Based on
[HDM-CartoCSS](https://github.com/hotosm/HDM-CartoCSS) by Yohan Boniface and
contributors, which was CC0 - that placed no conditions on reuse, so this work
can carry its own terms, but only for what is new here.

**Code.** `style.py`, `build.sh`, `fonts/fetch.sh`, the GitHub workflow, and
any tile pipeline added later. Full text in [COPYING](./COPYING). Split out
because Creative Commons
[recommend against](https://creativecommons.org/faq/#can-i-apply-a-creative-commons-license-to-software)
using their licences for software. The `style.json` that `style.py` outputs is
style, not code, so it is CC BY 4.0.

**Icons.** SVGs from [Maki](https://labs.mapbox.com/maki-icons/) and Nori,
plus our road shield. All CC0, so public domain regardless of the above.

**Fonts.** Not committed; `fonts/fetch.sh` pulls them at build time. SDF glyphs
generated from them are a format conversion, so they stay under OFL rather than
CC BY.

**Data.** Any map built from this style must show the OpenStreetMap attribution.
