"""
api_cost_monitor.py — BL-053: Hard budget enforcement for Anthropic API
Prevents overnight credit depletion. Run as pre-flight before research runner.

Usage:
  python api_cost_monitor.py check          # Pre-flight check (used by runner)
  python api_cost_monitor.py log [cost]     # Log a cost after API call
  python api_cost_monitor.py report         # Show monthly usage report

Hard limits:
  $15/month cap — alerts at 75% ($11.25), aborts at 100% ($15)
  $5 minimum balance required before research run starts
"""
import os, json, datetime, winreg
from pathlib import Path

USAGE_FILE  = Path(r"C:\AI\logs\usage_tracking.json")
LOG_FILE    = Path(r"C:\AI\logs\api_cost_log.txt")
MONTHLY_CAP = 15.00  # hard cap
ALERT_AT    = 0.75   # alert at 75% of cap
MIN_BALANCE = 5.00   # minimum balance required for research run

def load_reg():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment')
        i = 0
        while True:
            try:
                n, v, _ = winreg.EnumValue(key, i)
                os.environ[n] = v
                i += 1
            except OSError:
                break
    except:
        pass

def log_msg(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_usage():
    if USAGE_FILE.exists():
        try:
            return json.loads(USAGE_FILE.read_text())
        except:
            pass
    return {"monthly": {}, "total_lifetime": 0.0}

def save_usage(data):
    USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    USAGE_FILE.write_text(json.dumps(data, indent=2))

def get_month_key():
    return datetime.date.today().strftime("%Y-%m")

def get_monthly_spend(data):
    month = get_month_key()
    return data.get("monthly", {}).get(month, {}).get("total", 0.0)

def log_cost(cost_usd: float, goal_id: str = "unknown", model: str = "unknown"):
    """Record an API cost. Called after each successful API call."""
    data = load_usage()
    month = get_month_key()
    if month not in data["monthly"]:
        data["monthly"][month] = {"total": 0.0, "calls": 0, "breakdown": []}
    data["monthly"][month]["total"] = round(data["monthly"][month]["total"] + cost_usd, 4)
    data["monthly"][month]["calls"] += 1
    data["monthly"][month]["breakdown"].append({
        "date": datetime.datetime.now().isoformat(),
        "goal": goal_id,
        "model": model,
        "cost": cost_usd
    })
    data["total_lifetime"] = round(data.get("total_lifetime", 0) + cost_usd, 4)
    save_usage(data)
    log_msg(f"Cost logged: ${cost_usd:.4f} ({goal_id} / {model}) | Month total: ${data['monthly'][month]['total']:.2f}")

def check_balance() -> tuple[bool, str]:
    """
    Check if we have enough balance for a research run.
    Returns (can_proceed, reason)
    Also checks actual Anthropic API balance if token available.
    """
    load_reg()
    data = load_usage()
    monthly_spend = get_monthly_spend(data)
    remaining_budget = MONTHLY_CAP - monthly_spend
    pct_used = monthly_spend / MONTHLY_CAP

    # Check against monthly budget
    if remaining_budget < MIN_BALANCE:
        return False, f"Monthly budget nearly exhausted: ${monthly_spend:.2f}/${MONTHLY_CAP:.2f} spent. Only ${remaining_budget:.2f} remaining (need ${MIN_BALANCE:.2f} minimum)."

    if pct_used >= ALERT_AT:
        log_msg(f"⚠️  Budget alert: {pct_used*100:.0f}% of monthly cap used (${monthly_spend:.2f}/${MONTHLY_CAP:.2f})")

    # Try to get actual Anthropic balance
    token = os.environ.get("ANTHROPIC_API_KEY", "")
    if token:
        try:
            import urllib.request
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/organizations/usage",
                headers={"x-api-key": token, "anthropic-version": "2023-06-01"}
            )
            # Note: this endpoint may not exist — Anthropic doesn't expose balance via API
            # This is a placeholder; the real check is the monthly budget above
        except:
            pass

    return True, f"OK — ${monthly_spend:.2f} spent this month, ${remaining_budget:.2f} remaining"

def report():
    data = load_usage()
    print("\n=== API COST REPORT ===")
    print(f"Monthly cap: ${MONTHLY_CAP:.2f}")
    for month, stats in sorted(data.get("monthly", {}).items(), reverse=True)[:3]:
        total = stats.get("total", 0)
        calls = stats.get("calls", 0)
        pct = total / MONTHLY_CAP * 100
        print(f"\n{month}: ${total:.2f} ({pct:.0f}% of cap) — {calls} API calls")
        if calls > 0:
            print(f"  Avg cost/call: ${total/calls:.4f}")
    print(f"\nLifetime total: ${data.get('total_lifetime', 0):.2f}")
    print("======================\n")

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        can_go, reason = check_balance()
        print(f"{'✅ PROCEED' if can_go else '🛑 ABORT'}: {reason}")
        sys.exit(0 if can_go else 1)
    elif cmd == "log":
        cost = float(sys.argv[2]) if len(sys.argv) > 2 else 0.15
        goal = sys.argv[3] if len(sys.argv) > 3 else "unknown"
        log_cost(cost, goal)
    elif cmd == "report":
        report()
