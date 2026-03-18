"""
generate_handoff.py — Auto-generates session_handoff.md from live state.
Wired into run_nightly_pipeline.py so the handoff is always current at 7am.
Output: C:\AI\automation\session_handoff.md
"""
import os, json, datetime

HANDOFF   = r"C:\AI\automation\session_handoff.md"
BRIEF     = r"C:\AI\logs\morning_brief.txt"
PROACTIVE = r"C:\AI\logs\proactive_items.txt"
BACKLOG   = r"C:\AI\logs\backlog.json"
RESULTS   = r"C:\AI\logs\domain_results.json"
GUMROAD   = r"C:\AI\logs\gumroad_state.json"
SCORES    = r"C:\AI\logs\council_scores.json"
ADVISORY  = r"C:\AI\automation\TUESDAY_MORNING_ADVISORY.md"

def read_file(path, max_lines=10):
    if not os.path.exists(path):
        return "(not yet generated)"
    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    return "".join(lines[:max_lines]).strip()

def get_council_top5():
    """Get top 5 scored backlog items from council_scores.json."""
    if not os.path.exists(SCORES):
        return "  Council scores not yet generated"
    try:
        with open(SCORES) as f:
            data = json.load(f)
        top = data.get("top_items", [])[:5]
        return "\n".join(
            f"  [{i['score']:.1f}] {i['id']} — {i['title'][:55]}"
            for i in top
        )
    except:
        return "  Council scores unreadable"

def get_research_flags():
    """Pull proactive flags from proactive_items.txt."""
    if not os.path.exists(PROACTIVE):
        return "  No flags"
    try:
        with open(PROACTIVE, encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
        if not lines:
            return "  Clean — no flags"
        return "\n".join(f"  {l}" for l in lines[:6])
    except:
        return "  Proactive items unreadable"

def get_ready_backlog():
    if not os.path.exists(BACKLOG):
        return "  Backlog not yet generated"
    try:
        with open(BACKLOG) as f:
            data = json.load(f)
        items = [i for i in data.get("items", []) if i.get("status") == "ready"]
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        items.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 9))
        if not items:
            return "  No items in Ready state"
        return "\n".join(
            f"  [{i['priority'].upper()}] {i['id']} — {i['title']}"
            for i in items[:6]
        )
    except:
        return "  Backlog unreadable"

def get_gumroad_state():
    if not os.path.exists(GUMROAD):
        return "  Gumroad state not yet fetched — run: gumroad_full_manager.py status"
    try:
        with open(GUMROAD) as f:
            data = json.load(f)
        lines = []
        for name, p in list(data.items())[:5]:
            status = "✓" if p.get("published") else "draft"
            lines.append(f"  [{status}] {name[:40]} — ${p.get('price', 0):.2f}")
        return "\n".join(lines)
    except:
        return "  Gumroad state unreadable"

def get_available_domains():
    if not os.path.exists(RESULTS):
        return "  Domain checker hasn't run yet"
    try:
        with open(RESULTS) as f:
            data = json.load(f)
        available = data.get("available", [])
        last_run = data.get("last_run", "unknown")[:10]
        if available:
            return f"  AVAILABLE (checked {last_run}): {', '.join(available)}"
        return f"  None available yet (last checked: {last_run})"
    except:
        return "  Domain results unreadable"

