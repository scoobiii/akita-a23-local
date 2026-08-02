#!/usr/bin/env python3
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from harness.local_harness import get_harness
from benchmark.tasks.definitions import TASKS
from benchmark.rubric import score_result


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--quick", action="store_true", help="roda so 6 agentes (1 por tarefa-chave)")
    p.add_argument("--output", default="output/reports")
    return p.parse_args()


def main():
    args = parse_args()
    harness = get_harness()

    agents = harness.agents_cfg
    if args.quick:
        seen_tasks = set()
        quick_agents = []
        for a in agents:
            if a["task"] not in seen_tasks:
                quick_agents.append(a)
                seen_tasks.add(a["task"])
        agents = quick_agents

    print(f"Rodando {len(agents)} agentes locais no A23 (Termux, llama-cpp-python, CPU real)\n")

    results = []
    for agent in agents:
        task_def = TASKS.get(agent["task"])
        if task_def is None:
            continue
        try:
            raw = harness.run_agent(agent["id"], task_def["prompt"], max_tokens=200)
        except Exception as e:
            results.append({
                "agent_id": agent["id"], "model": agent["model"], "task": agent["task"],
                "error": str(e), "score": 0, "tier": "C-local",
            })
            print(f"  [ERRO] {agent['id']}: {e}")
            continue

        scored = score_result(raw, task_def["check"])
        results.append(scored)
        print(f"  {agent['id']:30} model={agent['model']:8} "
              f"score={scored['score']:3} tier={scored['tier']:8} "
              f"{scored['tok_per_s']:.1f} tok/s")

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    valid = [r for r in results if "score" in r]
    avg_score = sum(r["score"] for r in valid) / len(valid) if valid else 0
    print(f"\nScore medio (escala propria, NAO comparavel ao ranking Akita): {avg_score:.1f}/100")
    print(f"Relatorio salvo em: {report_path}")


if __name__ == "__main__":
    main()
