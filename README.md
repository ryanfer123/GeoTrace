# GeoTrace

A local investigation desk for comparing NASA satellite browse imagery across two
dates, retaining geographic bounds, observation notes, and exact source provenance.

The first milestone implements source/date validation, real-image caching,
SQLite investigation storage, and JSON/Markdown exports. The comparison interface
is being built next.

```sh
python3 -m geotrace
```

Open http://127.0.0.1:8767. Python 3.10+; no Python runtime dependencies or API keys.
The bundled Aral Sea reference pair is real MODIS Terra imagery requested from
NASA GIBS for 2001-08-01 and 2023-08-01. Other scenes require internet access.

Browse imagery supports visual investigation. It does not establish NDVI, burn
severity, water-loss area, or causal attribution. Clouds, season, missing data,
and viewing geometry can change appearance.

```sh
python3 -m unittest discover -s tests -v
```

Sources: [NASA GIBS access documentation](https://nasa-gibs.github.io/gibs-api-docs/access-basics/).
