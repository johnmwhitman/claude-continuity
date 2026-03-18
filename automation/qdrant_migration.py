# qdrant_migration.py — BL-008: ChromaDB to Qdrant migration script
# DO NOT RUN YET — trigger is: 500+ memories OR first corruption event
# This script is a "break glass" safety net.
#
# WHY QDRANT:
#   - ChromaDB embedded mode = single process, no concurrent writes
#   - Qdrant = production vector DB, REST API, filtering, snapshots
#   - At 500+ memories ChromaDB search degrades; Qdrant scales to millions
#
# PREREQUISITES (run once when triggered):
#   pip install qdrant-client
#   docker run -p 6333:6333 qdrant/qdrant  (or install binary)
#
# USAGE:
#   python qdrant_migration.py --dry-run   # Preview what will migrate
#   python qdrant_migration.py --migrate   # Actually run it
#   python qdrant_migration.py --verify    # Verify counts match after migration
import sys, os, json, winreg
from pathlib import Path

CHROMA_DIR    = Path(r"C:\AI\memory")
QDRANT_URL    = "http://localhost:6333"
OLLAMA_URL    = "http://localhost:11434"
EMBED_MODEL   = "nomic-embed-text"
BACKUP_PATH   = Path(r"C:\AI\backup\pre-qdrant-migration")

COLLECTIONS = ["projects", "people", "decisions", "conversations", "knowledge", "tasks"]

def load_reg():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
    i = 0
    while True:
        try:
            n, v, _ = winreg.EnumValue(key, i)
            os.environ[n] = v
            i += 1
        except OSError:
            break

def check_prerequisites():
    print("Checking prerequisites...")
    errors = []
    try:
        import chromadb
        print(f"  ChromaDB {chromadb.__version__}: OK")
    except ImportError:
        errors.append("chromadb not installed")
    try:
        import qdrant_client
        print(f"  qdrant-client: OK")
    except ImportError:
        errors.append("qdrant-client not installed — run: pip install qdrant-client")
    import urllib.request
    try:
        with urllib.request.urlopen(f"{QDRANT_URL}/healthz", timeout=3) as r:
            print(f"  Qdrant at {QDRANT_URL}: OK")
    except Exception as e:
        errors.append(f"Qdrant not running at {QDRANT_URL} — run: docker run -p 6333:6333 qdrant/qdrant")
    try:
        body = json.dumps({"model": EMBED_MODEL, "prompt": "test"}).encode()
        req = urllib.request.Request(f"{OLLAMA_URL}/api/embeddings", data=body,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            dims = len(data["embedding"])
            print(f"  Ollama nomic-embed-text: OK ({dims} dims)")
    except Exception as e:
        errors.append(f"Ollama/nomic unavailable: {e}")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  ERROR: {e}")
        return False
    return True

def get_embedding(text: str) -> list:
    import urllib.request
    body = json.dumps({"model": EMBED_MODEL, "prompt": text}).encode()
    req = urllib.request.Request(f"{OLLAMA_URL}/api/embeddings", data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())["embedding"]

def backup_chroma():
    """Backup ChromaDB before migration."""
    import shutil
    if BACKUP_PATH.exists():
        shutil.rmtree(BACKUP_PATH)
    shutil.copytree(CHROMA_DIR, BACKUP_PATH)
    print(f"Backed up to {BACKUP_PATH}")

def migrate_collection(chroma_client, qdrant_client, coll_name: str, dry_run: bool = True):
    """Migrate one ChromaDB collection to Qdrant."""
    from qdrant_client.models import Distance, VectorParams, PointStruct
    import uuid

    old_coll = chroma_client.get_collection(coll_name)
    total = old_coll.count()
    print(f"\n[{coll_name}] {total} documents")

    if dry_run:
        print(f"  DRY RUN — would migrate {total} docs")
        return total, 0

    # Create Qdrant collection (768-dim for nomic)
    try:
        qdrant_client.create_collection(
            collection_name=coll_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
        print(f"  Created Qdrant collection: {coll_name}")
    except Exception:
        print(f"  Collection {coll_name} already exists — will upsert")

    # Migrate in batches
    batch_size = 20
    offset = 0
    migrated = 0

    while True:
        results = old_coll.get(limit=batch_size, offset=offset,
                               include=["documents", "metadatas"])
        docs = results.get("documents", [])
        if not docs:
            break

        points = []
        for i, (doc_id, doc, meta) in enumerate(zip(
            results["ids"], docs, results.get("metadatas", [{}]*len(docs))
        )):
            embedding = get_embedding(doc)
            payload = {"content": doc, "collection": coll_name}
            if meta:
                payload.update(meta)
            points.append(PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id)),
                vector=embedding,
                payload=payload
            ))

        qdrant_client.upsert(collection_name=coll_name, points=points)
        migrated += len(points)
        print(f"  Migrated {migrated}/{total}...")
        offset += batch_size

    return total, migrated

def run_dry_run():
    import chromadb
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    print("\n=== DRY RUN — No changes will be made ===")
    total_docs = 0
    for name in COLLECTIONS:
        try:
            coll = client.get_collection(name)
            count = coll.count()
            total_docs += count
            print(f"  {name}: {count} documents")
        except Exception as e:
            print(f"  {name}: ERROR — {e}")
    print(f"\nTotal documents to migrate: {total_docs}")
    print("Migration estimated time: ~{:.0f} minutes (at ~1s/doc for embeddings)".format(total_docs/60))
    print("\nTo run migration: python qdrant_migration.py --migrate")

def run_migration():
    import chromadb
    try:
        from qdrant_client import QdrantClient
    except ImportError:
        print("Install qdrant-client first: pip install qdrant-client")
        return
    load_reg()
    if not check_prerequisites():
        return
    print("\n=== RUNNING MIGRATION ===")
    backup_chroma()
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    qdrant_client = QdrantClient(url=QDRANT_URL)
    for name in COLLECTIONS:
        try:
            total, migrated = migrate_collection(chroma_client, qdrant_client, name, dry_run=False)
            print(f"  {name}: {migrated}/{total} OK")
        except Exception as e:
            print(f"  {name}: FAILED — {e}")
    print("\nMigration complete. Verify with: python qdrant_migration.py --verify")

def run_verify():
    import chromadb
    try:
        from qdrant_client import QdrantClient
    except ImportError:
        print("Install qdrant-client: pip install qdrant-client")
        return
    load_reg()
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    qdrant_client = QdrantClient(url=QDRANT_URL)
    print("\n=== VERIFY: ChromaDB vs Qdrant ===")
    all_ok = True
    for name in COLLECTIONS:
        try:
            chroma_count = chroma_client.get_collection(name).count()
            qdrant_info = qdrant_client.get_collection(name)
            qdrant_count = qdrant_info.points_count
            ok = chroma_count == qdrant_count
            status = "OK" if ok else "MISMATCH"
            print(f"  {name}: chroma={chroma_count} qdrant={qdrant_count} [{status}]")
            if not ok:
                all_ok = False
        except Exception as e:
            print(f"  {name}: ERROR — {e}")
            all_ok = False
    print(f"\nVerification: {'PASSED' if all_ok else 'FAILED'}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    if cmd == "--dry-run":
        run_dry_run()
    elif cmd == "--migrate":
        run_migration()
    elif cmd == "--verify":
        run_verify()
    else:
        print("Usage: python qdrant_migration.py [--dry-run|--migrate|--verify]")
