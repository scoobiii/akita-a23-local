"""
8 tarefas simplificadas, inspiradas nos 14 objetivos do Akita v2, reescritas
para rodar 100% dentro de um processo Python no Termux — sem servidor web,
sem Docker, sem Redis. Cada tarefa tem um prompt e um validador automatico.
"""

TASKS = {
    "streaming": {
        "prompt": (
            "Escreva uma funcao Python `def stream_response(text: str):` que seja "
            "um generator e produza `text` palavra por palavra via yield, uma palavra "
            "por chamada de next()."
        ),
        "check": lambda code: "yield" in code and "def stream_response" in code,
    },
    "multiturn": {
        "prompt": (
            "Escreva uma funcao `def build_messages(history: list, new_msg: str) -> list` "
            "que retorne o historico + a nova mensagem, SEM duplicar `new_msg` se ja "
            "estiver no final do historico."
        ),
        "check": lambda code: "def build_messages" in code and "history" in code,
    },
    "persistence": {
        "prompt": (
            "Escreva funcoes `save_state(path, data, ttl_seconds)` e `load_state(path)` "
            "usando um arquivo JSON local, onde load_state retorna None se o TTL expirou."
        ),
        "check": lambda code: "def save_state" in code and "def load_state" in code and "ttl" in code.lower(),
    },
    "tools": {
        "prompt": (
            "Gere um JSON de tool call para a ferramenta `calculator` somando 7 e 5. "
            'Formato: {"tool": "calculator", "args": {...}}'
        ),
        "check": lambda code: '"tool"' in code and "calculator" in code,
    },
    "structured_output": {
        "prompt": (
            "A conversa foi sobre 'como configurar Docker no Termux'. "
            'Gere APENAS o JSON: {"title": "..."} com um titulo curto.'
        ),
        "check": lambda code: '"title"' in code,
    },
    "token_budget": {
        "prompt": (
            "Escreva `def truncate_to_budget(messages: list, max_tokens: int, count_fn) -> list` "
            "que remove as mensagens mais antigas ate caber no orcamento."
        ),
        "check": lambda code: "def truncate_to_budget" in code and "max_tokens" in code,
    },
    "error_handling": {
        "prompt": (
            "Escreva um bloco try/except Python que trate TimeoutError, um erro de "
            "rate limit (classe RateLimitError) e Exception generica, cada um com "
            "uma mensagem de log diferente."
        ),
        "check": lambda code: "except TimeoutError" in code and "except" in code,
    },
    "self_review": {
        "prompt": (
            "Revise a seguinte implementacao de `truncate_to_budget` e diga se ela "
            "PASSA, PARCIALMENTE PASSA ou FALHA no requisito de nunca estourar o "
            "orcamento de tokens. Justifique em 1 frase."
        ),
        "check": lambda code: any(w in code.upper() for w in ["PASS", "FALHA", "PARCIAL"]),
    },
}
