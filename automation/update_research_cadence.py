# update_research_cadence.py
# Switch research goals to biweekly/monthly to reduce API costs
# Run once to apply changes
import json, winreg, os
from pathlib import Path

def load_reg():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
        i = 0
        while True:
            try:
                n, v, _ = winreg.EnumValue(key, i)
                os.environ[n] = v
                i += 1
            except OSError:
                break
    except Exception:
        pass

GOALS_FILE = Path("C:/AI/automation/research_goals.json")

with open(GOALS_FILE, encoding="utf-8") as f:
    data = json.load(f)

changes = []
for goal in data["goals"]:
    gid = goal["id"]
    old_freq = goal.get("frequency", "weekly")

    # job-lead-monitoring: keep weekly (time-sensitive)
    if gid == "job-lead-monitoring":
        continue

    # Low urgency personal goals: monthly
    if gid in ("elk-river-conditions", "tinnitus-management",
               "gi-health-gentle", "eureka-springs-real-estate"):
        if old_freq != "monthly":
            goal["frequency"] = "monthly"
            changes.append(f"{gid}: {old_freq} -> monthly")
        continue

    # Everything else weekly -> biweekly
    if old_freq == "weekly":
        goal["frequency"] = "biweekly"
        changes.append(f"{gid}: weekly -> biweekly")

with open(GOALS_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Updated {len(changes)} goal frequencies:")
for c in changes:
    print(f"  {c}")
print("Est savings: ~60-70% reduction in nightly API spend")
