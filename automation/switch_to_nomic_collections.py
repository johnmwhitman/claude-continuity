# switch_to_nomic_collections.py
# After running upgrade_to_nomic.py, this patches the MCP server
# to use the new nomic-embedded collections instead of the defaults.
# Run ONCE after migration. Claude Desktop must be closed.
import json, os, winreg
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

load_reg()

# MCP server config location
CLAUDE_CONFIG = Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
MEMORY_SERVER = Path.home() / ".claude-memory" / "server" / "memory_server.py"

print("=== Switch to nomic collections ===")

# Check MCP config
if CLAUDE_CONFIG.exists():
    with open(CLAUDE_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    print(f"Claude config found: {CLAUDE_CONFIG}")

    # Look for CLAUDE_MEMORY_DIR env var in MCP config
    servers = config.get("mcpServers", {})
    for name, server in servers.items():
        env = server.get("env", {})
        if "CLAUDE_MEMORY_DIR" in env:
            print(f"  MCP server '{name}' uses: {env['CLAUDE_MEMORY_DIR']}")

# Patch memory_server.py to use nomic collection names
if MEMORY_SERVER.exists():
    content = MEMORY_SERVER.read_text(encoding="utf-8")
    COLLECTIONS_OLD = [
        '"projects"', '"people"', '"decisions"',
        '"conversations"', '"knowledge"', '"tasks"'
    ]
    COLLECTIONS_NEW = [
        '"projects_nomic"', '"people_nomic"', '"decisions_nomic"',
        '"conversations_nomic"', '"knowledge_nomic"', '"tasks_nomic"'
    ]
    changed = 0
    for old, new in zip(COLLECTIONS_OLD, COLLECTIONS_NEW):
        if old in content:
            content = content.replace(old, new)
            changed += 1

    if changed > 0:
        # Backup original first
        backup = MEMORY_SERVER.with_suffix(".py.bak")
        MEMORY_SERVER.rename(backup)
        MEMORY_SERVER.write_text(content, encoding="utf-8")
        print(f"  Patched {changed} collection names in memory_server.py")
        print(f"  Original backed up to: {backup}")
    else:
        print("  No collection name changes needed (already updated or not found)")
else:
    print(f"  memory_server.py not found at {MEMORY_SERVER}")
    print("  Manual step: update collection names in your MCP server config")

print("\nDone. Restart Claude Desktop to activate nomic embeddings.")
print("Verify with: python tmp_backlog_check.py  (should still show 354+ memories)")
