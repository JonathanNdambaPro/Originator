# Applied AI Engineer — Take-Home Exercise

## 1. Overview & Task Selection

- **Task Selection (`x`)**: Graph Coloring (Constraint Satisfaction Problem). The LLM is given a list of nodes, edges, and allowed colors, and must assign a color to each node such that no two adjacent nodes share the same color.
- **Model Choice (`y`)**: `openrouter:anthropic/claude-sonnet-4-5` (via Pydantic-AI with OpenRouter API integration). *Can easily be swapped to any frontier model in `evaluate.py`.*

**Why this task falls in the 10-90% success rate bucket:**
Current frontier LLMs generate text autoregressively (left-to-right) and lack native backtracking mechanisms. In a tightly constrained graph, if the model makes a sub-optimal color choice early on, it mathematically hits a dead-end later. Because it cannot "erase" its previous tokens, it will hallucinate a color or violate a constraint.

- **Trivial (5 nodes):** ~100% success.
- **Sweet Spot (12 nodes, 0.4 edge probability):** ~10-90% success. The model's forward-planning capacity is overloaded, causing it to randomly paint itself into a corner.
- **Impossible (>30 nodes):** ~0% success.

## 2. Synthetic Data Generation Strategy

Naively generating random graphs can inadvertently create NP-Hard, unsolvable problems (leading to a 0% success rate).
My `generate.py` script uses a **"Planted Solution"** algorithm:

1. It secretly assigns a valid color to each node.
2. It randomly generates edges, but *strictly prevents* edges between nodes sharing the same secret color.
3. It shuffles the arrays and discards the secret colors.
This ensures every generated problem in `problems.json` is 100% solvable.

## 3. Verification & Evaluation System

- **Verification (`verify.py`)**: Validation is completely deterministic ($O(E)$). The script loops through the edges and strictly checks if the LLM assigned the same color to both ends of any edge.
- **Evaluation (`evaluate.py`)**: Uses **Pydantic-AI** to enforce a strict JSON schema output (`OutputExpectedGraph`), eliminating brittle regex parsing. The script loops over the generated problems and calculates the exact success rate. (The LLM runs entirely locally via API without browsing the internet).

## 4. Advanced Observability (Logfire & Loguru)

In a post-training/RLHF context, a binary "Pass/Fail" is insufficient. We must know *why* the model drifted.
I instrumented the evaluation pipeline with **Loguru** (for rich console diagnostics) and **Pydantic Logfire** (OpenTelemetry for LLMs). If the model fails, the logs pinpoint the exact constraint violated.

> **⚠️ How to use or disable Logfire**
>
> - **To use it**: Run `logfire auth` in your terminal to link it to your Pydantic account.
> - **To disable it (Opt-out)**: If you prefer a clean local console without sending telemetry, simply open `evaluate.py` and comment out the instrumentation lines:
>
```python
# logfire.configure()
# logfire.instrument_pydantic_ai()
```
>
> The script will gracefully fall back to standard local Loguru terminal outputs.

## 5. Setup & Usage Instructions

**1. Set up Environment Variables**

Create a `.env` file in the root of the project with your API keys:

```env
OPENROUTER_API_KEY="your_openrouter_api_key"
```

*(Optional)* Add `LOGFIRE_TOKEN` if you wish to use remote Pydantic-AI observability.

**2. Install Dependencies**

This project relies on `uv` for lightning-fast environment management.

```bash
uv sync
```

**Docker Fallback Playground**

If `uv` does not install or work on your machine, you can launch the provided Docker container as an interactive playground:

```bash
docker build -t synthdata-playground .
docker run -d --name synthdata-env -v $(pwd):/app synthdata-playground
docker exec -it synthdata-env bash
```

Once inside the container shell, you can directly run the `generate.py` and `evaluate.py` commands as described below.

**3. Generate Synthetic Data**

Run the generator script. This will create a `problems.json` file in the same directory.

You can run the script as-is for a pre-configured acceptable complexity (~10-90% LLM success rate):

```bash
uv run synthdata/coloaration_graph/generate.py
```

*OR*

```bash
uv run python -m synthdata.coloaration_graph.generate
```

**Adjusting Complexity**
You can easily increase or reduce the complexity of the generated problems by playing with the CLI arguments:

- `--num-nodes`: Number of nodes in the graph (min: 3, default: 12). More nodes = harder.
- `--num-colors`: Allowed number of colors (min: 1, max: 5, default: 3). Fewer colors = harder.
- `--edge-probability`: Density of constraints between 0.0 and 1.0 (default: 0.4). Higher probability = harder.
- `--num-samples`: Number of problems to generate (default: 30).

*Example: Generating a highly complex dataset*

```bash
uv run coloaration_graph/generate.py --num-samples 50 --num-nodes 20 --num-colors 3 --edge-probability 0.6
```


**4. Evaluate the LLM**

Run the evaluation script to test `claude-sonnet-4-5` via OpenRouter against the generated problems.

```bash
uv run synthdata/coloaration_graph/evaluate.py
```

*OR*

```bash
uv run python -m synthdata.coloaration_graph.evaluate
```

Watch the console to see if the LLM achieves the targeted 10-90% success rate!

**5. Run Verification Unit Tests**

You can run the comprehensive tests for the verification logic using pytest.

```bash
uv run pytest synthdata/coloaration_graph/tests/ -v
```

---
Repository initiated with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).
