"""
Configuration for the LLM run process.
Note: using this module as a centralized configuration point, data is modifiable.
"""
log_dir = '.'
run_dir = '.' # required?
# Set at runtime from the scenario. When None (no data_schema defined), the
# extraction step is skipped and the raw LLM response is stored instead.
data_schema = None

# Base directory for logs/ and runs/ when the tool is used WITHOUT a config file.
user_dir = '~/.llmrunctl'

# Fallback model definition, used to synthesize a model configuration for a
# model name that is not declared in the `models` section of the config
# (typically `llmrunctl "<prompt>" -m <model>` without a config file).
model_default = {
    'backend': 'ollama_ollama',
    'name': 'gemma3',
    'options': {
        'temperature': 'temperature',
        'max_predict_tokens': 'num_predict',
        'top_p': 'top_p',
    }
}

# Default config used when no config.yaml file is provided: the minimal
# scenario, stripped of every parameter that is optional. Only the prompt is
# missing here: it is injected from the command line by `cli()`.
config_default = {
    'models': {
        'gemma3': {
            'backend': 'ollama_ollama',
            'name': 'gemma3',
            'options': {
                'temperature': 'temperature',
                'max_predict_tokens': 'num_predict',
                'top_p': 'top_p',
            }
        }
    },
    'scenarios': {
        'default': {
            'name': 'default scenario',
            # dataset omitted
            # data_schema omitted
            'variations': {
                # document_sets omitted
                # prompt_const_embeds omitted
                # prompts: populated from the command line, either as
                # {'template': {'content': '<prompt text>'}} or
                # {'template': {'filename': 'path/to/prompt.md'}}
                'prompts': [],
                'models': ['gemma3'],
                'model_options': {
                    # temperature omitted
                    # top_p omitted
                },
                'repeats': 1
            },
        }
    }
}
