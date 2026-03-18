# MNEMO / SUPER MEMORY — 6-MONTH ROI MODEL & CAPITAL PLAN
# Generated: March 16, 2026
# Author: Kael (Agency Controller + CFO review)
# Status: Board reviewed — open source pivot incorporated

---

## EXECUTIVE SUMMARY

Super Memory is a net-positive investment at current spend levels.
The open source pivot changes the revenue model from SaaS-first to consulting-first.
Break-even is achievable within 60 days of first GitHub stars.

---

## CURRENT BURN RATE

| Item | Monthly Cost |
|------|-------------|
| Claude Pro Max | $100 |
| Anthropic API (research runner) | $15 (new cap, down from $20) |
| yourbrief.io domain | $4.17 (amortized from $50/yr) |
| withmnemo.com domain | $0.83 (amortized) |
| **Total Monthly Burn** | **~$120** |

6-month total investment at current rate: **$720**

Note: API cost now capped at $15/mo after implementing api_cost_monitor.py
and switching research to biweekly cadence. Previous uncapped rate was $60-150/mo.

---

## REVENUE SCENARIOS

### Scenario 1: Consulting Only (Conservative)
One consulting engagement per quarter at $1,500 setup + $500/mo support.

| Month | Revenue | Cumulative | Notes |
|-------|---------|------------|-------|
| 1 | $0 | -$120 | Building, no clients yet |
| 2 | $0 | -$240 | GitHub repo live, HN post |
| 3 | $1,500 | +$1,260 | First consulting client via GitHub |
| 4 | $500 | +$1,640 | First client retainer |
| 5 | $1,500 | +$2,820 | Second client setup |
| 6 | $1,000 | +$3,700 | Two retainers running |

**6-month net: +$3,700** | Break-even: Month 3

### Scenario 2: YourBrief Passive + Consulting
YourBrief Gumroad products generate $200-500/month passive (10 products × modest sales).

| Month | Revenue | Notes |
|-------|---------|-------|
| 1 | $200 | First Gumroad sales after publish |
| 2 | $350 | Word-of-mouth + SEO |
| 3 | $1,850 | Consulting client #1 |
| 4 | $850 | Retainer + ongoing Gumroad |
| 5 | $2,350 | Consulting client #2 |
| 6 | $1,350 | Two retainers + Gumroad |

**6-month net: +$5,220**

### Scenario 3: Open Source Traction (Upside)
GitHub repo goes viral (>1,000 stars in first month).
Consulting inquiries → $3,000-5,000/month by Month 4.

Not modeling this yet — too speculative. But it's the asymmetric upside.

---

## BREAK-EVEN ANALYSIS

At $120/month burn:
- **1 consulting client** at $1,500 setup = covers 12.5 months of burn
- **3 Gumroad products sold/month** at $9.99 avg = covers monthly burn
- **500 GitHub stars** → realistic consulting inquiry rate ~2-5% → 10-25 leads

The economics are favorable. The key unlock is distribution (GitHub stars).

---

## OPEN SOURCE IMPACT ON ROI

### What changes with open source:
1. **Distribution cost → $0** (GitHub is free marketing)
2. **Consulting leads → inbound** (no cold outreach needed)
3. **YourBrief story strengthens** (credibility from open source)
4. **API costs → stay the same** (infrastructure doesn't change)

### What doesn't change:
- Monthly burn (~$120)
- Timeline to first client
- YourBrief passive income potential

### New revenue streams (open source creates):
- GitHub Sponsors: $0-500/mo (small but real)
- Enterprise consulting: $5,000-15,000 setup for company-wide deployment
- Hosted service (Month 6+): $49-99/mo SaaS once 3+ clients validate

---

## CAPITAL ALLOCATION RULES

**FROZEN until first Gumroad sale:**
- johnwhitman.ai domain ($80/2yr)
- Hetzner VPS for 24/7 uptime ($5/mo)
- GPU upgrade for local AI ($300)

**Can spend on:**
- Additional API credits when research value confirmed (cap: $15/mo)
- Domain renewals (mandatory, <$5/mo)
- No other spend without board approval

**Revenue triggers for spending:**
- First Gumroad sale ($7.99+) → ✅ unlock VPS consideration
- $500 total revenue → ✅ unlock GPU research
- First consulting client → ✅ unlock johnwhitman.ai domain

---

## MILESTONES & TIMELINE

| Week | Milestone | Revenue Unlock |
|------|-----------|----------------|
| 1 (now) | Publish Gumroad products (10 items) | $0-50 |
| 1-2 | GitHub repo public | Distribution |
| 2-3 | HackerNews post | Star velocity |
| 3-4 | OpenClaw plugin live on ClawKit | Dev community |
| 4-6 | First GitHub-referral consulting inquiry | $1,500+ |
| 8-12 | First consulting client contracted | Break-even |

---

## RISK FACTORS

| Risk | Probability | Mitigation |
|------|-------------|------------|
| API credits burn faster than cap | Low (monitor implemented) | api_cost_monitor.py |
| Gumroad sales = $0 | Medium | Publish immediately; iterate |
| GitHub stars stall at <100 | Medium | HN post + OpenClaw plugin |
| Consulting inquiry but can't close | Low | John closes; Kael preps |
| Market moves to built-in memory | Medium | Open source faster than wait |

---

## BOTTOM LINE

**Best case (12 months):** $20,000-40,000 consulting revenue + growing Gumroad passive
**Base case (12 months):** $5,000-10,000 total, 3-4 consulting clients
**Worst case:** $0 external revenue, but system pays for itself in personal productivity

The worst case is still a win. John gets a world-class AI assistant for $120/month.
The rest is upside.

*Last updated: March 16, 2026*
*Next review: After first Gumroad sale*
