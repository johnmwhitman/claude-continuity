# 🧠 Super Memory — Persistent AI Memory for Claude Desktop

> **Your AI finally knows you.** Wake up to a morning brief your AI wrote while you slept.

Super Memory gives Claude Desktop **persistent memory that works autonomously overnight** — storing context, running research, and surfacing intelligence — so every session starts warm instead of blank.

---

## The Problem

Every time you open Claude, it forgets everything. You re-explain your role, your projects, your preferences, your decisions. You're paying for a brilliant assistant with amnesia.

Current "memory" solutions are either:
- **Too expensive** — Mem0 charges $249/month
- **Too complex** — MemGPT requires a PhD to configure
- **Too limited** — Flat files that can't reason about relationships

## The Solution

Super Memory is a **local-first, autonomous AI memory system** built on:

```
Claude Desktop  ←→  MCP Server  ←→  ChromaDB (vector store)
                                  ↕
                         Nightly Research Runner
                         (researches topics while you sleep)
                                  ↕
                         Morning Brief Generator
                         (ready when you wake up)
```

**What it actually does:**
- Stores everything meaningful across all your Claude sessions
- Runs nightly research on topics you care about (job market, AI trends, your industry)
- Writes you a morning brief synthesizing overnight findings
- Surfaces proactive alerts when something important changes
- Works 100% locally — no data leaves your machine

---

## Demo

**Session 1 (Monday):**
> You: "I'm a Director of Product Management at a 140-location consumer finance company."

**Session 2 (Friday, different chat):**
> Claude: *[loads context automatically]* "By the way, the Palantir Foundry deprecation I flagged last night — it affects your March 31 deadline. Here's what changed..."

That's what this is.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/[username]/super-memory
cd super-memory

# 2. Install
python install.py --mode=full

# 3. Follow the Claude Desktop MCP config instructions printed at the end

# 4. Restart Claude Desktop
```

**Prerequisites:** Python 3.11+, [Claude Desktop](https://claude.ai/download), [Ollama](https://ollama.com)

Full install guide: [docs/INSTALL.md](docs/INSTALL.md)

---

## Architecture

```
super-memory/
├── server/           # MCP server (Claude Desktop integration)
│   └── memory_server.py
├── pipeline/         # Autonomous overnight pipeline
│   ├── run_research_missions.py    # Nightly web research
│   ├── morning_brief.py            # Brief generation
│   ├── council_score.py            # AI-powered priority scoring
│   └── reddit_curator.py           # Curated news digest
├── security/
│   └── memory_sanitizer.py         # Input sanitization / injection defense
├── install.py        # One-command installer
└── docs/
```

---

## Memory Collections

Super Memory organizes context into 6 typed collections:

| Collection | What goes here |
|-----------|----------------|
| `projects` | Active work, initiatives, features |
| `people` | Team members, stakeholders, relationships |
| `decisions` | Key choices, rationale, outcomes |
| `knowledge` | Domain expertise, frameworks, reference |
| `conversations` | Session summaries |
| `tasks` | Action items, commitments |

---

## Research Runner

The killer feature. Configure goals like:

```yaml
research_goals:
  - id: "ai-trends-weekly"
    title: "AI Trends — Stay Ahead of the Curve"
    frequency: "weekly"
    priority: "high"
    # Routes to Claude Sonnet w/ web search overnight
    # Personal goals route to local Ollama (never leave your machine)

  - id: "my-industry-intel"
    title: "Industry Intelligence"
    frequency: "biweekly"
    personal_context: false  # safe for cloud routing
```

Every night at 11pm:
1. Runner fires, searches the web for each goal
2. Synthesizes findings into structured briefs
3. Flags anything urgent to `proactive_items.txt`
4. Morning brief generated at 7am

**Cost:** ~$0.15/night for a typical set of goals (Anthropic API).

---

## Security Model

- **Local-first:** All memories stored in ChromaDB on your machine
- **Privacy routing:** Personal goals (health, finance, job search) route to Ollama only — never touch cloud APIs
- **Injection defense:** `memory_sanitizer.py` screens all research output for prompt injection patterns before it enters memory
- **No telemetry:** Nothing phoned home, ever

---

## OpenClaw Integration

Super Memory works as an OpenClaw plugin:

```bash
clawhub install super-memory/chromadb-memory
```

Gives any OpenClaw agent persistent semantic memory backed by your local ChromaDB.

---

## Comparison

| | Super Memory | Mem0 | MemGPT | OpenClaw built-in |
|---|---|---|---|---|
| Local-first | ✅ | ❌ | ✅ | ✅ |
| Autonomous research | ✅ | ❌ | ❌ | ❌ |
| Morning brief | ✅ | ❌ | ❌ | ❌ |
| Free | ✅ (infra) | ❌ ($249/mo) | ✅ | ✅ |
| Claude Desktop native | ✅ | ❌ | ❌ | ❌ |
| Works overnight | ✅ | ❌ | ❌ | ❌ |

---

## Consulting & Setup

Super Memory is free and open source. For teams or individuals who want a
guided setup, configuration for your specific context, and ongoing support —
[contact us](mailto:hello@withmnemo.com).

Setup fee: $1,000–$2,000. Monthly support: $500–$1,500.

---

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

The most valuable contributions right now:
- Memory backend adapters (Qdrant, Weaviate, pgvector)
- Research goal templates for different professions
- OpenClaw plugin improvements
- Windows/macOS/Linux install hardening

---

## License

MIT — use it, fork it, build on it.

---

*Built by a Director of Product Management who got tired of re-explaining himself to Claude every Monday morning.*
