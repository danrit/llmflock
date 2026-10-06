import argparse
import csv
import itertools
import re

import llmflock.config as config_module
from llmflock.concise_schema.utils_external import schema_dsl
from llmflock.concise_schema.prompt_instructions import build_schema_prompt
import json
import os
from datetime import datetime
from time import perf_counter
from copy import deepcopy
from jsonschema import validate, ValidationError

# from dotenv import load_dotenv
# WIP: about adding another provider (openrouter)

import logging
import yaml
from llmflock.ollama_ollama import ollama_ollama_call
from llmflock.simonw_llm import simonw_llm_call

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="Run multiple LLM scenarios over dataset.")
parser.add_argument('prompt', nargs='?', default=None,
                    help="Prompt text to submit (mandatory when no --configfile is given)")
parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help="keep LLM prompts, responses, execution time (+...)")
parser.add_argument('--dry-run', action='store_true', default=False,)
parser.add_argument('-c', '--configfile', default=None,
                    help="Specify the configuration file to use (without it, the built-in default config is used)")
parser.add_argument('--scenario', default='default',
                    help="Specify the scenario to run (see config.yaml)")
parser.add_argument('--dataset-filename', default=None,
                    help="Override the dataset file specified in config.yaml")
parser.add_argument('--prompt-filename', default=None,
                    help="Override the prompt template file specified in config.yaml")
parser.add_argument('-m', '--model', default=None,
                    help="Override the models specified in config.yaml (Comma-separated list of model names)")
parser.add_argument('-r', '--repeats', type=int, default=None,
                    help="Override the number of repeats of each variation")
parser.add_argument('--schema', default=None,
                    help="Override the JSON schema")
parser.add_argument('--schema-multi', default=None,
                    help="Override the JSON schema")
args = parser.parse_args()

# Ollama-powered models all accept the Ollama modelfile parameters as options
# see: https://github.com/ollama/ollama/blob/main/docs/modelfile.md#parameter

# Hard-coded max tokens (never part of the variations)
# TODO: move somewhere else?
MAX_PREDICT_TOKENS = 8192

# trying to stick to [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)


def logger_debug_file(content, filename, directory=None):
    """Write debug text to a file in the specified directory."""
    if args.debug:
        if directory is None:
            directory = config_module.log_dir
        with open(os.path.join(directory, filename), 'w') as f:
            f.write(content)
        logger.debug(f"File saved: {os.path.join(directory, filename)}")



def build_prompt(template: str, variables: dict) -> str:
    """ Template processing function to build the prompt.

    :param template:
    :param variables:
    :return:
    """
    # No variable at all (eg a prompt submitted directly on the command line):
    # the template IS the prompt. Skipping .format() also keeps any literal
    # brace of that prompt intact.
    if not variables:
        return template

    # if a variable name is suffixed by "_filename", load the file content
    # into a new variable named without that suffix (eg "doc_content_filename"
    # -> "doc_content")
    variables_loaded = {}
    for k, v in variables.items():
        if k.endswith('_filename'):
            var_name = k[:-len('_filename')]
            with open(v, 'r') as file:
                variables_loaded[var_name] = file.read()
        else:
            variables_loaded[k] = v

    prompt = template.format(**variables_loaded)
    # for k, v in vars.items():
    #     placeholder = f'<{k}>'
    #     prompt = prompt.replace(placeholder, v)

    return prompt


def extract_validate_json(text: str, schema: dict) -> dict:
    extraction = {
        'status': 0,
        'message': None,
        'data': {},
    }
    json_match = re.findall(r"```json\n(.*?)\n```", text, re.DOTALL)
    if json_match:
        logger.debug('JSON code block found in LLM response')
        # Extract the JSON content from the last match
        # Note: we use the last match to avoid issues with multiple JSON
        # blocks in the response
        json_content = json_match[-1].strip()

        try:
            extraction['data'] = json.loads(json_content)
            validate(instance=extraction['data'], schema=schema)

        except json.JSONDecodeError as e:
            logger.error(f'Invalid JSON from LLM: {str(e)}')
            logger.error(f'Raw JSON content: {json_content[:200]}...')
            extraction['message'] = f'Invalid JSON from LLM: {str(e)} ; Raw JSON content: {json_content[:200]}...'
            extraction['status'] = 2
        except ValidationError as e:
            logger.error(f'JSON does not conform to schema: {str(e)}')
            logger.error(f'Extracted JSON content: {json_content[:200]}...')
            extraction['message'] = f'JSON does not conform to schema: {str(e)} ; Extracted JSON content: {json_content[:200]}...'
            extraction['status'] = 3
    else:
        logger.error(f'Failed to extract JSON fenced-block from LLM response')
        extraction['message'] = 'Failed to extract JSON fenced-block from LLM response'
        extraction['status'] = 1

    return extraction


