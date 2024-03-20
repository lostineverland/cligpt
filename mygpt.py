import json, argparse
import os, datetime
import urllib.request
import urllib.error

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

def latest():
    ISO_8601_MINUTES = '%Y-%m-%dT%H-%M'
    return datetime.datetime.now().strftime(ISO_8601_MINUTES)

def get_key():
    keypath = os.path.join(os.getenv('HOME'), '.mygpt')
    try:
        with open(keypath) as f:
            return f.read().rstrip()
    except:
        raise Exception(f'did not find the API key at: {keypath}')

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
    print(rendered_a, flush=True)

def enter_query_loop(args, query):
    api_key = get_key()
    os.makedirs(os.path.join(os.getcwd(), 'GPT_logs'), exist_ok=True)
    messages = [{"role": "system", "content": args.role}]
    model = args.model
    log_path = os.path.join('GPT_logs', '{}.md'.format(latest()))
    with open(log_path, 'w') as log:
        while query:
            messages += [dict(role='user', content=query)]
            response = callgpt(messages, args.model, api_key)
            message, model = process_response(response)
            messages += [message]
            log_interaction(log, query, message['content'])
            query = input(f"{model}:\n")        


def cli_parser():
    '''CLI tools'''
    parser = argparse.ArgumentParser(description='This runs OpenAI GPT from the terminal. Press CTRL-C to exit.')
    parser.add_argument('role', nargs='?', default="You are a Google Search replacement",
        help='Describe What kind of agent/helper you want, (default: "You are a Google Search replacement")')
    parser.add_argument('-m', '--model', dest='model', default="gpt-4", help='Which model ie "gpt-4-turbo-preview"')
    return parser.parse_args()

def main():
    args = cli_parser()
    query = input(f"{args.model}:\n")
    if query:
        enter_query_loop(args, query)

if __name__ == '__main__':
    main()
