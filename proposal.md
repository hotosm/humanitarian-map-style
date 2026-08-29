# Proposal

Rebuild the Humanitarian style for OpenStreetMap as vector tiles.

OSM already publishes free vector tiles at `vector.openstreetmap.org`, on the
Shortbread v1 schema, minutely fresh. So we build only what those don't give
us, in three stages, and stop when the next stops being worth it.

Served from `hdm-style.hotosm.org`, split by path.

## Stage 1 - Style on OSM's tiles

No infrastructure, under $1/month.

- Port the palette, road widths and POI rules. See
  [docs/cartography.md](./docs/cartography.md).
- Build the sprite from `icons/` with **spreet**.
- Fetch Noto with `fonts/fetch.sh`, build glyphs with **pbf_font_tools**.
- Point the style at `vector.openstreetmap.org`.
- Publish `style.json`, sprite and glyphs to S3.

This is the destination, not a stepping stone. Later stages only add to it.

## Stage 2 - Humanitarian overlay

Shortbread drops the attributes this style exists to show. Most are sparse
points and polygons, so they can be a second small source layered on top:
damaged and collapsed buildings, `healthcare=*`, water points and storage,
power.

Built from a filtered extract with **tilemaker**. Small enough to rebuild
daily, ~$5/month.

Limit: we can add to OSM's tiles, never suppress or restyle what they draw.

## Stage 3 - Our own planet tiles

Only **road surface** forces a full planet build. It is an attribute of road
geometry, and MapLibre cannot style one source using another source's data, so
it cannot be an overlay.

The tradeoff: minutely tiles become weekly, to gain one attribute.

**Decision gate.** Measure a tilemaker planet build first. Estimates run 8-20
hours, a 2.5x spread that changes the economics, and a roads-only build is much
smaller than full Shortbread. Go ahead only if it fits the cadence we want.

## Pipeline

One Kubernetes CronJob, weekly.

| Step | What happens | Tool |
| --- | --- | --- |
| 1 | Provision a spot node with local NVMe | Karpenter |
| 2 | Update the local planet file from diffs | pyosmium / osmium-tool |
| 3 | Generate tiles | tilemaker |
| 4 | Upload under a dated key | aws-cli |
| 5 | Publish `style.json` pointing at the new key | aws-cli |
| 6 | Delete archives older than 21 days | S3 lifecycle rule |

**Node.** `r6id.4xlarge` or similar: 16 vCPU, 128 GB RAM, ~950 GB instance-store
NVMe included with the node. Exists only for the build; scaling to zero between
runs is the main cost control.

**Planet update.** A 150 GB gp3 volume keeps `planet.osm.pbf` and its
replication state between runs, so we apply diffs rather than re-downloading.

**Dated keys, never overwrites.** A PMTiles client reads an archive over many
range requests using offsets learned earlier, and CloudFront caches those ranges
independently. Overwrite the file and clients read the wrong bytes.

**Release.** `style.json` names the archive it was built against, so rewriting
that one small object is the release. Rollback is editing the URL back. Clients
only ever see `style.json`.

**Retention.** S3 expires by age, not count. 21 days leaves 3 archives at
$1.84 each per month - current, plus two to roll back to.

**On failure.** `style.json` is not rewritten and the previous archive keeps
serving. The map goes stale rather than down.

## Hosting

One bucket, one CloudFront distribution.

| Path | Contents | Cache-Control |
| --- | --- | --- |
| `/style.json` | The style, and the release pointer | `max-age=300` |
| `/sprite@2x.{png,json}` | Icon sprite | `max-age=86400` |
| `/font/{stack}/{range}.pbf` | SDF glyphs | `immutable` |
| `/tiles/hdm-YYYY-MM-DD.pmtiles` | The archive, ~80 GB | `immutable` |

Two things that break the map silently: CORS must be open, and tiles must be
served `Content-Encoding: gzip` with CloudFront compression off for that prefix.

## Cost

| Stage | Monthly |
| --- | --- |
| 1 - style, sprite, glyphs | <$1 |
| 2 - overlay, rebuilt daily | ~$5 |
| 3 - weekly planet build | ~$37 |

Stage 3 breakdown, us-east-1 list prices. Verify before budgeting.

| Line | Sizing | Monthly |
| --- | --- | --- |
| Build compute | `r6id.4xlarge` spot, ~10 h x 4 runs | $18 |
| Persistent gp3 | 150 GB | $12 |
| S3 storage | 3 archives x ~80 GB | $6 |
| Build scratch | instance-store NVMe | $0 |
| CloudFront egress | under the 1 TB free tier | $0 |

Faster cadences buy little: twice weekly ~$56, daily ~$145. Daily also leaves as
little as 4 hours slack per cycle, so runs would overlap and the node would
never scale to zero.

Egress stays free for a long time. A session is ~3-8 MB, so 200,000
sessions/month is about 1 TB, the edge of the free tier. Past that, front S3
with Cloudflare or apply to the AWS Open Data Sponsorship Program.

## Not doing

- **Minutely updates.** osm2pgsql, ~1 TB of NVMe, constant attention - what got
  HDM-CartoCSS archived. Stage 1 gives us minutely for free.
- **Daily planet rebuilds.** 7x the compute for content that barely changes.
- **Style inside the archive.** Different lifecycles, and separating them is
  what makes the release a small atomic write.