def call_llm(prompt: str, model_config: dict, model_options: dict) -> dict:
    # generate options by mapping model_options keys to model specific option keys
    model_options_specific = {}
    for key, value in model_options.items():
        if key in model_config['options']:
            model_options_specific[model_config['options'][key]] = value

    # call appropriate backend
    if model_config['backend'] == 'ollama_ollama':
        response = ollama_ollama_call(prompt, model_config['name'],
                                  model_options_specific)
    elif model_config['backend'] == 'simonw_llm':
        response = simonw_llm_call(prompt, model_config['name'],
                               model_options_specific)
    else:
        raise ValueError(f"Unknown backend: {model_config['backend']}")

    return response


def build_variations(scenario_variations: dict) -> list:
    """Build the list of variations to run (the "matrix"), one dict per LLM call
    (per dataset record).

    Every parameter is optional but `prompts`: an omitted parameter simply
    contributes a single "unset" value to the product.

    :param scenario_variations: the `variations` object of the active scenario
    :return: the flat list of variations, in nested-loop order
    """
    document_sets = scenario_variations.get('document_sets') or [None]
    prompts = scenario_variations.get('prompts') or []
    prompt_const_embeds = scenario_variations.get('prompt_const_embeds') or [None]
    models = scenario_variations.get('models')
    model_options_config = scenario_variations.get('model_options') or {}
    repeats = scenario_variations.get('repeats', 1)

    # the model options are generic: any key defined in the scenario is a
    # dimension of the matrix, none of them is mandatory.
    option_names = list(model_options_config.keys())
    option_value_combinations = list(itertools.product(
        *[model_options_config[name] for name in option_names]))

    variations = []
    for (document_set, prompt, prompt_const_embed, model, option_values,
         repeat) in itertools.product(document_sets, prompts,
                                      prompt_const_embeds, models,
                                      option_value_combinations,
                                      range(1, repeats + 1)):
        variations.append({
            'document_set': document_set,
            'prompt': prompt,
            'prompt_const_embed': prompt_const_embed,
            'model': model,
            'model_options': dict(zip(option_names, option_values)),
            'repeat': repeat,
        })

    return variations


def variations_breakdown(scenario_variations: dict) -> str:
    """Human readable breakdown of the variations matrix (eg "1 document set x
    2 prompt x 1 model x 3 temperature x 1 repeat")."""
    factors = [
        (len(scenario_variations.get('document_sets') or [None]), 'document set'),
        (len(scenario_variations.get('prompts') or []), 'prompt'),
        (len(scenario_variations.get('prompt_const_embeds') or [None]), 'prompt const embed'),
        (len(scenario_variations.get('models') or [None]), 'model'),
    ]
    for parameter, values in (scenario_variations.get('model_options') or {}).items():
        factors.append((len(values), parameter))
    factors.append((scenario_variations.get('repeats', 1), 'repeat'))

    return ' x '.join(f'{count} {label}' for count, label in factors)


def variation_label(variation: dict) -> dict:
    """The identity of a variation, as stored in output.jsonl and used to name
    the debug files."""
    document_set = variation['document_set']
    prompt_const_embed = variation['prompt_const_embed']
    return {
        'document': document_set['name'] if document_set else None,
        'prompt': variation['prompt']['name'],
        'prompt_const_embed': prompt_const_embed['name'] if prompt_const_embed else None,
        'model': variation['model'],
        'model_options': variation['model_options'],
        'repeat': variation['repeat'],
    }


def variation_slug(data_id, label: dict) -> str:
    """Filename-friendly rendering of a variation label."""
    options = '-'.join(f'{name}{value}'
                       for name, value in label['model_options'].items())
    parts = [str(data_id), str(label['document']), str(label['prompt']),
             str(label['prompt_const_embed']), str(label['model'])]
    if options:
        parts.append(options)
    parts.append(f'repeat{label["repeat"]}')
    return '-'.join(parts)


