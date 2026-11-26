# Humanitarian Map Style

The Humanitarian OpenStreetMap style, rebuilt for MapLibre on OSM's own
[Shortbread](https://shortbread-tiles.org) vector tiles. Replaces the archived
[HDM-CartoCSS](https://github.com/hotosm/HDM-CartoCSS) raster style.

Everything is static: the style, icons and fonts are served from GitHub Pages,
and map data comes from `vector.openstreetmap.org`. No servers to run.

## Use it

```js
new maplibregl.Map({
  container: "map",
  style: "https://map-style.hotosm.org/style.json",
});
```

Demo map: https://map-style.hotosm.org

In QGIS: Vector Tiles > New Generic Connection, and use the same URL as the
Style URL.

## Build

`style.py` generates `style.json`. To change colours, road widths or icons,
edit the tables at the top of `style.py`, not the JSON.

Preview with Docker, then open http://localhost:8765:

```sh
docker build --target build -t humanitarian-style .
docker run --rm -p 8765:8765 humanitarian-style
```

Without Docker, install the tools once and run the script:

```sh
cargo install spreet build_pbf_glyphs
./build.sh http://localhost:8765
python3 -m http.server -d dist 8765
```

Pushing to `main` builds with the Dockerfile and publishes to GitHub Pages.

| Path | Contents |
| --- | --- |
| `style.py` | Generates `style.json`. |
| `build.sh` | Builds the style, icon sprite and fonts into `dist/`. |
| `Dockerfile` | Pinned build tools; used locally and in CI. |
| `index.html` | Preview page. |
| `icons/` | Icon SVGs. |
| `fonts/` | Font list and download script. |
| `docs/cartography.md` | Colours and tag rules from HDM-CartoCSS. |

## Next steps

The style uses everything OSM's tiles provide. Remaining work:

- **Review.** Compare with HDM-CartoCSS and tune label sizes. Some town dots
  show without a name where labels collide.
- **Humanitarian overlay.** OSM's tiles leave out damaged buildings, water
  points, power lines, fords and peaks. A small extra tile set, built daily
  with tilemaker from a filtered extract, could add them on top.
- **Road surface.** Paved vs unpaved needs our own road tiles: a weekly planet
  build to PMTiles on S3, roughly $40/month. Time a build first. The earlier
  design and costs are in `proposal.md` in commit `198e971`.
- **Alternative.** [VersaTiles](https://versatiles.org) has polished styles on
  the same tiles. If upkeep here is a burden, recolour a VersaTiles style with
  HDM's palette and add the humanitarian layers on top.

## Licence

Code is GPL-3.0-or-later. The style and sprite are CC BY 4.0, icons CC0, and
fonts and glyphs OFL. See [LICENCE.md](./LICENCE.md).
