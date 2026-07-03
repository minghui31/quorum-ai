"""FastAPI server — the hosted demo, and how Summit (or anything else) calls Quorum.

    pip install "quorum-ai[server]"
    uvicorn quorum.server:app --reload
    # or: docker compose up

GET  /                     → live web demo (watch the council argue, get a verdict card)
POST /deliberate           → full verdict JSON
GET  /deliberate/stream    → Server-Sent Events: the live deliberation feed
GET  /councils             → available councils
GET  /stats                → councils_run counter (the traction number)
POST /waitlist             → email capture (stored locally, plain text, never trained on)

Privacy: case/CV text is processed in memory only and never persisted.
"""
from __future__ import annotations

import asyncio
import json
import os
import queue
import re
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from . import deliberate, load_council
from .backends import load_env_file
from .schema import Case

load_env_file()
app = FastAPI(title="Quorum", version="0.1.0")

_COUNCILS_DIR = Path(__file__).parent / "councils"
_WEB_INDEX = Path(__file__).parent.parent / "web" / "index.html"
_DATA_DIR = Path(os.environ.get("QUORUM_DATA_DIR", "."))

_lock = threading.Lock()
_councils_run = 0


def _bump() -> None:
    global _councils_run
    with _lock:
        _councils_run += 1


class CaseIn(BaseModel):
    title: str
    body: str
    council: str = "careers"
    language: str = "auto"
    context: dict = Field(default_factory=dict)

    def to_case(self) -> Case:
        return Case(**self.model_dump())


class WaitlistIn(BaseModel):
    email: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_WEB_INDEX)


@app.get("/councils")
def councils() -> list[dict]:
    out = []
    for f in sorted(_COUNCILS_DIR.glob("*.yaml")):
        c = load_council(f.stem)
        out.append({
            "name": c.name,
            "description": c.description,
            "councilors": [{"id": m.id, "role": m.role, "emoji": m.emoji} for m in c.councilors],
        })
    return out


@app.get("/stats")
def stats() -> dict:
    return {"councils_run": _councils_run}


@app.post("/waitlist")
def waitlist(item: WaitlistIn) -> dict:
    if not re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.-]+", item.email):
        raise HTTPException(422, "invalid email")
    with _lock:
        with open(_DATA_DIR / "waitlist.txt", "a", encoding="utf-8") as f:
            f.write(item.email + "\n")
    return {"ok": True}


@app.post("/deliberate")
def run(case: CaseIn) -> dict:
    verdict = deliberate(case.to_case()).to_dict()
    _bump()
    return verdict


@app.get("/deliberate/stream")
async def stream(title: str, body: str, council: str = "careers", language: str = "auto"):
    """SSE stream of deliberation events — the 'watch them argue' feed."""
    from sse_starlette.sse import EventSourceResponse

    q: queue.Queue = queue.Queue()
    case = Case(title=title, body=body, council=council, language=language)

    def work():
        try:
            deliberate(case, on_event=q.put)
            _bump()
        except Exception as exc:  # surface errors to the client
            q.put({"type": "error", "message": str(exc)})
        finally:
            q.put(None)

    threading.Thread(target=work, daemon=True).start()

    async def gen():
        loop = asyncio.get_event_loop()
        while True:
            event = await loop.run_in_executor(None, q.get)
            if event is None:
                break
            yield {"event": event.get("type", "message"), "data": json.dumps(event, ensure_ascii=False)}

    return EventSourceResponse(gen())
