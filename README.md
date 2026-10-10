# LLM Flock

A CLI tool to interact with local and remote LLM, define multiple scenario variations (model × prompt × options), run them over a dataset and capture structured results for comparison or to build knowledge through meta analysis.

## Getting started

### Prerequisites

To run most examples you'll need Ollama installed and the default local model `gemma3` and optionally `gpt-oss` downloaded.

1. Install Ollama: several ways:
    - For everyone: Follow instructions from [Ollama.com](https://ollama.com/download)
    - On MacOS, using brew, just run `brew install ollama`
2. download the locals models (takes some time...)
   - `ollama pull gemma3` (default to `gemma3:4b`, 3.4GB to date)
   - `ollama pull gpt-oss` (default to `gpt-oss:20b`, 14GB to date)

### Install the library

Two ways:

- From PyPI: `pip install llmflock`
- From downloaded source code: Clone the repository and install it with pip: `pip install .` (Or use `pip install -e .` if you want to install in editable mode.)

## Usage

### Basic examples

- submitting a simple prompt: `llmflock "What years mark the start and end of Queen Elizabeth II's reign in the United Kingdom?"` (= 1 llm call)
- add extra model: `llmflock "What years mark the start and end of Queen Elizabeth II's reign in the United Kingdom?" --model=gemma3,gpt-oss` (= 2 llm calls)
- add repeat count: `llmflock "What years mark the start and end of Queen Elizabeth II's reign in the United Kingdom?" --model=gemma3,gpt-oss -r 3` (= 6 llm calls)
- add a schema: `llmflock "What years mark the start and end of King Charles III's reign in the United Kingdom?" --schema 'start int NULL, end int NULL'` (= 1 llm call)

### Advanced examples

- switch from the default model: `llmflock "extract Company and Location entities in JSON format from the following text: 'EU clears merger of Essilor , Luxottica without conditions'" -m gpt-oss` (note: the model need to be defined in the default config)
- specify a CSV dataset: `llmflock --prompt-filename=data/example4-noconfig/PROMPT.md --dataset-filename=data/example4-noconfig/dataset.csv`
- specify a schema: `llmflock --prompt-filename=data/example4-noconfig/PROMPT.dates.md --dataset-filename=data/example4-noconfig/dataset.dates.csv --schema 'start int NULL, end int NULL'`
- specify a multi-schema: `llmflock --prompt-filename=data/example4-noconfig/PROMPT.borders.md --dataset-filename=data/example4-noconfig/dataset.borders.csv --schema-multi 'name str'`

There are also three working examples (to download from the source code repository first) based on provided config file and the associated data:
- `llmflock --configfile=data/example1-ev/config.yaml`
- `llmflock --configfile=data/example2-img-transform/config.yaml`
- `llmflock --configfile=data/example3-finance/config.yaml`

## Origin of the name

The namespace in Python Package Index pypi.org is busy and one rarely get the first choice those days. Ending up with `llmflock` as a short, memorisable name, to amuse rather than impress LLM users.
I wanted also to highlight the non-deterministic and "black-box" nature of the models, yet they have very interesting behavior statistically. The behavior of one individual is hard to predict, but the knowledge of the behavior of a large group is a reachable and provide scientific value, like for birds flock!