def run_variation(data: dict, variation: dict, models: dict, schema: dict | None):
    """Run a single variation for a single dataset record (one LLM call)."""
    data_id = data.get('id')
    label = variation_label(variation)

    # the document set is optional: without it the record carries no
    # variation-specific data
    document_set = variation['document_set']
    if document_set is None:
        document = {}
    else:
        docs_by_id = {}
        # For later: for each run of run_variations (ie for each data item)
        # we are doing this load file operation for the same file. I note that
        # it can be optimized but I think there may be not significant gain in
        # the overall performance of the process. So keeping it simple for now.
        with open(document_set['filename'], 'r') as infile:
            for line in infile:
                if not line.strip():
                    continue
                item = json.loads(line.strip())
                docs_by_id[item['id']] = item
        document = docs_by_id[data_id]

    # the prompt template is either passed directly ('content')
    #  or read from a file ('filename')
    template = variation['prompt']['template']
    if template.get('content') is not None:
        prompt_template = template['content']
    else:
        with open(template['filename'], 'r') as file:
            prompt_template = file.read()

    prompt_const_embed = variation['prompt_const_embed']
    if prompt_const_embed is None:
        const_embed_variables = {}
    else:
        # convert to the "<var_name>_filename" convention expected by build_prompt
        const_embed_variables = {
            f'{var_name}_filename': var_config['filename']
            for var_name, var_config in prompt_const_embed['variables'].items()
        }

    variables = {**data, **document, **const_embed_variables}
    prompt = build_prompt(prompt_template, variables)

    # the prompt only depends on the record + document set + prompt + const
    # embed, hence the shorter filename here
    logger_debug_file(prompt, 'prompt-{}-{}-{}-{}.md'.format(
        data_id, label['document'], label['prompt'], label['prompt_const_embed']))

    model_config = models[variation['model']]
    model_options = {**variation['model_options'],
                     'max_predict_tokens': MAX_PREDICT_TOKENS}

    print('LLM Call for id={} doc={}, prompt={}, const_embed={}, model={}, options={}, repeat={}'.format(
        data_id, label['document'], label['prompt'], label['prompt_const_embed'],
        label['model'], json.dumps(label['model_options']), label['repeat']))
    if args.dry_run:
        return

    start_variation = perf_counter()
    response = call_llm(prompt, model_config, model_options)

    logger_debug_file(response['data']['text'],
                      f'response-{variation_slug(data_id, label)}.txt')

    record = {
        'id': data_id,
        'variation': label,
        'llm_call': response['meta'],
    }

    # the data schema is optional: without it there is nothing to extract and
    # validate, so the raw LLM response is stored instead
    if schema:
        extracted_data = extract_validate_json(response['data']['text'],
                                               schema)
        logger.debug('Extracted data: ' + json.dumps(extracted_data))
        record['extraction'] = extracted_data
    else:
        record['response'] = response['data']['text']

    record['duration_ms'] = f'{(perf_counter() - start_variation) * 1000:.0f}'

    # output in output.jsonl
    with open(os.path.join(config_module.run_dir, 'output.jsonl'), 'a') as f:
        f.write(json.dumps(record) + '\n')

    return


def run_variations(dataset, variations: list, models: dict, schema: dict | None):
    """Run every variation of the matrix for every record of the dataset."""
    for data in dataset:
        for variation in variations:
            run_variation(data, variation, models, schema)

    return


