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

### Changed
- Replaced inherited FLAT template changelog content with CORE-specific history.

## [1.0.0] - 2026-06-25

### Added
- Initial CORE single-record editor release.
- Project folder and CSV file selection with auto-discovery for likely metadata CSV files.
- Single-record dropdown selection and generated field-edit form based on CSV headers.
- In-place row editing and CSV write-back to the selected metadata file.
- New record creation for metadata files that need additional rows.
- Persistent local state in ~/CORE-data/ for last folder, CSV path, and selected record.
- Script reorganization into scripts/ with root run.sh compatibility shortcut.
