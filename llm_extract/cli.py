import argparse
import re

import llm_extract.config as config_module
import json
import os
from datetime import datetime
from jsonschema import validate, ValidationError

# from dotenv import load_dotenv
# WIP: about adding another provider (openrouter)

import logging
import yaml
from llm_extract.ollama_ollama import ollama_ollama_call
from llm_extract.simonw_llm import simonw_llm_call

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="Extract structured data from raw content using LLM.")
parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help="keep LLM prompts, responses, execution time (+...)")
parser.add_argument('--dry-run', action='store_true', default=False,)
parser.add_argument('-c', '--configfile', default='config.yaml',
                    help="Specify the configuration file to use (default: config.yaml)")
parser.add_argument('--scenario', default='default',
                    help="Specify the scenario to run (see config.yaml)")
args = parser.parse_args()

# Ollama-powered models all accept the Ollama modelfile parameters as options
# see: https://github.com/ollama/ollama/blob/main/docs/modelfile.md#parameter

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
    data = {}
    json_match = re.findall(r"```json\n(.*?)\n```", text, re.DOTALL)
    if json_match:
        logger.debug('JSON code block found in LLM response')
        # Extract the JSON content from the last match
        # Note: we use the last match to avoid issues with multiple JSON
        # blocks in the response
        json_content = json_match[-1].strip()

        try:
            data = json.loads(json_content)
            validate(instance=data, schema=schema)

        except json.JSONDecodeError as e:
            logger.error(f'Invalid JSON from LLM: {str(e)}')
            logger.error(f'Raw JSON content: {json_content[:200]}...')
        except ValidationError as e:
            logger.error(f'JSON does not conform to schema: {str(e)}')
            logger.error(f'Extracted JSON content: {json_content[:200]}...')
    else:
        logger.warning(f'Failed to extract JSON from LLM response')


    return data


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


def run_variations(data: dict, variations: dict, config: dict):
    data_id = data['id']
    # print('data:', json.dumps(data, indent=2))
    # print('data_schema:', json.dumps(data_schema, indent=2))
    # print('variations:', json.dumps(variations, indent=2))

    # iterate over the document sets
    for document_set_name in variations['document_sets']:
        document_set_config = config['document_sets'][document_set_name]
        docs_by_id = {}
        # For later: for each run of run_variations (ie for each data item)
        # we are doing this load file operation for the same file. I note that
        # it can be optimized but I think there may be not significant gain in
        # the overall performance of the process. So keeping it simple for now.
        with open(document_set_config['filename'], 'r') as infile:
            for line in infile:
                if not line.strip():
                    continue
                item = json.loads(line.strip())
                docs_by_id[item['id']] = item
        document = docs_by_id[data['id']]



        # iterate over the prompts
        for prompt_name in variations['prompts']:
            # load the prompt definition
            prompt_config = config['prompts'][prompt_name]
            # load the file whose name is in prompt_config['template']['filename']
            with open(prompt_config['template']['filename'], 'r') as file:
                prompt_template = file.read()

            variables = {**data, **document}
            prompt = build_prompt(prompt_template, variables)

            logger_debug_file(prompt, f'prompt-{data_id}-{document_set_name}-{prompt_name}.md')

            # iterate over the models
            for model_name in variations['models']:
                model_config = config['models'][model_name]
                if 'name' not in model_config:
                    model_config['name'] = model_name

                # iterate over the model options temperature and top_p
                for temp in variations['model_options']['temperature']:
                    for top_p in variations['model_options']['top_p']:
                        model_options = {
                            'temperature': temp,
                            'top_p': top_p,
                            # Hard-coded max tokens (never part of the variations)
                            # TODO: move somewhere else?
                            'max_predict_tokens': 8192,
                        }

                        # iterate over the number of repeats
                        for repeat in range(1, variations['repeats'] + 1):
                            print(f'Repeat {repeat} for id={data_id} doc={document_set_name}, prompt={prompt_name}, model={model_name}, temp={temp}, top_p={top_p} ')

                            if args.dry_run:
                                continue

                            response = call_llm(prompt, model_config, model_options)

                            # append more meta information to response
                            response['meta'].update(model_options)
                            response['meta']['prompt'] = prompt_name
                            response['meta']['model'] = model_name # may override existing key
                            response['meta']['repeat'] = repeat

                            logger_debug_file(json.dumps(response, indent=2),
                                              f'response-{data_id}-{document_set_name}-{prompt_name}-{model_name}-temp{temp}-topp{top_p}-repeat{repeat}.json')

                            # extract and validate JSON from response
                            extracted_data = extract_validate_json(response['data']['text'], config_module.data_schema)
                            logger.debug('Extracted data: ' + json.dumps(extracted_data))


    return


