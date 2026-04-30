import json
from collections import Counter

with open('dados/cards_raw.json', encoding='utf-8') as f:
    cards = json.load(f)

tamanhos = Counter()
for card in cards:
    fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
    if fase_atual != "Venda":
        continue
    for campo in card.get("fields", []):
        label = campo.get("field", {}).get("label") or campo.get("name", "")
        valor = campo.get("value")
        if label == "Tamanho da empresa":
            tamanhos[valor] += 1

print("Tamanhos encontrados nas vendas:")
for t, c in tamanhos.most_common():
    print(f"  {c}x - {t}")