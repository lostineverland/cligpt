#! /usr/bin/env python3

import json, argparse
import os, datetime
import urllib.request
import urllib.error
from collections import namedtuple

def callgpt(messages, model, api_key):
    endpoint = 'https://api.openai.com/v1/chat/completions'
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(api_key)
    }
    data = json.dumps({
             "model": model,
             "messages": messages,
             "temperature": 0.7
           }).encode('utf-8')
    req = urllib.request.Request(endpoint, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            raw_response = response.read()
            response = json.loads(raw_response.decode('utf-8'))
            return response
    except urllib.error.URLError as e:
        raise e

def iso_year():
    ISO_8601_YEAR = '%Y'
    return datetime.datetime.now().strftime(ISO_8601_YEAR)

def iso_month():
    ISO_8601_MONTH = '%Y-%m'
    return datetime.datetime.now().strftime(ISO_8601_MONTH)

def iso_minute():
    ISO_8601_MINUTES = '%Y-%m-%dT%H-%M'
    return datetime.datetime.now().strftime(ISO_8601_MINUTES)

def input_block(prompt):
    block = ''
    line = input(prompt)
    while line:
        block += '{}\n'.format(line)
        line = input()
    print('processing...')
    return block

def process_response(resp):
    message = resp['choices'][0]['message']
    model = resp['model']
    return message, model

def log_interaction(log, query, answer):
    u_ = lambda s: '-' * len(s) # underline function
    q = 'Question:'
    a = 'Answer:'
    rendered_q = f'{q}\n{u_(q)}\n{query}\n\n'
    rendered_a = f'{a}\n{u_(a)}\n{answer}\n\n\n'
    log.write(rendered_q + rendered_a)
    log.flush()
    print('\n' + rendered_a, flush=True)

def setpath(config):
    log_path = config.get('log_path', 'GPT_logs')
    os.makedirs(os.path.join(os.getcwd(), log_path, iso_year(), iso_month()), exist_ok=True)
    return log_path

def set_default_config(config_path):
    with open(config_path, 'x') as f:
        json.dump(dict(
            api_key='sk-################################################',
            log_path='GPT_logs',
            model='gpt-4',
            role='You are a Google Search replacement',
            ), f, indent=4)
    raise Exception('Please set configuration $HOME/.cligpt')

def get_config():
    config_path = os.path.join(os.getenv('HOME'), '.cligpt')
    default_api_key = 'sk-################################################'
    try:
        with open(config_path) as f:
            config = json.load(f)
        if config.get('api_key', default_api_key) == default_api_key:
            raise Exception(f'Please set the API key at: {config_path}')
        return config
    except FileNotFoundError:
        set_default_config(config_path)

def enter_query_loop(args, query, config):
    api_key = config.get('api_key')
    log_path = os.path.join(setpath(config), iso_year(), iso_month(), '{}.md'.format(iso_minute()))
    messages = [{"role": "system", "content": args.role}]
    with open(log_path, 'w') as log:
        while query:
            messages += [dict(role='user', content=query)]
            response = callgpt(messages, args.model, api_key)
            message, model = process_response(response)
            messages += [message]
            log_interaction(log, query, message['content'])
            query = input_block(f"{model}:\n")        

def update(config):
    if config.get('source'):
        src = config.get('source')
    elif config.force:
        src = os.path.dirname(os.path.realpath(__file__))
    else:
        print('Update only works if `source` is defined in `~/.cligpt` to:', os.path.dirname(os.path.realpath(__file__)))
        return
    cmd = ['cd', src, '&&', 'git pull']
    process = subprocess.Popen(cmd, stdout=None, stderr=None)
    process.wait()
    print('update succeeded')

def cli_parser(config):
    '''CLI tools'''
    parser = argparse.ArgumentParser(description='This runs OpenAI GPT from the terminal. Press CTRL-C to exit.')
    parser.add_argument('role', nargs='?', default=config.get('role', 'You are a knowledge engine'),
        help='Describe What kind of agent/helper you want, (default is set in $HOME/.cligpt)')
    parser.add_argument('-m', '--model',
        dest='model',
        default=config.get('model', 'gpt-4'),
        help='Which model ie "gpt-4-turbo-preview"')
    parser.add_argument('--update', dest='update', action='store_true', default=False, help='Update cligpt')
    parser.add_argument('--force', dest='force', action='store_true', default=False, help='Add to force an update without having to define `source`')
    return parser.parse_args()

def main():
    config = get_config()
    args = cli_parser(config)
    if args.update: return update(config)
    print('role: {}\nmodel: {}'.format(args.role, args.model))
    query = input_block(f"{args.model}:\n")
    if query:
        enter_query_loop(args, query, config)

if __name__ == '__main__':
    main()
