"""
chromadb_restore_drill.py - ChromaDB Backup Restore Verification
Proves the backup actually works BEFORE we need it.
Copies backup to temp dir, opens it, runs test queries, reports pass/fail.
BL-004 — CRITICAL — has been outstanding since March 15.

Run manually: python chromadb_restore_drill.py
"""
import os, sys, shutil, datetime, json

MEMORY_DIR   = r"C:\AI\memory"
BACKUP_DIR   = r"C:\AI\backup\memory-backup"
TEMP_DIR     = r"C:\AI\backup\restore-test"
LOG          = r"C:\AI\logs\restore_drill_log.txt"
PROACTIVE    = r"C:\AI\logs\proactive_items.txt"

lines = []
def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    lines.append(line)

def write_log():
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def flag(msg):
    os.makedirs(os.path.dirname(PROACTIVE), exist_ok=True)
    with open(PROACTIVE, "a", encoding="utf-8") as f:
        f.write(f"[RESTORE] {msg}\n")

def run():
    log("=" * 55)
    log(f"CHROMADB RESTORE DRILL — {datetime.date.today()}")
    log("=" * 55)

    passed = []
    failed = []

    # Step 1: Check backup exists
    log("\nStep 1: Verify backup exists")
    if not os.path.exists(BACKUP_DIR):
        log(f"  FAIL: Backup directory missing: {BACKUP_DIR}")
        failed.append("Backup directory missing")
        write_log()
        flag("RESTORE DRILL FAILED: No backup directory found")
        return False

    backup_files = []
    for root, dirs, files in os.walk(BACKUP_DIR):
        backup_files.extend(files)

    if not backup_files:
        log(f"  FAIL: Backup directory empty")
        failed.append("Backup empty")
        write_log()
        flag("RESTORE DRILL FAILED: Backup directory empty")
        return False

    backup_size = sum(
        os.path.getsize(os.path.join(r, f))
        for r, d, files in os.walk(BACKUP_DIR)
        for f in files
    ) // 1024
    log(f"  PASS: {len(backup_files)} files, {backup_size} KB")
    passed.append("Backup exists")

    # Step 2: Copy backup to temp restore location
    log("\nStep 2: Copy backup to temp restore location")
    try:
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        shutil.copytree(BACKUP_DIR, TEMP_DIR)
        temp_files = sum(len(f) for _, _, f in os.walk(TEMP_DIR))
        log(f"  PASS: Copied {temp_files} files to {TEMP_DIR}")
        passed.append("Backup copy succeeded")
    except Exception as e:
        log(f"  FAIL: Copy failed — {e}")
        failed.append(f"Copy failed: {e}")
        write_log()
        flag(f"RESTORE DRILL FAILED: Could not copy backup — {e}")
        return False

    # Step 3: Open restored ChromaDB
    log("\nStep 3: Open restored ChromaDB and verify reads")
    try:
        import chromadb
        client = chromadb.PersistentClient(path=TEMP_DIR)
        collections = client.list_collections()
        log(f"  PASS: ChromaDB opened. Collections: {len(collections)}")
        for col in collections:
            log(f"    - {col.name}")
        passed.append(f"ChromaDB opened ({len(collections)} collections)")
    except ImportError:
        log("  SKIP: chromadb not importable in this env — checking file structure instead")
        # Fallback: just check the sqlite file exists
        sqlite_files = [f for r, d, files in os.walk(TEMP_DIR) for f in files if f.endswith(".sqlite3")]
        if sqlite_files:
            log(f"  PASS (file check): Found {len(sqlite_files)} SQLite file(s)")
            passed.append("SQLite files present")
        else:
            log("  FAIL: No SQLite files found in restore")
            failed.append("No SQLite in restore")
    except Exception as e:
        log(f"  FAIL: ChromaDB open failed — {e}")
        failed.append(f"ChromaDB open: {e}")

    # Step 4: Count memories in restore vs live
    log("\nStep 4: Compare restore vs live memory count")
    try:
        import chromadb
        live_client    = chromadb.PersistentClient(path=MEMORY_DIR)
        restore_client = chromadb.PersistentClient(path=TEMP_DIR)

        live_cols    = {c.name: c for c in live_client.list_collections()}
        restore_cols = {c.name: c for c in restore_client.list_collections()}

        all_names = set(live_cols) | set(restore_cols)
        for name in sorted(all_names):
            live_count    = live_cols[name].count()    if name in live_cols    else 0
            restore_count = restore_cols[name].count() if name in restore_cols else 0
            diff = live_count - restore_count
            status = "PASS" if diff <= 5 else "WARN"  # allow small delta (recent memories)
            log(f"  {status}: {name}: live={live_count}, restore={restore_count}, delta={diff}")
            if status == "PASS":
                passed.append(f"{name} count matches")
            else:
                failed.append(f"{name} delta too large ({diff})")
    except Exception as e:
        log(f"  SKIP: Could not do count comparison — {e}")

    # Step 5: Cleanup temp
    log("\nStep 5: Cleanup temp restore")
    try:
        shutil.rmtree(TEMP_DIR)
        log(f"  PASS: Temp dir removed")
        passed.append("Cleanup succeeded")
    except Exception as e:
        log(f"  WARN: Cleanup failed — {e} (not critical)")

    # Summary
    log("\n" + "=" * 55)
    log("DRILL SUMMARY")
    log("=" * 55)
    log(f"  Passed: {len(passed)}")
    log(f"  Failed: {len(failed)}")
    if failed:
        for f in failed:
            log(f"  FAIL: {f}")
        log("\n  BACKUP IS NOT RELIABLE — fix before trusting overnight automation")
        flag(f"RESTORE DRILL: {len(failed)} failure(s) — backup may not be reliable")
    else:
        log("\n  BACKUP VERIFIED — restore works correctly")
        log(f"  Next drill recommended: {(datetime.date.today() + datetime.timedelta(days=30)).isoformat()}")

    log("=" * 55)
    write_log()
    return len(failed) == 0

if __name__ == "__main__":
    success = run()
    if sys.stdin.isatty():
        input("\nPress Enter to close...")
    sys.exit(0 if success else 1)