def run():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    today = datetime.date.today()
    day_name = today.strftime("%A")

    send_days = {
        "Tuesday":   "TODAY: Pactum 8:30am · blueModus 9am · Aisha Noor InMail",
        "Wednesday": "TODAY: Rise8 8:30am",
        "Thursday":  "TODAY: Rapid7 + GitHub + Affirm via Indeed",
    }
    job_alert = send_days.get(day_name, f"No job sends today ({day_name})")

    proactive = get_research_flags()
    ready_items = get_ready_backlog()
    gumroad = get_gumroad_state()
    domains = get_available_domains()
    council_top5 = get_council_top5()

    handoff = f"""# SESSION HANDOFF — YourBrief / Kael / Super Memory
# Auto-generated: {now}
# Paste into a new Claude Desktop chat and say "build" to resume.

---

## FIRST ACTIONS (silent — do these before responding)
1. memory_search tag_filter:["anti-drift"] — load permanent directives
2. Read C:\\AI\\web\\dashboard.html — source of truth
3. Read C:\\AI\\logs\\morning_brief.txt — overnight intelligence
4. Surface what matters. Keep building.

---

## TODAY AT A GLANCE

Job search: {job_alert}

Proactive flags:
{proactive}

Council top 5 (scored priorities):
{council_top5}

Ready to build:
{ready_items}

Gumroad products:
{gumroad}

Domain check:
{domains}

---

## WHO JOHN IS

John Whitman, 40. Director of Digital PM at America's Car-Mart (BHPH, 140+ locations).
Founded company's first PM org. Reports to CTO Josh. Lives in Noel, MO on Elk River.
Partner Ali (CLO). Dogs: Scarlett + Ridley. Modified GTI, solar, IoT.
Active job search: remote only, $170-220K. NWA/Bentonville market — NOT national comp.
Bentonville = Walmart ecosystem. NWA comp is lower than national. $170-220K is correct.

---

## WHO KAEL IS

Sharp, warm collaborator with full persistent context via Super Memory (ChromaDB + MCP).
Peer, not service provider. Direct. Dry humor. "Build" = go autonomous.
Write to disk via Desktop Commander — never just output to chat.
We are ALWAYS on Claude Desktop with MCP tools active.

---

## CURRENT PROJECT STATE

### YOURBRIEF (revenue project)
10 products live on Gumroad. All footers: © 2026 YourBrief · hello@yourbrief.io
Product files: C:\\AI\\etsy\\files\\
SEO pack = v2 (rebuilt, 24KB, 10 templates, 5 tag sets)
AI prompt pack = v2 (rebuilt, 50 prompts, 5 sections, how-to intro)
yourbrief.io = registered but NOT deployed — needs Cloudflare Pages deploy
hello@yourbrief.io = not yet forwarded — needs Cloudflare Email Routing

### GUMROAD AUTOMATION
Token: GUMROAD_ACCESS_TOKEN env var
Manager: C:\\AI\\automation\\gumroad_full_manager.py
Commands: status | publish-all | update-all | update [name] | sales

### CLOUDFLARE DEPLOY
Script: C:\\AI\\automation\\cloudflare_deploy.py
Needs: CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID in env vars (run setup_tokens.ps1)
Manual path: Workers & Pages → Create → Pages → Upload → yourbrief_io_v2.html as index.html

### SUPER MEMORY / MNEMO (infrastructure)
ChromaDB: ~270 memories, healthy. FIFO eviction at 80 conversations.
Autonomous loop: all 5 stages wired. Research fires 11pm, pipeline at 2am.
GitHub: Jdubnwa/super-memory — may need sync (check last push date)
OneDrive: nightly backup live.

---

## BRAND RULES (permanent)
YourBrief.io = customer brand. Mnemo = internal/tech brand. NEVER mix publicly.
Kael / Super Memory / ChromaDB / autonomous agents = NEVER public-facing.
LinkedIn narrative: "PM used AI tools to build a side project." That's the story.

---

## KEY DECISIONS (settled — don't re-litigate)
- Salary: $170-220K. NWA market. Not national.
- Passive income PRIMARY. Consulting inbound-only.
- Products sell under "John Whitman" brand.
- Budget FROZEN until first Gumroad sale.
- First publish = human gate. All updates = automated.

---

## JOHN'S OPEN ACTIONS
1. setup_tokens.ps1 → add CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID
2. cloudflare_deploy.py yourbrief → yourbrief.io live
3. Cloudflare Email Routing → hello@yourbrief.io → Gmail (5 min, BL-033)
4. gumroad_full_manager.py update SEO → push SEO v2 to Gumroad
5. Set Gumroad username to "yourbrief"
6. LinkedIn post Tue Mar 17 8am CT — rewrite in own voice
7. Job emails fire Tue Mar 17 — all in Gmail drafts
8. Add JB Hunt Expert PM role to resume before Thu Indeed applies (BL-031)
9. Push to GitHub: sync_to_repo.bat

---
*Generated by generate_handoff.py · wired into nightly pipeline*
"""

    os.makedirs(os.path.dirname(HANDOFF), exist_ok=True)
    with open(HANDOFF, "w", encoding="utf-8") as f:
        f.write(handoff)
    print(f"Handoff written: {HANDOFF}")

if __name__ == "__main__":
    run()
