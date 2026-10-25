# Contributing

Keep the distinction between visual observation and quantitative environmental
measurement explicit. Browse JPEG imagery must not be described as raw scientific
reflectance or used to claim vegetation indices, land-loss areas, or attribution.

Run `python -m unittest discover -s tests -v`. Retrieval tests use actual bundled
NASA reference images; network failures use controlled mocks. Source URL changes
must include an axis-order test and a provenance test. Keep cached image keys
content-addressed so a later reprocessed source cannot silently alter a saved view.

Frontend changes need desktop and mobile checks, keyboard-accessible controls,
visible validation feedback, and reduced-motion support. No changes should require
accounts, paid APIs, or credentials for the default offline reference workflow.
