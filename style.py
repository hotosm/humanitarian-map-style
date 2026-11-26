# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate the Humanitarian MapLibre style on OSM's Shortbread vector tiles.

Colours and POI rules come from HDM-CartoCSS. Road widths are based on
VersaTiles Colorful.

Usage: python3 style.py BASE_URL > style.json
BASE_URL is where the sprite and glyphs are served.
"""

import json
import sys
from itertools import pairwise
from typing import NamedTuple

TILES = "https://vector.openstreetmap.org/shortbread_v1/tilejson.json"
ATTRIBUTION = (
    '<a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>, '
    'style <a href="https://www.hotosm.org">HOT</a>'
)
REGULAR = ["Noto Sans Regular"]
MEDIUM = ["Noto Sans Medium"]
BOLD = ["Noto Sans Bold"]
KIND = ["get", "kind"]
NAME = ["get", "name"]
ADMIN_LEVEL = ["get", "admin_level"]

# Palette

LAND = "#F7F6F1"
WATER = "#90CCCB"
WATER_TEXT = "#42908F"
BUILDING = "#DCD7D7"
BUILDING_EDGE = "#C9C3C3"
AEROWAY = "#DDD"
PATH = "#BFA286"
RAIL = "#999"
RAIL_DASH = "#FFF"
COUNTRY_BORDER = "#537076"
STATE_BORDER = "#A59C9B"
COUNTRY_TEXT = "#435"
STATE_TEXT = "#A6A6AA"
CITY_TEXT = "#222"
TOWN_TEXT = "#444"
VILLAGE_TEXT = "#888"
LOCALITY_TEXT = "#AAA"
POI_TEXT = "#537076"
SHOP_TEXT = "#868E90"
ROAD_TEXT = "#525252"
HOUSENUMBER_TEXT = "#797979"
PLACE_DOT = "#FFF"
PLACE_HALO = "rgba(255,255,255,0.66)"
ROAD_HALO = "rgba(255,255,255,0.8)"
SHIELD_TEXT = "#FFF"
STRUCTURE = "#C9C3C3"
AERIALWAY = "#999"
PARK = "#D0DCAE"
CEMETERY = "#D6DED2"
WETLAND_KINDS = ["swamp", "bog", "marsh", "wet_meadow", "string_bog", "reedbed", "wetland"]

LANDUSE = {
    "#F0EEE4": ["residential", "retail"],
    "#D7C8CB": ["industrial", "commercial", "quarry", "railway", "landfill", "brownfield"],
    PARK: ["park", "garden", "playground", "village_green", "recreation_ground",
           "golf_course", "grass", "allotments"],
    "#B2C29D": ["forest", "wood"],
    "#E1E9D6": ["heath", "meadow", "scrub", "grassland"],
    "#DEDDBE": ["farmland", "farmyard", "orchard", "vineyard", "plant_nursery",
                "greenhouse_horticulture", "greenfield"],
    "#E3E9E2": WETLAND_KINDS,
    "#EEE5B2": ["beach", "sand"],
    CEMETERY: ["cemetery", "grave_yard"],
}
SITES = {
    "#E5C6C3": ["hospital"],
    "#E2D6CD": ["school", "college", "university", "kindergarten"],
    "#D1BFAA": ["military", "danger_area"],
}

# Roads


def darken(hex_colour, amount):
    """Darken an #RRGGBB colour by a fraction, e.g. 0.1 for 10%."""
    rgb = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{round(c * (1 - amount)):02X}" for c in rgb)


class RoadClass(NamedTuple):
    fill: str
    casing: str
    kinds: list
    width: dict  # total px by zoom

    @property
    def bridge_casing(self):
        return darken(self.casing, 0.1)


URBAN_ROAD = RoadClass("#F7F6F1", "#DEDDD9", ["residential", "living_street"],
                       {12: 0.5, 13: 1.5, 14: 3.5, 16: 7, 18: 18, 20: 72})
