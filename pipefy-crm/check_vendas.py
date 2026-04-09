
import json
from datetime import datetime

with open('dados/cards_raw.json', encoding='utf-8') as f:
    cards = json.load(f)

CICLO1_INICIO = datetime(2025, 10, 1)
CICLO1_FIM = datetime(2025, 12, 31, 23, 59, 59)
CICLO2_INICIO = datetime(2026, 1, 1)
CICLO2_FIM = datetime(2026, 3, 31, 23, 59, 59)

vendas_c1_por_proposta = []
vendas_c1_por_venda = []
vendas_c2_por_proposta = []
vendas_c2_por_venda = []

for card in cards:
    fase_atual = card.get('current_phase', {}).get('name') if card.get('current_phase') else None
    if fase_atual != 'Venda':
        continue

    data_proposta = None
    data_venda = None

    for ph in card.get('phases_history', []):
        nome = ph.get('phase', {}).get('name')
        fit = ph.get('firstTimeIn')
        if not fit:
            continue
        dt = datetime.strptime(fit[:19], '%Y-%m-%dT%H:%M:%S')
        if nome in ['6. Proposta comercial feita', '7. Follow-up', 'Venda']:
            if data_proposta is None or dt < data_proposta:
                data_proposta = dt
        if nome == 'Venda':
            data_venda = dt

    if data_proposta and CICLO1_INICIO <= data_proposta <= CICLO1_FIM:
        vendas_c1_por_proposta.append(card['title'])
    if data_proposta and CICLO2_INICIO <= data_proposta <= CICLO2_FIM:
        vendas_c2_por_proposta.append(card['title'])
    if data_venda and CICLO1_INICIO <= data_venda <= CICLO1_FIM:
        vendas_c1_por_venda.append(card['title'])
    if data_venda and CICLO2_INICIO <= data_venda <= CICLO2_FIM:
        vendas_c2_por_venda.append(card['title'])

print('=== CICLO 1 ===')
print('Vendas por data da PROPOSTA:', len(vendas_c1_por_proposta))
print('Vendas por data da VENDA:', len(vendas_c1_por_venda))
print()
print('=== CICLO 2 ===')
print('Vendas por data da PROPOSTA:', len(vendas_c2_por_proposta))
print('Vendas por data da VENDA:', len(vendas_c2_por_venda))