# if __name__ == "__main__":
def cli():
    # Load the config file config.yaml:
    with open(args.configfile, 'r') as file:
        config = yaml.safe_load(file)

    logs_dir = os.path.join(os.path.dirname(args.configfile), 'logs')
    runs_dir = os.path.join(os.path.dirname(args.configfile), 'runs')
    run_timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    config_module.log_dir = os.path.join(logs_dir, run_timestamp)
    config_module.run_dir = os.path.join(runs_dir, run_timestamp)

    os.makedirs(config_module.log_dir, exist_ok=True)
    os.makedirs(config_module.run_dir, exist_ok=True)

    # Configure logger for all (this package + dependencies).
    logging.basicConfig(filename=os.path.join(config_module.log_dir, 'llm_extract.log'), encoding='utf-8',
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    # Override this package's logger for level
    if args.debug:
        logging.getLogger('llm_extract').setLevel(logging.DEBUG)

    logger.info('Run started')

    # load_dotenv()
    # api_key = os.getenv('API_KEY')

    if args.scenario not in config['scenarios']:
        print(f"Scenario '{args.scenario}' not found in config.yaml")
        exit(1)

    scenario = config['scenarios'][args.scenario]
    dataset = config['datasets'][scenario['dataset']]
    # config_module.dataset = config['datasets'][scenario['dataset']]
    # config_module.document_sets = config['document_sets']
    config_module.data_schema = config['data_schemas'][scenario['data_schema']]

    print(dataset)

    # print('variations:', json.dumps(scenario['variations'], indent=2))
    # print('data_schema:', json.dumps(config_module.data_schema, indent=2))

    variations = []
    variations_count = 1

    factor = len(scenario['variations']['document_sets'])
    variations_count *= factor
    variations.append(f'{factor} document set')

    factor = len(scenario['variations']['prompts'])
    variations_count *= factor
    variations.append(f'{factor} prompt')

    factor = len(scenario['variations']['models'])
    variations_count *= factor
    variations.append(f'{factor} model')

    for parameter, values in scenario['variations']['model_options'].items():
        # print(f"Parameter: {parameter}, Values: {values}")
        # print(f'Total variations: {len(values)}')
        variations_count *= len(values)
        variations.append(f'{len(values)} {parameter}')

    factor = scenario['variations']['repeats']
    variations_count *= factor
    variations.append(f'{factor} repeat')

    print(f'Total Variations: {variations_count} ({" x ".join(variations)})')
    
    dataset_length = 0
    with open(dataset['filename'], 'r') as infile:
        dataset_length = sum(1 for line in infile if line.strip())

    print(f'Total dataset items: {dataset_length} (in {dataset["filename"]})')


    # Iterate over the dataset and run the variations for each item:
    with open(dataset['filename'], 'r') as infile:
        for line in infile:
            if not line.strip():
                continue
            # print(line.strip())
            data = json.loads(line.strip())
            run_variations(data, scenario['variations'], config)

    meta_file_content = {}
    meta_file_content['run_timestamp'] = run_timestamp
    meta_file_content['config'] = config
    meta_file_content['stats'] = {
        'dataset_length': dataset_length,
        'variations_count': variations_count,
    }
    with open(os.path.join(config_module.run_dir, 'meta.json'), 'w') as f:
        f.write(json.dumps(meta_file_content, indent=2))

    logger.info('Run completed')
