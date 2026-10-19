# Spec Review — Cleanup & Prepare for GitHub

**Branch**: `005-cleanup-prepare-github`
**Date**: 2026-10-18

## Round 1 (FAIL)
**Issue (blocking, constitution VIII)**: FR-001 removed `TECH_STACK.md`, but the constitution requires a documented tech stack ("HALT if undocumented"). Removing it outright was non-landable.

**Fix (applied)**: keep `TECH_STACK.md` in the public tree (remove it from the deletion list). Remaining deletions: `specs/000---example-sprint/`, `HANDOFF_RESUME.md`, `PRODUCT_PLAN.md` (recoverable from history).

## Post-review additions (owner-decided)
- **Rename plugin/repo to `hermes-second-thoughts`** (Dustin chose the `hermes-` prefix, official style). Folded into FR-003 (manifest name, version 0.2.0, homepage, author), FR-006/FR-008/US3/SC-004 (repo/install/push URLs).
- **FR-010 added**: reinstall the LIVE plugin under the new name (`~/.hermes/plugins/hermes-second-thoughts/`, dir = manifest name to avoid the enable/list key mismatch), retire the old `second-thoughts` install.

## Review Result
Round 1: STATUS: FAIL — TECH_STACK.md removal contradicted constitution VIII.
Round 2: STATUS: PASS — TECH_STACK kept; rename + live-reinstall folded in; cleanup/publish scope otherwise sound (zero functional change, 0.2.0, MIT, measurability).