# Work In Progress

### Done

- better README (explaining the config.yaml)
- create config.yaml for example2 + run it! (note that it currently my local llm fail the extraction)
- create config.yaml for example3 + run it!
- Save debug prompt/response files per variation
- Extract JSON from LLM response and validate against schema
- Split `data` + `document` in `run_variations`; use generic `data['id']` instead of domain-specific identifiers
- Separate `logs/` (debug files, log file) and `runs/` (structured outputs) directories
- Terminology: `variations` instead of `combinations`
- Write `meta.json` at end of run (timestamp, full config, dataset length, variations count)
- Two additional extraction examples (beside EV attributes): image transformation, financial NER)
- Write `output.jsonl` per run — one line per LLM call (see schema in `data/example1-ev/runs/YYYYMMDD-HHMISS/output.jsonl`)
- Capture token counts and processing time per call (needed for `extracted.jsonl` and stats)
- support for yaml anchor/alias - or in other words, simplify the current syntax of `config.yaml` where I have "mandated" to use "manual references" in the `scenario` object. ie that is a simplification.
- update `meta.json` `scenarios` attribute: with the scenario name and CLI args passed in: during argument parsing / scenario preparation, build the "real-active" scenario (made of selected scenario in config.yaml + overrides with args) and that is the one used to build variations AND stored in meta.json. The intent with that is that meta.json contains everything to re-run the same scenario
- update the looping: work WITHOUT a `config.yaml` (falling back on `config_default`), every variation parameter optional, and `run_variations` split into `build_variations()` (the matrix) + `run_variations()`/`run_variation()` (running it). See "the looping" notes below.

### in progress

#### context: provide `llm` iso-functionality (for basic feature)

