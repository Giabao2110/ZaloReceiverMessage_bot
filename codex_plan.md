# ZaloReceiverMessage_bot — Codex Execution Plan

## Objective
Stabilize and finish the project so it is no longer just a local prototype.  
Target outcome: a clean, runnable, documented repository with one clear architecture, complete dependencies, better configuration hygiene, and basic test coverage.

---

## Current State Summary

The repository already has the following promising parts:

- Core message polling logic from Zalo
- Telegram forwarding utility
- State tracking with `last_message_id`
- A Selenium-based Zalo Web monitoring approach
- Keyword configuration in JSON

However, the project is still incomplete as a proper public repo / portfolio project because of these issues:

- `README.md` is almost empty
- `requirements.txt` is incomplete
- sensitive/local/generated files appear to be committed:
  - `.env`
  - `venv/`
  - `__pycache__/`
  - `system.log`
- there are 2 parallel approaches (`main.py` and `zalo_monitor.py`) without one clearly declared primary architecture
- no tests
- no CI workflow
- no cleanup/documentation/deployment guidance

Estimated completion status: prototype works, but overall project is only around mid-stage and not production-ready.

---

## High-Level Goal

Bring the project from "working prototype" to "clean, reproducible, portfolio-ready repo".

---

## Execution Rules

1. Do not rewrite everything from scratch unless necessary.
2. Preserve existing functionality.
3. Prefer small, clean refactors.
4. Keep the project simple and maintainable.
5. Make the repository runnable by another developer using only the README.
6. Remove any sensitive or machine-specific files from version control.
7. If both architectures are kept, clearly separate them and document them.
8. If one architecture is clearly better, make it the primary path and mark the other as experimental.

---

## Phase 1 — Repository Cleanup

### Tasks
- Add a proper `.gitignore`
- Remove tracked local/generated files from the repository:
  - `.env`
  - `venv/`
  - `__pycache__/`
  - `*.log`
  - any runtime state files that should not be versioned
- Keep only source code, config templates, docs, and necessary project assets
- Ensure the repo tree is clean and understandable

### Expected Result
The repository should look professional and safe to publish.

### Suggested `.gitignore`
Include at least:
- `.env`
- `venv/`
- `.venv/`
- `__pycache__/`
- `*.pyc`
- `*.log`
- `.idea/`
- `.vscode/`
- runtime state files such as `last_message_id.txt` if generated locally

---

## Phase 2 — Dependency and Environment Fixes

### Tasks
- Audit imports across all Python files
- Update `requirements.txt` so it includes every actually used dependency
- Verify whether the project uses:
  - `requests`
  - `python-dotenv`
  - `selenium`
  - `webdriver-manager`
  - any others currently imported in code
- Remove unused dependencies if found
- Add `.env.example` with placeholder variables only

### Expected Result
A fresh clone should be installable with:

```bash
pip install -r requirements.txt