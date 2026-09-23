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
- update the looping: work WITHOUT a `config.yaml` (falling back on `config_default`), every variation parameter optional, and `run_variations` split into `build_variations()` (the matrix) + `run_variations()`/`run_variation()` (running it).
- add support for CSV dataset
- add support for `--schema` option

### in progress

#### provide `llm` iso-functionality (for basic feature)

I want to allow user of popular [llm](https://llm.datasette.io/en/stable/index.html) tool to transition easy to that tool, that mean replicating some of the features, replicating the pattern, ie working WITHOUT config file. (note: To create an optional positional argument in Python using the argparse module, you need to use the nargs='?' parameter. eg: `parser.add_argument("prompt", help="...", nargs="?", default=None)`)
(...)

#### Next - implement schema option

The grand idea is to mimic LLM’s [concise schema syntax](https://llm.datasette.io/en/stable/schemas.html#schemas-dsl)
- `llmrunctl --schema 'name, age int, one_sentence_bio' 'invent a cool dog'`
- `llmrunctl --schema 'count int' "How many r's in strawberry?"`

With 2 added features:

##### Support for null value

I understand that by default in [JSON Schema](https://json-schema.org/), a property type definition implicitly does not allow nullable fields, yet in the context of data extraction it will be often require to allow the LLM to set NULL. Hence need to add that feature on the current simonw implementation that I have copied into the file `llmrunctl/utils_external.py`.

Continuing on the original implementation that look similar to a SQL column declaration in a `CREATE table` statement, I want the format of the nullable field to look like in a mariadb/sqlite column definition: `column_1 int [NOT NULL | NULL]`

examples:
- `llmrunctl "What years mark the start and end of Queen Elizabeth II's reign in the United Kingdom?" --schema 'start int, end int'`
- `llmrunctl "What years mark the start and end of King Charles III's reign in the United Kingdom?" --schema 'start int NULL, end int NULL'` _currently ignored_
- `llmrunctl --prompt-filename=data/example4-noconfig/PROMPT.dates.md --dataset-filename=data/example4-noconfig/dataset.dates.csv --schema 'start int, end int NULL'`

##### Update user prompt to add schema instruction

When a schema has been provided by arguments (via `--schema` or `--schema-multi`) I want that the tool automatically append to the prompt text given the instructions to output the response inside a JSON Markdown fenced code block, following the json schema given. That is stage 2.

I have already implemented stage 1: support for the `--schema` option to override the `data_schema` attribute. 
I have prepared the prompt template `prompt_schema_default` in `llmrunctl/config.py`: 

Now I want to create logic to create 2 things, based on the json schema been passed with `--schema` option:
- build (and replace in the prompt template) `<human_json_schema_rules>` token: the "human explanation of the rule defined in the json schema"
- build (and replace in the prompt template) `<json_example_1>`, `<json_example_2>` and `<json_example_3>` tokens: 3 different example of dummy valid data for the schema.

Json schema is a vast specification and I just want to support a subset of it: what is currently supported by the `--schema` and `--schema-multi` option (defined by function `schema_dsl` in `llmrunctl/concise_schema/utils_external.py`)

Technical requirements:
- for the example the generation should be deterministic (ie not random): two run of the same command should generate the same example file. There are 4 supported types: `bool`, `int`, `float` and `str`. Example values should be taken from the values from the respective variables `bools`, `ints`, `floats` and `strs` defined in `llmrunctl/concise_schema/lookup_tables.py`. For string generation, it should combine one element from `strs.left` and one element from `strs.right` separated by a space.
- when using the option `--schema-multi` the produced json schema contains a 5th supported type `Array`, wrapping the schema defined by the argument value. The generation logic of the tokens should support that. Eg: `llmrunctl "list the countries sharing a border with USA" --schema-multi 'name str'`
- Here is the main steps It needs to follow:
  1. After `schema_dsl()` is called on the schema arguments, use the output to generate a hash (used later for deterministic generation of the examples data)
  2. Generate `<human_json_schema_rules>` token: iterate trough the schema definition and generate bullet points instruction, attributes by attributes of the requested response format. See examples below. Adjustment in the wording can be made to output better plain english or cater more cases.
  3. Generate `<json_example_1>`, `<json_example_2>` and `<json_example_3>` tokens: for each examples, iterate trough the schema definition and generate different but deterministic json examples using the hash produced above. And run json validation on each one, throw exception if it fails.
- Add the logic for that feature in a new dedicated file in `llmrunctl/concise_schema` folder, import and call it from `cli.py`

Note: refer to the prompt files used in the following commands to have example of the expanded tokens `<human_json_schema_rules>`, `<json_example_1>`, `<json_example_2>` and `<json_example_3>`:
- `llmrunctl --prompt-filename=data/example4-noconfig/PROMPT.md --dataset-filename=data/example4-noconfig/dataset.csv --schema 'count int'`
- `llmrunctl --prompt-filename=data/example4-noconfig/PROMPT.dates.md --dataset-filename=data/example4-noconfig/dataset.dates.csv --schema 'start int, end int NULL'`
- examples for a schema-multi: `llmrunctl --prompt-filename=data/example4-noconfig/PROMPT.borders.md --dataset-filename=data/example4-noconfig/dataset.borders.csv --schema-multi 'name str'`

Note: this behavior (Update user prompt to add schema instruction) should be triggered only when schema AND prompt are been provided by arguments. (ie if not, it is assume that the user want control of the exact prompt instructions through a custom prompt file, hence no automatic add of instructions.)


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
- add a sort of hash of experiment condition so future `llmrunviewer` can target only similar/relevant runs to compare.
- with the tool available as a python package in pypi.org, need a way to make the 3 examples easily available to package user
- make a default naming for models provided by on backend (example if ollama backend is available, all the local models of that backend should be available with the `--models=modela,modelb` option.) ie moving `config_module.model_default` to `ollama` backend source
- do a output format option `-o`, default to json
  - pretty-print output
  - csv output
- implicitly implement check on whether the variable used in prompt are defined in the dataset
- make validation more generic: from mandate `data_schema` (ie json_schema) can go for `data_validation`: with currently 2 choice: `json_schema` or `callback`
- add multi in schema feature like in `llm` tool to support prompt like: `llmrunctl "list the countries sharing a border with USA"` ; `llmrunctl "list the countries sharing a border with Australia"`


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
