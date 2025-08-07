from firebase_admin import initialize_app, firestore
import os
import json

default_app = initialize_app()
db = firestore.client()

# Backup users collection
docs = db.collection("users").stream()
os.makedirs("db/backup/users", exist_ok=True)
for doc in docs:
    with open(f"db/backup/users/{doc.id}.json", "w", encoding="utf-8") as f:
        json.dump(doc.to_dict(), f, ensure_ascii=False, indent=2)

# Backup tournaments collection
docs = db.collection("tournaments").stream()
os.makedirs("db/backup/tournaments", exist_ok=True)
for doc in docs:
    with open(f"db/backup/tournaments/{doc.id}.json", "w", encoding="utf-8") as f:
        json.dump(doc.to_dict(), f, ensure_ascii=False, indent=2, default=str)


# Backup brackets collection
docs = db.collection("brackets").stream()
os.makedirs("db/backup/brackets", exist_ok=True)
for doc in docs:
    with open(f"db/backup/brackets/{doc.id}.json", "w", encoding="utf-8") as f:
        json.dump(doc.to_dict(), f, ensure_ascii=False, indent=2)

