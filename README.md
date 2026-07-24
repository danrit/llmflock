# LLMR - LLM Runner

Define a matrix of LLM variations (model × prompt × options), run it reproducibly over a dataset and capture structured results.

DRAFT: more on the objective of this tool: it is built to run extraction the same structured data (`data_schemas.default`) in a list (`datasets.default`) of documents (`document_sets.default`) usings LLM and output tabular data. It is designed to run the extraction several times - or variations - (`scenarios.default.variations`) with different models, prompts or model options (temperature, top_p). It also designed to repeat one variation several times (reference to non-deterministic behaviour of LLMs...) (`scenarios.default.variations.repeat`).

Note: actually this is not limited to extraction of structured data (ie a task where the research data is already in the input document but drowned in it), but to any task which generate structured data (because then structured data can then be easily compared/assessed)

Note 2: maybe that tool is more aimed at smaller models (local or cloud-hosted). By design it will have to be run **very** repetitively on big dataset so cost of running huge models from the frontier labs can be dissuasive. But big models need to be tested too sometimes to make sure the small models jobs remains relevant.

Note 3: how to we rate and compare (benchmark) the resulting output structured data, what will be the coverage of the comparison part of this tool?

- wanted to find an example of llm comparison tool: found [this one](https://www.simonpcouch.com/blog/2025-04-01-gemini-2-5-pro) (here applied to Gemini 2.5 Pro) from Simon P. Couch ([via](https://simonwillison.net/2026/Jan/20/electricity-use-of-ai-coding-agents/) then [via](https://www.simonpcouch.com/blog/2026-01-20-cc-impact/)) : which lead me to a even more popular approach ? [https://inspect.aisi.org.uk/] .....  take-aways are:
  - use a repeat parameter (epoch) to "Evaluate each sample multiple times to better quantify variation"

Note 4: more thought one the viewing result part: need to have a too to aggregate results, adding comparison with one selected IDEAL run and output all of it in a easy spreadsheet format (csv, excel) for further analysis and visualization. aim to keep it to minimum, focusing on the llm-extract typical combining results for multi-run part.


**On where it sits in the ecosystem of LLM tools:** It is a LLM gateway: meaning it can call different LLM providers (local inference framework or cloud-hosted) with a rudimentary plugin system. If the project matures enough it could be beneficial the transition to a more established LLM gateway tool (like liteLLm, anyLLM).

HEREHEREHERE - last updated July-2026 (work started March/June-2026)

### Done
- Save debug prompt/response files per variation
- Extract JSON from LLM response and validate against schema
- Split `data` + `document` in `run_variations`; use generic `data['id']` instead of domain-specific identifiers
- Separate `logs/` (debug files, log file) and `runs/` (structured outputs) directories
- Terminology: `variations` instead of `combinations`
- Write `meta.json` at end of run (timestamp, full config, dataset length, variations count)
- Two additional extraction examples (beside EV attributes): image transformation, financial NER)

### In progress — meta information capture
- `meta.json` still missing: scenario name and CLI args passed in
- Write `extracted.jsonl` per run — one line per LLM call (see schema in `data/example1-ev/runs/YYYYMMDD-HHMISS/extracted.jsonl`): fields are `id`, `document`, `prompt`, `model`, `temp`, `topp`, `repeat`, `exit_code`, `exit_message`, `processing_time`, `prompt_tokens`, `response_tokens`, `extracted`
- Capture token counts and processing time per call (needed for `extracted.jsonl` and stats)

### Next — OpenRouter provider
- Add `openrouter` backend module (alongside `ollama_ollama.py` and `simonw_llm.py`)
- Load API key from `.env` via `load_dotenv()` / `os.getenv('API_KEY')` (groundwork: `python-dotenv` already in dependencies, commented import already in `cli.py`)
- Motivation: cloud-hosted provider is a must-have; also needed to build generic response metadata (token counts) that local Ollama may not return consistently

### Backlog
- Run stats output (similar to vader-llm)
- Aggregate results across runs into CSV/JSON
- Result comparison: pick an "ideal" run, diff others against it, export to spreadsheet


## Getting started

1. [Ollama](https://ollama.com/download) should be installed and running
2. Clone the repository and install it with pip: `pip install .` (At this stage the package is not distributed, ie not published to PyPI, hence cannot be installed directly from PyPI)
    1. Or use `pip install -e .` if you want to install in editable mode.

## Usage

To run the example in `data/example1-ev`, use the command: `llmr --configfile=data/example1-ev/config.yaml` or `llmr --configfile=data/example1-ev/config.yaml --debug`
