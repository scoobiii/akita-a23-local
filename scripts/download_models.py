#!/usr/bin/env python3
from huggingface_hub import hf_hub_download

DOWNLOADS = [
    ("Qwen/Qwen2.5-0.5B-Instruct-GGUF", "qwen2.5-0.5b-instruct-q4_k_m.gguf"),
    ("Qwen/Qwen2.5-1.5B-Instruct-GGUF", "qwen2.5-1.5b-instruct-q4_k_m.gguf"),
    ("google/gemma-2-2b-it-GGUF", "gemma-2-2b-it-q4_k_m.gguf"),
]

if __name__ == "__main__":
    for repo, filename in DOWNLOADS:
        print(f"Baixando {filename} de {repo} ...")
        path = hf_hub_download(repo_id=repo, filename=filename, local_dir="models")
        print(f"  -> {path}")
