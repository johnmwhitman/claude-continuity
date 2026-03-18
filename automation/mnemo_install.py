"""
mnemo_install.py — Mnemo Modular Installer
Supports component selection for personal vs work environments.

Usage:
  python mnemo_install.py              # Interactive mode
  python mnemo_install.py --mode=work  # Work laptop (minimal, privacy-safe)
  python mnemo_install.py --mode=full  # Full personal stack
  python mnemo_install.py --mode=custom # Choose components

COMPONENTS:
  core      - ChromaDB + MCP server + Claude Desktop config (always required)
  ollama    - Local LLM inference (Qwen + Llama)
  research  - Nightly research runner (Anthropic API required)
  github    - Git + GitHub auto-push
  scheduler - Task Scheduler automation jobs
  gemini    - Gemini Flash free tier routing
  dashboard - System health dashboard
  kanban    - Project kanban board

MODES:
  work    = core + ollama + dashboard (no external calls, no GitHub, no scheduler)
  full    = all components
  custom  = interactive component selection
"""
import os, sys, subprocess, json, datetime, platform

VERSION = "1.0.0"
BASE_DIR = "C:\\AI"
PYTHON = sys.executable

COMPONENTS = {
    "core": {
        "label": "Mnemo Core (ChromaDB + MCP + Claude config)",
        "required": True,
        "description": "The memory system itself. Always installed.",
        "work_safe": True,
    },
    "ollama": {
        "label": "Ollama Local LLM (Qwen + Llama)",
        "required": False,
        "description": "Free local AI inference. No internet required.",
        "work_safe": True,
    },
    "dashboard": {
        "label": "System Health Dashboard",
        "required": False,
        "description": "Python dashboard showing system status.",
        "work_safe": True,
    },
    "scheduler": {
        "label": "Task Scheduler Automation",
        "required": False,
        "description": "Windows Task Scheduler jobs for nightly automation.",
        "work_safe": False,
        "work_note": "Excluded: Task Scheduler jobs may trigger IT security alerts.",
    },
    "research": {
        "label": "Nightly Research Runner",
        "required": False,
        "description": "Autonomous research via Anthropic API. Requires ANTHROPIC_API_KEY.",
        "work_safe": False,
        "work_note": "Excluded: External API calls may violate corporate policy.",
    },
    "github": {
        "label": "GitHub Integration",
        "required": False,
        "description": "Git install + auto-push to private repo.",
        "work_safe": False,
        "work_note": "Excluded: Git may conflict with corporate VPN/proxy.",
    },
    "gemini": {
        "label": "Gemini Flash Routing",
        "required": False,
        "description": "Google Gemini free tier for generic queries.",
        "work_safe": False,
        "work_note": "Excluded: External Google API not appropriate for work context.",
    },
    "kanban": {
        "label": "Project Kanban Board",
        "required": False,
        "description": "HTML kanban board for backlog/roadmap visualization.",
        "work_safe": True,
    },
}

MODES = {
    "work": {
        "label": "Work Mode (safe for corporate environments)",
        "description": "Core memory + local AI only. No external APIs, no GitHub, no schedulers.",
        "components": ["core", "ollama", "dashboard"],
        "notes": [
            "Only outbound traffic: Anthropic API (same as normal Claude Desktop usage)",
            "No GitHub, no Google APIs, no Task Scheduler jobs",
            "Safe for domain-joined machines with strict security policies",
        ]
    },
    "full": {
        "label": "Full Personal Stack",
        "description": "Everything. For personal machines with no corporate restrictions.",
        "components": list(COMPONENTS.keys()),
        "notes": []
    },
    "custom": {
        "label": "Custom (choose components)",
        "description": "Interactive component selection.",
        "components": [],
        "notes": []
    }
}

