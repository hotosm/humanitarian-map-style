# Humanitarian Map Style

The Humanitarian style for OpenStreetMap, rebuilt as vector tiles. Holds both
the style and the pipeline that generates the tiles.

Host: `hdm-style.hotosm.org`. Status: Stage 1, porting the cartography.

| Path | Contents |
| --- | --- |
| `proposal.md` | What we are building and how. |
| `docs/cartography.md` | Colours, road widths and tag rules from HDM-CartoCSS. |
| `icons/` | 117 SVGs. Source for the sprite. |
| `fonts/` | Manifest and fetch script for the Noto faces. |

Replaces [HDM-CartoCSS](https://github.com/hotosm/HDM-CartoCSS), archived. That
rendered raster tiles from a PostGIS database on minutely diffs, which needed
constant maintenance. This is a static style on OSM's own vector tiles, with our
own tiles built only for what those don't carry.

Licences differ by component - see [LICENCE.md](./LICENCE.md).