I want to allow user of popular [llm](https://llm.datasette.io/en/stable/index.html) tool to transition easy to that tool, that mean replicating some of the features, replicating the pattern, ie working WITHOUT config file. (note: To create an optional positional argument in Python using the argparse module, you need to use the nargs='?' parameter. eg: `parser.add_argument("prompt", help="...", nargs="?", default=None)`)
(...)

#### my thought process so far
Have the entire system working WITHOUT a config.yaml file take a bit more time...
doing there are more parameters that need to be optional: models options, document set, prompts... even dataset. I think that to make those optional I need to re-architecture the browsing of all variations: go away from "intricated loops" to 2 steps process: Building the matrix/list of variations - running it (+ it will allow parallelization later...)
As a preliminary work in config.py: I have defined `config_default`, which contains what `scenario` can be at the minimum, that is stripped of all parameters that I want to make optional. My idea is that this default config should be the base of the `scenario` structure when the user is using it WITHOUT the YAML config file.

#### Done: update the looping — implementation notes

Decisions taken while implementing (all 3 aims done):

- CLI: `prompt` is now an optional positional argument (`nargs='?'`), `-m/--model` and the new `-r/--repeats` override the scenario. `-c/--configfile` no longer defaults to `config.yaml`: a bare `llmrunctl` errors, a prompt OR a `--configfile` is required.
- Without a config file, `config_default` (in `config.py`) is the base scenario and the prompt is injected as `prompts[0].template.content` (`build_prompt` skips `.format()` when there is no variable, so braces in an ad-hoc prompt are safe).
- Without a config file, `logs/` and `runs/` go to `~/.llmrunctl/` (`config.user_dir`) instead of the config file's directory.
- Without a `dataset`, a single synthetic record `{'id': None}` is used; its null id contributes no prompt variable and is stored as `"id": null` in `output.jsonl`.
- `model_options` is now generic: every key of `variations.model_options` is a dimension of the matrix (no more hard-coded temperature/top_p loops), and `output.jsonl` stores them nested: `variation.model_options: {temperature, top_p}` — replaces the former flat `variation.temp` / `variation.top_p`.
- A model requested but not declared in the `models` section (of the config file, or of `config_default`) is an error: message + exit, like the other invalid arguments. Consequence: `-m <model>` without a config file only accepts the models declared in `config_default['models']` (today: `gemma3`).
- Without a `data_schema`, the extraction is skipped and the record carries `response` (raw LLM text) instead of `extraction`.

The 3 examples were re-run and still work; the 3 showcase commands work too:
- `llmrunctl "extract Company and Location entities in JSON format from the following text: 'EU clears merger of Essilor , Luxottica without conditions'"`
- same with `-m gpt-oss` — needs `gpt-oss` declared in `config_default['models']` (see the model error rule above)
- same with `-r 3`

#### Next - implement schema option

Using LLM’s [concise schema syntax](https://llm.datasette.io/en/stable/schemas.html#schemas-dsl)
`llm --schema 'name, age int, one_sentence_bio' 'invent a cool dog'`

### Next — OpenRouter provider
- Add `openrouter` backend module (alongside `ollama_ollama.py` and `simonw_llm.py`)
- Load API key from `.env` via `load_dotenv()` / `os.getenv('API_KEY')` (groundwork: `python-dotenv` already in dependencies, commented import already in `cli.py`)
- Motivation: cloud-hosted provider is a must-have; also needed to build generic response metadata (token counts) that local Ollama may not return consistently

### Backlog
- Run stats output (similar to vader-llm) ??
- Add the data/context hash: a way to capture into one unique hash all what can not be separatly defined (with limited options) so there is a reliable way to compare run from different time, different machines...
- Aggregate results across runs into CSV/JSON
- Result comparison: pick an "ideal" run: can be the run of on (big) model OR a user-defined `ground_truth.jsonl`, diff others against it. Note: there is not always a ground_truth, but that can useful for my tests while developing.
- export `output.jsonl` to spreadsheet
- make model_options (tekp, top_p) optional and removing it from default config
- add a sort of hash of experiment condition so future `llmrunviewer` can target only similar/relevant runs to compare.
- with the tool available as a python package in pypi.org, need a way to make the 3 examples easily available to package user

### currently studied

With my latest commit about adding some command line options to run simpler scenario WITHOUT a *.yaml file, I was looking for a simple/minimalist choice of argument to build that: hence I checked https://llm.datasette.io/en/stable/ and read instructions patterns like:

- `llm -m gemini-2.0-flash 'Tell me fun facts about Mountain View'`
- or just `llm 'tell me something about year 2020`
    - with setting the default model beforehand: `llm models default gpt-4o`


Note2: one particular interesting (and similar to me) approach is the definition of https://llm.datasette.io/en/stable/templates.html#templates . Example: `llm --system 'Translate in French' --model gemma3:latest -o temperature 1.8 --save wild-french`

a lot of similarities: "yeah and oh :(" at the same time.

And beside the UX for CLI of https://llm.datasette.io is good, proven (all the options defined from the outside I mean) so I want to replicate it wherever it make sense too.


## (note to publish)

mostly following https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#upload-your-distributions

1. build: `python -m build`
2. check: `twine check dist/*`
3. upload to pypi.org: `twine upload dist/*`

## Documentation

### config.yaml description

Description of the structure and usage of `config.yaml`: main part is the last attribute `scenarios`: which described the variations of the experiment to run. All other attributes - `datasets`, `data_schemas`, `document_sets`, `prompts`, `models`, `prompts` -  define the different value of one propriety of the scenario and give a convenient way to modify experiment conditions. Each of those attributes is a object of possible values to use. (During on given variation run, only one value is used.)

There one recommended element to each attribute: `default`: this will be the value choose in some situation when nothing else has been specified (...). In the documentation below this is the element chosen to illustrate the purpose. But it could be read as any other attribute name for that propriety.

#### `datasets.default`

By design the tool aims to run extraction of structured data on multiple similar records of data. Not just one-off sample extraction. The output is structured data for multiple records, extraction cross-check by multiple variations to reinforce the confidence, and that can then be stored in traditional relational database. This is the added value created by the tool.
(Actually the tool has secondary aim: to benchmark llm run. This aim can be pursued independently but it can be used as well to improve result of the first aim. So really, actual data extraction is the primary aim)

This attribute is where the multiple records to run the tool on are stored in a jsonl file. Each record have one mandatory attribute `id` and a list of dataset-specific optional attributes. This contains only the non-variable (ie no different variations) attributes of a record. By contrast the attribute `document_sets.default` contains variation-specific version of data for the same record (eg: difference document source format related to the same record, to test LLM)

#### `data_schemas.default`

Definition of the expected structured data format (JSON Schema)

#### `document_sets.default` - Optional

Different variations of the data applicable to one record in `datasets.default` in a jsonl file. Each record have one mandatory attribute `id`, which need to match with the `id` of a record in dataset.

#### `prompts.default`

Define THE prompt for the extraction, in a markdown file. The prompt is a dataset-specific, but dataset-record-agnostic template. It contains variables replaced at runtime: there are 2 types of variables:

- record-specific variables, ie attribute of `dataset`: variation-agnostic or `document_set`: variation-specific. At least one of them should exist (otherwise I don't think that makes sense here).
- record-agnostic but variation-specific variables, ie attribute of `prompt_const_embed` (Optional). attribute name need to start with `const_embed_*` (Note that record-agnostic and variation-agnostic content IS the prompt itself!)

Note 1: For both type of variables, there is a convenient logic implemented for file manipulation: if the variable name defined in yaml file or jsonl file is suffixed by `<var_name>_filename`: a new attribute is created `<var_name>` the file is loaded at runtime and its content is used for the value of `<var_name>`. Hence the template just need to use `<var_name>`.

Note 2: to "embed" document inside the prompt, leveraging the simple prompt templating system describe here, one can: 
- markdown document: just plonk the markdown content in the prompt (like example3-img-transform)
- other text format document: embedded them with a markdown code block with the language set to the format of the document (like for example1-ev)

### `prompt_const_embeds` - Optional

If the Prompt template contains usage of record-agnostic but variation-specific variables, ie starting with `const_embed_*`, here is the place to define them.

#### `models.default`

Definition of the LLM to use.

### combination of output.

In this tool the intention is to make possible the aggregation of output from different scenario runs. This is important as it allow the user to combine resource-intensive runs made overtime, or by other users, or add to an existing output a new output produced by a new model, a new backend.
This aggregation is not part of the scope of this tool.
In order for 2 run of scenario to be "aggregate-able" they need to run on the same dataset-records AND with the same data_schema. That's it. 

## TEMP - use uv instead of conda

What you'd need to change:
1. Install uv (`brew install uv` or the install script) — no folder structure change needed.
2. Nothing required in pyproject.toml — it already works as-is with uv.
3. Run `uv sync` once in the project root — this creates a .venv/ and generates a uv.lock file (new file, replaces the implicit conda env).
4. Replace conda activate <env> habits with either uv run llmrunctl ... (no activation needed) or source .venv/bin/activate if you prefer activating manually.
5. Delete/retire your old conda env once you've verified things work (conda env remove -n <name>) — optional, not urgent.
6. Add .venv/ to .gitignore if not already there (worth checking).
