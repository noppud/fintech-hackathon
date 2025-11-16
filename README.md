# Mangler / Sheet Mangler Monorepo

Agentic assistant for Google Sheets that can inspect, repair, and create spreadsheets using LLMs, with a web UI, Google Sheets sidebar, and REST API.

This repo hosts all major parts of the Mangler stack:

- Python FastAPI backend (chat + spreadsheet tools)
- SvelteKit web UI
- Google Apps Script sidebar for Sheets
- Supabase migrations and SQL helpers
- Local tools for working with Google Sheets
- Brand assets, plans, and design docs

---

## Tech Stack

**Backend**
- Language: Python 3.11+
- Framework: FastAPI (ASGI) with Uvicorn / Hypercorn
- Data models: Pydantic v2
- HTTP client: `httpx`
- LLM integration: OpenRouter (Anthropic and other models)
- Google integrations: `google-api-python-client`, `google-auth`, `google-auth-oauthlib`
- Config: `python-dotenv` + `.env` files
- Persistence: Supabase (Postgres) for:
  - conversation messages
  - sheet tab metadata
  - cell-color and cell-value snapshots
- Deployment:
  - Docker + `docker-compose`
  - Railway via `railway.json` (Nixpacks, `hypercorn python_backend.api:app`)

**Frontend / UI**
- Framework: SvelteKit `^2.47.1`
- UI library: Svelte `^5.41.0`
- Language: TypeScript `^5.9.3`
- Tooling: Vite `^7.1.10`
- Auth: `@kinde-oss/kinde-auth-sveltekit`
- Package manager: `pnpm` (see `mangler-ui/package.json`)

**Google Sheets & Integrations**
- Google Apps Script sidebar (`app-script/`) written in JS/HTML
- Google Sheets & Drive APIs via service account / OAuth
- Supabase-backed snapshots of cell colors and values
- Embeddable HTML widget (served from the Python backend)

**Planning / Extensions**
- MCP (Model Context Protocol) integration design (`docs/MCP_IMPLEMENTATION_PLAN.md`)
- Product and agent orchestration plans (`plans/agentic_google_sheet_mangler.md`)

---

## Repository Layout

- `python_backend/` – Python FastAPI backend and tools
  - `api.py` – FastAPI app exposing:
    - `POST /chat` – main chat endpoint
    - `POST /chat/stream` – SSE streaming endpoint
    - `/tools/color`, `/tools/restore`, `/tools/update_cells`, `/tools/restore_cells`
    - `/widget` – embeddable HTML widget
  - `backend.py`, `orchestrator.py`, `mistake_detector.py`, `modifier.py`, `creator.py` – agent orchestration, issue detection, sheet modification, and sheet creation flows
  - `sheets_client.py`, `supabase_client.py` – Google Sheets and Supabase clients
  - `memory.py`, `conversation_logger.py` – in‑memory + Supabase conversation storage
  - `cli.py` – terminal chat client using the same tools as `/chat`
  - `migrations/` – Supabase/Postgres migrations for conversation & MCP-related tables
  - `API_USAGE.md` – detailed `/chat` API usage examples
  - `LOGGING.md` – logging design and configuration
  - `README.md` – full backend documentation (env vars, setup, endpoints)
  - `Dockerfile`, `docker-compose.yml`, `README.Docker.md` – container & deployment

- `mangler-ui/` – SvelteKit + Svelte 5 web app
  - `src/routes/chat/+page.svelte` – streaming chat UI with detected-issues panel
  - `src/routes/extension/` – entrypoints for extension-style integrations
  - `src/routes/login/`, `@kinde-oss/kinde-auth-sveltekit` – auth plumbing
  - `svelte.config.js`, `vite.config.ts`, `tsconfig.json` – tooling configuration
  - `package.json`, `pnpm-lock.yaml` – frontend dependencies and scripts

