# akita-a23-local

Benchmark de agentes LLM locais rodando de fato num Samsung A23 via Termux.
Inspirado na estrutura de 3 fases do LLM Coding Benchmark v2 (Akita), **adaptado
para caber na física real de um telefone**, sem Docker, sem Rails completo,
sem NPU mágica.

## O que este projeto NÃO é

- Não compete com o ranking do Akita (Claude/GPT/Kimi rodando com dezenas de
  GB de VRAM ou clusters de API). Comparar um Qwen2.5-1.5B local com esses
  modelos em engenharia de software completa é category error — o próprio
  Akita tirou os locais do v2 por isso.
- Não roda Docker/Compose/Redis dentro do Termux. Termux não tem os
  namespaces de kernel necessários para containers reais.
- Não carrega "24 modelos" simultâneos. Isso é matematicamente impossível
  num telefone com poucos GB livres.

## O que este projeto É

- **24 personas de agente**, não 24 pesos diferentes. Todas compartilham
  2-3 modelos base reais, carregados um de cada vez (lazy-load/unload),
  diferenciados por system prompt e tarefa.
- **Tarefas simplificadas** adaptadas dos 14 objetivos do v2, reescritas
  para rodar 100% em processo Python/Ruby dentro do Termux — sem subir
  servidor web, sem container.
- **Métrica própria**: tokens/s, RAM de pico, e um rubric de 0-100
  numa escala separada (não comparável ao ranking do Akita).

## Matemática real de RAM (Q4_K_M, contexto 2048)

| Modelo                        | Peso em disco | RAM em uso (pico) |
|-------------------------------|---------------|--------------------|
| Qwen2.5-0.5B-Instruct-GGUF     | ~380 MB       | ~550 MB            |
| Qwen2.5-1.5B-Instruct-GGUF     | ~1.0 GB       | ~1.3 GB            |
| Gemma-2-2B-it-GGUF             | ~1.6 GB       | ~2.0 GB            |

Um A23 com 4-6GB de RAM tem tipicamente 1.5-3GB livres para um processo em
primeiro plano. Por isso o harness carrega **um modelo por vez** e descarrega
antes do próximo — rodar os três ao mesmo tempo é possível só nas variantes
de 6-8GB, e mesmo assim sem margem de segurança.

## Setup

```bash
bash scripts/setup_termux.sh
bash scripts/download_models.sh
python benchmark/run_benchmark.py --quick
```

## Estrutura

```
config/models.yaml     -> 3 modelos GGUF reais (caminho, RAM estimada)
config/agents.yaml     -> 24 personas, cada uma referenciando um dos 3 modelos
harness/local_harness.py -> carga via llama-cpp-python, medição real de tok/s e RAM
benchmark/tasks/*.py    -> 8 tarefas simplificadas, sem Docker/Rails
benchmark/rubric.py     -> scoring 0-100, tiers próprios (não comparáveis ao Akita)
benchmark/run_benchmark.py -> orquestração + relatório JSON
```
