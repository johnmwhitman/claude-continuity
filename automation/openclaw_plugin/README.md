# chromadb-memory

Persistent semantic memory for OpenClaw agents. 
ChromaDB + Ollama. Local-first. Zero cloud. Auto-recall every turn.

## What it does

Before every agent turn, queries your local ChromaDB for relevant memories 
and injects them as context. After every turn, saves new context automatically.

Your agent remembers. Forever.

## Requirements

- ChromaDB running: `docker run -p 8100:8000 chromadb/chroma`
- Ollama running with nomic-embed-text: `ollama pull nomic-embed-text`

## Install

```bash
clawhub install super-memory/chromadb-memory
```

## Config

```json
{
  "plugins": {
    "chromadb-memory": {
      "enabled": true,
      "config": {
        "chromaUrl": "http://localhost:8100",
        "collectionName": "agent_memory",
        "ollamaUrl": "http://localhost:11434",
        "embeddingModel": "nomic-embed-text",
        "autoRecall": true,
        "autoRecallResults": 5,
        "minScore": 0.5,
        "autoSave": true
      }
    }
  }
}
```

## Part of Super Memory

This plugin is part of [Super Memory](https://github.com/[username]/super-memory) —
the open-source persistent AI memory system for Claude Desktop.

Super Memory adds: autonomous overnight research, morning briefs, 
council-based prioritization, and a full MCP server integration.
