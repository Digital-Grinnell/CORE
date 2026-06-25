# FLAT - AI Agent Instructions

FLAT is a Python desktop application template built with Flet. It is designed as a reusable foundation for workflow tools, with persistent UI state, per-project app settings, logging, function dispatch, and function-specific markdown help.

This repository currently ships example functions (0 to 3):

- Function 0: App Settings (with encrypted sensitive fields)
- Function 1: List Files in an input folder
- Function 2: Count Files by extension
- Function 3: System Information

Companion file in this repo: `HUMANS.md` is the human-facing guide for working with AI on FLAT.

## Change Priority Order

Always make the smallest change at the highest appropriate layer before editing lower-level runtime code:

1. `FUNCTION_*.md`, `README.md`, `QUICKSTART.md`, and related docs for behavior clarification
2. Targeted launch/packaging scripts (`run.sh`, `run.bat`, `build_dmg.sh`, `build_windows_zip.sh`)
3. `python_requirements.txt` for dependency changes
4. `app.py` for core application logic and UI behavior
5. Backup or generated artifacts only when explicitly requested

If the issue is documentation, usage text, or function help wording, do not edit `app.py` first.

## Critical Rules

### Source of Truth
- Treat `app.py` as the active runtime source
- Do not edit `app.py.bak`, `app_from_ohm.py`, or `app_ohm_full.py` unless explicitly requested
- Keep function docs synchronized with user-visible behavior

### Settings and Security
- Function 0 settings are stored in `flat_settings.json` inside the selected working/output folder
- Sensitive fields are encrypted by app logic; do not bypass or remove encryption behavior casually
- Do not hardcode credentials, API keys, or machine-specific secrets in tracked source files

### Runtime Data and Logs
- Runtime state is stored outside the repo under `~/FLAT-data/`
- Typical runtime artifacts include `persistent.json` and `logfiles/`
- Do not treat runtime logs or user-generated settings files as code edit targets

### Folder Terminology
- Use "folder" in user-facing content
- "directory" is acceptable in technical implementation comments but prefer "folder" in docs and UI text

### Function-Specific Documentation
- When behavior changes for Function 0 through Function 3, update the matching `FUNCTION_*.md`
- Keep `README.md` or `QUICKSTART.md` aligned when behavior affects broader onboarding

### Packaging and Launchers
- `run.sh` and `run.bat` are launch scripts
- `build_dmg.sh` and `build_windows_zip.sh` are distribution scripts
- Avoid packaging changes for requests that are purely workflow/UI logic

## Ask Before Doing These

Explain plan and ask for confirmation before:

- Refactoring large sections of `app.py` for small behavior tweaks
- Changing encryption handling for sensitive settings fields
- Renaming or removing existing function IDs/labels that affect workflow docs
- Broad dependency upgrades that may alter packaging/runtime behavior
- Deleting backup files, historical notes, or release-related artifacts

## FLAT Surface Map

| File or Area | What it controls |
|---|---|
| `app.py` | Main Flet app, function handlers, dialogs, state persistence wiring, logging |
| `FUNCTION_0_APP_SETTINGS.md` | User help for Function 0 settings and encryption behavior |
| `FUNCTION_1_LIST_FILES.md` | User help for Function 1 behavior |
| `FUNCTION_2_COUNT_FILES.md` | User help for Function 2 behavior |
| `FUNCTION_3_SYSTEM_INFO.md` | User help for Function 3 behavior |
| `README.md` / `QUICKSTART.md` | Onboarding and high-level usage |
| `run.sh` / `run.bat` | Cross-platform launch behavior |
| `build_dmg.sh` / `build_windows_zip.sh` | Packaging workflows |
| `python_requirements.txt` | Python dependency set |

## Common Mistakes to Avoid

1. Editing `app.py.bak` or legacy reference files instead of `app.py`
2. Changing function runtime behavior without updating its `FUNCTION_*.md` help file
3. Treating runtime artifacts in `~/FLAT-data/` as repository source files
4. Modifying packaging scripts for a request that only needs app behavior/docs changes
5. Weakening or removing sensitive-field encryption in Function 0
6. Replacing user-facing "folder" language with more technical wording in docs/UI

## Validation

Use focused validation for touched areas:

```bash
python3 -m py_compile app.py
bash -n run.sh build_dmg.sh build_windows_zip.sh
```

For docs-only changes, a focused diff review is sufficient.

## Working Instructions

When handling a task:

1. Identify whether it is docs, runtime app behavior, launcher/packaging, or dependencies
2. Read the closest relevant file first instead of broad rewrites
3. Prefer minimal edits preserving current function model and terminology
4. Update matching docs when user-visible behavior changes
5. Validate the changed slice before finishing
