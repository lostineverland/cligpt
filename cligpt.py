#! /usr/bin/env python3

import json, argparse
import functools, subprocess
import os, datetime
import urllib.request
import urllib.error
from collections import namedtuple

nullfunc = lambda *a, **k: None
nullfile = namedtuple('nullfile',
    ['write', 'flush']
    )(print, nullfunc)

def once(func):
    c = 0
    res = []
    @functools.wraps(func)
    def f(*args, **kwargs):
        nonlocal c
        if c == 0:
            c += 1
            res.append(func(*args, **kwargs))
        return res[0]
    return f

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
    ISO_8601_MINUTES = '%Y-%m-%dT%H:%M'
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

@once # this function will only run once
def log_front_matter(log, params):
    log.write(f'---\n{json.dumps(params, indent=2)}\n---\n')

def render_response(query, answer):
    u_ = lambda s: '-' * len(s) # underline function
    q = 'Question:'
    a = 'Answer:'
    rendered_q = f'{q}\n{u_(q)}\n{query}\n\n'
    rendered_a = f'{a}\n{u_(a)}\n{answer}\n\n\n'
    return rendered_q, rendered_a

def write_interaction(log, content):
    log.write(content)
    log.flush()
    
def log_interaction(log, query, answer):
    rendered_q, rendered_a = render_response(query, answer)
    write_interaction(log, rendered_q + rendered_a)
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

def summary(log, args, config, messages):
    api_key = config.get('api_key')
    messages += [dict(role='user', content='summarize this conversation in 4 keywords or less')]
    print('\n\nfetching summary keywords...')
    response = callgpt(messages, args.model, api_key)
    message, model = process_response(response)
    print(message.get('content'))
    s = 'Summary Keywords'
    log.write('\n\n{}\n{}\n{}\n'.format(s, '-'*len(s), message.get('content')))

def enter_query_loop(args, query, config, resume=None):
    api_key = config.get('api_key')
    if resume:
        mode = 'a'
        log_path = resume['path']
        messages = [{"role": "system", "content": resume.get('role', args.role)}] \
                    + resume.get('messages')
    else:
        mode = 'w'
        log_path = os.path.join(setpath(config), iso_year(), iso_month(), '{}.md'.format(iso_minute().replace(':', '-')))
        messages = [{"role": "system", "content": args.role}]
    with open(log_path, mode) as log:
        while query:
            messages += [dict(role='user', content=query)]
            response = callgpt(messages, args.model, api_key)
            message, model = process_response(response)
            messages += [message]
            log_front_matter(log, dict(
                    role=args.role,
                    model=model,
                    timestamp=iso_minute(),
                ))
            log_interaction(log, query, message['content'])
            query = input_block(f"{model}:\n")        
        summary(log, args, config, messages)

def update(config, args):
    if config.get('source'):
        src = config.get('source')
    elif args.force:
        src = os.path.dirname(os.path.realpath(__file__))
    else:
        print('Update only works if `source` is defined in `~/.cligpt` to:', os.path.dirname(os.path.realpath(__file__)))
        return
    cmd = ['cd', src, '&&', 'git pull']
    process = subprocess.Popen(cmd, stdout=None, stderr=None)
    process.wait()
    print('update succeeded')

def process_question(question):
    a_delimeter = '\n\nAnswer:\n-------\n'
    s_delimeter = '\n\n\nSummary Keywords'
    msg = question.split(a_delimeter)
    ans = msg[1].split(s_delimeter)[0]
    return [
        dict(role='user', content=msg[0]),
        dict(role='assistant', content=ans),
        ]

def get_front_matter(raw_msg):
    if raw_msg.split()[0] == '---':
        try:
            return json.loads(raw_msg.split('---')[1])
        except:
            pass
    return {}

def load_messages(path):
    q_delimeter = 'Question:\n---------\n'
    messages = []
    with open(path) as f:
        raw_msg = f.read()
        front_matter = get_front_matter(raw_msg)
        for question in raw_msg.split(q_delimeter)[1:]:
            messages += process_question(question)
    return messages, front_matter

def show_history(args, role, messages):
    print("The previous conversation was:")
    for q, a in zip(messages[::2], messages[1::2]):
        question, answer = render_response(q['content'], a['content'])
        write_interaction(nullfile, question)
        write_interaction(nullfile, answer)
    print('role: {}\nmodel: {}'.format(role, args.model))


def resume_chat(args, config):
    if os.access(args.path, os.F_OK):
        path = args.path
    elif os.access(os.path.join(config.get('log_path'), args.path), os.F_OK):
        path = os.path.join(config.get('log_path'), args.path)
    else:
        assert False, f"couldn't find {args.path}"
    messages, front_matter = load_messages(path)
    role = front_matter.get('role', args.role)
    resume = dict(
        path=path,
        role=role,
        messages=messages)
    show_history(args, role, messages)
    query = input_block(f"{args.model}:\n")
    if query:
        enter_query_loop(args, query, config, resume)

def cli_parser(config):
    '''CLI tools'''
    parser = argparse.ArgumentParser(description='This runs OpenAI GPT from the terminal. Press CTRL-C to exit.')
    parser.add_argument('role', nargs='?', default=config.get('role', 'You are a knowledge engine'),
        help='Describe What kind of agent/helper you want, (default is set in $HOME/.cligpt)')
    parser.add_argument('-m', '--model',
        dest='model',
        default=config.get('model', 'gpt-4'),
        help='Which model ie "gpt-4-turbo-preview"')
    parser.add_argument('-r', '--resume',
        dest='path',
        help='Resume from a previous chat by providing the path to that chat.')
    parser.add_argument('--update', dest='update', action='store_true', default=False, help='Update cligpt')
    parser.add_argument('--force', dest='force', action='store_true', default=False, help='Add to force an update without having to define `source`')
    args = parser.parse_args()
    if args.path and not args.path.lower().endswith('.md'):
        args.path = args.path + '.md'
    return args

def main():
    config = get_config()
    args = cli_parser(config)
    if args.update: return update(config, args)
    if args.path:
        resume_chat(args, config)
    else:
        print('role: {}\nmodel: {}'.format(args.role, args.model))
        query = input_block(f"{args.model}:\n")
        if query:
            enter_query_loop(args, query, config)

if __name__ == '__main__':
    main()
