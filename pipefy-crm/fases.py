import json

with open('dados/cards_raw.json', encoding='utf-8') as f:
    cards = json.load(f)

fases = set(c['current_phase']['name'] for c in cards if c.get('current_phase'))

for fase in sorted(fases):
    print(fase)