# Up to z16: VersaTiles plus ~15%, so roads stand out. Beyond: close to true
# width, so roads don't hide buildings. Unclassified roads and tracks show
# early because in rural areas they are the network.
ROAD_CLASSES = [
    RoadClass("#A098B0", "#857B9A", ["motorway", "trunk"],
              {5: 0.5, 7: 1, 10: 2.5, 12: 4, 14: 6, 16: 16, 18: 40, 20: 160}),
    RoadClass("#D2938E", "#BD8480", ["primary"],
              {7: 0.5, 9: 1.5, 10: 2.5, 12: 4, 14: 7, 16: 14, 18: 34, 20: 136}),
    RoadClass("#E9CBB0", "#D2B79E", ["secondary"],
              {8: 0.5, 9: 1, 11: 2.5, 14: 6, 16: 9, 18: 28, 20: 112}),
    RoadClass("#DBDE99", "#C5C88A", ["tertiary"],
              {9: 0.5, 10: 1, 12: 2.5, 14: 4.5, 16: 7.5, 18: 24, 20: 96}),
    RoadClass("#E4E1D1", "#CDCABC", ["unclassified", "road", "busway"],
              {11: 0.5, 12: 1.5, 14: 3.5, 16: 7, 18: 20, 20: 80}),
    URBAN_ROAD,
    RoadClass("#E4E1D1", "#CDCABC", ["service"],
              {13: 0.5, 14: 1.5, 16: 3.5, 18: 11, 20: 44}),
    RoadClass("#F0EEE4", "#CCC5A2", ["track"],
              {12: 0.5, 14: 2, 16: 4.5, 18: 12, 20: 48}),
]
# Roads are a single line in the darker casing colour below this zoom.
CASING_FROM_ZOOM = 11
CASING_WIDTH = {11: 0.5, 14: 1, 18: 1.5, 20: 2}
ROAD_KINDS = [kind for road in ROAD_CLASSES for kind in road.kinds]
PATH_KINDS = ["pedestrian", "footway", "path", "cycleway", "steps", "bridleway"]
RAIL_KINDS = ["rail", "narrow_gauge", "light_rail", "tram"]
SHIELD_KINDS = ["motorway", "trunk", "primary", "secondary"]

# POIs

# Simplified icons (icons/poi/low), keyed by the zoom they first show at.
POI_LOW = {14: ["townhall", "fire_station"],
           15: ["government", "university", "police", "bank", "taxi", "hospital"],
           16: ["embassy", "school"]}
POI_LABEL_Z16 = ["townhall", "fire_station", "hospital", "school", "university",
                 "government", "pharmacy"]
POI_LABEL_Z18 = ["courthouse", "bank", "post_office", "bus_stop", "ngo", "guest_house",
                 "hostel", "hotel", "viewpoint", "camp_site", "museum", "embassy",
                 "doctors", "clinic", "library", "theatre", "restaurant", "kindergarten",
                 "cafe", "bar", "studio", "car_rental", "money_transfer", "fuel",
                 "social_facility", "community_centre", "dentist", "arts_centre",
                 "fast_food", "pub", "place_of_worship"]
# Icons are named after tag values. Religion first so worship gets a faith icon.
POI_ICON_KEYS = ["religion", "amenity", "healthcare", "office", "emergency", "man_made",
                 "tourism", "leisure", "historic", "craft", "shop"]
POI_MAIN = ["coalesce", ["get", "amenity"], ["get", "office"], ["get", "tourism"],
            ["get", "leisure"], ["get", "shop"], ["get", "man_made"], ""]
# Shortbread has no area labels, so name areas from their POI point.
# Coloured a darker shade of the area fill, as in HDM.
AREA_LABELS = {darken(PARK, 0.4): ["park", "garden", "nature_reserve", "golf_course"],
               darken(CEMETERY, 0.4): ["grave_yard"]}
AREA_KINDS = [kind for kinds in AREA_LABELS.values() for kind in kinds]


# Helpers

def is_kind(kinds):
    return ["match", KIND, kinds, True, False]


def is_true(key):
    """Shortbread omits false booleans at low zooms, so compare rather than get."""
    return ["==", ["get", key], True]


def by_kind(values, default, key=KIND):
    """A match expression from {output: [kinds]}."""
    expr = ["match", key]
    for output, kinds in values.items():
        expr += [kinds, output]
    return expr + [default]


