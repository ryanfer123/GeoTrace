# GeoTrace

An earth-observation notebook for comparing satellite browse images across two
dates. Choose a place, inspect a shared geographic view, record what you see, and
save the exact source requests alongside your notes.

![GeoTrace homepage](docs/screenshots/home-desktop.png)

## Run

```sh
git clone https://github.com/ryanfer123/GeoTrace.git
cd GeoTrace
python3 -m geotrace
```

Open **http://127.0.0.1:8767** for the homepage, then choose **Open workspace**
or visit **http://127.0.0.1:8767/workspace**. Python 3.10+ is sufficient; the local
analysis runtime uses the standard library. Local investigations live in SQLite,
and browser fonts, icons, and motion libraries are served from the application.

The homepage and default workspace use a real Aral Sea MODIS Terra reference pair from **2001-08-01** and
**2023-08-01**. Both original NASA GIBS JPEGs are bundled with request provenance,
so this comparison works offline. New dates or areas require a connection to NASA.

## What you can do

- Select Aral Sea, Lake Urmia, northern California, or a custom geographic box.
- Choose among MODIS Terra, MODIS Aqua, and VIIRS Suomi NPP true-color layers.
- Compare dates with a keyboard/touch-accessible split slider.
- Inspect exact NASA requests, download sizes, retrieval times, and SHA256 hashes.
- Save observation notes and reopen investigations after restarting the app.
- Export complete investigation JSON or a readable Markdown report.
- Refresh NASA's advertised date availability when the bundled metadata gets old.
- Optionally sign in through **Cloud notebook** to save private copies in Supabase.

## A traceable visual workflow

Enter bounds as **west, south, east, north** in decimal degrees. The server uses
**WMS 1.1.1, EPSG:4326**, with explicit longitude/latitude order and an explicit
`TIME` value for each image. Both images use the same layer, bounds, and dimensions.
Antimeridian-crossing boxes are not currently supported.

Dates are checked against the exact daily intervals NASA advertises, including
gaps. No nearest-date substitution is requested. An advertised day can still have
clouds, missing coverage, or a blank scene. Source failures are shown explicitly.
The metadata snapshot was verified on 2026-10-24; the refresh button updates the
current server session's catalog.

The local cache validates image signatures and hashes, and local saved image keys
are content-addressed. A later reprocessed NASA image does not silently replace a
local cached snapshot. Cloud copies retain the selected specification, notes, and
source metadata; reopening a cloud copy validates and reloads the sources, rather
than trusting stored image URLs. Hosted views request imagery directly from NASA.
Reports retain source URLs, response hashes, request dates, metadata dates, and
retrieval times. The dates label requested
GIBS data days, not an independent verification of sensor acquisition timestamps.

## Interpretation limits

These are browse images for **visual inspection**. Clouds, haze, season, view angle,
missing observations, sensor differences, and processing can affect appearance.
The application does not compute NDVI, burn severity, water-loss area, or causal
attribution. A visual difference is an observation to investigate, not an automatic
environmental conclusion.

## Development and checks

```sh
python3 -m unittest discover -s tests -v
python3 -m pip wheel . --no-deps -w dist
```

The suite covers date gaps, geometry validation, WMS axis order, source errors,
cache integrity, immutable saved images, closed database connections, local request
boundaries, and the complete compare/save/export HTTP workflow. The wheel packages
all frontend assets and NASA reference images. GitHub Actions tests Python 3.10,
3.12, and 3.13 and builds the package.

Use a separate local workspace when needed:

```sh
python3 -m geotrace --port 8792 --database field.sqlite3 --cache .field-images
```

## Optional private cloud copies and hosting

**Cloud notebook** connects directly from the browser to Supabase Auth and the
private investigation table using a publishable key and the signed-in user's
access token. Saving creates a new private copy; local work stays local until that
explicit action. Restoring a copy recomputes a validated comparison through the
normal API. See [SUPABASE.md](SUPABASE.md) for public configuration, RLS, session
behavior, and verification boundaries.

In local mode, SQLite and cached images stay on the same computer. In hosted mode,
computation is stateless and current work is temporary in the browser tab until
saved as a private cloud copy or exported. [DEPLOYMENT.md](DEPLOYMENT.md) documents
the Vercel build, routing, browser-session adapter, and operational limits.
GeoTrace remains a visual investigation tool, not a scientific raster-processing
pipeline.

## Design and assets

The image-led interface follows a field-notebook direction: mineral surfaces,
forest-green controls, editorial typography, and quiet source annotations. GSAP
introduces the headline and image frame. Lenis is the sole smooth-scroll engine;
reduced motion bypasses it. Three.js is omitted because the source imagery should
remain readable and geographic controls should stay in normal document flow.

[Asset provenance](THIRD_PARTY.md) lists exact dependencies and image sources.
[Contributing](CONTRIBUTING.md) describes the development contract.
[Validation evidence](docs/VALIDATION.md) records tests and desktop/mobile checks.

## Sources and license

Imagery: **NASA EOSDIS Global Imagery Browse Services (GIBS)**.
[Service documentation](https://nasa-gibs.github.io/gibs-api-docs/access-basics/)
describes supported WMS endpoints, time dimensions, and projections.

Application source: MIT. Third-party assets retain their original terms; see
[THIRD_PARTY.md](THIRD_PARTY.md).
