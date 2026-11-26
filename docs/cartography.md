# Cartography

What to port out of HDM-CartoCSS. Enough to write `style.json` without the
archive. Less expressions (`darken()`, `* 0.9`) are given as computed hex.

For more, see [hotosm/HDM-CartoCSS](https://github.com/hotosm/HDM-CartoCSS):
`palette.mss` colours, `roads.mss` widths, `project.yml` the classifying SQL,
`labels.mss` label placement - the one thing not summarised here.

## Colours

### Land

| Name | Hex | Used for |
| --- | --- | --- |
| land | `#F7F6F1` | Base landmass |
| residential | `#F0EEE4` | `landuse=residential`, `retail` |
| industrial | `#D7C8CB` | `industrial`, `commercial`, `quarry` |
| park | `#D0DCAE` | `park`, `garden`, `pitch`, `playground`, `village_green` |
| wooded | `#B2C29D` | `forest`, `wood` |
| heath | `#E1E9D6` | `heath`, `meadow`, `scrub` |
| agriculture | `#DEDDBE` | Farmland |
| wetland | `#E3E9E2` | Marsh, swamp |
| beach | `#EEE5B2` | Beach |
| salt | `#ECF0F1` | Salt flats |
| cemetery | `#D6DED2` | `cemetery`, `grave_yard` |
| military | `#D1BFAA` | Military |
| water | `#90CCCB` | Water areas and waterways |

### Buildings

| Name | Hex | Used for |
| --- | --- | --- |
| building | `#DCD7D7` | Building fill |
| damaged | `#C87C38` | `building=damaged` outline |
| collapsed | `#B25047` | `building=collapsed` outline |
| hospital | `#E5C6C3` | Hospital grounds |
| school | `#E2D6CD` | School, college, university grounds |

Damaged and collapsed buildings get a coloured outline, dashed (`6,3`) at z19
and above, with a lightened fill.

### Roads

`line` is the single stroke used at low zoom; `fill` plus `case` at high zoom.

| Class | Line / fill | Casing |
| --- | --- | --- |
| motorway, trunk | `#A098B0` | `#857B9A` |
| primary | `#D2938E` | `#BD8480` |
| secondary | `#E9CBB0` | `#D2B79E` |
| tertiary | `#DBDE99` | `#C5C88A` |
| standard (unclassified, road, service) | `#E4E1D1` | `#CDCABC` |
| urban (residential, living_street) | `#F7F6F1` | `#DEDDD9` |
| track | `#F0EEE4` fill, `#BFA286` line | `#CCC5A2` |
| pedestrian, path | `#BFA286` fill, `#CBC5BF` line | `#F7F6F1` |
| cycleway | `#FAFAF5` | `#F7F6F1` |
| rail | `#FFF` fill, `#999` line | `#F7F6F1` |
| ferry | `#42908F` | - |
| aeroway | `#DDD` | - |

Surfaces:

| Name | Hex |
| --- | --- |
| paved | `#AEA1A0` |
| unpaved | `#F0EEE4` |
| unpaved casing | `#D5CFB3` |

### Labels and boundaries

| Name | Hex |
| --- | --- |
| admin level 2 | `#537076` |
| admin level 3 | `#A59C9B` |
| country, capital | `#443355` |
| state | `#A6A6AA` |
| city | `#222` |
| town | `#444` |
| village, other | `#888` |
| locality | `#AAA` |
| POI | `#537076`, secondary `#868E90` |
| road | `#525252` |
| house number | `#797979` |
| contour line | `#D2CCB0` |
| power line | `#9A747C` |
| place halo | white, 66% opacity |
| road halo | white, 80% opacity |

## Road widths

HDM's widths, for reference. `style.py` uses its own, based on VersaTiles
Colorful, since HDM's were tuned for raster tiles.

`r` is total width, `c` is casing, inline is `r - c`. Pixels at `@2x`. Below
z11 roads are a single line: motorway and trunk at z5-8 (0.4 to 1 px), adding
primary, secondary and tertiary at z9-10 (0.6 to 1.8 px).

Total width `r`:

| Zoom | motorway | main | inter | minor | narrow | noauto |
| --- | --- | --- | --- | --- | --- | --- |
| 11 | 3 | 3 | 1.5 | 0 | 0 | 0 |
| 12 | 4 | 3.5 | 2 | 0 | 0 | 0 |
| 13 | 5 | 4.5 | 3.5 | 2.5 | 1.5 | 0 |
| 14 | 5 | 4.5 | 3.5 | 2 | 2 | 1.2 |
| 15 | 6 | 5 | 4 | 3 | 2.5 | 1.5 |
| 16 | 8 | 8 | 6 | 5 | 4 | 1.7 |
| 17 | 10 | 10 | 8 | 6 | 5 | 2 |
| 18 | 16 | 14 | 12 | 8 | 8 | 3 |

Casing width `c`:

| Zoom | motorway | main | inter | minor | narrow | noauto |
| --- | --- | --- | --- | --- | --- | --- |
| 11 | 1 | 1 | 0 | 0 | 0 | 0 |
| 12 | 1.5 | 1.5 | 1 | 0 | 0 | 0 |
| 13 | 2 | 2 | 1 | 1 | 0.2 | 0 |
| 14 | 2 | 2 | 1 | 1 | 0.2 | 1 |
| 15 | 2.5 | 2 | 2 | 1.5 | 0.2 | 2 |
| 16 | 2.5 | 2 | 1.5 | 1.5 | 1 | 2 |
| 17 | 3 | 2 | 2 | 2 | 1 | 3 |
| 18 | 4 | 3 | 3 | 3 | 2 | 4 |

Unpaved roads are drawn slightly narrower than paved, and appear earlier in
some cases. Urban roads start at z13 paved, z15 unpaved. Unpaved casing starts
at z11.

## Tag rules

HDM-CartoCSS did this in SQL. Any tiles we build ourselves need the same rules.

### Surface

```sql
CASE
  WHEN surface IN ('paved', 'paving_stones', 'asphalt', 'concrete')
    THEN 'paved'
  WHEN surface IS NULL AND type IN ('trunk', 'motorway', 'primary',
       'secondary', 'tertiary', and their _link forms)
    THEN 'paved'
  ELSE 'unpaved'
END
```

The fallback matters: most roads in the areas HOT works in have no `surface`
tag at all.

### Road class

| `highway` | Class |
| --- | --- |
| `motorway`, `trunk`, `trunk_link` | motorway |
| any `*_link` | parent class |
| `unclassified`, `road`, `service` | standard |
| `residential`, `living_street` | urban |
| `path`, `cycleway`, `footway`, `pedestrian`, `steps`, `bridleway` | noauto |
| anything else | itself |

### Condition

`smoothness` in `bad`, `very_bad`, `horrible`, `very_horrible` gives `bad`,
otherwise `good`.

### Structure

`tunnel`, else `bridge`, else `ford`. Ford is an HDM addition, worth keeping.

## Humanitarian attributes

Shortbread v1 drops most of these. Its `pois` layer does keep raw `amenity`,
`office`, `man_made`, `emergency` and `tower:type` tags, so healthcare, NGO and
water-tower icons already work. Its `streets` layer lists a `surface` field
but leaves it empty. See Next steps in the README for the rest.

| Attribute | Tags |
| --- | --- |
| Damaged buildings | `building=damaged` |
| Collapsed buildings | `building=collapsed` |
| Road surface | `surface=*`, plus the fallback above |
| Healthcare | `healthcare=*`, `amenity=clinic|hospital|doctors|dentist|pharmacy` |
| Water points | `man_made=water_well`, `pump=manual|powered`, `drinking_water=yes` |
| Water storage | `man_made=water_tower|storage_tank|watermill` |
| Power | `power=*`, `generator:source=solar|wind|nuclear`, `tower:type` |
| Ford | `ford=*` |
| NGO offices | `office=ngo` |
| Border control | `barrier=border_control` |

## Assets

### Icons

`../icons/` - 117 SVGs plus 4 legacy PNGs, all CC0 (Maki and Nori). Build the
sprite with [spreet](https://github.com/flother/spreet).

| Directory | Count |
| --- | --- |
| `poi/` | 99 SVG |
| `poi/low/` | 11 SVG, simplified for low zoom |
| `place/`, `natural/`, `pattern/` | 5 SVG, 4 PNG |
| root | 2 SVG, oneway arrows |

The 4 PNGs are place dots and a peak marker with no SVG equivalent, and need
redrawing. `_place.svg` and `_natural.svg` are the Inkscape sources.

### Fonts

Not committed. `fonts/fetch.sh` pulls them from a pinned Noto release at build
time; `fonts/fonts.txt` lists the families. Build glyph ranges with
[pbf_font_tools](https://github.com/stadiamaps/sdf_font_tools).

Latin, Greek and Cyrillic, plus Arabic, Bengali, Devanagari, Ethiopic, Khmer,
Lao, Myanmar, Sinhala, Tamil, Thai, Armenian, Georgian, Hebrew. Regular, Medium
and Bold each.

No CJK - MapLibre renders it from the client's own fonts by default. Clients
fetch only the 256-codepoint ranges a label needs, so wide coverage is cheap to
serve. Note QGIS ignores glyph PBFs entirely and uses system fonts, so
`text-font` names must resolve locally there.

## Not carried over

- The Mapnik and Carto stack. Tag rules are summarised above; the rest is in
  the archive.
- Hillshade and contours. Raster terrain is out of scope, and the SRTM scripts
  pointed at a URL that has since moved.
- `compare.html`, a Leaflet 0.5 viewer on dead CDN URLs.
