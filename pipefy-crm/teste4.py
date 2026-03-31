import requests, os, json
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('PIPEFY_TOKEN')
headers = {'Authorization': 'Bearer ' + TOKEN, 'Content-Type': 'application/json'}
query = 'query { organizations { id name pipes { id name } } }'
r = requests.post('https://api.pipefy.com/graphql', json={'query': query}, headers=headers)
print(json.dumps(r.json(), indent=2, ensure_ascii=False))