def read_dataset(filename: str):
    """Yield the records of a dataset file (.jsonl or .csv), detected by file extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.csv':
        with open(filename, 'r', newline='') as infile:
            for record in csv.DictReader(infile):
                if not record.get('id'):
                    raise ValueError(f"Dataset record missing mandatory 'id' field: {record}")
                yield record
    else:
        with open(filename, 'r') as infile:
            for line in infile:
                if not line.strip():
                    continue
                record = json.loads(line.strip())
                if not record.get('id'):
                    raise ValueError(f"Dataset record missing mandatory 'id' field: {record}")
                yield record


# if __name__ == "__main__":
def cli():
    if not args.configfile and not args.prompt and not args.prompt_filename:
        parser.error('a prompt (direct or through prompt-filename) or a --configfile is required')

    if args.configfile:
        # Load the config file config.yaml:
        with open(args.configfile, 'r') as file:
            config = yaml.safe_load(file)
        base_dir = os.path.dirname(args.configfile)
    else:
        config = deepcopy(config_module.config_default)
        base_dir = os.path.expanduser(config_module.user_dir)

    logs_dir = os.path.join(base_dir, 'logs')
    runs_dir = os.path.join(base_dir, 'runs')
    run_timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    config_module.log_dir = os.path.join(logs_dir, run_timestamp)
    config_module.run_dir = os.path.join(runs_dir, run_timestamp)

    os.makedirs(config_module.log_dir, exist_ok=True)
    os.makedirs(config_module.run_dir, exist_ok=True)

    # Configure logger for all (this package + dependencies).
    logging.basicConfig(filename=os.path.join(config_module.log_dir, 'llmrunctl.log'), encoding='utf-8',
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    # Override this package's logger for level
    if args.debug:
        logging.getLogger('llmrunctl').setLevel(logging.DEBUG)

    logger.info('Run started')

    # load_dotenv()
    # api_key = os.getenv('API_KEY')

    if args.scenario not in config['scenarios']:
        print(f"Scenario '{args.scenario}' not found in "
              f"{args.configfile if args.configfile else 'the default config'}")
        exit(1)

    # Creating a detached/clone copy of the original data, as it will be
    # overridden by various passed-on argument (right approach?)
    scenario = deepcopy(config['scenarios'][args.scenario])
    scenario_variations = scenario['variations']

    if args.dataset_filename:
        scenario['dataset'] = {'filename': args.dataset_filename}

    if args.model:
        scenario_variations['models'] = args.model.split(',')

    if args.repeats is not None:
        scenario_variations['repeats'] = args.repeats

    schema_from_args = args.schema is not None or args.schema_multi is not None
    if args.schema is not None:
        scenario['data_schema'] = schema_dsl(args.schema)
    if args.schema_multi is not None:
        scenario['data_schema'] = schema_dsl(args.schema_multi, True)

    # a prompt passed on the command line (text or file) replaces the whole set
    # of variations['prompts']
    if args.prompt_filename:
        scenario_variations['prompts'] = [{
            'name': 'default',
            'template': {
                'filename': args.prompt_filename
            }
        }]
    elif args.prompt:
        prompt_content = args.prompt
        if schema_from_args:
            prompt_content = build_schema_prompt(
                args.prompt, scenario['data_schema'],
                config_module.prompt_schema_default)
        scenario_variations['prompts'] = [{
            'name': 'default',
            'template': {
                'content': prompt_content
            }
        }]

    if not scenario_variations.get('prompts'):
        print('No prompt defined: pass a prompt, --prompt-filename, or define one in the config file')
        exit(1)

    # every model of the scenario must be defined in the `models` section of
    # the config
    model_names = scenario_variations.get('models')
    models_config = config.get('models') or {}
    models_undefined = [name for name in model_names if name not in models_config]
    if models_undefined:
        print("Model(s) {} not found in {}".format(
            ', '.join(f"'{name}'" for name in models_undefined),
            args.configfile if args.configfile else 'the default config'))
        exit(1)

    models = {name: deepcopy(models_config[name]) for name in model_names}
    for model_name, model_config in models.items():
        # the model name defaults to the key of the `models` section
        model_config.setdefault('name', model_name)

    variations = build_variations(scenario_variations)
    print(f'Total Variations: {len(variations)} ({variations_breakdown(scenario_variations)})')

    # the dataset is optional: without it a single synthetic record is used
    dataset_config = scenario.get('dataset')
    if dataset_config:
        dataset_filename = dataset_config['filename']
        dataset = list(read_dataset(dataset_filename))
        dataset_length = len(dataset)
        print(f'Total dataset items: {dataset_length} (in {dataset_filename})')
    else:
        dataset_length = 1
        dataset = [{'id': None}]
        print('No dataset: running the variations once')

    # Iterate over the dataset and run the variations for each item:
    start = perf_counter()
    run_variations(dataset, variations, models, scenario.get('data_schema'))

    duration_ms = (perf_counter() - start) * 1000

    meta_file_content = {
        'run_timestamp': run_timestamp,
        'models': models,
        'scenarios': {'default': scenario},
        'stats': {
            'dataset_length': dataset_length,
            'variations_count': len(variations),
            'llm_calls': dataset_length * len(variations),
            'duration_ms': f'{duration_ms:.0f}',
    }}
    with open(os.path.join(config_module.run_dir, 'meta.json'), 'w') as f:
        f.write(json.dumps(meta_file_content, indent=2))

    print(f'Run completed in {duration_ms:.0f}ms')
    print(f'Run output: {config_module.run_dir}')
    logger.info(f'Run completed in {duration_ms:.0f}ms')