- `app-script/` – Google Apps Script project for Sheets sidebar
  - `Code.gs` – menu entry (“AI Mangler”), chat handler, issue highlighting and undo
  - `Sidebar.html` – original non‑streaming sidebar
  - `SidebarStreaming.html` – streaming-enabled sidebar UI
  - Calls the deployed backend at `/chat`, `/tools/color`, `/tools/restore`, `/tools/update_cells`, `/tools/restore_cells`

- `tools/` – local Python tools for Google Sheets
  - `google_sheets.py` – shared helper for authenticating to the Sheets API
  - `snapshot_input_colors.py` / `restore_input_colors.py` – snapshot/restore cell colors
  - `visualize_formulas.py` – utilities for inspecting formulas
  - `function_to_color_things.py` – example color/highlighting logic

- `helper-functions/`
  - `reset-color.py` – helper for resetting colors in Sheets during experiments

- `brand/sheet-mangler/` – brand and marketing assets
  - `theme.css` – color + typography tokens and UI kit
  - `landing.html` – minimal responsive landing page
  - `logo-*.svg` – wordmarks and logo marks
  - `README.md` – brand guidelines

- `supabase/`
  - `create_cell_color_snapshots.sql` – SQL for the `cell_color_snapshots` table + index

- `docs/`
  - `MCP_IMPLEMENTATION_PLAN.md` – detailed design for user-scoped MCP integrations

- `plans/`
  - `agentic_google_sheet_mangler.md` – product and technical roadmap for the agent

- `kinde-sveltekit-starter-kit/`
  - Placeholder directory for the Kinde SvelteKit starter template (used as a base for `mangler-ui`)

- Root utilities & config
  - `main.py` – small entrypoint that runs `uvicorn main:app` (importing `python_backend.api:app`)
  - `requirements.txt` – installs FastAPI + `python_backend/requirements.txt`
  - `railway.json` – Railway deployment config (Nixpacks + Hypercorn)
  - `STREAMING_CHAT_README.md` – streaming chat and UI behaviour
  - `TOOLS_API_GUIDE.md` – focused guide for `/tools/color` and `/tools/restore`
  - `test_run.py`, `input.json` – local test harnesses / examples
  - `venv/` or `.venv/` – optional local virtual environment (not tracked in docs)

---

## Development Overview

Backend and frontend have their own detailed READMEs; below is a high-level flow.

**Python backend (FastAPI)**
- Create and activate a virtualenv in `python_backend/`
- Install dependencies with `pip install -r python_backend/requirements.txt`
- Configure environment as described in `python_backend/README.md`:
  - `OPENROUTER_API_KEY`, `DEFAULT_LLM_MODEL`
  - Google service account (`GOOGLE_SERVICE_ACCOUNT_FILE` or `GOOGLE_SERVICE_ACCOUNT_JSON`)
  - Optional Supabase vars for persistence and snapshots
- Run locally, e.g.:
  - `uvicorn python_backend.api:app --reload --port 8000`, or
  - `python -m python_backend.main`

**SvelteKit UI (`mangler-ui/`)**
- Install Node + `pnpm`
- In `mangler-ui/`:
  - `pnpm install`
  - `pnpm dev` – dev server (typically on `http://localhost:5173`)
- Configure Kinde and backend URLs via SvelteKit env vars (see `mangler-ui` source).

**Google Sheets sidebar (Apps Script)**
- Copy `app-script/Code.gs` and `Sidebar*.html` into a Google Apps Script project.
- Deploy as a Sheets-bound script; use the “AI Mangler” menu to open the sidebar.
- The script calls the deployed FastAPI backend for chat and tool actions.

---

## Key Documentation

- Backend details: `python_backend/README.md`
- Chat API examples: `python_backend/API_USAGE.md`
- Streaming behaviour & endpoints: `STREAMING_CHAT_README.md`
- Tools API examples: `TOOLS_API_GUIDE.md`
- Logging and observability: `python_backend/LOGGING.md`
- MCP integration plan: `docs/MCP_IMPLEMENTATION_PLAN.md`
- Brand system: `brand/sheet-mangler/README.md`

Use this root README as an index into the repo; each subdirectory’s README or Markdown file contains deeper implementation and usage details.
