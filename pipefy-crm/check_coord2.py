import json
from collections import Counter

with open('dados/cards_raw.json', encoding='utf-8') as f:
    cards = json.load(f)

IDS_PROBLEMAS = [
    "1314868539", "1269758103", "1324032565", "1241747373", "1241206398",
    "1255818251", "1257474940", "1265436682", "1189209373", "1259610954",
    "1324021924", "1201341268", "1241204289", "1253252152", "1289076022",
    "1296556665", "1194107128", "1217101137"
]

# Verifica todos os labels de campos nesses cards
todos_labels = Counter()
for card in cards:
    if str(card.get("id")) in IDS_PROBLEMAS:
        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name", "")
            valor = campo.get("value")
            if valor and label:
                todos_labels[label] += 1

print("Campos presentes nesses 18 cards:")
for label, count in todos_labels.most_common():
    print(f"  {count}x [{label}]")