# HUMANS.md - Working with AI on FLAT

This guide is for you, the human. Its companion, `AGENTS.md`, is written for AI coding assistants. Agents can use `AGENTS.md` as repository guidance for how FLAT is structured and where to make changes. This file focuses on what AI cannot do for you: setting intent, giving clear prompts, and reviewing edits.

## What these two files do

- `AGENTS.md` teaches the agent FLAT-specific rules: edit priorities, source-of-truth files, function-doc sync expectations, settings security constraints, and validation habits.
- `HUMANS.md` teaches you how to ask for changes and quickly review whether the agent touched the right places.

If FLAT conventions change, update `AGENTS.md` first so future agent sessions inherit correct rules.

## Mental model for this repo

FLAT is a reusable template app. Most requests fit one of these buckets:

1. App behavior/UI in `app.py`
2. Function help docs in `FUNCTION_*.md`
3. Launch or packaging scripts (`run.sh`, `scripts/run.sh`, `scripts/run.bat`, `scripts/build_dmg.sh`, `scripts/build_windows_zip.sh`)
4. Dependencies in `python_requirements.txt`
5. High-level documentation (`README.md`, `QUICKSTART.md`, `CHANGELOG.md`)

For best outcomes, describe the behavior you want, not only the file you want edited.

## Prompting patterns that work

Prefer outcome-based prompts.

| Instead of | Try |
|---|---|
| "Edit `app.py` to change Function 2" | "Make Function 2 include hidden files in extension counts and update its help doc" |
| "Change the settings JSON behavior" | "Add a new Function 0 setting with encryption if sensitive, and document it" |
| "Update script" | "Improve `scripts/run.sh` startup checks for missing Python and keep behavior aligned with `scripts/run.bat`" |

Helpful details to include:

- Function number
- Exact setting or field name
- Expected user-visible message or output
- Platform scope (macOS, Windows, both)
- Whether docs and changelog should be updated

## Diff review checklist

Review carefully if the AI:

- Edited `app.py.bak`, `app_from_ohm.py`, or `app_ohm_full.py` when you asked for normal app changes
- Changed packaging scripts when the request was only about a function or UI behavior
- Changed encryption behavior for sensitive settings fields without explanation
- Updated `README.md` but not the matching `FUNCTION_*.md` for a function behavior change
- Touched runtime artifacts outside the repo (such as files under `~/FLAT-data/`)

Usually, a clean targeted change touches one of these sets:

- One function section in `app.py` plus one matching `FUNCTION_*.md`
- One launcher or packager script plus supporting docs
- `python_requirements.txt` plus import/use guards in `app.py`

## When to ask for a plan first

Ask the agent to show a short plan before editing when work is broad or risky:

- Large refactor of `app.py`
- Any change to sensitive-field encryption or settings persistence model
- Dependency upgrades that may impact packaging/startup
- Cross-platform launcher changes

## Example prompts

Behavior change:

> Update Function 1 to optionally include subfolders recursively. Keep default behavior unchanged, add a toggle in the UI, and update Function 1 documentation.

Settings change:

> Add a new Function 0 setting named `export_prefix`. Keep existing sensitive field handling unchanged and document defaults in the Function 0 help file.

Packaging change:

> Improve macOS DMG build error messages in `scripts/build_dmg.sh` without changing output file naming conventions.

## Working rhythm

1. Make one focused change at a time
2. Validate the touched slice (`py_compile`, script syntax, or doc diff)
3. Keep function docs synced with behavior
4. Keep `AGENTS.md` current as your template evolves
