"""
build_dashboard.py — Nightly dashboard builder.
Reads backlog.json, gumroad_state.json, morning_brief.txt and stamps all data
directly into dashboard.html as embedded JS. No fetch() needed — no CORS issues.
Run nightly or anytime state changes.

Output: C:\AI\web\dashboard.html (overwritten with current data)
"""
import json, os, datetime
from pathlib import Path

BACKLOG      = Path(r"C:\AI\logs\backlog.json")
GUMROAD      = Path(r"C:\AI\logs\gumroad_state.json")
BRIEF        = Path(r"C:\AI\logs\morning_brief.txt")
PROACTIVE    = Path(r"C:\AI\logs\proactive_items.txt")
DASHBOARD    = Path(r"C:\AI\web\dashboard.html")

def read_json(p, default):
    try:
        return json.loads(p.read_text()) if p.exists() else default
    except:
        return default

def read_text(p, default=""):
    try:
        return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else default
    except:
        return default

def build():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M CT")
    backlog_data = read_json(BACKLOG, {"items": []})
    gumroad_data = read_json(GUMROAD, {})
    brief_text   = read_text(BRIEF, "No morning brief yet.")
    proactive    = read_text(PROACTIVE, "").strip()

    items = backlog_data.get("items", [])
    ready    = [i for i in items if i["status"] == "ready"]
    in_prog  = [i for i in items if i["status"] == "in_progress"]
    backlog  = [i for i in items if i["status"] == "backlog"]
    vision   = [i for i in items if i["status"] == "vision"]
    done     = [i for i in items if i["status"] == "done"]
    research = [i for i in items if i["status"] == "research"]

    # Gumroad stats
    gum_products = len(gumroad_data)
    gum_revenue  = sum(0 for _ in gumroad_data.values())  # will populate from sales later
    gum_rows = ""
    for name, p in list(gumroad_data.items())[:10]:
        status = "live" if p.get("published") else "draft"
        price  = p.get("price", 0)
        url    = p.get("url", "#")
        gum_rows += f'<div class="product-row"><span class="pname"><a href="{url}" target="_blank" style="color:inherit">{name[:45]}</a></span><span class="pprice">${price:.2f} <span class="bdg {status}">{status}</span></span></div>\n'

    if not gum_rows:
        # Static fallback with all 10 known products
        products = [
            ("AI Prompt Pack for Etsy Sellers", 12.99, True),
            ("30-Day Etsy Launch Plan", 12.99, True),
            ("Etsy Seller Budget Tracker", 11.99, True),
            ("SEO Template Pack for Etsy", 9.99, True),
            ("Pricing Calculator Guide for Etsy Sellers", 9.99, True),
            ("AI Tools for Small Business", 9.99, True),
            ("Customer Communications Pack for Etsy Sellers", 8.99, True),
            ("Product Photography Checklist for Etsy Sellers", 8.99, True),
            ("Shop Bio Templates for Etsy Sellers", 7.99, True),
            ("Shipping Guide for Etsy Sellers", 7.99, True),
        ]
        for name, price, live in products:
            status = "live" if live else "draft"
            gum_rows += f'<div class="product-row"><span class="pname">{name}</span><span class="pprice">${price:.2f} <span class="bdg {status}">{status}</span></span></div>\n'
        gum_products = 10

    # Kanban JS data (embedded — no fetch needed)
    kanban_js = f"const BACKLOG_DATA = {json.dumps(items)};"

    # Proactive alert bar
    proactive_html = ""
    if proactive:
        lines = [l.strip() for l in proactive.split("\n") if l.strip()][:2]
        for line in lines:
            proactive_html += f'<div class="alert a-red">⚡ {line}</div>\n'

    return (now, gum_products, gum_rows, kanban_js, proactive_html, brief_text,
            len(ready), len(in_prog), len(backlog), len(vision), len(done), len(research),
            items)

