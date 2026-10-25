"""NASA GIBS source selection, date checks, and reproducible provenance."""

from datetime import date, datetime, timezone
import hashlib
import json
import math
import re
import tempfile
from pathlib import Path
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ENDPOINT = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
LAYER_NAMES = {
    "MODIS_Terra_CorrectedReflectance_TrueColor": "MODIS Terra · true color",
    "MODIS_Aqua_CorrectedReflectance_TrueColor": "MODIS Aqua · true color",
    "VIIRS_SNPP_CorrectedReflectance_TrueColor": "VIIRS Suomi NPP · true color",
}
SNAPSHOT = Path(__file__).parent / "data/layers.json"


def now():
    return datetime.now(timezone.utc).isoformat()


def available(day, intervals):
    try:
        if not isinstance(day, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            raise ValueError("Invalid ISO date")
        selected = date.fromisoformat(day)
    except (ValueError, TypeError):
        raise ValueError("Dates must use YYYY-MM-DD.") from None
    for interval in intervals:
        parts = interval.split("/")
        if len(parts) == 1 and selected == date.fromisoformat(parts[0]):
            return True
        if (
            len(parts) == 3
            and parts[2] == "P1D"
            and date.fromisoformat(parts[0]) <= selected <= date.fromisoformat(parts[1])
        ):
            return True
    return False


def validate_investigation(data, catalog):
    if not isinstance(data, dict):
        raise ValueError("Investigation must be a JSON object.")
    name, notes = data.get("name", ""), data.get("notes", "")
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 120:
        raise ValueError("Give this investigation a name of 1 to 120 characters.")
    if not isinstance(notes, str) or len(notes) > 10000:
        raise ValueError("Notes must be text, at most 10,000 characters.")
    bounds = data.get("bounds")
    if (
        not isinstance(bounds, list)
        or len(bounds) != 4
        or any(
            type(n) not in (int, float) or abs(n) > 1000000 or not math.isfinite(n)
            for n in bounds
        )
    ):
        raise ValueError(
            "Bounds must be four finite numbers: west, south, east, north."
        )
    west, south, east, north = bounds
    if not (-180 <= west < east <= 180 and -85 <= south < north <= 85):
        raise ValueError(
            "Use west < east within ±180° and south < north within ±85°. Antimeridian crossing is not supported."
        )
    if not (0.01 <= east - west <= 90 and 0.01 <= north - south <= 90):
        raise ValueError("Each bounding-box span must be between 0.01° and 90°.")
    layer = next((x for x in catalog["layers"] if x["id"] == data.get("layer")), None)
    if layer is None:
        raise ValueError("Choose a supported satellite layer.")
    before, after = data.get("before"), data.get("after")
    for day in (before, after):
        if not available(day, layer["intervals"]):
            raise ValueError(
                f"{day} is not advertised for this layer in the {catalog['verified']} metadata. Choose another day or refresh the metadata."
            )
    if before >= after:
        raise ValueError("The second date must be later than the first date.")
    return {
        "name": name.strip(),
        "notes": notes,
        "bounds": [float(x) for x in bounds],
        "layer": layer["id"],
        "before": before,
        "after": after,
    }


def image_url(spec, day):
    west, south, east, north = spec["bounds"]
    height = max(240, min(1200, round(1200 * (north - south) / (east - west))))
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetMap",
        "LAYERS": spec["layer"],
        "STYLES": "",
        "FORMAT": "image/jpeg",
        "SRS": "EPSG:4326",
        "BBOX": ",".join(f"{v:g}" for v in spec["bounds"]),
        "WIDTH": 1200,
        "HEIGHT": height,
        "TIME": day,
    }
    return ENDPOINT + "?" + urllib.parse.urlencode(params)


