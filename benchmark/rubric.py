"""
Scoring numa escala PROPRIA deste projeto. Nao comparavel ao ranking do Akita
(modelos de 0.5B-2B nao competem com Claude/GPT/Kimi em engenharia completa).

Pontuacao por tarefa (0-100):
  - 60 pts: check automatico (validador de definitions.py) passou
  - 20 pts: resposta gerada sem erro de runtime/parsing
  - 20 pts: tempo de geracao dentro do esperado para o tamanho do modelo
            (throughput minimo aceitavel no A23)
"""

MIN_ACCEPTABLE_TOK_PER_S = {
    "qwen05": 8.0,
    "qwen15": 4.0,
    "qwen3b": 2.0,
}

TIERS = [
    (85, "A-local", "Cumpre a tarefa simplificada de forma consistente no A23"),
    (60, "B-local", "Cumpre parcialmente; precisa de revisao humana"),
    (0, "C-local", "Nao cumpre o objetivo simplificado de forma confiavel"),
]


def score_result(result: dict, check_fn) -> dict:
    code = result["response"]
    passed_check = False
    try:
        passed_check = bool(check_fn(code))
    except Exception:
        passed_check = False

    score = 0
    if passed_check:
        score += 60
    if code.strip():
        score += 20
    min_tok_s = MIN_ACCEPTABLE_TOK_PER_S.get(result["model"], 3.0)
    if result["tok_per_s"] >= min_tok_s:
        score += 20

    tier = next(name for threshold, name, _ in TIERS if score >= threshold)

    return {**result, "score": score, "tier": tier, "check_passed": passed_check}
