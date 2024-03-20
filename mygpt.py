import json, argparse
import os, datetime
import urllib.request
import urllib.error

def callgpt(messages, model, api_key):
    endpoint = 'https://api.openai.com/v1/chat/completions'
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bear {}".format(api_key)
    }
    data = json.dumps({
             "model": model,
             "messages": messages,
             "temperature": 0.7
           }).encode('utf-8')
    print('data:', data)
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
    lambda: datetime.datetime.now().strftime(ISO_8601_MINUTES)

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

def log_interaction(log, header, message):
    underline = '-' * len(header)
    rendered_text = f'{header}\n{underline}\n\n'
    log.write(rendered_text)
    print(rendered_text, flush=True)

def enter_query_loop(args):
    api_key = get_key()
    os.makedirs(os.path.join(os.getcwd(), 'GPT_logs'), exist_ok=True)
    messages = [{"role": "system", "content": args.role}]
    model = args.model
    print('entering query loop')
    with open(f"{latest()}.md", 'w') as log:
        while True:
            query = input(f"{model}:\n")
            log_interaction(log, 'Question:', query)
            messages += [dict(role='user', content=query)]
            response = callgpt(messages, args.model, api_key)
            message, model = process_response(response)
            messages += message
            log_interaction(log, 'Answer:', message['content'])


def cli_parser():
    '''CLI tools'''
    parser = argparse.ArgumentParser(description='This runs OpenAI GPT from the terminal. Press CTRL-C to exit.')
    parser.add_argument('role', nargs='?', default="You are a Google Search replacement",
        help='Describe What kind of agent/helper you want, (default: "You are a Google Search replacement")')
    parser.add_argument('-m', '--model', dest='model', default="gpt-4", help='Which model ie "gpt-4-turbo-preview"')
    return parser.parse_args()

def main():
    args = cli_parser()
    enter_query_loop(args)

if __name__ == '__main__':
    main()