def interpolate_at(stops, zoom):
    """Linear interpolation of {zoom: value}, zero before the first stop."""
    zooms = sorted(stops)
    if zoom < zooms[0]:
        return 0
    for lo, hi in pairwise(zooms):
        if lo <= zoom <= hi:
            t = (zoom - lo) / (hi - lo)
            return round(stops[lo] + t * (stops[hi] - stops[lo]), 2)
    return stops[zooms[-1]]


def road_width(with_casing):
    """Width by class and zoom. The fill is the casing width minus both edges."""
    zooms = {z for road in ROAD_CLASSES for z in road.width} | set(CASING_WIDTH)
    expr = ["interpolate", ["linear"], ["zoom"]]
    for zoom in sorted(zooms):
        has_edge = not with_casing and zoom >= CASING_FROM_ZOOM
        edges = 2 * interpolate_at(CASING_WIDTH, zoom) if has_edge else 0
        match = ["match", KIND]
        for road in ROAD_CLASSES:
            match += [road.kinds, max(interpolate_at(road.width, zoom) - edges, 0)]
        expr += [zoom, match + [0]]
    return expr


def road_colour(part):
    expr = ["match", KIND]
    for road in ROAD_CLASSES:
        expr += [road.kinds, getattr(road, part)]
    return expr + [LAND]


def road_line_colour():
    return ["step", ["zoom"], road_colour("casing"), CASING_FROM_ZOOM, road_colour("fill")]


def symbol_paint(colour, halo=PLACE_HALO, width=1.5):
    return {"text-color": colour, "text-halo-color": halo, "text-halo-width": width}


NOT_TUNNEL = ["!", is_true("tunnel")]
ABOVE_GROUND = ["all", is_kind(ROAD_KINDS), NOT_TUNNEL]
ROAD = ["all", ABOVE_GROUND, ["!", is_true("bridge")]]
BRIDGE = ["all", ABOVE_GROUND, is_true("bridge")]
TUNNEL = ["all", is_kind(ROAD_KINDS), is_true("tunnel")]
ROAD_SORT = by_kind({7: ["motorway", "trunk"], 6: ["primary"], 5: ["secondary"],
                     4: ["tertiary"], 3: ["unclassified", "road"]}, 1)
ROAD_LAYOUT = {"line-cap": "round", "line-join": "round", "line-sort-key": ROAD_SORT}


# Layers

def base_layers():
    land_kinds = [k for kinds in LANDUSE.values() for k in kinds]
    site_kinds = [k for kinds in SITES.values() for k in kinds]
    river = ["river", "canal"]
    return [
        {"id": "background", "type": "background", "paint": {"background-color": LAND}},
        {"id": "ocean", "type": "fill", "source": "osm", "source-layer": "ocean",
         "paint": {"fill-color": WATER}},
        {"id": "landuse", "type": "fill", "source": "osm", "source-layer": "land",
         "filter": is_kind(land_kinds), "paint": {"fill-color": by_kind(LANDUSE, LAND)}},
        {"id": "wetland-pattern", "type": "fill", "source": "osm", "source-layer": "land",
         "minzoom": 12, "filter": is_kind(WETLAND_KINDS),
         "paint": {"fill-pattern": "pattern/marsh"}},
        {"id": "sites", "type": "fill", "source": "osm", "source-layer": "sites",
         "filter": is_kind(site_kinds), "paint": {"fill-color": by_kind(SITES, LAND)}},
        {"id": "military-pattern", "type": "fill", "source": "osm", "source-layer": "sites",
         "filter": is_kind(["military", "danger_area"]),
         "paint": {"fill-pattern": "pattern/military"}},
        {"id": "water", "type": "fill", "source": "osm", "source-layer": "water_polygons",
         "paint": {"fill-color": WATER}},
        {"id": "pier", "type": "fill", "source": "osm", "source-layer": "pier_polygons",
         "paint": {"fill-color": LAND}},
        {"id": "pier-line", "type": "line", "source": "osm", "source-layer": "pier_lines",
         "paint": {"line-color": LAND, "line-width": [
             "interpolate", ["linear"], ["zoom"], 12, 1, 18, 6]}},
        {"id": "dam", "type": "fill", "source": "osm", "source-layer": "dam_polygons",
         "paint": {"fill-color": STRUCTURE}},
        {"id": "dam-line", "type": "line", "source": "osm", "source-layer": "dam_lines",
         "paint": {"line-color": STRUCTURE, "line-width": [
             "interpolate", ["linear"], ["zoom"], 14, 2, 18, 6]}},
        {"id": "waterway", "type": "line", "source": "osm", "source-layer": "water_lines",
         "filter": NOT_TUNNEL,
         "layout": {"line-cap": "round", "line-join": "round"},
         "paint": {"line-color": WATER, "line-width": [
             "interpolate", ["linear"], ["zoom"],
             9, ["match", KIND, river, 1, 0],
             14, ["match", KIND, river, 4, 1],
             18, ["match", KIND, river, 14, 3]]}},
        {"id": "building", "type": "fill", "source": "osm", "source-layer": "buildings",
         "paint": {"fill-color": BUILDING, "fill-outline-color": BUILDING_EDGE}},
        {"id": "bridge-area", "type": "fill", "source": "osm", "source-layer": "bridges",
         "paint": {"fill-color": LAND, "fill-outline-color": STRUCTURE}},
    ]


