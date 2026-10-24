# GeoTrace

Build a local investigation desk for comparing satellite browse imagery across two
dates. The focal asset is real NASA GIBS imagery, displayed in an aligned swipe
comparison with clear dates and bounds. Selecting a preset or entering a bounding
box defines the area; every saved investigation retains exact source URLs and notes.

Art direction: an earth-observation field desk, forest ink #163D35, pale mineral
#EEF2ED, warm white #FAFBF6, muted moss #6B8172, copper #AF642E. Use local Manrope
for controls, Georgia for an editorial observation headline. The image comparison
owns the first viewport; controls and notebook occupy a quieter side panel.

Use the Awwwards quality skill with frontend-design. GSAP introduces the headline
and image frame; Lenis is the sole smooth-scroll engine (chosen over Locomotive to
preserve native scroll layout). Reduced motion bypasses effects. No Three.js is
needed: geographic imagery should stay readable. Solar icons come from Iconify;
NASA imagery is credited and comes with exact request provenance. No invented
environmental metrics or endorsements.

Implementation: strict bounds/date/layer validation, fixed NASA WMS endpoint,
SQLite investigations, cached image responses, JSON/Markdown export, responsive
comparison UI, unit and HTTP integration tests, packaged static assets, and
verified GitHub milestones.
