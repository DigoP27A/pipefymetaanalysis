import requests, os, json
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('PIPEFY_TOKEN')
PIPE_ID = int(os.getenv('PIPE_ID'))
headers = {'Authorization': 'Bearer ' + TOKEN, 'Content-Type': 'application/json'}
query = 'query { pipes(ids: [%d]) { id name phases { name cards_count } } }' % PIPE_ID
r = requests.post('https://api.pipefy.com/graphql', json={'query': query}, headers=headers)
print(json.dumps(r.json(), indent=2, ensure_ascii=False))