def header():
    print("\n" + "=" * 60)
    print(f"  🧠 MNEMO INSTALLER v{VERSION}")
    print(f"  Autonomous AI Memory System")
    print(f"  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def select_mode():
    print("\nSelect installation mode:\n")
    mode_list = list(MODES.items())
    for i, (key, mode) in enumerate(mode_list, 1):
        print(f"  {i}. {mode['label']}")
        print(f"     {mode['description']}")
        if mode.get("notes"):
            for note in mode["notes"]:
                print(f"     ✓ {note}")
        print()

    while True:
        choice = input("Enter choice (1-3): ").strip()
        if choice in ("1", "2", "3"):
            return mode_list[int(choice)-1][0]
        print("Please enter 1, 2, or 3.")

def select_components_custom():
    selected = ["core"]  # always required
    print("\nSelect components to install:\n")
    optional = [(k, v) for k, v in COMPONENTS.items() if not v["required"]]
    for i, (key, comp) in enumerate(optional, 1):
        print(f"  {i}. {comp['label']}")
        print(f"     {comp['description']}")
    print()
    choices = input("Enter component numbers (e.g. 1,2,4) or 'all': ").strip()
    if choices.lower() == "all":
        return list(COMPONENTS.keys())
    for c in choices.split(","):
        c = c.strip()
        if c.isdigit() and 1 <= int(c) <= len(optional):
            selected.append(optional[int(c)-1][0])
    return selected

def show_plan(mode_key, components):
    mode = MODES[mode_key]
    print(f"\n{'=' * 60}")
    print(f"INSTALLATION PLAN: {mode['label']}")
    print(f"{'=' * 60}")
    print("\nComponents to install:")
    for comp in components:
        c = COMPONENTS[comp]
        status = "✅ REQUIRED" if c["required"] else "✅ Selected"
        print(f"  {status}: {c['label']}")

    excluded = [k for k in COMPONENTS if k not in components and not COMPONENTS[k]["required"]]
    if excluded:
        print("\nComponents NOT installing:")
        for comp in excluded:
            c = COMPONENTS[comp]
            note = c.get("work_note", "Not selected")
            print(f"  ⬜ {c['label']}: {note}")

    print(f"\nInstall directory: {BASE_DIR}")
    confirm = input("\nProceed? (y/n): ").strip().lower()
    return confirm == "y"

def run_step(label, fn):
    print(f"\n  ▶ {label}...", end="", flush=True)
    try:
        fn()
        print(" ✅")
        return True
    except Exception as e:
        print(f" ❌ ({e})")
        return False

def install_core():
    """Always runs. Creates directory structure, verifies ChromaDB."""
    dirs = [
        f"{BASE_DIR}\\memory",
        f"{BASE_DIR}\\automation",
        f"{BASE_DIR}\\logs",
        f"{BASE_DIR}\\backup",
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # Install ChromaDB and requests
    subprocess.run([PYTHON, "-m", "pip", "install", "chromadb", "requests",
                   "--quiet", "--break-system-packages"],
                   capture_output=True)

def install_ollama():
    """Checks if Ollama is installed, installs if not."""
    result = subprocess.run(["ollama", "--version"],
                          capture_output=True, text=True)
    if result.returncode != 0:
        subprocess.run(["winget", "install", "--id", "Ollama.Ollama",
                       "-e", "--source", "winget", "--silent"],
                      capture_output=True)

def install_scheduler(components):
    """Installs only appropriate Task Scheduler jobs."""
    # Import and run task_manager
    sys.path.insert(0, f"{BASE_DIR}\\automation")
    try:
        import task_manager
        # Only install jobs relevant to selected components
        jobs_to_install = ["ClaudeMemory-OnLogon", "ClaudeMemory-OnWake"]
        if "research" in components:
            jobs_to_install += ["ClaudeMemory-ResearchRunner",
                               "ClaudeMemory-NightlyPipeline",
                               "ClaudeMemory-MorningBrief"]
        if "github" in components:
            jobs_to_install.append("ClaudeMemory-GitHubPush")
        for job in jobs_to_install:
            task_manager.install_task(job)
    except ImportError:
        raise Exception("task_manager.py not found")

def write_work_config():
    """Writes a work-safe claude_desktop_config.json (no external API servers)."""
    config = {
        "mcpServers": {
            "claude-memory": {
                "command": f"{os.path.expanduser('~')}\\.claude-memory\\venv\\Scripts\\python.exe",
                "args": [f"{os.path.expanduser('~')}\\.claude-memory\\server\\memory_server.py"],
                "env": {"CLAUDE_MEMORY_DIR": f"{BASE_DIR}\\memory"}
            }
        },
        "preferences": {
            "coworkScheduledTasksEnabled": False,
            "sidebarMode": "chat"
        }
    }
    config_path = os.path.join(os.environ.get("APPDATA", ""), "Claude",
                               "claude_desktop_config.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

def write_install_manifest(mode_key, components):
    """Records what was installed for future reference and upgrades."""
    manifest = {
        "version": VERSION,
        "installed": datetime.datetime.now().isoformat(),
        "mode": mode_key,
        "components": components,
        "machine": platform.node(),
        "python": sys.version,
    }
    with open(f"{BASE_DIR}\\automation\\install_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

def run_install(mode_key, components):
    print(f"\n{'=' * 60}")
    print("INSTALLING...")
    print(f"{'=' * 60}")

    results = {}

    # Always: core
    results["core"] = run_step("Creating directory structure + installing Python deps",
                                install_core)

    if "ollama" in components:
        results["ollama"] = run_step("Checking/installing Ollama", install_ollama)

    if "scheduler" in components:
        results["scheduler"] = run_step("Installing Task Scheduler jobs",
                                         lambda: install_scheduler(components))

    if mode_key == "work":
        results["work_config"] = run_step("Writing work-safe Claude Desktop config",
                                           write_work_config)

    # Always: record manifest
    results["manifest"] = run_step("Writing install manifest",
                                    lambda: write_install_manifest(mode_key, components))

    # Summary
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n{'=' * 60}")
    print(f"INSTALL COMPLETE: {passed}/{total} steps succeeded")

    if mode_key == "work":
        print("\n⚠️  WORK MODE NOTES:")
        print("  • Only core memory + local AI installed")
        print("  • No external API calls beyond normal Claude Desktop usage")
        print("  • Restart Claude Desktop to activate MCP server")
        print("  • Your conversations stay private — context stored locally only")

    print(f"{'=' * 60}\n")

def main():
    header()

    # Check for command line mode
    mode_key = None
    for arg in sys.argv[1:]:
        if arg.startswith("--mode="):
            mode_key = arg.split("=")[1]

    if mode_key not in MODES:
        mode_key = select_mode()

    if mode_key == "custom":
        components = select_components_custom()
    else:
        components = MODES[mode_key]["components"]

    if show_plan(mode_key, components):
        run_install(mode_key, components)
    else:
        print("\nInstall cancelled.")

if __name__ == "__main__":
    main()