def transport_layers():
    rail = ["all", is_kind(RAIL_KINDS), NOT_TUNNEL]
    return [
        {"id": "aeroway", "type": "line", "source": "osm", "source-layer": "streets",
         "minzoom": 11, "filter": is_kind(["runway", "taxiway"]),
         "paint": {"line-color": AEROWAY, "line-width": [
             "interpolate", ["linear"], ["zoom"],
             11, ["match", KIND, "runway", 1, 0],
             14, ["match", KIND, "runway", 16, 2],
             18, ["match", KIND, "runway", 160, 20]]}},
        {"id": "road-tunnel", "type": "line", "source": "osm", "source-layer": "streets",
         "minzoom": 12, "filter": TUNNEL,
         "paint": {"line-color": road_colour("casing"), "line-width": road_width(True),
                   "line-dasharray": [1, 1], "line-opacity": 0.6}},
        {"id": "pedestrian-area", "type": "fill", "source": "osm",
         "source-layer": "street_polygons", "filter": NOT_TUNNEL,
         "paint": {"fill-color": URBAN_ROAD.fill, "fill-outline-color": URBAN_ROAD.casing}},
        {"id": "road-casing", "type": "line", "source": "osm", "source-layer": "streets",
         "minzoom": CASING_FROM_ZOOM, "filter": ROAD, "layout": ROAD_LAYOUT,
         "paint": {"line-color": road_colour("casing"), "line-width": road_width(True)}},
        {"id": "path", "type": "line", "source": "osm", "source-layer": "streets",
         "minzoom": 14, "filter": ["all", is_kind(PATH_KINDS), NOT_TUNNEL],
         "paint": {"line-color": PATH, "line-dasharray": [2, 1], "line-width": [
             "interpolate", ["linear"], ["zoom"], 14, 1, 16, 1.5, 18, 4, 20, 7]}},
        {"id": "road", "type": "line", "source": "osm", "source-layer": "streets",
         "filter": ROAD, "layout": ROAD_LAYOUT,
         "paint": {"line-color": road_line_colour(), "line-width": road_width(False)}},
        {"id": "rail", "type": "line", "source": "osm", "source-layer": "streets",
         "minzoom": 9, "filter": rail,
         "paint": {"line-color": RAIL, "line-width": [
             "interpolate", ["linear"], ["zoom"], 9, 0.5, 14, 2.5, 18, 5]}},
        {"id": "rail-dash", "type": "line", "source": "osm", "source-layer": "streets",
         "minzoom": 14, "filter": rail,
         "paint": {"line-color": RAIL_DASH, "line-dasharray": [3, 3], "line-width": [
             "interpolate", ["linear"], ["zoom"], 14, 1, 18, 3]}},
        # Drawn last so bridges pass over roads and water.
        {"id": "road-bridge-casing", "type": "line", "source": "osm", "source-layer": "streets",
         "minzoom": CASING_FROM_ZOOM, "filter": BRIDGE,
         "layout": {**ROAD_LAYOUT, "line-cap": "butt"},
         "paint": {"line-color": road_colour("bridge_casing"), "line-width": road_width(True)}},
        {"id": "road-bridge", "type": "line", "source": "osm", "source-layer": "streets",
         "filter": BRIDGE, "layout": {**ROAD_LAYOUT, "line-cap": "butt"},
         "paint": {"line-color": road_line_colour(), "line-width": road_width(False)}},
        {"id": "aerialway", "type": "line", "source": "osm", "source-layer": "aerialways",
         "paint": {"line-color": AERIALWAY, "line-width": 1}},
        {"id": "ferry", "type": "line", "source": "osm", "source-layer": "ferries",
         "paint": {"line-color": WATER_TEXT, "line-width": 1, "line-dasharray": [4, 3]}},
    ]


