"""
council_score.py — Autonomous nightly backlog prioritization
BL-045: Council scores backlog items overnight so John sees a priority-ranked list
        in the morning brief, not raw backlog.

Model: Ollama qwen2.5:7b (local, free, fast enough for scoring)
Fallback: Simple rule-based scoring if Ollama unavailable

Output:
  logs/council_scores.json  — full scored backlog
  Appended to logs/morning_brief.txt — top 5 items surfaced for John
"""

import json, os, datetime, urllib.request
from pathlib import Path

BACKLOG     = Path(r"C:\AI\logs\backlog.json")
SCORES_OUT  = Path(r"C:\AI\logs\council_scores.json")
BRIEF       = Path(r"C:\AI\logs\morning_brief.txt")
LOG         = Path(r"C:\AI\logs\council_score_log.txt")
OLLAMA_URL  = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"

EFFORT_SCORE = {
    "30min": 9, "15min": 10, "10min": 10,
    "2hr": 7, "1hr": 8, "half_day": 5,
    "full_day": 3, "research": 4, "purchase": 2
}

VALUE_SCORE = {"critical": 10, "high": 8, "medium": 5, "low": 2}
PRIORITY_SCORE = {"critical": 10, "high": 8, "medium": 5, "low": 2}

# Status weights — items closer to action score higher
STATUS_WEIGHT = {
    "in_progress": 10, "ready": 9, "backlog": 5,
    "research": 3, "blocked": 1, "done": 0, "vision": 2
}


def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def rule_based_score(item):
    """Deterministic score when Ollama unavailable. Fast, consistent."""
    status   = item.get("status", "backlog")
    priority = item.get("priority", "medium")
    effort   = item.get("effort", "half_day")
    value    = item.get("value", "medium")

    s_status   = STATUS_WEIGHT.get(status, 5)
    s_priority = PRIORITY_SCORE.get(priority, 5)
    s_effort   = EFFORT_SCORE.get(effort, 5)
    s_value    = VALUE_SCORE.get(value, 5)

    # Bonus: job-search tagged items get urgency boost (Tuesday emails are live)
    tags = item.get("tags", [])
    urgency_bonus = 2 if any(t in tags for t in ["job-search", "resume", "revenue"]) else 0

    # Penalty: blocked items
    blocked_penalty = 3 if status == "blocked" else 0

    raw = (s_priority * 0.35 + s_value * 0.25 + s_effort * 0.20 +
           s_status * 0.20 + urgency_bonus - blocked_penalty)
    return round(min(max(raw, 0), 10), 2)

def ollama_score(item):
    """Ask local Ollama to score an item with brief rationale."""
    prompt = (
        f"Score this software project backlog item from 0-10 on BUILD PRIORITY.\n"
        f"10 = build immediately, 0 = never build.\n\n"
        f"Item: {item['title']}\n"
        f"Description: {item.get('description', '')[:200]}\n"
        f"Status: {item['status']} | Priority: {item['priority']} | "
        f"Effort: {item.get('effort','?')} | Value: {item.get('value','?')}\n"
        f"Tags: {', '.join(item.get('tags', []))}\n\n"
        f"Respond ONLY with: SCORE: X.X | REASON: one sentence\n"
        f"Example: SCORE: 7.5 | REASON: High value quick win that unblocks revenue."
    )

    body = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 80}
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            OLLAMA_URL, data=body,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = data.get("response", "").strip()
        # Parse: SCORE: X.X | REASON: ...
        if "SCORE:" in text:
            parts = text.split("|")
            score_str = parts[0].replace("SCORE:", "").strip()
            reason = parts[1].replace("REASON:", "").strip() if len(parts) > 1 else ""
            return float(score_str), reason
    except Exception as e:
        log(f"  Ollama scoring error: {e}")
    return None, None


def check_ollama_available():
    """Quick health check — also checks if Ollama is free (not loaded with big model)."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status != 200:
                return False
        # Quick probe: send tiny prompt with 3s timeout — if busy, fail fast to rule-based
        probe_body = json.dumps({
            "model": OLLAMA_MODEL, "prompt": "hi", "stream": False,
            "options": {"num_predict": 2, "temperature": 0}
        }).encode("utf-8")
        probe_req = urllib.request.Request(OLLAMA_URL, data=probe_body,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(probe_req, timeout=8) as resp:
            return resp.status == 200
    except:
        return False

def run():
    log("=" * 50)
    log("council_score.py — nightly backlog prioritization")

    if not BACKLOG.exists():
        log("No backlog.json found — nothing to score")
        return

    data  = json.loads(BACKLOG.read_text(encoding="utf-8"))
    items = data.get("items", [])

    # Skip done/vision — only score actionable items
    actionable = [i for i in items if i["status"] not in ("done",)]
    log(f"Scoring {len(actionable)} actionable items")

    use_ollama = check_ollama_available()
    log(f"Ollama available: {use_ollama} — {'AI scoring' if use_ollama else 'rule-based scoring'}")

    scored = []
    for item in actionable:
        iid = item["id"]
        if use_ollama:
            score, reason = ollama_score(item)
            if score is None:
                score = rule_based_score(item)
                reason = "rule-based fallback"
        else:
            score = rule_based_score(item)
            reason = "rule-based (Ollama offline)"

        scored.append({
            "id": iid,
            "title": item["title"],
            "status": item["status"],
            "priority": item["priority"],
            "score": score,
            "reason": reason,
            "tags": item.get("tags", [])
        })

    # Sort descending by score
    scored.sort(key=lambda x: x["score"], reverse=True)

    output = {
        "generated": datetime.datetime.now().isoformat(),
        "method": "ollama" if use_ollama else "rule-based",
        "top_items": scored[:10],
        "all_scored": scored
    }

    SCORES_OUT.parent.mkdir(parents=True, exist_ok=True)
    SCORES_OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    log(f"Scores written: {SCORES_OUT}")

    # Surface top 5 to morning brief
    top5 = scored[:5]
    brief_section = "\n\n" + "=" * 50 + "\n"
    brief_section += "COUNCIL PRIORITY RANKING — TOP BUILD ITEMS\n"
    brief_section += "=" * 50 + "\n"
    for rank, item in enumerate(top5, 1):
        brief_section += f"{rank}. [{item['score']:.1f}] {item['id']}: {item['title'][:55]}\n"
        if item.get("reason"):
            brief_section += f"   Reason: {item['reason']}\n"
    brief_section += "\n(Full scores: C:\\AI\\logs\\council_scores.json)\n"

    if BRIEF.exists():
        with open(BRIEF, "a", encoding="utf-8") as f:
            f.write(brief_section)
        log("Top 5 appended to morning_brief.txt")

    log(f"Top 3 tonight:")
    for item in scored[:3]:
        log(f"  [{item['score']:.1f}] {item['id']}: {item['title'][:55]}")
    log("=" * 50)

if __name__ == "__main__":
    run()
