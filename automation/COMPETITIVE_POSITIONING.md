# COMPETITIVE POSITIONING — Super Memory vs The Field
# Generated: March 16, 2026 | Agency: CMO + VP Product + Board Advisor
# Purpose: Know exactly where we win, where we lose, how to talk about it

---

## THE COMPETITIVE LANDSCAPE (as of March 2026)

### Tier 1: Direct Competitors

**Mem0** (mem0.ai)
- Funding: $24M Series A
- Users: 50,000+ developers
- Model: Cloud API — you send prompts, they store extracted memories server-side
- Pricing: Free tier (limited), Pro $249/month, Enterprise custom
- Stack: Hosted vector DB + graph DB, REST API
- What they do well: Drop-in API, great for developers building apps, multi-user
- Fatal flaw: Your data lives on their servers. Privacy-conscious users can't use it.
- Fatal flaw 2: $249/mo is too expensive for individual knowledge workers
- Our angle: "Same outcome, runs on your machine, costs $0 in infrastructure"

**MemGPT / Letta**
- Model: Open source framework for LLM agents with hierarchical memory
- Stack: Python framework, multiple backends
- What they do well: Academic rigor, great for researchers building agents
- Fatal flaw: Setup complexity is brutal. Not for non-technical users.
- Fatal flaw 2: Designed for building systems, not for end users
- Our angle: "Built for people, not for engineers building for people"

**OpenClaw built-in memory**
- Model: File-first, Markdown daily notes + MEMORY.md long-term
- Stack: SQLite + sqlite-vec + FTS5 hybrid search
- What they do well: Works out of the box with OpenClaw, zero config
- Fatal flaw: Flat files. No structured collections. No relationship reasoning.
- Fatal flaw 2: No autonomous overnight operation. No research runner.
- Fatal flaw 3: Context compaction loses memories. Their own blog post admits it.
- Our angle: "OpenClaw's memory forgets. Ours doesn't."

**Memori Labs** (memorilabs.ai) — NEWEST, most relevant threat
- Launched: March 13, 2026 (3 days ago)
- Model: SQL-native memory as a service for OpenClaw agents
- Stack: Cloud service with OpenClaw plugin
- What they do well: Production-ready, structured records, knowledge graph
- Fatal flaw: Cloud service — data leaves your machine
- Fatal flaw 2: Requires OpenClaw gateway — not Claude Desktop native
- Fatal flaw 3: $0 info on pricing yet — likely enterprise/B2B
- Our angle: "We built this for Claude Desktop users, not OpenClaw gateway operators"

---

### Tier 2: Adjacent Competitors

**Obsidian + AI plugins** — Knowledge management nerds love this. Complex. Our users don't want to manage a second system.

**NotebookLM** — Google's product. Read-only. No persistent memory across sessions.

**ChatGPT Memory** — OpenAI's built-in. Works only in ChatGPT. Not for Claude users.

**Claude Projects** — Anthropic's own feature. Great for static context. No autonomous research, no overnight operation, no structured collections, no morning brief.

---

## WHERE WE WIN DECISIVELY

1. **Local-first privacy** — Nothing leaves the machine. Mem0 can't touch us here.
2. **Claude Desktop native** — We ARE the MCP server. Deepest integration possible.
3. **Autonomous overnight operation** — Nobody else does this for end users. Research runner + morning brief is genuinely novel.
4. **Structured collections** — 6 typed collections (projects, people, decisions, knowledge, conversations, tasks). Not flat files.
5. **Cost** — Infrastructure is free. API is $15/mo cap. Mem0 Pro is $249/mo.
6. **Built for the persona** — We're built for senior professionals (Directors, PMs, execs). Everyone else is building for developers.

---

## WHERE WE'RE BEHIND

1. **Multi-user** — Mem0 handles teams. We're single-user only right now.
2. **Mobile** — No iOS/Android client. Desktop-only.
3. **Knowledge graph** — Memori has graph relationships. We have flat vector search.
4. **Ease of install** — Still requires CLI. VIS-002 (GUI installer) is the fix.
5. **Distribution** — 0 GitHub stars vs Mem0's 50K devs. Open source pivot addresses this.

---

## THE ONE-LINER

> "The only AI memory system that runs overnight, researches topics autonomously, and wakes you up with a morning brief — all on your own machine."

No competitor has that sentence. Own it.

---

## MESSAGING BY AUDIENCE

**For HackerNews / developers:**
"Persistent memory for Claude Desktop using ChromaDB + MCP. Runs locally. Has an autonomous research loop that writes you a morning brief. Open source."

**For Directors / PMs / knowledge workers:**
"Claude finally remembers you. Every session picks up where the last left off. While you sleep, it researches the topics that matter to your work. You wake up to a brief."

**For OpenClaw community:**
"chromadb-memory plugin — drop-in persistent memory for your OpenClaw agents. Local, zero cloud, auto-recall every turn."

**For consulting prospects:**
"I'll set up a system that gives your AI a persistent, structured memory of your work — built on open-source infrastructure, running on your machine, fully private."

---

## AGAINST-MEMORI SPECIFIC (most urgent)

Memori launched 3 days ago into the exact space we're building. Key differentiators:

| | Super Memory | Memori |
|---|---|---|
| Data location | Local machine | Memori cloud |
| Claude Desktop native | Yes (MCP server) | No (OpenClaw plugin) |
| Works offline | Yes | No |
| Morning brief | Yes | No |
| Autonomous research | Yes | No |
| Knowledge graph | No (roadmap) | Yes |
| Pricing | Free / $15mo API | Unknown (B2B) |
| Target user | Individual professional | Developer / ops team |

Their CEO quote: "Agents are only as good as the context they have access to."
Our response: "Agreed. That's why ours runs overnight to get more of it."

---
*Last updated: March 16, 2026 | Next review: After HN launch + first 100 GitHub stars*