def fetch_bytes(url, limit=8 * 1024 * 1024):
    # Only internal callers construct URLs; there is no arbitrary proxy endpoint.
    if not url.startswith(ENDPOINT + "?"):
        raise ValueError("Unsupported imagery endpoint.")
    request = urllib.request.Request(
        url, headers={"User-Agent": "GeoTrace/0.1 (local investigation workbench)"}
    )
    with urllib.request.urlopen(request, timeout=35) as response:
        data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError("NASA response exceeds the download limit.")
        return data, response.headers.get("Content-Type", "")


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile(
        dir=path.parent, suffix=".tmp", delete=False
    ) as temporary:
        temporary.write(data)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def fetch_image(url, cache):
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()
    path = cache / (key + ".jpg")
    metadata_path = cache / (key + ".json")
    reference = SNAPSHOT.parent / "reference"
    if not path.exists() and (reference / (key + ".jpg")).exists():
        atomic_write(path, (reference / (key + ".jpg")).read_bytes())
        atomic_write(metadata_path, (reference / (key + ".json")).read_bytes())
    if path.exists() and metadata_path.exists():
        try:
            image = path.read_bytes()
            metadata = json.loads(metadata_path.read_text())
            if hashlib.sha256(image).hexdigest() == metadata["sha256"]:
                metadata["key"] = metadata["sha256"]
                content_path = cache / (metadata["key"] + ".jpg")
                if not content_path.exists():
                    atomic_write(content_path, image)
                return metadata
        except (OSError, ValueError, KeyError):
            pass  # A damaged local cache is re-fetched, never presented as verified.
    image, kind = fetch_bytes(url)
    if "image/jpeg" not in kind or not image.startswith(b"\xff\xd8"):
        raise ValueError(
            "NASA returned no JPEG image. This date or area may be unavailable."
        )
    metadata = {
        "key": hashlib.sha256(image).hexdigest(),
        "url": url,
        "sha256": hashlib.sha256(image).hexdigest(),
        "bytes": len(image),
        "fetched_at": now(),
        "content_type": "image/jpeg",
    }
    atomic_write(path, image)
    atomic_write(cache / (metadata["key"] + ".jpg"), image)
    atomic_write(metadata_path, json.dumps(metadata, indent=2).encode())
    return metadata


def refresh_catalog():
    url = ENDPOINT + "?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetCapabilities"
    content, _ = fetch_bytes(url, 4 * 1024 * 1024)
    root = ET.fromstring(content)
    layers = []
    for layer in root.findall(".//Layer"):
        identifier = layer.findtext("Name")
        if identifier in LAYER_NAMES:
            extent = next(
                (e for e in layer.findall("Extent") if e.get("name") == "time"), None
            )
            if extent is not None and extent.text:
                intervals = extent.text.split(",")
                # Validate dates before retaining remote metadata.
                for interval in intervals:
                    for value in interval.split("/")[:2]:
                        date.fromisoformat(value)
                layers.append(
                    {
                        "id": identifier,
                        "name": LAYER_NAMES[identifier],
                        "intervals": intervals,
                        "default_date": extent.get("default"),
                    }
                )
    if len(layers) != len(LAYER_NAMES):
        raise ValueError("NASA metadata did not contain all supported layers.")
    return {
        "verified": date.today().isoformat(),
        "endpoint": ENDPOINT,
        "layers": layers,
    }


def markdown_report(record):
    spec = record["spec"]
    lines = [
        "# " + spec["name"],
        "",
        f"Created: {record['created']}",
        f"Layer: {spec['layer']}",
        f"Bounds (west, south, east, north): {spec['bounds']}",
        "CRS: EPSG:4326; WMS 1.1.1 longitude/latitude ordering.",
        f"Metadata verified: {record['catalog_verified']}",
        "",
        "## Observation notes",
        "",
        spec["notes"] or "No observations recorded.",
        "",
        "## Source provenance",
        "",
    ]
    for label, source in record["sources"].items():
        lines.extend(
            [
                f"### {label.title()} · {spec[label]}",
                f"URL: {source['url']}",
                f"SHA256: {source['sha256']}",
                f"Fetched: {source['fetched_at']}",
                f"Bytes: {source['bytes']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation limits",
            "",
            "NASA GIBS browse imagery is for visual inspection. Cloud, haze, season, viewing geometry, missing observations, and processing can change appearance. These RGB images are not quantitative reflectance measurements. No NDVI, burn severity, land-loss area, or causal attribution is computed.",
            "",
            "Imagery: NASA EOSDIS Global Imagery Browse Services (GIBS).",
            "Documentation: https://nasa-gibs.github.io/gibs-api-docs/access-basics/",
        ]
    )
    return "\n".join(lines) + "\n"
