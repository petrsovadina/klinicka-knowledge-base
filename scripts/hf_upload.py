#!/usr/bin/env python3
import os
import sys
from huggingface_hub import HfApi

def upload_to_hf(file_path):
    """Uploads a file to the Hugging Face dataset."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)

    # Token is expected to be set as an environment variable
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("Error: HF_TOKEN environment variable not set.")
        sys.exit(1)

    repo_id = "petrsovadina/klinicka-knowledge-base"
    
    try:
        api = HfApi(token=hf_token)
        
        # Upload the file, renaming it to the final name in the repo
        api.upload_file(
            path_or_fileobj=file_path,
            path_in_repo="data/knowledge_base_final.jsonl",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=f"Phase 3 Progress: Updated knowledge base with {os.path.basename(file_path)} (456 units)"
        )
        print(f"✓ Successfully uploaded {file_path} to {repo_id} as data/knowledge_base_final.jsonl")
        
        # Also upload the metadata file
        api.upload_file(
            path_or_fileobj="sources/metadata.json",
            path_in_repo="sources/metadata.json",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message="Phase 3 Progress: Updated sources metadata"
        )
        print(f"✓ Successfully uploaded sources/metadata.json to {repo_id}")

    except Exception as e:
        print(f"Error during Hugging Face upload: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 hf_upload.py <path_to_jsonl_file>")
        sys.exit(1)
    
    # Change directory to the project root for correct path resolution
    os.chdir("/home/ubuntu/klinicka-knowledge-base")
    upload_to_hf(sys.argv[1])
