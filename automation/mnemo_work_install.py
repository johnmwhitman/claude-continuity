"""
mnemo_work_install.py
CLEAN WORK LAPTOP INSTALLER — Legal IP Protection Mode

This installs ONLY the core Mnemo infrastructure on a work laptop.
NO personal data. NO business data. NO GitHub connection.
Designed so employer cannot claim ownership of anything installed.

What gets installed:
  - Python packages (chromadb, requests, anthropic)
  - Ollama (local AI — runs offline, no cloud)
  - Work-safe research goals only
  - MCP server config for Claude Desktop

What does NOT get installed:
  - Personal research goals (health, finance, job search, real estate)
  - Etsy/Gumroad business context
  - Personal memory from home laptop
  - GitHub repo connection
  - Any Mnemo business IP

Run: python mnemo_work_install.py
"""
import os, sys, json, subprocess, shutil
from pathlib import Path

WORK_DIR    = Path(r"C:\AI-Work")
MEMORY_DIR  = WORK_DIR / "memory"
LOG_DIR     = WORK_DIR / "logs"
AUTO_DIR    = WORK_DIR / "automation"
PYTHON      = r"C:\Python314\python.exe"

BANNER = """
╔══════════════════════════════════════════════════════╗
║         MNEMO WORK INSTALL — CLEAN BUILD             ║
║                                                      ║
║  This is a SEPARATE install from your personal       ║
║  Mnemo system. No personal data. No GitHub.          ║
║  Safe for a work laptop.                             ║
╚══════════════════════════════════════════════════════╝
"""


WORK_RESEARCH_GOALS = {
    "version": "1.0",
    "description": "Work-safe research goals — professional development only. No personal data.",
    "privacy_policy": {
        "note": "Work build only. All queries are professional/generic. No personal context ever."
    },
    "goals": [
        {
            "id": "pm-skills-weekly",
            "title": "Product Management — Skills & Trends",
            "priority": "high",
            "frequency": "weekly",
            "active": True,
            "personal_context": False,
            "search_queries": [
                "product management trends 2026",
                "AI product management skills enterprise 2026",
                "MCP model context protocol enterprise adoption 2026"
            ],
            "output_format": "3 bullets: skill/trend, why it matters, one actionable takeaway.",
            "tags": ["pm", "skills", "professional"]
        },
        {
            "id": "ai-agent-patterns",
            "title": "AI Agent Patterns — Enterprise Use Cases",
            "priority": "high",
            "frequency": "weekly",
            "active": True,
            "personal_context": False,
            "search_queries": [
                "autonomous AI agents enterprise deployment 2026",
                "agentic AI workflow patterns production 2026",
                "LLM RAG enterprise knowledge management 2026"
            ],
            "output_format": "3 bullets: pattern name, enterprise use case, technical approach.",
            "tags": ["ai", "enterprise", "agents"]
        },
        {
            "id": "palantir-updates-work",
            "title": "Palantir Foundry — Updates & Best Practices",
            "priority": "medium",
            "frequency": "weekly",
            "active": True,
            "personal_context": False,
            "search_queries": [
                "Palantir Foundry AIP updates 2026",
                "Palantir Workshop best practices reporting 2026"
            ],
            "output_format": "2 bullets: update/feature, practical application.",
            "tags": ["palantir", "work"]
        }
    ],
    "output_settings": {
        "briefs_folder": "C:\\AI-Work\\logs\\research_briefs\\",
        "brief_filename_format": "{goal_id}_{YYYY-MM-DD}.txt"
    }
}

def step(n, total, msg):
    print(f"\n[{n}/{total}] {msg}")
    print("-" * 50)

def run_command(cmd, description):
    print(f"  Running: {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  OK")
        return True
    else:
        print(f"  WARNING: {result.stderr[:100] if result.stderr else 'non-zero exit'}")
        return False

def create_directories():
    dirs = [WORK_DIR, MEMORY_DIR, LOG_DIR, AUTO_DIR,
            WORK_DIR / "backup", LOG_DIR / "research_briefs"]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print(f"  Created: {WORK_DIR}")

def install_python_packages():
    packages = ["chromadb", "requests", "anthropic"]
    for pkg in packages:
        run_command(f'"{PYTHON}" -m pip install {pkg} --quiet', pkg)

def write_work_goals():
    goals_path = AUTO_DIR / "research_goals.json"
    goals_path.write_text(json.dumps(WORK_RESEARCH_GOALS, indent=2), encoding="utf-8")
    print(f"  Written: {goals_path}")

def write_mcp_config_instructions():
    instructions = """
# CLAUDE DESKTOP MCP CONFIG — Work Laptop
# Add this to: C:\\Users\\[USERNAME]\\AppData\\Roaming\\Claude\\claude_desktop_config.json

{
  "mcpServers": {
    "claude-memory-work": {
      "command": "node",
      "args": ["[PATH_TO_CLAUDE_MEMORY_SERVER]/index.js"],
      "env": {
        "MEMORY_DIR": "C:\\\\AI-Work\\\\memory"
      }
    }
  }
}

# NOTE: Install claude-memory MCP server separately.
# This points it at C:\\AI-Work\\memory (work data only, isolated from personal)
"""
    (AUTO_DIR / "MCP_CONFIG_INSTRUCTIONS.txt").write_text(instructions, encoding="utf-8")
    print("  Written: MCP_CONFIG_INSTRUCTIONS.txt")

def main():
    print(BANNER)
    print("Starting work laptop install...")
    print("This creates C:\\AI-Work\\ — completely separate from any personal install.")

    step(1, 5, "Creating directory structure")
    create_directories()

    step(2, 5, "Installing Python packages")
    install_python_packages()

    step(3, 5, "Writing work-safe research goals")
    write_work_goals()

    step(4, 5, "Writing MCP config instructions")
    write_mcp_config_instructions()

    step(5, 5, "Writing environment variable setup")
    env_script = f'''# Run this in PowerShell to set work environment variables
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", (Read-Host "Enter Anthropic API Key"), "User")
Write-Host "API key set."
'''
    (AUTO_DIR / "set_work_env.ps1").write_text(env_script, encoding="utf-8")
    print("  Written: set_work_env.ps1")

    print("\n" + "=" * 55)
    print("WORK INSTALL COMPLETE")
    print("=" * 55)
    print(f"""
Next steps:
  1. Install Ollama at ollama.com
  2. Run: ollama pull llama3.2:3b
  3. Install Claude Desktop at claude.ai/download
  4. Follow MCP_CONFIG_INSTRUCTIONS.txt
  5. Run set_work_env.ps1 to set API key
  6. Restart Claude Desktop and verify memory works

What's installed:   C:\\AI-Work\\
Personal laptop:    C:\\AI\\  (completely separate)
No data shared between the two. Employer has no claim.
""")

if __name__ == "__main__":
    main()