def boundary_layers():
    on_land = ["!", is_true("maritime")]
    country_width = ["interpolate", ["linear"], ["zoom"], 2, 0.6, 6, 1.5, 10, 2.5]
    return [
        {"id": "boundary-state", "type": "line", "source": "osm", "source-layer": "boundaries",
         "filter": ["all", [">", ADMIN_LEVEL, 2], on_land],
         "paint": {"line-color": STATE_BORDER, "line-dasharray": [4, 2], "line-width": [
             "interpolate", ["linear"], ["zoom"], 4, 0.5, 10, 1.5]}},
        {"id": "boundary-country", "type": "line", "source": "osm", "source-layer": "boundaries",
         "filter": ["all", ["==", ADMIN_LEVEL, 2], on_land, ["!", is_true("disputed")]],
         "layout": {"line-join": "round"},
         "paint": {"line-color": COUNTRY_BORDER, "line-width": country_width}},
        {"id": "boundary-disputed", "type": "line", "source": "osm", "source-layer": "boundaries",
         "filter": ["all", ["==", ADMIN_LEVEL, 2], on_land, is_true("disputed")],
         "paint": {"line-color": COUNTRY_BORDER, "line-width": country_width,
                   "line-dasharray": [3, 2]}},
    ]


def label_layers():
    oneway_icon = ["case", is_true("oneway_reverse"), "oneway-reverse", "oneway"]
    return [
        {"id": "oneway", "type": "symbol", "source": "osm", "source-layer": "streets",
         "minzoom": 16, "filter": ["all", ABOVE_GROUND, is_true("oneway")],
         "layout": {"symbol-placement": "line", "symbol-spacing": 150,
                    "icon-image": oneway_icon}},
        {"id": "waterway-label", "type": "symbol", "source": "osm",
         "source-layer": "water_lines_labels", "minzoom": 13,
         "layout": {"symbol-placement": "line", "text-field": NAME, "text-font": REGULAR,
                    "text-size": 11, "text-letter-spacing": 0.1},
         "paint": symbol_paint(WATER_TEXT, ROAD_HALO, 1)},
        {"id": "water-label", "type": "symbol", "source": "osm",
         "source-layer": "water_polygons_labels", "minzoom": 10,
         "layout": {"text-field": NAME, "text-font": REGULAR, "text-size": 12,
                    "text-max-width": 8},
         "paint": symbol_paint(WATER_TEXT, ROAD_HALO, 1)},
        {"id": "street-label", "type": "symbol", "source": "osm", "source-layer": "street_labels",
         "minzoom": 13, "filter": ["has", "name"],
         "layout": {"symbol-placement": "line", "text-field": NAME, "text-font": REGULAR,
                    "text-size": ["interpolate", ["linear"], ["zoom"], 13, 10, 18, 13]},
         "paint": symbol_paint(ROAD_TEXT, ROAD_HALO)},
        {"id": "pedestrian-area-label", "type": "symbol", "source": "osm",
         "source-layer": "streets_polygons_labels",
         "layout": {"text-field": NAME, "text-font": REGULAR, "text-size": 11,
                    "text-max-width": 8},
         "paint": symbol_paint(ROAD_TEXT, ROAD_HALO)},
        {"id": "road-shield", "type": "symbol", "source": "osm", "source-layer": "street_labels",
         "minzoom": 10, "filter": ["all", is_kind(SHIELD_KINDS), ["has", "ref"]],
         "layout": {"symbol-placement": "line", "symbol-spacing": 400,
                    "text-field": ["get", "ref"], "text-font": BOLD, "text-size": 10,
                    "text-rotation-alignment": "viewport",
                    "icon-image": "shield", "icon-rotation-alignment": "viewport",
                    "icon-text-fit": "both", "icon-text-fit-padding": [2, 4, 2, 4]},
         "paint": {"text-color": SHIELD_TEXT}},
        {"id": "housenumber", "type": "symbol", "source": "osm", "source-layer": "addresses",
         "minzoom": 17,
         "layout": {"text-field": ["get", "housenumber"], "text-font": REGULAR, "text-size": 10},
         "paint": symbol_paint(HOUSENUMBER_TEXT, ROAD_HALO, 1)},
    ]


