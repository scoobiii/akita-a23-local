#!/bin/bash
set -e

echo "Setup real para akita-a23-local (Termux)"

pkg update -y && pkg upgrade -y
pkg install -y python python-pip git wget curl cmake clang make

pip install --upgrade pip
pip install --break-system-packages \
    llama-cpp-python \
    pyyaml \
    psutil \
    huggingface-hub

echo "Setup concluido. Rode: bash scripts/download_models.sh"
