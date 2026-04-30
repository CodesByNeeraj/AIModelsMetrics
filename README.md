# Frontier Model Benchmarks On A Product Task: Speed, Latency & Token Throughput 

Benchmarking Claude, GPT, and Gemini on a real product task — measuring TTFT, total latency, throughput, and token usage using a Spotify Discover Weekly PRD prompt.

---

## What This Project Does

Each model receives the same prompt asking it to write a detailed PRD for Spotify's Discover Weekly feature. The response is streamed, and the following metrics are captured per run:

- **TTFT** — Time to First Token: wall-clock time from request submission to the first token arriving
- **Total Latency (e2e)** — wall-clock time from request submission to the last token received
- **TPS** — Tokens Per Second: output tokens divided by total latency
- **Input / Output / Total Tokens** — token counts from each model's usage API

---

## Project Structure

```
AIModelsMetrics/
├── anthropic/
│   └── model.py        # Claude runner (streaming via client.messages.stream)
├── openai/
│   └── model.py        # GPT runner (streaming via client.chat.completions.create)
├── gemini/
│   └── model.py        # Gemini runner (streaming via GenerativeModel.generate_content)
├── main.py             # Entry point
├── results.txt         # Raw benchmark output
└── pyproject.toml
```

---

## Models Tested

| Provider  | Model                  |
|-----------|------------------------|
| OpenAI    | gpt-5.4                |
| Anthropic | claude-opus-4-7        |
| Google    | gemini-3.1-pro-preview |

---

## Benchmark Results

### Raw Metrics

| Metric            | GPT-5.4     | Claude Opus 4.7 | Gemini 3.1 Pro Preview |
|-------------------|-------------|-----------------|------------------------|
| TTFT              | 2.490s      | **1.198s**      | 14.507s                |
| Total Latency     | 99.072s     | 49.213s         | **31.178s**            |
| TPS               | 50.62 t/s   | **62.61 t/s**   | 60.62 t/s              |
| Input Tokens      | 120         | 213             | 128                    |
| Output Tokens     | **5,015**   | 3,081           | 1,890                  |
| Total Tokens      | **5,135**   | 3,294           | 2,018                  |

> Bold = best value in that row.

---

### Latency Breakdown

| Phase                         | GPT-5.4  | Claude Opus 4.7 | Gemini 3.1 Pro Preview |
|-------------------------------|----------|-----------------|------------------------|
| TTFT (queue + first token)    | 2.490s   | **1.198s**      | 14.507s                |
| Streaming duration (e2e − TTFT) | 96.582s | 48.015s        | **16.671s**            |
| Total e2e latency             | 99.072s  | 49.213s         | **31.178s**            |

**Takeaway:** Gemini had the fastest total wall-clock time, but its TTFT was ~12x slower than Claude — it took 14.5 seconds before a single token arrived. Claude had the fastest TTFT and a balanced streaming duration. GPT-5.4 was the slowest overall.

---

### Output Volume vs. Speed

| Model                  | Output Tokens | TPS        | Time to stream all output |
|------------------------|---------------|------------|---------------------------|
| GPT-5.4                | 5,015         | 50.62 t/s  | ~99s                      |
| Claude Opus 4.7        | 3,081         | 62.61 t/s  | ~49s                      |
| Gemini 3.1 Pro Preview | 1,890         | 60.62 t/s  | ~31s                      |

**Takeaway:** GPT-5.4 produced 2.65x more output tokens than Gemini. Claude and Gemini ran at similar throughput (~61–63 t/s), while GPT-5.4 was the slowest per token.

---

### Token Efficiency

| Model                  | Input Tokens | Output Tokens | Output : Input Ratio |
|------------------------|--------------|---------------|----------------------|
| GPT-5.4                | 120          | 5,015         | 41.8x                |
| Claude Opus 4.7        | 213          | 3,081         | 14.5x                |
| Gemini 3.1 Pro Preview | 128          | 1,890         | 14.8x                |

**Note:** Claude received a slightly longer system prompt (213 input tokens vs. ~120–128 for the others), likely due to how the Anthropic SDK counts tokens.

---

## Setup

### Prerequisites

- Python 3.14+
- [`uv`](https://github.com/astral-sh/uv) for dependency management

### Install

```bash
uv sync
```

### Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

### Run

```bash
# Run a specific provider
python anthropic/model.py
python openai/model.py
python gemini/model.py
```

Results are appended to `results.txt`.

---

## Metrics Explained

| Metric | Definition |
|--------|------------|
| **TTFT** | Time from `requests.send()` to the first streamed chunk. Reflects server queue time + network RTT + model startup. |
| **Total Latency (e2e)** | Time from `requests.send()` to the final streamed chunk. Includes all of TTFT plus the full generation + streaming duration. |
| **TPS** | `output_tokens / total_latency`. Measures sustained generation throughput across the entire response. |
| **Streaming duration** | `total_latency − TTFT`. Time spent actively receiving tokens after the first one arrived. |

---

## Notes

- All runs used streaming mode. Token counts come from each provider's usage metadata returned at end of stream.
- Runs were not parallelised — each model was called independently in sequence.
- A single run per model was used; results will vary across runs due to server load and network conditions.
