# Asset provenance

| Asset | Source | Version / date | Terms |
| --- | --- | --- | --- |
| Satellite reference pair | NASA EOSDIS GIBS, MODIS Terra corrected reflectance true color | 2001-08-01 and 2023-08-01, Aral Sea bounds 56,42,62,47 | NASA imagery; credited in UI and every exported report; original request URLs and SHA256 are retained next to each image |
| Manrope font | `@fontsource-variable/manrope` | 5.3.0 | SIL Open Font License; bundled notice |
| GSAP and ScrollTrigger | `gsap` | 3.15.0 | GSAP Standard License; original bundled notices preserved |
| Lenis | `lenis` | 1.3.27 | MIT; bundled notice |
| Solar line icons | `@iconify-json/solar` via Iconify | 1.2.13 | Solar by [480 Design](https://www.figma.com/community/file/1166831539721848736), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

Solar icons used: `layers-linear`, `refresh-linear`, `document-add-linear`,
`map-point-linear`, and `eye-linear`. Their colors and dimensions adapt to the
interface. The small `gt` brand mark is original. No portraits, endorsements,
company logos, fake map artwork, or generated satellite imagery are included.

Reference image JPEG files and their provenance JSON are in `geotrace/data/reference`.
The metadata catalog snapshot was downloaded from NASA GIBS capabilities on
2026-10-24, preserving exact advertised daily intervals, including gaps.

NASA service documentation: https://nasa-gibs.github.io/gibs-api-docs/access-basics/
NASA Earthdata imagery background: https://www.earthdata.nasa.gov/data/tools/gibs

The application source is MIT licensed. Third-party browser assets retain their
own terms in `geotrace/web/vendor`.


## Homepage assets

The homepage reuses the same original NASA reference pair at
`geotrace/web/home-assets/aral-earlier.jpg` and `aral-later.jpg`. Their source URLs,
retrieval times, byte counts, and SHA256 hashes are retained in the adjacent
`provenance.json`. Hero and detail crops are presentation crops of those original
browse images; the comparison workspace retains the full requested view.

Additional homepage Solar icons from the same credited Iconify package:
`arrow-right-up-linear`, `arrow-down-linear`, `hamburger-menu-linear`,
`double-alt-arrow-left-linear`, `notebook-linear`, `check-circle-linear`,
`document-text-linear`, and `code-square-linear`. Existing map, layers, and eye
icons are reused. No new imagery source or external font service is introduced.