def name_if(mains):
    return ["match", POI_MAIN, mains, NAME, ""]


def poi_layers():
    low_icon = ["step", ["zoom"], ""]
    shown = []
    for zoom, mains in POI_LOW.items():
        shown += mains
        low_icon += [zoom, ["match", POI_MAIN, shown, ["concat", "poi/low/", POI_MAIN], ""]]
    icon = ["coalesce"] + [["image", ["concat", "poi/", ["get", key]]] for key in POI_ICON_KEYS]
    icon.append(["image", ["case", ["has", "shop"], "poi/shop", ""]])
    poi_label = {"text-font": MEDIUM, "text-size": 10, "text-max-width": 8,
             "text-anchor": "top", "text-offset": [0, 0.9], "text-optional": True}
    is_area = ["match", POI_MAIN, AREA_KINDS, True, False]
    airport = ["match", KIND, "aerodrome", "poi/airport", ""]
    airport_or_bus = ["match", KIND, "aerodrome", "poi/airport",
                      ["bus_stop", "bus_station"], "poi/bus_stop", ""]
    return [
        {"id": "area-label", "type": "symbol", "source": "osm", "source-layer": "pois",
         "minzoom": 15, "filter": is_area,
         "layout": {"text-field": NAME, "text-font": REGULAR, "text-size": 11,
                    "text-max-width": 8},
         "paint": symbol_paint(by_kind(AREA_LABELS, POI_TEXT, POI_MAIN))},
        {"id": "transport", "type": "symbol", "source": "osm", "source-layer": "public_transport",
         "filter": is_kind(["aerodrome", "bus_stop", "bus_station"]),
         "layout": {"icon-image": ["step", ["zoom"], airport, 17, airport_or_bus],
                    "text-field": ["step", ["zoom"], "",
                                   12, ["match", KIND, "aerodrome", NAME, ""], 18, NAME],
                    **poi_label},
         "paint": symbol_paint(POI_TEXT)},
        {"id": "poi-low", "type": "symbol", "source": "osm", "source-layer": "pois",
         "minzoom": 14, "maxzoom": 17, "filter": ["!", is_area],
         "layout": {"icon-image": low_icon, "icon-size": 0.8,
                    "text-field": ["step", ["zoom"], "", 16, name_if(POI_LABEL_Z16)], **poi_label},
         "paint": symbol_paint(POI_TEXT)},
        {"id": "poi", "type": "symbol", "source": "osm", "source-layer": "pois", "minzoom": 17,
         "filter": ["!", is_area],
         "layout": {"icon-image": icon,
                    "text-field": ["step", ["zoom"], name_if(POI_LABEL_Z16),
                                   18, name_if(POI_LABEL_Z16 + POI_LABEL_Z18), 19, NAME],
                    **poi_label},
         "paint": symbol_paint(["case", ["has", "shop"], SHOP_TEXT, POI_TEXT])},
    ]


