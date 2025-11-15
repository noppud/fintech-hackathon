from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from .backend import PythonChatBackend
from .memory import ConversationStore
from .models import ChatRequest, ChatResponse
from .service import ChatService
from .tools.api_handlers import (
    apply_colors_tool,
    restore_colors_tool,
    visualize_formulas_tool,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

# * Lazy initialization - only create when chat endpoint is called
store = None
backend = None
service = None

app = FastAPI(title="Sheet Mangler Chat API (Python Frontend)")


def _init_chat_service() -> ChatService:
    """Lazily initialize chat service on first use."""
    global store, backend, service
    if service is None:
        store = ConversationStore()
        backend = PythonChatBackend()
        service = ChatService(backend=backend, store=store)
    return service


# * ============================================================================
# * Pydantic Models for Tool APIs
# * ============================================================================

class ColorRequest(BaseModel):
    """Request to apply colors to cells based on JSON input."""
    cell_location: str
    message: str
    color: str  # hex color like #FF0000
    url: str    # sheet URL indicating target spreadsheet/tab


class RestoreRequest(BaseModel):
    """Request to restore colors from Supabase snapshot."""
    snapshot_batch_id: str
    cell_locations: Optional[List[str]] = None


# * ============================================================================
# * Chat Endpoint
# * ============================================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
  """
  Single chat endpoint that mirrors the existing /api/chat contract.

  For now this proxies to the Next.js backend while adding conversation
  memory keyed by sessionId.
  """
  # This implementation assumes the client is sending the full message history.
  # If you prefer CLI-style incremental messages, use ChatService.simple_chat
  # directly or adapt this endpoint accordingly.
  svc = _init_chat_service()
  return svc.chat(request)


# * ============================================================================
# * Tools Endpoints (delegating to python_backend.tools)
# * ============================================================================

@app.post("/tools/color")
async def apply_colors(requests: List[ColorRequest]) -> Dict[str, Any]:
    """Apply background colors by delegating to the tools package."""
    try:
        payloads = [req.dict() for req in requests]
        return apply_colors_tool(payloads)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/tools/visulize-formulas")
async def visulize_formulas() -> Dict[str, Any]:
    """Visualize formulas by delegating to the tools package."""
    try:
        return visualize_formulas_tool()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/tools/restore")
async def restore_colors(request: RestoreRequest) -> Dict[str, Any]:
    """Restore colors from Supabase snapshots via the tools package."""
    try:
        return restore_colors_tool(
            snapshot_batch_id=request.snapshot_batch_id,
            cell_locations=request.cell_locations,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


