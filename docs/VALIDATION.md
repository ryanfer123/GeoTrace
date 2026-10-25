# Validation record

Final local and rendered checks: 2026-10-25.

## Reproducible checks

- 18 Python unit and real loopback HTTP tests pass locally.
- Tests use bundled real NASA reference JPEGs for compare/save/export.
- Offline/source failure paths use controlled mocks, not invented scene metrics.
- `node --check` passes for app.js and motion.js.
- An installable wheel builds successfully; archive inspection confirms both
  reference JPEGs and the complete self-hosted frontend assets are included.
- The first API milestone passed GitHub's Python 3.10/3.12/3.13 matrix and wheel build.

## Rendered workflow

Verified in the browser at http://127.0.0.1:8767:

| Check | Result |
| --- | --- |
| Page and source images | Both actual NASA reference images fully loaded at 1200 × 1000 |
| Split control | Keyboard End reached 100 and Home returned to 0 |
| Notes and persistence | Edited notes, saved one investigation, and reopened its comparison |
| Narrow mobile view | 390 px viewport; document width equals 390 px with no horizontal overflow |
| Console | No application errors in the tested flow |
| Reduced motion | Emulated reduce preference: Lenis absent, title visible, no overflow |
| Browser settings | Normal motion preference restored after the check |

Screenshot evidence: [desktop](screenshots/desktop.jpg), [mobile](screenshots/mobile.jpg).
The actual browser window remains a local application; no public deployment was
created. JSON and Markdown response bodies, attachment headers, source provenance,
and storage were also verified in the real loopback HTTP tests.

## Source verification

NASA GIBS WMS 1.1.1 capabilities were downloaded on 2026-10-24. Exact advertised
intervals for MODIS Terra, MODIS Aqua, and VIIRS Suomi NPP were retained, including
gaps. Actual GetMap requests for the Aral Sea on 2001-08-01 and 2023-08-01 returned
JPEG data; the images were visually inspected. Source URLs, retrieval times,
byte counts, and SHA256 hashes are bundled next to them.

The server requests no nearest-date substitution and validates both requested
days against the current catalog. This does not prove cloud-free coverage or
independently establish sensor acquisition timestamps.

## Skills and decisions

- **Awwwards quality + frontend-design:** a satellite-image-led field notebook,
  responsive mineral/forest surfaces, editorial type, original brand mark,
  actual NASA imagery, and quiet source annotations. No award claim is made.
- **Karpathy guidelines:** one local Python application, explicit input contracts,
  focused source-validation tests, no account system or unnecessary cloud stack.
- **Python testing:** regressions cover exact date gaps, malformed input, source
  failures, immutable content-addressed image keys, connection closure, and the
  actual HTTP import/save/export paths.
- **Frontend testing/debugging:** primary flow is initial reference comparison,
  split adjustment, note editing, save, reopen, and export. Desktop, mobile,
  keyboard controls, console health, and reduced motion were verified in the rendered app.

GSAP is the primary animation system; Lenis is the only smooth-scroll engine.
Lenis was chosen over Locomotive Scroll to preserve native document flow. Reduced
motion bypasses both effects. Listeners/ticker resources are removed at cleanup.
Three.js is omitted because geographic imagery should remain legible and there
is no spatial interaction that requires a 3D scene. All library, font, and icon
sources are recorded in [THIRD_PARTY.md](../THIRD_PARTY.md).

## Limits

This is a single-user loopback tool. There is no independent environmental
validation, cloud mask, quantitative reflectance processing, NDVI, burn severity,
or change-area estimator. The default reference workflow works offline; new
scenes and live metadata refresh depend on NASA service/network availability.
