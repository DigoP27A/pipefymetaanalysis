
import json
from datetime import datetime

with open('dados/cards_raw.json', encoding='utf-8') as f:
    cards = json.load(f)

CICLO_INICIO = datetime(2025, 10, 1)
CICLO_FIM = datetime(2025, 12, 31, 23, 59, 59)
FASES_PROPOSTA = ['6. Proposta comercial feita', '7. Follow-up', 'Venda']

por_criacao = set()
por_fase = set()

for card in cards:
    card_id = card.get('id')
    created = card.get('created_at')
    fases_visitadas = [ph.get('phase', {}).get('name') for ph in card.get('phases_history', [])]
    passou_proposta = any(f in fases_visitadas for f in FASES_PROPOSTA)
    if passou_proposta:
        por_fase.add(card_id)
        if created:
            dt = datetime.strptime(created, '%Y-%m-%dT%H:%M:%SZ')
            if CICLO_INICIO <= dt <= CICLO_FIM:
                por_criacao.add(card_id)

fora_do_ciclo = por_fase - por_criacao
print('Propostas no ciclo 1 (por data criacao):', len(por_criacao))
print('Cards fora do ciclo mas com proposta:', len(fora_do_ciclo))
for card in cards:
    if card.get('id') in fora_do_ciclo:
        dt = datetime.strptime(card['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        print(' -', card['id'], '|', card['title'], '| criado em', dt.strftime('%d/%m/%Y'))
