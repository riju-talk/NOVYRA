import os
import sys
from pathlib import Path

REQUIRED_VARS = [
    "GOOGLE_API_KEY",
    "DATABASE_URL",
    "NEO4J_URI",
    "NEO4J_USER",
    "NEO4J_PASSWORD",
    "PINECONE_API_KEY",
    "PINECONE_INDEX_NAME"
]

def validate():
    missing = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)
    
    print("SUCCESS: All required environment variables are set.")
    sys.exit(0)

if __name__ == "__main__":
    validate()
