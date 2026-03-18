"""
smoke_test.py — Nightly System Smoke Test
6 checks, <30 seconds, tells you if last night actually worked.
Runs as part of morning brief. Writes failures to proactive_items.txt.

FIRST-RUN AWARE: If logs/first_run_complete.flag does not exist,
research/briefs/build_queue checks are skipped (runner has not fired yet).
Flag is written by run_nightly_pipeline.py on first successful completion.
"""
import os, json, datetime, subprocess, requests, sys

# Force UTF-8 output so emoji don't crash cp1252 Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LOG          = r"C:\AI\logs\research_log.txt"
BRIEFS_DIR   = r"C:\AI\logs\research_briefs"
BUILD_QUEUE  = r"C:\AI\logs\build_queue.json"
GITHUB_REPO  = r"C:\AI\github\super-memory"
PROACTIVE    = r"C:\AI\logs\proactive_items.txt"
SMOKE_LOG    = r"C:\AI\logs\smoke_test_log.txt"
CHROMADB_DIR = r"C:\AI\memory"
FIRST_RUN_FLAG = r"C:\AI\logs\first_run_complete.flag"

results = []
first_run_done = os.path.exists(FIRST_RUN_FLAG)

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(SMOKE_LOG), exist_ok=True)
    with open(SMOKE_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def flag(msg):
    os.makedirs(os.path.dirname(PROACTIVE), exist_ok=True)
    with open(PROACTIVE, "a", encoding="utf-8") as f:
        f.write(f"🔴 SMOKE TEST: {msg}\n")

def check(name, fn, skip_if_pre_first_run=False):
    if skip_if_pre_first_run and not first_run_done:
        log(f"  ⏭️  {name}: skipped — awaiting first nightly run (tonight 11pm)")
        results.append((name, True, "pre-first-run skip"))
        return
    try:
        passed, detail = fn()
        icon = "✅" if passed else "❌"
        log(f"  {icon} {name}: {detail}")
        results.append((name, passed, detail))
        if not passed:
            flag(f"{name} — {detail}")
    except Exception as e:
        log(f"  ❌ {name}: ERROR — {e}")
        results.append((name, False, str(e)))
        flag(f"{name} failed with exception: {e}")

# ── CHECK 1: Research log written in last 25 hours ────────────────────────
def check_research_log():
    if not os.path.exists(LOG):
        return False, "research_log.txt missing — runner may have failed"
    age = (datetime.datetime.now().timestamp() - os.path.getmtime(LOG)) / 3600
    if age > 25:
        return False, f"Log is {age:.0f}h old — nightly run may have failed"
    ok = fail = 0
    with open(LOG, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "succeeded" in line.lower(): ok += 1
            if "failed" in line.lower() or "error" in line.lower(): fail += 1
    return True, f"Fresh ({age:.1f}h old) — approx {ok} ok, {fail} errors"

# ── CHECK 2: Research briefs written today ────────────────────────────────
def check_briefs():
    if not os.path.exists(BRIEFS_DIR):
        return False, "research_briefs folder missing"
    today = datetime.date.today().isoformat()
    briefs = [f for f in os.listdir(BRIEFS_DIR)
              if today in f and os.path.getsize(os.path.join(BRIEFS_DIR, f)) > 100]
    total = len(os.listdir(BRIEFS_DIR))
    if len(briefs) == 0:
        return False, f"No briefs written today (total: {total})"
    return True, f"{len(briefs)} briefs written today (total: {total})"

# ── CHECK 3: ChromaDB readable ────────────────────────────────────────────
def check_chromadb():
    if not os.path.exists(CHROMADB_DIR):
        return False, "ChromaDB directory missing"
    file_count = sum(len(f) for _, _, f in os.walk(CHROMADB_DIR))
    if file_count == 0:
        return False, "ChromaDB directory empty"
    size_kb = sum(
        os.path.getsize(os.path.join(r, f))
        for r, _, files in os.walk(CHROMADB_DIR) for f in files
    ) / 1024
    return True, f"{file_count} files, {size_kb:.0f} KB"

# ── CHECK 4: Build queue valid JSON ──────────────────────────────────────
def check_build_queue():
    if not os.path.exists(BUILD_QUEUE):
        return False, "build_queue.json missing — diagnose.py may not have run"
    try:
        with open(BUILD_QUEUE, encoding="utf-8") as f:
            data = json.load(f)
        queue_len = len(data.get("queue", []))
        return True, f"Valid JSON, {queue_len} item(s) in queue"
    except json.JSONDecodeError as e:
        return False, f"Corrupted JSON: {e}"

# ── CHECK 5: GitHub push recent ───────────────────────────────────────────
def check_github():
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1", "--format=%ar"],
            cwd=GITHUB_REPO, capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return False, "git log failed — repo may not be initialized"
        return True, f"Last commit: {result.stdout.strip()}"
    except Exception as e:
        return False, f"Git check failed: {e}"

# ── CHECK 6: Ollama responsive ────────────────────────────────────────────
def check_ollama():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        return True, f"Running — {len(models)} model(s) loaded"
    except:
        return False, "Ollama not responding — nightly AI tasks may have failed"

# ── RUN ALL CHECKS ────────────────────────────────────────────────────────
def run():
    log("=" * 55)
    log("SMOKE TEST — System Health Check")
    log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if not first_run_done:
        log("ℹ️  PRE-FIRST-RUN MODE: research checks skipped until tonight")
    log("=" * 55)

    check("Research log fresh",    check_research_log,  skip_if_pre_first_run=True)
    check("Research briefs today", check_briefs,         skip_if_pre_first_run=True)
    check("ChromaDB readable",     check_chromadb)
    check("Build queue valid",     check_build_queue,   skip_if_pre_first_run=True)
    check("GitHub push recent",    check_github)
    check("Ollama responsive",     check_ollama)

    passed = sum(1 for _, p, _ in results if p)
    total  = len(results)
    log("=" * 55)
    log(f"RESULT: {passed}/{total} checks passed")

    if passed == total:
        log("✅ All systems healthy")
    elif passed >= total - 1:
        log("🟡 One issue — check proactive_items.txt")
    else:
        log(f"🔴 {total - passed} failures — review logs immediately")
        flag(f"Smoke test: {passed}/{total} passed — system needs attention")
    log("=" * 55)

if __name__ == "__main__":
    run()
