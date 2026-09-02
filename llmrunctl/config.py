"""
Configuration for the LLM run process.
Note: using this module as a centralized configuration point, data is modifiable.
"""
log_dir = '.'
run_dir = '.' # required?
data_schema = {}
# dataset = {}
# document_sets = {}
# WIP Set a default model SO with that + few optional arguments the tool can be called WITHOUT config.yaml too
model_default = {
    'backend': 'ollama_ollama',
    'name': 'gemma3',
    'options': {
        'temperature': 'temperature',
        'max_predict_tokens': 'num_predict',
        'top_p': 'top_p',
    }
}
# WIP default config yaml when no config.yaml file is provided:
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
                # prompt: the only thing to be populated
                'prompts': [
                    {
                        'name': 'default',
                        'template': {
                            # approach a: prompt directly passed-on: with 'content' attribute TODO
                            'content': '<HERE is the TEXT CONTENT of the PROMPT>',
                            # approach b: prompt passed-on through a file with 'filename' attribute
                            'filename': 'path/to/prompt.md'
                        }
                    }
                ],
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