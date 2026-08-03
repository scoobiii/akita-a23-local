#!/usr/bin/env python3
"""
Harness real para rodar GGUF quantizados via llama-cpp-python no Termux/A23.
Sem NPU, sem TFLite fantasioso, sem MoE onde nao existe MoE.
Carrega um modelo por vez (ou combinacao que caiba em max_concurrent_ram_mb),
mede tokens/s e RSS de memoria de verdade via /proc/self/status.
"""

import os
import time
import yaml
from pathlib import Path
from typing import Optional

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False


class LocalHarness:
    def __init__(self, config_dir: str = "config", model_dir: str = "models"):
        self.config_dir = Path(config_dir)
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        with open(self.config_dir / "models.yaml") as f:
            models_cfg = yaml.safe_load(f)
        self.models_cfg = models_cfg["models"]
        self.max_concurrent_ram_mb = models_cfg["max_concurrent_ram_mb"]

        with open(self.config_dir / "agents.yaml") as f:
            self.agents_cfg = yaml.safe_load(f)["agents"]

        self._loaded: dict[str, Llama] = {}

        if not LLAMA_CPP_AVAILABLE:
            print("AVISO: llama-cpp-python nao instalado. "
                  "Instale com: pip install llama-cpp-python --break-system-packages")

    def _process_rss_mb(self) -> float:
        """Le VmRSS de /proc/self/status. Funciona no Termux porque o kernel
        Linux por baixo do Android expoe /proc normalmente, mesmo sem psutil
        (que nao compila em Android)."""
        try:
            with open("/proc/self/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        kb = int(line.split()[1])
                        return kb / 1024
        except (FileNotFoundError, PermissionError, IndexError, ValueError):
            pass
        return 0.0

    def _current_loaded_ram_mb(self) -> int:
        return sum(self.models_cfg[m]["ram_estimate_mb"] for m in self._loaded)

    def _unload_all(self):
        for name in list(self._loaded.keys()):
            del self._loaded[name]
        self._loaded.clear()

    def load_model(self, model_id: str) -> "Llama":
        if model_id in self._loaded:
            return self._loaded[model_id]

        cfg = self.models_cfg[model_id]
        projected = self._current_loaded_ram_mb() + cfg["ram_estimate_mb"]
        if projected > self.max_concurrent_ram_mb:
            print(f"  descarregando modelos ativos para caber {model_id} "
                  f"({projected}MB projetado > limite {self.max_concurrent_ram_mb}MB)")
            self._unload_all()

        model_path = self.model_dir / cfg["file"]
        if not model_path.exists():
            raise FileNotFoundError(
                f"{model_path} nao encontrado. Rode scripts/download_models.py primeiro."
            )

        if not LLAMA_CPP_AVAILABLE:
            raise RuntimeError("llama-cpp-python nao instalado.")

        llm = Llama(
            model_path=str(model_path),
            n_ctx=cfg["ctx"],
            n_threads=cfg["threads"],
            n_gpu_layers=0,  # CPU real no Termux; sem alegacao de NPU
            verbose=False,
        )
        self._loaded[model_id] = llm
        return llm

    def run_agent(self, agent_id: str, user_prompt: str, max_tokens: int = 256) -> dict:
        agent = next((a for a in self.agents_cfg if a["id"] == agent_id), None)
        if agent is None:
            raise KeyError(f"agente {agent_id} nao existe em config/agents.yaml")

        model_id = agent["model"]
        llm = self.load_model(model_id)

        system_prompt = agent["system_prompt"]
        full_prompt = f"<system>\n{system_prompt}\n</system>\n<user>\n{user_prompt}\n</user>\n"

        rss_before = self._process_rss_mb()
        start = time.time()

        out = llm(
            full_prompt,
            max_tokens=max_tokens,
            temperature=0.2,
            stop=["</user>", "<user>"],
        )

        elapsed = time.time() - start
        rss_after = self._process_rss_mb()

        text = out["choices"][0]["text"].strip()
        tokens_generated = out["usage"]["completion_tokens"]
        tok_per_s = tokens_generated / elapsed if elapsed > 0 else 0.0

        return {
            "agent_id": agent_id,
            "model": model_id,
            "task": agent["task"],
            "response": text,
            "tokens_generated": tokens_generated,
            "elapsed_s": round(elapsed, 2),
            "tok_per_s": round(tok_per_s, 1),
            "rss_mb_before": round(rss_before, 1),
            "rss_mb_after": round(rss_after, 1),
        }


def get_harness() -> LocalHarness:
    return LocalHarness()