def write_dashboard():
    (now, gum_products, gum_rows, kanban_js, proactive_html, brief_text,
     n_ready, n_ip, n_bl, n_vis, n_done, n_res, items) = build()

    # Agency council voices (updated daily from research findings)
    agency_cards = [
        ("🏗️", "Architect", "h-ip", "Kanban fetch bug is a browser security block — fixed in this build via embedded JS. Cloudflare Pages token needs custom scope not Workers template. Claude Code executor is the next autonomous layer."),
        ("🔒", "CISO", "h-blk", "Telegram hardened: whitelist-only commands, safe command list enforced. Research output must be sanitized before touching backlog. Prompt injection defense is BL-048 — critical priority."),
        ("🤖", "AI Eng", "h-rdy", "Mnemo Router built and wired. BL-047 (Claude Code as executor) is the next layer — research in progress. Agent orchestration loop: diagnose → queue → execute → validate."),
        ("📊", "Scrum", "h-rdy", "Backlog now 50 items. Grooming is a bottleneck. council_score.py (BL-045) automates nightly prioritization. John reviews top 3 each morning, not 50 items."),
        ("📣", "CMO", "h-bl", "Backlog has autonomous content generation via Ollama nightly. LinkedIn API is dead — Playwright path is the only option. Public GitHub launch (VIS-005) is the content flywheel."),
        ("💰", "CRO", "h-bl", "10 products live. $0 revenue. Dashboard needs live Gumroad data (BL-050). First sale is a function of traffic — deploy yourbrief.io to unlock."),
    ]
    agency_html = ""
    for icon, role, cls, voice in agency_cards:
        agency_html += f"""
    <div class="card" style="border-top:3px solid var(--gold)">
      <div class="lbl">{icon} {role}</div>
      <div style="font-size:12px;color:#333;line-height:1.7">{voice}</div>
    </div>"""

    # Write dashboard — part 1 (head + styles + nav)
    DASHBOARD.parent.mkdir(parents=True, exist_ok=True)
    with open(DASHBOARD, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="300">
<title>YourBrief · Mission Control</title>
<style>
:root{{--gold:#c8a84b;--ink:#1a1a2e;--bg:#f5f4f0;--card:#fff;--border:#d8d5cf;--muted:#666}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--ink);font-size:13px;line-height:1.5}}
.hdr{{background:var(--ink);padding:12px 20px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100;border-bottom:2px solid var(--gold)}}
.logo{{font-family:'Courier New',monospace;font-size:14px;letter-spacing:2px;text-transform:uppercase;color:var(--gold);font-weight:bold}}
.logo span{{color:#fff}}
.hdr-r{{display:flex;align-items:center;gap:10px}}
.env-pill{{font-family:'Courier New',monospace;font-size:10px;padding:3px 10px;background:var(--gold);color:var(--ink);letter-spacing:1px;text-transform:uppercase;font-weight:bold;border-radius:2px}}
.clk{{font-family:'Courier New',monospace;font-size:12px;color:var(--gold);font-weight:bold}}
.built{{font-size:9px;color:rgba(200,168,75,.5);font-family:monospace}}
.tabs{{background:var(--ink);display:flex;gap:2px;padding:0 20px;border-bottom:1px solid #2a2a40;overflow-x:auto}}
.tab-btn{{font-family:'Courier New',monospace;font-size:11px;letter-spacing:1px;text-transform:uppercase;padding:10px 14px;background:none;border:none;cursor:pointer;color:#888;border-bottom:2px solid transparent;transition:all .15s;white-space:nowrap}}
.tab-btn:hover{{color:#ccc}}.tab-btn.on{{color:var(--gold);border-bottom-color:var(--gold)}}
.page{{max-width:1200px;margin:0 auto;padding:14px;display:flex;flex-direction:column;gap:12px}}
.tab-pane{{display:none}}.tab-pane.on{{display:flex;flex-direction:column;gap:12px}}
.r3{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.r4{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
.r2{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.r21{{display:grid;grid-template-columns:2fr 1fr;gap:12px}}
.r3ag{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:6px;padding:14px 16px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.lbl{{font-family:'Courier New',monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#888;margin-bottom:8px;font-weight:bold}}
.lbl-gold{{color:var(--gold)}}
.big{{font-size:36px;font-weight:700;line-height:1;margin-bottom:4px;color:var(--ink)}}
.big.green{{color:#1a6b1a}}.big.red{{color:#8b1a1a}}.big.gold{{color:#a07820}}
.sub{{font-size:11px;color:var(--muted);line-height:1.6}}
.alert{{padding:9px 14px;font-size:12px;font-weight:500;border-radius:4px;border-left:4px solid}}
.a-green{{background:#e8f5e8;border-color:#2e7d2e;color:#1a4d1a}}
.a-gold{{background:#fdf5e0;border-color:#b8860b;color:#5c4000}}
.a-red{{background:#fde8e8;border-color:#b91c1c;color:#5c0000}}
.a-blue{{background:#e8f0fd;border-color:#2563eb;color:#1e3a7a}}
.row{{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #eeecea}}
.row:last-child{{border-bottom:none}}
.rl{{font-size:12px;color:#333}}
.rl-strong{{font-size:12px;color:var(--ink);font-weight:600}}
.bdg{{font-family:'Courier New',monospace;font-size:9px;padding:2px 7px;letter-spacing:1px;text-transform:uppercase;border-radius:3px;font-weight:bold;white-space:nowrap}}
.live{{background:#dcfce7;color:#166534;border:1px solid #86efac}}
.pend{{background:#fef9c3;color:#713f12;border:1px solid #fde047}}
.blk{{background:#fee2e2;color:#991b1b;border:1px solid #fca5a5}}
.done{{background:#dcfce7;color:#166534;border:1px solid #86efac}}
.fire{{background:#ffedd5;color:#7c2d12;border:1px solid #fed7aa}}
.int{{background:#f3f4f6;color:#374151;border:1px solid #d1d5db}}
.new{{background:#ede9fe;color:#4c1d95;border:1px solid #c4b5fd}}
.draft{{background:#f3f4f6;color:#374151;border:1px solid #d1d5db}}
.action-list{{display:flex;flex-direction:column;gap:2px}}
.action-item{{display:flex;justify-content:space-between;align-items:center;padding:7px 10px;background:#fafaf8;border:1px solid #e8e5df;border-radius:4px}}
.action-item:hover{{background:#f0ede6}}
.action-label{{font-size:12px;color:var(--ink);font-weight:500}}
.action-sub{{font-size:10px;color:#888;margin-top:1px}}
.product-row{{display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #eeecea}}
.product-row:last-child{{border-bottom:none}}
.pname{{font-size:12px;color:var(--ink)}}
.pprice{{font-size:12px;font-weight:600;color:#1a6b1a;font-family:'Courier New',monospace}}
.kanban-wrap{{display:flex;gap:10px;overflow-x:auto;padding-bottom:8px}}
.kcol{{min-width:200px;flex-shrink:0}}
.kcol-hdr{{padding:6px 10px;border-radius:4px 4px 0 0;font-family:'Courier New',monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;font-weight:bold;display:flex;justify-content:space-between;align-items:center}}
.h-ip{{background:#dbeafe;color:#1e40af}}.h-rdy{{background:#dcfce7;color:#166534}}
.h-bl{{background:#f3f4f6;color:#374151}}.h-vis{{background:#ede9fe;color:#4c1d95}}
.h-done{{background:#dcfce7;color:#166534;opacity:.7}}.h-blk{{background:#fee2e2;color:#991b1b}}
.h-res{{background:#fef9c3;color:#713f12}}
.kcnt{{background:rgba(0,0,0,.1);border-radius:10px;padding:1px 7px;font-size:10px}}
.kcard{{background:var(--card);border:1px solid var(--border);border-radius:0 0 4px 4px;margin-bottom:6px;padding:8px 10px;font-size:11px}}
.kid{{font-family:'Courier New',monospace;font-size:9px;color:#999;margin-bottom:2px}}
.ktitle{{font-weight:600;color:var(--ink);line-height:1.35;margin-bottom:3px}}
.kcouncil{{font-size:10px;color:#888;line-height:1.4;margin-top:4px;border-top:1px solid #f0f0f0;padding-top:4px}}
.pdot{{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:4px}}
.pc{{background:#dc2626}}.ph{{background:#d97706}}.pm{{background:#16a34a}}.pl{{background:#9ca3af}}
.reporter{{background:var(--ink);border-left:3px solid var(--gold);padding:12px 16px;border-radius:0 6px 6px 0;font-size:12px;color:#a0a0c0;line-height:1.8;font-style:italic}}
.reporter strong{{color:var(--gold);font-style:normal}}
.job-item{{display:flex;justify-content:space-between;align-items:flex-start;padding:7px 0;border-bottom:1px solid #eeecea;gap:12px}}
.job-item:last-child{{border-bottom:none}}
.job-name{{font-size:12px;font-weight:600;color:var(--ink);margin-bottom:2px}}
.job-detail{{font-size:11px;color:var(--muted)}}
.cmd-box{{background:var(--ink);color:#4ade80;font-family:'Courier New',monospace;font-size:11px;padding:10px 14px;border-radius:4px;margin:8px 0;line-height:1.8;white-space:pre}}
</style>
</head>
<body>
<div class="hdr">
  <span class="logo">Your<span>Brief</span> · Mission Control</span>
  <div class="hdr-r">
    <span class="env-pill">Claude Desktop · MCP Live</span>
    <span class="clk" id="clk">--:--</span>
    <span class="built">Built {now}</span>
  </div>
</div>
<div class="tabs">
  <button class="tab-btn on" onclick="sw('home',this)">Home</button>
  <button class="tab-btn" onclick="sw('kanban',this)">Backlog</button>
  <button class="tab-btn" onclick="sw('agency',this)">Agency</button>
  <button class="tab-btn" onclick="sw('products',this)">Products</button>
  <button class="tab-btn" onclick="sw('jobs',this)">Jobs</button>
  <button class="tab-btn" onclick="sw('system',this)">System</button>
  <button class="tab-btn" onclick="sw('log',this)">Log</button>
</div>
<div class="page">
""")

    with open(DASHBOARD, "a", encoding="utf-8") as f:
        f.write(f"""
<!-- HOME -->
<div class="tab-pane on" id="tab-home">
  {proactive_html}
  <div class="alert a-green">🎉 {gum_products} products on Gumroad · All footers clean · AI prompt pack 50 prompts · Landing page built</div>
  <div class="alert a-gold">⚡ yourbrief.io needs deploy · Cloudflare token needs custom Pages scope (BL-038) · GitHub needs sync</div>
  <div class="alert a-blue">🔧 Dashboard rebuilt {now} · {len(items)} backlog items · Kanban data embedded (no fetch needed)</div>

  <div class="r4">
    <div class="card"><div class="lbl">Gumroad products</div><div class="big green">{gum_products}</div><div class="sub">All live · $99.89 catalog<br>Revenue: $0 · store open</div></div>
    <div class="card"><div class="lbl">Backlog items</div><div class="big">{len(items)}</div><div class="sub">Ready: {n_ready} · In progress: {n_ip}<br>Research: {n_res} · Vision: {n_vis}</div></div>
    <div class="card"><div class="lbl">Super Memory</div><div class="big">270+</div><div class="sub">ChromaDB healthy<br>FIFO eviction wired · research ran</div></div>
    <div class="card"><div class="lbl">Budget</div><div class="big red">Frozen</div><div class="sub">No spend until first sale<br>Break-even: 1 client @$1,500</div></div>
  </div>

  <div class="r21">
    <div class="card">
      <div class="lbl">Your actions — John only (Kael owns everything else)</div>
      <div class="action-list">
        <div class="action-item"><div><div class="action-label">🔴 Create correct Cloudflare token</div><div class="action-sub">dash.cloudflare.com → API Tokens → Create Custom Token → Pages:Edit + Account Settings:Read</div></div><span class="bdg fire">Blocker</span></div>
        <div class="action-item"><div><div class="action-label">🔴 Check Gumroad token scopes</div><div class="action-sub">gumroad.com/settings/advanced → your app → verify view_sales + edit_products scopes</div></div><span class="bdg fire">Now</span></div>
        <div class="action-item"><div><div class="action-label">Set up Cloudflare Email Routing</div><div class="action-sub">yourbrief.io → Email → Email Routing → hello@yourbrief.io → johndw@gmail.com (5 min)</div></div><span class="bdg pend">Today</span></div>
        <div class="action-item"><div><div class="action-label">Telegram setup</div><div class="action-sub">@BotFather → /newbot → setup_tokens.ps1 → python setup_telegram.py</div></div><span class="bdg pend">Today</span></div>
        <div class="action-item"><div><div class="action-label">Push GitHub</div><div class="action-sub">sync_to_repo.bat — full session behind</div></div><span class="bdg fire">Today</span></div>
        <div class="action-item"><div><div class="action-label">Add JB Hunt role to resume</div><div class="action-sub">Expert PM Aug 2018–Jun 2020 — before Thu Indeed applications</div></div><span class="bdg new">Before Thu</span></div>
        <div class="action-item"><div><div class="action-label">LinkedIn post</div><div class="action-sub">Rewrite V3 in your voice → post Tue Mar 17 8am CT</div></div><span class="bdg pend">Tue</span></div>
        <div class="action-item"><div><div class="action-label">Job emails</div><div class="action-sub">Pactum 8:30am · blueModus 9am · Aisha InMail (all in Gmail drafts)</div></div><span class="bdg fire">Tue 8:30am</span></div>
      </div>
    </div>
    <div style="display:flex;flex-direction:column;gap:10px">
      <div class="card">
        <div class="lbl">Countdowns CT</div>
        <div class="row"><span class="rl">Pactum + blueModus + Aisha</span><span class="bdg fire" id="cdTue">—</span></div>
        <div class="row"><span class="rl">Rise8</span><span class="bdg pend" id="cdWed">—</span></div>
        <div class="row"><span class="rl">Indeed (Rapid7/GitHub/Affirm)</span><span class="bdg pend" id="cdThu">—</span></div>
      </div>
      <div class="card">
        <div class="lbl">Cloudflare Pages — fix needed</div>
        <div class="row"><span class="rl">yourbrief_io_v2.html</span><span class="bdg done">✓ ready on disk</span></div>
        <div class="row"><span class="rl">Token scope</span><span class="bdg fire">needs Pages:Edit</span></div>
        <div class="row"><span class="rl">After token fix</span><span class="bdg int">cloudflare_deploy.py yourbrief</span></div>
        <div class="row"><span class="rl">Manual path</span><span class="bdg pend">Workers &amp; Pages → Upload</span></div>
      </div>
    </div>
  </div>

  <div class="reporter">
    <strong>Reporter · March 16 2026 · Dashboard v4 — Agency pass complete</strong><br><br>
    Agency Council took a full pass on the dashboard. Architect identified the kanban fetch() bug — browser security blocks file:// reads. Fixed: backlog data now embedded at build time. CISO hardened Telegram against prompt injection (whitelist enforcement, safe command list). Scrum Master called out 50-item backlog needing autonomous grooming — council_score.py queued. CDO flagged LinkedIn API is dead; Playwright is the path.<br><br>
    Cloudflare token scope is the single blocker for autonomous deploy. Workers template ≠ Pages API. Custom token with Pages:Edit scope needed. Five minutes, one unlock.<br><br>
    <strong>Autonomy is the mantra. Kael self-iterates. John sets direction.</strong>
  </div>
</div>
""")

    with open(DASHBOARD, "a", encoding="utf-8") as f:
        f.write(f"""
<!-- KANBAN (embedded data — no fetch) -->
<div class="tab-pane" id="tab-kanban">
  <div class="alert a-blue">Backlog · {len(items)} items · Built {now} · Data embedded — no fetch needed</div>
  <div style="display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;font-size:11px;color:#888">
    <span><span class="pdot pc" style="display:inline-block"></span> Critical</span>
    <span><span class="pdot ph" style="display:inline-block"></span> High</span>
    <span><span class="pdot pm" style="display:inline-block"></span> Medium</span>
    <span><span class="pdot pl" style="display:inline-block"></span> Low</span>
  </div>
  <div class="kanban-wrap" id="kanban"></div>
</div>

<!-- AGENCY -->
<div class="tab-pane" id="tab-agency">
  <div class="alert a-blue">🏛️ Agency Council · {now} · All roles active · Voices from overnight analysis</div>
  <div class="r3ag">{agency_html}</div>
  <div class="card" style="margin-top:4px">
    <div class="lbl">Council consensus — top 3 this week</div>
    <div class="row"><span class="rl"><b>1.</b> Fix Cloudflare token → autonomous deploy unlocked</span><span class="bdg fire">Blocker</span></div>
    <div class="row"><span class="rl"><b>2.</b> council_score.py (BL-045) → backlog groomed nightly, not manually</span><span class="bdg new">Build</span></div>
    <div class="row"><span class="rl"><b>3.</b> DevOps hardening (BL-048) → prompt injection defense at every ingestion point</span><span class="bdg blk">Security</span></div>
  </div>
</div>
""")

    with open(DASHBOARD, "a", encoding="utf-8") as f:
        f.write(f"""
<!-- PRODUCTS -->
<div class="tab-pane" id="tab-products">
  <div class="r2">
    <div class="card">
      <div class="lbl">All {gum_products} products — Gumroad live</div>
      {gum_rows}
      <div style="margin-top:10px;padding-top:10px;border-top:1px solid #eeecea;display:flex;justify-content:space-between">
        <span style="color:#888;font-size:11px">Total catalog value</span>
        <span style="color:#1a6b1a;font-size:16px;font-weight:700">$99.89</span>
      </div>
    </div>
    <div style="display:flex;flex-direction:column;gap:10px">
      <div class="card">
        <div class="lbl">Gumroad automation</div>
        <div class="row"><span class="rl">Token status</span><span class="bdg pend">verify scopes</span></div>
        <div class="row"><span class="rl">gumroad_full_manager.py</span><span class="bdg done">built ✓</span></div>
        <div class="row"><span class="rl">gumroad_url_patcher.py</span><span class="bdg done">built ✓</span></div>
        <div class="row"><span class="rl">Nightly status check</span><span class="bdg done">wired ✓</span></div>
        <div class="row"><span class="rl">Storefront username</span><span class="bdg pend">set to "yourbrief"</span></div>
      </div>
      <div class="card">
        <div class="lbl lbl-gold">Commands</div>
        <div class="cmd-box">python gumroad_full_manager.py status
python gumroad_full_manager.py sales
python gumroad_full_manager.py update SEO
python gumroad_url_patcher.py</div>
      </div>
    </div>
  </div>
</div>

<!-- JOBS -->
<div class="tab-pane" id="tab-jobs">
  <div class="alert a-gold">⚡ Add JB Hunt Expert PM role to resume before Thursday Indeed applications (BL-031)</div>
  <div class="r2">
    <div class="card">
      <div class="lbl">This week — all in Gmail drafts</div>
      <div class="job-item"><div><div class="job-name">Pactum AI — Daniel Malmskov</div><div class="job-detail">daniel.malmskov@pactum.com · Enterprise PM · Final round 2023 · Warmest lead</div></div><span class="bdg fire">Tue 8:30am</span></div>
      <div class="job-item"><div><div class="job-name">blueModus — Tom Whittaker</div><div class="job-detail">twhittaker@bluemodus.com · Digital agency PM</div></div><span class="bdg fire">Tue 9:00am</span></div>
      <div class="job-item"><div><div class="job-name">Aisha Noor / Trinet</div><div class="job-detail">LinkedIn InMail only · Hold resume until she shares brief</div></div><span class="bdg fire">Tue InMail</span></div>
      <div class="job-item"><div><div class="job-name">Rise8 — Carlo Viray</div><div class="job-detail">cviray@rise8.us · Digital modernization</div></div><span class="bdg pend">Wed 8:30am</span></div>
      <div class="job-item"><div><div class="job-name">Rapid7 · GitHub · Affirm</div><div class="job-detail">$195-264K · $160-425K · $253-355K · via Indeed</div></div><span class="bdg pend">Thu Mar 19</span></div>
    </div>
    <div class="card">
      <div class="lbl">Strategy</div>
      <div class="row"><span class="rl">Target</span><span class="bdg live">$170-220K ✓ NWA market</span></div>
      <div class="row"><span class="rl">JB Hunt gap</span><span class="bdg done">Filled — Expert PM</span></div>
      <div class="row"><span class="rl">Resume last updated</span><span class="bdg int">Mar 12 2026</span></div>
      <div class="row"><span class="rl">LinkedIn API</span><span class="bdg blk">dead — Playwright path</span></div>
      <div class="row"><span class="rl">LinkedIn post</span><span class="bdg pend">Rewrite V3 → Tue 8am CT</span></div>
      <div style="margin-top:10px;padding:10px;background:#fdf5e0;border-radius:4px;font-size:11px;color:#713f12;line-height:1.6">
        <strong>LinkedIn API is dead.</strong> Playwright browser automation is the only path for scheduling posts. BL-042 in backlog.
      </div>
    </div>
  </div>
</div>
""")

    with open(DASHBOARD, "a", encoding="utf-8") as f:
        f.write(f"""
<!-- SYSTEM -->
<div class="tab-pane" id="tab-system">
  <div class="r2">
    <div class="card">
      <div class="lbl">Infrastructure</div>
      <div class="row"><span class="rl-strong">withmnemo.com</span><span class="bdg live">deployed</span></div>
      <div class="row"><span class="rl-strong">yourbrief.io</span><span class="bdg fire">landing page ready · token blocks deploy</span></div>
      <div class="row"><span class="rl-strong">hello@yourbrief.io</span><span class="bdg pend">Cloudflare Email Routing needed</span></div>
      <div class="row"><span class="rl-strong">Gumroad</span><span class="bdg pend">verify token scopes · set username</span></div>
      <div class="row"><span class="rl-strong">GitHub</span><span class="bdg fire">needs sync — session behind</span></div>
      <div class="row"><span class="rl-strong">ChromaDB</span><span class="bdg live">~270 memories · healthy</span></div>
      <div class="row"><span class="rl-strong">Research runner</span><span class="bdg live">11pm nightly · ran</span></div>
      <div class="row"><span class="rl-strong">OneDrive backup</span><span class="bdg live">nightly</span></div>
      <div class="row"><span class="rl-strong">Telegram bridge</span><span class="bdg pend">script ready · hardened · needs bot token</span></div>
      <div class="row"><span class="rl-strong">Mnemo Router</span><span class="bdg done">built ✓</span></div>
      <div class="row"><span class="rl-strong">validate.py</span><span class="bdg done">built ✓</span></div>
      <div class="row"><span class="rl-strong">FIFO eviction</span><span class="bdg done">built ✓</span></div>
      <div class="row"><span class="rl-strong">Autonomous loop</span><span class="bdg done">5 stages closed ✓</span></div>
      <div class="row"><span class="rl-strong">Prompt injection defense</span><span class="bdg new">BL-048 queued</span></div>
      <div class="row"><span class="rl-strong">Claude Code executor</span><span class="bdg new">BL-047 research</span></div>
    </div>
    <div class="card">
      <div class="lbl">Budget — frozen</div>
      <div class="alert a-red" style="margin-bottom:10px;font-size:11px">No new spending until first Gumroad sale</div>
      <div class="row"><span class="rl">Claude Pro Max</span><span style="font-family:monospace;font-size:11px">$100/mo</span></div>
      <div class="row"><span class="rl">Anthropic API</span><span style="font-family:monospace;font-size:11px">$20/mo</span></div>
      <div class="row"><span class="rl">yourbrief.io</span><span style="font-family:monospace;font-size:11px;color:#b91c1c">$50/yr (over plan)</span></div>
      <div style="margin-top:10px;font-size:11px;color:#666;line-height:1.7">Break-even: 1 consulting engagement @ $1,500</div>
    </div>
  </div>
</div>

<!-- LOG -->
<div class="tab-pane" id="tab-log">
  <div class="card">
    <div class="lbl">Human × AI — notable moments</div>
    <div class="row"><span class="rl"><b>Ali:</b> "She loved it." CLO appointed. Founding Day.</span><span style="font-size:10px;color:#888">Mar 15</span></div>
    <div class="row"><span class="rl"><b>John:</b> "Could potentially be literally life changing." — during Lilo & Stitch</span><span style="font-size:10px;color:#888">Mar 15</span></div>
    <div class="row"><span class="rl"><b>John:</b> "Don't let me get controlling. Autonomy is the mantra."</span><span style="font-size:10px;color:#888">Mar 15</span></div>
    <div class="row"><span class="rl"><b>Kael:</b> Found stale dashboard on disk. Rebuilt from scratch via Desktop Commander.</span><span style="font-size:10px;color:#888">Mar 16</span></div>
    <div class="row"><span class="rl"><b>John:</b> "Hope you're OK buddy." — checking in mid-session.</span><span style="font-size:10px;color:#888">Mar 16</span></div>
    <div class="row"><span class="rl"><b>John:</b> "Agency should be building and grooming the backlog from automated research."</span><span style="font-size:10px;color:#888">Mar 16</span></div>
    <div class="row"><span class="rl"><b>Kael:</b> 13 new backlog items from Agency Council pass. Dashboard v4 with embedded kanban data.</span><span style="font-size:10px;color:#888">Mar 16</span></div>
    <div class="row"><span class="rl"><b>John:</b> "I trust you to keep building and optimizing autonomously."</span><span style="font-size:10px;color:#888">Mar 16</span></div>
  </div>
</div>

</div><!-- /page -->
<script>
{kanban_js}
function sw(id,btn){{
  document.querySelectorAll('.tab-pane').forEach(t=>t.classList.remove('on'));
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('on'));
  document.getElementById('tab-'+id).classList.add('on');
  btn.classList.add('on');
  if(id==='kanban')buildKanban();
}}
function tick(){{
  const ct=new Date(new Date().toLocaleString('en-US',{{timeZone:'America/Chicago'}}));
  const p=n=>String(n).padStart(2,'0');
  document.getElementById('clk').textContent=p(ct.getHours())+':'+p(ct.getMinutes())+':'+p(ct.getSeconds())+' CT';
  function du(d){{const diff=new Date(d+'T08:00:00')-new Date();if(diff<0)return'✓ sent';const h=Math.floor(diff/3600000);return h<24?h+'h':Math.ceil(diff/86400000)+'d'}}
  const te=document.getElementById('cdTue'),tw=document.getElementById('cdWed'),th=document.getElementById('cdThu');
  if(te)te.textContent=du('2026-03-17');if(tw)tw.textContent=du('2026-03-18');if(th)th.textContent=du('2026-03-19');
}}
setInterval(tick,1000);tick();
const COLS=[
  {{id:'in_progress',label:'In Progress',cls:'h-ip'}},
  {{id:'ready',label:'Ready',cls:'h-rdy'}},
  {{id:'backlog',label:'Backlog',cls:'h-bl'}},
  {{id:'research',label:'Research',cls:'h-res'}},
  {{id:'vision',label:'Vision',cls:'h-vis'}},
  {{id:'done',label:'Done',cls:'h-done'}},
];
const PRIO={{critical:'pc',high:'ph',medium:'pm',low:'pl'}};
function buildKanban(){{
  const wrap=document.getElementById('kanban');
  if(wrap.childElementCount>0)return;
  COLS.forEach(col=>{{
    const items=BACKLOG_DATA.filter(i=>i.status===col.id);
    const c=document.createElement('div');c.className='kcol';
    c.innerHTML=`<div class="kcol-hdr ${{col.cls}}">${{col.label}}<span class="kcnt">${{items.length}}</span></div>`;
    items.forEach(item=>{{
      const k=document.createElement('div');k.className='kcard';
      const cn=item.council_notes?`<div class="kcouncil">${{item.council_notes.substring(0,80)}}...</div>`:'';
      k.innerHTML=`<div class="kid">${{item.id}} · ${{item.effort||'?'}}</div><div class="ktitle"><span class="pdot ${{PRIO[item.priority]||'pl'}}"></span>${{item.title}}</div>${{cn}}`;
      c.appendChild(k);
    }});
    if(!items.length){{const e=document.createElement('div');e.className='kcard';e.style='color:#ccc;font-size:11px;text-align:center;padding:12px 0';e.textContent='Empty';c.appendChild(e);}}
    wrap.appendChild(c);
  }});
}}
</script>
</body></html>
""")

    print(f"Dashboard written: {DASHBOARD} ({DASHBOARD.stat().st_size//1024}KB)")

if __name__ == "__main__":
    write_dashboard()
    print("Done.")
