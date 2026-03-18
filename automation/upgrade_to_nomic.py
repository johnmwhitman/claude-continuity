# upgrade_to_nomic.py — BL-009: Switch ChromaDB to nomic-embed-text embeddings
# nomic-embed-text: 768-dim, trained on 235M text pairs, much better semantic search
# vs ChromaDB default (all-MiniLM-L6-v2: 384-dim, general purpose)
#
# APPROACH: Create new collections with nomic embeddings alongside existing ones.
# We can't change embedding function of existing collections — must migrate.
# Strategy: read all docs from each collection, re-embed with nomic, write to new collection.
# Then swap collection names.
#
import sys, os, json, winreg
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
MEMORY_DIR = Path(r"C:\AI\memory")
LOG = Path(r"C:\AI\logs\nomic_upgrade_log.txt")

def log(msg):
    print(msg)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== nomic-embed-text upgrade check ===")

try:
    import chromadb
    from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
    log(f"ChromaDB version: {chromadb.__version__}")
except ImportError as e:
    log(f"ChromaDB import failed: {e}")
    sys.exit(1)

# Connect to existing ChromaDB
client = chromadb.PersistentClient(path=str(MEMORY_DIR))
existing = client.list_collections()
log(f"Existing collections: {[c.name for c in existing]}")

# Set up nomic embedding function
nomic_ef = OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="nomic-embed-text"
)

# Test nomic embeddings
test_emb = nomic_ef(["test sentence"])
log(f"nomic-embed-text working: {len(test_emb[0])} dimensions")

COLLECTIONS = ["projects", "people", "decisions", "conversations", "knowledge", "tasks"]
migrated = 0
skipped = 0

for coll_name in COLLECTIONS:
    new_name = f"{coll_name}_nomic"
    try:
        # Get existing collection (default embeddings)
        old_coll = client.get_collection(coll_name)
        total = old_coll.count()
        log(f"\n[{coll_name}] {total} documents to migrate")

        if total == 0:
            log(f"  Empty — skipping")
            skipped += 1
            continue

        # Delete existing _nomic collection if it exists (clean slate)
        try:
            client.delete_collection(new_name)
            log(f"  Deleted existing {new_name}")
        except Exception:
            pass

        # Create new collection with nomic embeddings
        new_coll = client.create_collection(
            name=new_name,
            embedding_function=nomic_ef,
            metadata={"description": f"{coll_name} with nomic-embed-text embeddings"}
        )

        # Get all documents in batches
        batch_size = 50
        offset = 0
        batch_num = 0

        while True:
            results = old_coll.get(
                limit=batch_size,
                offset=offset,
                include=["documents", "metadatas"]
            )
            docs = results.get("documents", [])
            if not docs:
                break

            ids = results["ids"]
            metadatas = results.get("metadatas", [{}] * len(docs))

            # Add to new collection (nomic_ef will auto-embed)
            new_coll.add(
                ids=ids,
                documents=docs,
                metadatas=metadatas
            )
            batch_num += 1
            log(f"  Batch {batch_num}: migrated {len(docs)} docs (offset {offset})")
            offset += batch_size

        final_count = new_coll.count()
        log(f"  DONE: {final_count}/{total} docs in {new_name}")
        migrated += 1

    except Exception as e:
        log(f"  ERROR on {coll_name}: {e}")
        skipped += 1

log(f"\n=== Migration complete: {migrated} collections migrated, {skipped} skipped ===")
log("Next step: update MCP server to use _nomic collections")
log("Run: python C:\\AI\\automation\\upgrade_to_nomic.py --swap  (to rename collections)")
