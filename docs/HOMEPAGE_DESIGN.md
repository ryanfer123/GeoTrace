# Homepage direction

The homepage introduces GeoTrace as an observation notebook before opening the
working comparison tool at `/workspace`. The original tool is preserved as
`workspace.html`; its API and state flow are not redesigned here.

## Art direction before implementation

- **Visual thesis:** an earth-observation journal whose primary visual is the
  evidence itself. The hero is an actual, aligned Aral Sea image pair, not a mock
  dashboard or generated landscape. A user-operated split gives the first viewport
  a useful interaction immediately.
- **Palette:** forest ink `#163D35`, deep pine `#193E34`, pale mineral `#EEF2ED`,
  warm white `#FAFBF6`, moss `#6B8172`, and subdued brass `#A28A51`.
- **Typography:** locally served Manrope for navigation, controls, and body text;
  Georgia for large editorial headings. Headlines remain a single accessible name
  when decorative word spans animate.
- **Layout:** a broad two-column introduction and image comparison, followed by
  a real three-step workflow, a source-provenance section, a notebook/export
  section, practical questions, and a final workspace CTA. Left-aligned copy,
  restrained borders, no decorative metric cards or endorsement wall.
- **Motion:** one GSAP intro sequence, then modest section-heading reveals.
  Lenis is the sole smooth-scroll engine, selected over Locomotive Scroll to keep
  native document flow and simple anchor navigation. Reduced motion bypasses both
  systems. The image split is always under user control. No pointer-only effects.
- **Three.js:** omitted. A scene would obscure the real imagery and add no useful
  geographic capability.
- **Assets:** reuse the two original NASA GIBS reference JPEGs and their existing
  source metadata. Use existing licensed local font/motion bundles and Solar
  icons from the already installed Iconify package. No new portraits, invented
  imagery, logo endorsements, or environmental measurements.

## Review against the brief

A conventional SaaS hero with a decorative product screenshot was rejected. The
actual source-image split is the focal asset and also demonstrates the product's
central action. Pale mineral surfaces stay consistent with the workspace, while a
pine workflow section gives the longer page a clear change of pace. The copy
promises only implemented visual comparison, notes, provenance, and exports.

Root owns backend routes, Supabase integration, and authentication UI. This page
adds no speculative account features or cloud-status claims. All main CTAs lead
to the actual `/workspace` route.
