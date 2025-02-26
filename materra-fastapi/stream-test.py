import requests

def get_stream(url):
    s = requests.Session()

    with s.post(url, data=json.dumps([{'role': 'user', 'content': 'send me a 100 word message'}]), headers=None, stream=True) as resp:
        for line in resp.iter_lines():
            if line:
                print(line)
                print('----------------')
import json
url = 'http://localhost:8001'
get_stream(url)

