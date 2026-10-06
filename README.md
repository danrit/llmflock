# LLM Flock

A CLI tool to interact with local and remote LLM, define multiple scenario variations (model × prompt × options), run them over a dataset and capture structured results for comparison or to build knowledge through meta analysis.

DRAFT: more on the objective of this tool: it is built to run extraction the same structured data (`data_schemas.default`) in a list (`datasets.default`) of documents (`document_sets.default`) usings LLM and output tabular data. It is designed to run the extraction several times - or variations - (`scenarios.default.variations`) with different models, prompts or model options (temperature, top_p). It also designed to repeat one variation several times (reference to non-deterministic behaviour of LLMs...) (`scenarios.default.variations.repeat`).

Note: actually this is not limited to extraction of structured data (ie a task where the research data is already in the input document but drowned in it), but to any task which generate structured data (because then structured data can then be easily compared/assessed)

Note 2: maybe that tool is more aimed at smaller models (local or cloud-hosted). By design it will have to be run **very** repetitively on big dataset so cost of running huge models from the frontier labs can be dissuasive. But big models need to be tested too sometimes to make sure the small models jobs remains relevant.

Note 3: how to we rate and compare (benchmark) the resulting output structured data, what will be the coverage of the comparison part of this tool?

- wanted to find an example of llm comparison tool: found [this one](https://www.simonpcouch.com/blog/2025-04-01-gemini-2-5-pro) (here applied to Gemini 2.5 Pro) from Simon P. Couch ([via](https://simonwillison.net/2026/Jan/20/electricity-use-of-ai-coding-agents/) then [via](https://www.simonpcouch.com/blog/2026-01-20-cc-impact/)) : which lead me to a even more popular approach ? [https://inspect.aisi.org.uk/] .....  take-aways are:
  - use a repeat parameter (epoch) to "Evaluate each sample multiple times to better quantify variation"

Note 4: more thought one the viewing result part: need to have a tool to aggregate results, adding comparison with one selected IDEAL run and output all of it in a easy spreadsheet format (csv, excel) for further analysis and visualization. by design, the tool will produce was amount of llm-generated data (over dataset and multiple variation) and exact match is illusionist / unrealistic goal. While study of individual result is still valuable to understand, an essential metric is CONVERGENCE, not EQUALITY when comparing generated data.

Hence that tool `llmflock` aim to keep it to minimum, focusing on the run+extract part.


**On where it sits in the ecosystem of LLM tools:** It is a LLM gateway: meaning it can call different LLM providers (local inference framework or cloud-hosted) with a rudimentary plugin system. If the project matures enough it could be beneficial the transition to a more established LLM gateway tool (like liteLLm, anyLLM).


## Getting started

1. [Ollama](https://ollama.com/download) should be installed and running
2. Clone the repository and install it with pip: `pip install .` (At this stage the package is not distributed, ie not published to PyPI, hence cannot be installed directly from PyPI)
    1. Or use `pip install -e .` if you want to install in editable mode.

## Usage

To run the example in `data/example1-ev`, use the command: `llmr --configfile=data/example1-ev/config.yaml` or `llmr --configfile=data/example1-ev/config.yaml --debug`

### Examples

- submitting a prompt: `llmflock "extract Company and Location entities in JSON format from the following text: 'EU clears merger of Essilor , Luxottica without conditions'"`
- switch from the default model: `llmflock "extract Company and Location entities in JSON format from the following text: 'EU clears merger of Essilor , Luxottica without conditions'" -m gpt-oss` (note: the model need to be defined in the default config)
- specify repeat count: `llmflock "extract Company and Location entities in JSON format from the following text: 'EU clears merger of Essilor , Luxottica without conditions'" -r 3`
- specify a CSV dataset: `llmflock --prompt-filename=data/example4-noconfig/PROMPT.md --dataset-filename=data/example4-noconfig/dataset.csv`
- specify a schema: `llmflock --prompt-filename=data/example4-noconfig/PROMPT.dates.md --dataset-filename=data/example4-noconfig/dataset.dates.csv --schema 'start int NULL, end int NULL'`
  - `llmflock "What years mark the start and end of Queen Elizabeth II's reign in the United Kingdom?" --schema 'start int, end int'`
  - `llmflock "What years mark the start and end of King Charles III's reign in the United Kingdom?" --schema 'start int NULL, end int NULL'`
- specify a multi-schema: `llmflock --prompt-filename=data/example4-noconfig/PROMPT.borders.md --dataset-filename=data/example4-noconfig/dataset.borders.csv --schema-multi 'name str'`

- There are also currently 3 working examples based on provided config file (and associated data):
- `llmflock --configfile=data/example1-ev/config.yaml`
- `llmflock --configfile=data/example2-img-transform/config.yaml`
- `llmflock --configfile=data/example3-finance/config.yaml`

## Origin of the name

The namespace in Python Package Index pypi.org is busy and one rarely get the first choice those days! Ending up with `llmflock` as a short, memorisable name, to amuse rather than impress LLM users. I wanted also to highlight the non-deterministic and "black-box" nature of those models, yet they have very interesting behavior statistically. The behavior of one individual is hard to predict, but the knowledge of the behavior of a large group is a reachable and provide value.
