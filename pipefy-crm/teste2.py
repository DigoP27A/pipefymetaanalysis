import requests, os, json
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('PIPEFY_TOKEN')
PIPE_ID = os.getenv('PIPE_ID')

headers = {'Authorization': 'Bearer ' + TOKEN, 'Content-Type': 'application/json'}

# Testa buscar histórico de um card específico
query = """
{
  allCards(pipeId: %s, first: 1) {
    edges {
      node {
        id
        title
        phases_history {
          phase {
            name
          }
          firstTimeIn
          lastTimeOut
          duration
        }
      }
    }
  }
}
""" % PIPE_ID

r = requests.post('https://api.pipefy.com/graphql', json={'query': query}, headers=headers)
print(json.dumps(r.json(), indent=2, ensure_ascii=False))