def place_layers():
    big = ["capital", "city", "town"]
    colour = by_kind({COUNTRY_TEXT: ["capital"], CITY_TEXT: ["city"], TOWN_TEXT: ["town"],
                      LOCALITY_TEXT: ["locality"]}, VILLAGE_TEXT)
    # Capitals from z4, cities from z7, towns from z9.
    dot_opacity = ["step", ["zoom"], by_kind({1: ["capital"]}, 0),
                   7, by_kind({0: ["town"]}, 1), 9, 1]
    small = ["locality", "isolated_dwelling", "farm"]
    size = ["interpolate", ["linear"], ["zoom"],
            4, by_kind({9: ["capital"]}, 0),
            7, by_kind({11: ["capital"], 10: ["city"]}, 0),
            9, by_kind({11: ["capital", "city"], 9: ["town"]}, 0),
            11, by_kind({12: ["capital", "city"], 11: ["town"], 10: ["village"]}, 0),
            13, by_kind({14: ["capital", "city"], 12: ["town"], 0: small}, 10),
            15, by_kind({16: ["capital", "city"], 14: ["town"], 9: ["locality"]}, 11),
            18, by_kind({18: ["capital", "city"], 16: ["town"], 12: ["locality"]}, 14)]
    country_size = ["interpolate", ["linear"], ["zoom"],
                    3, ["match", ADMIN_LEVEL, 2, 9, 0],
                    5, ["match", ADMIN_LEVEL, 2, 11, 9],
                    7, ["match", ADMIN_LEVEL, 2, 14, 11],
                    10, ["match", ADMIN_LEVEL, 2, 0, 14]]
    return [
        {"id": "place-dot", "type": "circle", "source": "osm", "source-layer": "place_labels",
         "minzoom": 4, "maxzoom": 11, "filter": is_kind(big),
         "paint": {"circle-color": PLACE_DOT, "circle-stroke-color": colour,
                   "circle-stroke-width": 1.5,
                   "circle-radius": by_kind({3.5: ["capital"], 3: ["city"]}, 2.5),
                   "circle-opacity": dot_opacity, "circle-stroke-opacity": dot_opacity}},
        {"id": "place-label", "type": "symbol", "source": "osm", "source-layer": "place_labels",
         "minzoom": 4,
         "layout": {
             "text-field": NAME,
             "text-font": ["match", KIND, "capital", ["literal", BOLD], ["literal", MEDIUM]],
             "text-size": size,
             "text-transform": ["step", ["zoom"], "none",
                                13, by_kind({"uppercase": big}, "none"), 15, "uppercase"],
             "text-letter-spacing": ["step", ["zoom"], 0, 14, 0.05, 16, 0.1],
             "text-max-width": 8,
             # Beside the dot until z11, then centred once the dots are gone.
             "text-variable-anchor": ["step", ["zoom"], ["literal", ["left", "right"]],
                                      11, ["literal", ["center"]]],
             "text-radial-offset": ["step", ["zoom"], 0.5, 11, 0],
             "symbol-sort-key": ["-", ["coalesce", ["get", "population"], 0]]},
         "paint": symbol_paint(colour)},
        {"id": "boundary-label", "type": "symbol", "source": "osm",
         "source-layer": "boundary_labels", "maxzoom": 11,
         "filter": ["<=", ADMIN_LEVEL, 4],
         "layout": {"text-field": NAME, "text-font": BOLD, "text-max-width": 8,
                    "text-size": country_size,
                    "text-letter-spacing": ["step", ["zoom"], 0, 7, 0.1]},
         "paint": symbol_paint(["match", ADMIN_LEVEL, 2, COUNTRY_TEXT, STATE_TEXT])},
    ]


def style(base_url):
    return {
        "version": 8,
        "name": "Humanitarian",
        "metadata": {"licence": "CC BY 4.0, Humanitarian OpenStreetMap Team"},
        "sources": {"osm": {"type": "vector", "url": TILES, "attribution": ATTRIBUTION}},
        "sprite": f"{base_url}/sprite",
        "glyphs": f"{base_url}/font/{{fontstack}}/{{range}}.pbf",
        "layers": base_layers() + transport_layers() + boundary_layers()
                  + label_layers() + poi_layers() + place_layers(),
    }


if __name__ == "__main__":
    json.dump(style(sys.argv[1].rstrip("/")), sys.stdout, indent=2, ensure_ascii=False)
