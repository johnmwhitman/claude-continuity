"""
chromadb-memory — OpenClaw ContextEngine Plugin
Gives any OpenClaw agent persistent semantic memory via local ChromaDB + Ollama.

ContextEngine lifecycle hooks (OpenClaw v2026.3.7+):
  bootstrap  — verify ChromaDB + Ollama are reachable, log health
  ingest     — extract and save memorable content after each turn
  assemble   — query relevant memories, inject into context window
  compact    — summarize and consolidate old conversation memories
  afterTurn  — lightweight post-turn hook for metrics/logging

Install:
  clawhub install super-memory/chromadb-memory

Manual install:
  cp -r openclaw_plugin ~/.openclaw/extensions/chromadb-memory/

Requirements:
  - ChromaDB running (python -m chromadb.app --port 8100)
  - Ollama running with nomic-embed-text pulled
  - OR: Super Memory full stack (includes both)
"""
import json, os, uuid
import urllib.request
from typing import Optional

# Config from env or openclaw.plugin.json defaults
CHROMA_URL   = os.environ.get("SM_CHROMA_URL",   "http://localhost:8100")
OLLAMA_URL   = os.environ.get("SM_OLLAMA_URL",   "http://localhost:11434")
EMBED_MODEL  = os.environ.get("SM_EMBED_MODEL",  "nomic-embed-text")
RECALL_N     = int(os.environ.get("SM_RECALL_N", "5"))
MIN_SCORE    = float(os.environ.get("SM_MIN_SCORE", "0.5"))
AUTO_SAVE    = os.environ.get("SM_AUTO_SAVE", "true").lower() == "true"
COLLECTIONS  = ["projects", "people", "decisions", "knowledge", "conversations", "tasks"]


# ── Core helpers ─────────────────────────────────────────────────────────────

def _http(url: str, body: dict = None, method: str = None) -> Optional[dict]:
    try:
        data = json.dumps(body).encode() if body else None
        m = method or ("POST" if data else "GET")
        req = urllib.request.Request(
            url, data=data, method=m,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"[chromadb-memory] HTTP error {url}: {e}")
        return None


def embed(text: str) -> Optional[list]:
    r = _http(f"{OLLAMA_URL}/api/embeddings", {"model": EMBED_MODEL, "prompt": text})
    return r.get("embedding") if r else None


def recall(query: str, n: int = RECALL_N) -> list[dict]:
    """Query all collections for relevant memories, sorted by score."""
    vec = embed(query)
    if not vec:
        return []
    results = []
    for col in COLLECTIONS:
        r = _http(f"{CHROMA_URL}/api/v1/collections/{col}/query", {
            "query_embeddings": [vec], "n_results": min(n, 3),
            "include": ["documents", "distances", "metadatas"]
        })
        if not r:
            continue
        docs   = r.get("documents",  [[]])[0]
        dists  = r.get("distances",  [[]])[0]
        metas  = r.get("metadatas",  [[]])[0]
        for doc, dist, meta in zip(docs, dists, metas):
            score = max(0.0, 1.0 - dist)
            if score >= MIN_SCORE:
                results.append({"content": doc, "score": score,
                                 "collection": col, "meta": meta})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:n]


def save(content: str, collection: str = "conversations", meta: dict = None):
    """Save content to a ChromaDB collection."""
    vec = embed(content)
    if not vec:
        return False
    r = _http(f"{CHROMA_URL}/api/v1/collections/{collection}/add", {
        "ids":        [str(uuid.uuid4())],
        "embeddings": [vec],
        "documents":  [content],
        "metadatas":  [meta or {"source": "openclaw"}]
    })
    return bool(r)


def format_context(memories: list[dict]) -> str:
    if not memories:
        return ""
    lines = ["--- Relevant memory context ---"]
    for m in memories[:RECALL_N]:
        snippet = m["content"][:280].replace("\n", " ")
        lines.append(f"[{m['score']:.0%} | {m['collection']}] {snippet}")
    lines.append("--- End memory context ---")
    return "\n".join(lines)



# ── ContextEngine Lifecycle Hooks ────────────────────────────────────────────

def bootstrap(config: dict) -> dict:
    """
    Called once when the agent session initializes.
    Verify ChromaDB and Ollama are reachable. Log health.
    """
    health = {"chroma": False, "ollama": False, "collections": []}

    # Check ChromaDB
    r = _http(f"{CHROMA_URL}/api/v1/heartbeat")
    health["chroma"] = bool(r)

    # Check Ollama
    r2 = _http(f"{OLLAMA_URL}/api/tags")
    if r2:
        models = [m["name"] for m in r2.get("models", [])]
        health["ollama"] = EMBED_MODEL in " ".join(models)
        health["ollama_models"] = models

    # List available collections
    r3 = _http(f"{CHROMA_URL}/api/v1/collections")
    if r3:
        health["collections"] = [c.get("name") for c in r3]

    ok = health["chroma"] and health["ollama"]
    status = "ready" if ok else "degraded"
    print(f"[chromadb-memory] Bootstrap {status}: chroma={health['chroma']} ollama={health['ollama']}")
    return {"status": status, "health": health}


def ingest(context: dict) -> dict:
    """
    Called after each agent turn.
    Extracts memorable content and saves to appropriate collection.
    """
    if not AUTO_SAVE:
        return context

    user_msg   = context.get("userMessage", "")
    agent_msg  = context.get("assistantMessage", "")

    # Only save substantive turns
    if len(user_msg) > 40 and len(agent_msg) > 80:
        turn_summary = f"User: {user_msg[:250]}\nAssistant: {agent_msg[:400]}"
        save(turn_summary, collection="conversations",
             meta={"source": "openclaw-turn", "auto": True})

    # Check for explicit memory-worthy content
    keywords = ["decided", "deadline", "project:", "remember", "critical", "contact"]
    combined = (user_msg + agent_msg).lower()
    if any(k in combined for k in keywords):
        save(agent_msg[:500], collection="decisions",
             meta={"source": "openclaw-ingest", "trigger": "keyword"})

    return context


def assemble(context: dict) -> dict:
    """
    Called before each agent turn.
    Queries memories and injects relevant context into the system prompt.
    """
    user_msg = context.get("userMessage", "")
    if not user_msg:
        return context

    memories = recall(user_msg)
    if memories:
        recall_block = format_context(memories)
        existing = context.get("systemPrompt", "")
        context["systemPrompt"] = f"{existing}\n\n{recall_block}" if existing else recall_block
        print(f"[chromadb-memory] Injected {len(memories)} memories")

    return context


def compact(context: dict) -> dict:
    """
    Called periodically to consolidate old memories.
    Summarizes conversation collection to prevent unbounded growth.
    Placeholder — full implementation in v1.2.
    """
    print("[chromadb-memory] Compact: no-op in v1.1 (scheduled for v1.2)")
    return context


def after_turn(context: dict) -> dict:
    """Lightweight post-turn hook. Currently just logs."""
    memories_injected = context.get("_sm_injected", 0)
    if memories_injected:
        print(f"[chromadb-memory] Turn complete. {memories_injected} memories were active.")
    return context


# ── Plugin entrypoint ────────────────────────────────────────────────────────

HOOKS = {
    "bootstrap":  bootstrap,
    "ingest":     ingest,
    "assemble":   assemble,
    "compact":    compact,
    "after_turn": after_turn,
}

def handle(hook: str, context: dict) -> dict:
    fn = HOOKS.get(hook)
    if fn:
        return fn(context)
    print(f"[chromadb-memory] Unknown hook: {hook}")
    return context
