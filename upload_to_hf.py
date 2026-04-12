"""
Upload all project files to a Hugging Face Space via the HF Hub API.
Usage: python3 upload_to_hf.py <HF_TOKEN> <SPACE_ID>
Example: python3 upload_to_hf.py hf_xxx anonymous08ms/SQl-M
"""
import sys
import os
import base64
import urllib.request
import urllib.error
import json

HF_TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""
SPACE_ID = sys.argv[2] if len(sys.argv) > 2 else "anonymous08ms/SQl-M"
BRANCH = "main"

# Files to upload
FILES = [
    "Dockerfile",
    "openenv.yaml",
    "pyproject.toml",
    "requirements.txt",
    "inference.py",
    "README.md",
    "sql_query_env/__init__.py",
    "sql_query_env/models.py",
    "sql_query_env/client.py",
    "sql_query_env/tasks.py",
    "sql_query_env/server/__init__.py",
    "server/__init__.py",
    "server/app.py",
    "sql_query_env/server/database.py",
    "sql_query_env/server/grader.py",
    "sql_query_env/server/sql_query_env_environment.py",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def upload_file(token, space_id, filepath, content):
    api_url = f"https://huggingface.co/api/spaces/{space_id}/upload"
    # Use the HF Hub file upload API
    url = f"https://huggingface.co/api/repos/create"
    
    # Use direct file upload via the commit API
    encoded = base64.b64encode(content).decode("utf-8")
    payload = json.dumps({
        "commitTitle": f"Upload {filepath}",
        "files": [{
            "path": filepath,
            "content": encoded,
            "encoding": "base64"
        }]
    }).encode("utf-8")
    
    commit_url = f"https://huggingface.co/api/spaces/{space_id}/commit/{BRANCH}"
    req = urllib.request.Request(
        commit_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return True, resp.read().decode()
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return False, str(e)


def upload_all_files(token, space_id):
    """Upload all files in one commit using HF Hub API."""
    files_payload = []
    
    for filepath in FILES:
        full_path = os.path.join(BASE_DIR, filepath)
        if not os.path.exists(full_path):
            print(f"  SKIP (not found): {filepath}")
            continue
        with open(full_path, "rb") as f:
            content = f.read()
        encoded = base64.b64encode(content).decode("utf-8")
        files_payload.append({
            "operation": "addOrUpdate",
            "path": filepath,
            "content": encoded,
            "encoding": "base64"
        })
        print(f"  Queued: {filepath}")
    
    payload = json.dumps({
        "summary": "Phase 1 fix: self-contained /reset /step /health endpoints",
        "description": "Fix: no openenv-core dependency, explicit endpoints, db_schema only",
        "operations": files_payload
    }).encode("utf-8")
    
    commit_url = f"https://huggingface.co/api/spaces/{space_id}/commit/{BRANCH}"
    print(f"\nUploading {len(files_payload)} files to {space_id}...")
    
    req = urllib.request.Request(
        commit_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = resp.read().decode()
            print(f"  SUCCESS: {result[:200]}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        print(f"  FAILED HTTP {e.code}: {body}")
        return False
    except Exception as e:
        print(f"  FAILED: {e}")
        return False


if __name__ == "__main__":
    if not HF_TOKEN:
        print("Usage: python3 upload_to_hf.py <HF_TOKEN> <SPACE_ID>")
        sys.exit(1)
    
    print("Skipping whoami token verification to prevent fine-grained token rejection...")
    
    success = upload_all_files(HF_TOKEN, SPACE_ID)
    if success:
        print(f"\n✅ All files uploaded to https://huggingface.co/spaces/{SPACE_ID}")
        print("The space will rebuild automatically in ~1-2 minutes.")
    else:
        print("\n❌ Upload failed. Please check the token and space ID.")
        sys.exit(1)
