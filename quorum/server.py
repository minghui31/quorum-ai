"""FastAPI server — the hosted demo, and how Summit (or anything else) calls Quorum.

    pip install "quorum-council[server]"
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

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from . import deliberate, load_council
from .backends import load_env_file
from .schema import Case

load_env_file()
app = FastAPI(title="Quorum", version="0.1.0")

_ASSETS_DIR = Path(__file__).parent.parent / "assets"
if _ASSETS_DIR.is_dir():
    from fastapi.staticfiles import StaticFiles

    app.mount("/assets", StaticFiles(directory=str(_ASSETS_DIR)), name="assets")

_COUNCILS_DIR = Path(__file__).parent / "councils"
_WEB_INDEX = Path(__file__).parent.parent / "web" / "index.html"
_DATA_DIR = Path(os.environ.get("QUORUM_DATA_DIR", "."))

_lock = threading.Lock()
_COUNTER_FILE = _DATA_DIR / "councils_run.txt"


def _read_count() -> int:
    try:
        return int(_COUNTER_FILE.read_text().strip() or 0)
    except (OSError, ValueError):
        return 0


# Survives free-tier sleeps via file; QUORUM_COUNT_FLOOR (env) guards against
# resets on redeploys (set it to the last known count in the dashboard).
_councils_run = max(_read_count(), int(os.environ.get("QUORUM_COUNT_FLOOR", "0")))


def _bump() -> None:
    global _councils_run
    with _lock:
        _councils_run += 1
        try:
            _COUNTER_FILE.write_text(str(_councils_run))
        except OSError:
            pass  # counter is best-effort; never break a deliberation over it


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
    # no-cache: visitors always get the latest UI (browsers cached stale pages during launch prep)
    return FileResponse(_WEB_INDEX, headers={"Cache-Control": "no-cache"})


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


# --- hosted-demo guards: per-IP daily limit + graceful capacity fallback -----

_ip_hits: dict[str, list] = {}  # ip -> [YYYY-MM-DD, count]


def _client_ip(request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    return (fwd.split(",")[0].strip() or getattr(request.client, "host", "?")) if request else "?"


def _ip_allowed(ip: str) -> bool:
    """True if this IP still has free deliberations today (env: QUORUM_IP_DAILY_LIMIT)."""
    import datetime as _dt

    limit = int(os.environ.get("QUORUM_IP_DAILY_LIMIT", "12"))
    if limit <= 0:  # 0 disables the limit
        return True
    today = _dt.date.today().isoformat()
    with _lock:
        day, n = _ip_hits.get(ip, [today, 0])
        if day != today:
            day, n = today, 0
        if n >= limit:
            return False
        _ip_hits[ip] = [day, n + 1]
    return True


def _has_real_backend() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY"))


def _run_with_fallback(fn_real, fn_mock, q: queue.Queue) -> None:
    """Run the real deliberation; if the model API fails (credits exhausted,
    overloaded, auth), tell the client honestly and replay in mock mode so the
    demo NEVER breaks — the failure state itself converts to `pip install`."""
    try:
        fn_real()
        _bump()
    except Exception as exc:
        if _has_real_backend():
            q.put({"type": "fallback", "message": str(exc)[:120]})
            try:
                fn_mock()
                _bump()
            except Exception as exc2:
                q.put({"type": "error", "message": str(exc2)})
        else:
            q.put({"type": "error", "message": str(exc)})
    finally:
        q.put(None)


@app.post("/deliberate")
def run(case: CaseIn) -> dict:
    verdict = deliberate(case.to_case()).to_dict()
    _bump()
    return verdict


@app.post("/simulate")
def run_ensemble(case: CaseIn, runs: int = 10) -> dict:
    """Monte-Carlo: N independent councils → verdict distribution."""
    from .montecarlo import simulate

    ens = simulate(case.to_case(), load_council(case.council), runs=runs)
    _bump()
    return ens.to_dict()


@app.get("/deliberate/stream")
async def stream(request: Request, title: str, body: str, council: str = "careers", language: str = "auto"):
    """SSE stream of deliberation events — the 'watch them argue' feed."""
    from sse_starlette.sse import EventSourceResponse

    from .backends import MockBackend

    q: queue.Queue = queue.Queue()
    case = Case(title=title, body=body, council=council, language=language)

    if not _ip_allowed(_client_ip(request)):
        async def limited():
            yield {"event": "limit", "data": json.dumps({"type": "limit"})}
        return EventSourceResponse(limited())

    def work():
        _run_with_fallback(
            lambda: deliberate(case, on_event=q.put),
            lambda: deliberate(case, backend=MockBackend(), on_event=q.put),
            q,
        )

    threading.Thread(target=work, daemon=True).start()

    async def gen():
        loop = asyncio.get_event_loop()
        while True:
            event = await loop.run_in_executor(None, q.get)
            if event is None:
                break
            yield {"event": event.get("type", "message"), "data": json.dumps(event, ensure_ascii=False)}

    return EventSourceResponse(gen())


@app.get("/simulate/stream")
async def simulate_stream(request: Request, title: str, body: str, council: str = "careers",
                          language: str = "auto", runs: int = 5):
    """SSE ensemble: N independent councils; per-run tallies stream in live,
    final event is the distribution. Hosted-demo cost guard: runs capped by
    QUORUM_WEB_MAX_RUNS (default 5) on top of QUORUM_MAX_RUNS."""
    from sse_starlette.sse import EventSourceResponse

    from .backends import MockBackend
    from .montecarlo import simulate as mc_simulate

    web_cap = int(os.environ.get("QUORUM_WEB_MAX_RUNS", "5"))
    runs = max(1, min(runs, web_cap))

    if not _ip_allowed(_client_ip(request)):
        async def limited():
            yield {"event": "limit", "data": json.dumps({"type": "limit"})}
        return EventSourceResponse(limited())

    # Ensembles measure the SPLIT, not prose quality → run them on a cheap fast
    # model (~5x cheaper). The single-council flagship stays on the premium model.
    ens_backend = None
    if os.environ.get("ANTHROPIC_API_KEY"):
        from .backends import AnthropicBackend

        ens_backend = AnthropicBackend(
            model=os.environ.get("QUORUM_ENSEMBLE_MODEL", "claude-haiku-4-5-20251001"))

    q: queue.Queue = queue.Queue()
    case = Case(title=title, body=body, council=council, language=language)

    def work():
        _run_with_fallback(
            lambda: mc_simulate(case, load_council(council), runs=runs, backend=ens_backend, on_event=q.put),
            lambda: mc_simulate(case, load_council(council), runs=runs, backend=MockBackend(), on_event=q.put),
            q,
        )

    threading.Thread(target=work, daemon=True).start()

    async def gen():
        loop = asyncio.get_event_loop()
        while True:
            event = await loop.run_in_executor(None, q.get)
            if event is None:
                break
            yield {"event": event.get("type", "message"), "data": json.dumps(event, ensure_ascii=False)}

    return EventSourceResponse(gen())
