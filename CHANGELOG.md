# CORE Changelog

All notable changes to the CORE (Collection Object Record Editor) project are documented in this file.

The format is based on Keep a Changelog,
and this project follows Semantic Versioning.

## [Unreleased]

### Added
- DART-style version history foundation:
  - Added root VERSION file as the single source of truth for the app version.
  - Added runtime version loading in app.py via get_app_version() and APP_VERSION.
  - Updated UI title/header/status to display the active version.
- Per-save backup workflow in `.CORE-working-directory` beside the active CSV.
- `CORE-settings.json` support for per-field characteristics.
- Session-only **Unhide/Enable All** action to temporarily override hidden/disabled settings.

### Changed
- Replaced inherited FLAT template changelog content with CORE-specific history.
- Source flow is now CSV-first (project folder picker removed from active workflow).
- Record details layout is now a 75/25 split with vertical action buttons on the right.
- Diagnostics is now a compact panel that can expand to show status/log details.
- Header is more compact and combines app name/version into a single line.
- Settings filename changed from `.CORE-settings.json` to `CORE-settings.json`.
- Disabled fields now use more pronounced subdued text styling for clearer distinction from editable fields.

### Fixed
- Preserved CSV dialect on read/write to reduce delimiter/format mismatches.
- Added safe CSV writer handling for `QUOTE_NONE` dialects without an escape character.
- Save flow now writes through a temp file in `.CORE-working-directory` before atomic replacement of the source CSV.

## [1.0.0] - 2026-06-25

### Added
- Initial CORE single-record editor release.
- Project folder and CSV file selection with auto-discovery for likely metadata CSV files.
- Single-record dropdown selection and generated field-edit form based on CSV headers.
- In-place row editing and CSV write-back to the selected metadata file.
- New record creation for metadata files that need additional rows.
- Persistent local state in ~/CORE-data/ for last folder, CSV path, and selected record.
- Script reorganization into scripts/ with root run.sh compatibility shortcut.
