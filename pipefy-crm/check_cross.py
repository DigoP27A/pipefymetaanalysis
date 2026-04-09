import json

with open('dados/cards_raw.json', encoding='utf-8') as f:
    cards = json.load(f)

COORDENACOES = ["ACE", "CCE", "MNP", "PRO", "QAB"]
FASES_PROPOSTA = ["6. Proposta comercial feita", "7. Follow-up", "Venda"]

def parse_lista(x):
    if not x or not isinstance(x, str): return []
    if x.startswith("["):
        try:
            import json as j
            return j.loads(x)
        except: return [x]
    return [x]

sem_coord = []
for card in cards:
    fases_visitadas = [ph.get("phase", {}).get("name") for ph in card.get("phases_history", [])]
    chegou_proposta = any(f in fases_visitadas for f in FASES_PROPOSTA)
    if not chegou_proposta:
        continue

    coords = []
    for campo in card.get("fields", []):
        label = campo.get("field", {}).get("label") or campo.get("name", "")
        valor = campo.get("value")
        if label == "Coordenação":
            coords = [c.strip() for c in parse_lista(valor) if c.strip() in COORDENACOES]

    if not coords:
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        sem_coord.append({
            "id": card.get("id"),
            "titulo": card.get("title"),
            "fase_atual": fase_atual,
            "coord_raw": card.get("fields", []),
        })

print(f"Total sem coordenação: {len(sem_coord)}")
for c in sem_coord:
    # Busca o valor bruto do campo coordenação
    coord_val = None
    for campo in c["coord_raw"]:
        label = campo.get("field", {}).get("label") or campo.get("name", "")
        if label == "Coordenação":
            coord_val = campo.get("value")
    print(f"  - {c['id']} | {c['titulo']} | fase: {c['fase_atual']} | coord_raw: {coord_val}")

import json

with open('dados/cards_raw.json', encoding='utf-8') as f:
    cards = json.load(f)

IDS_PROBLEMAS = [
    "1314868539", "1269758103", "1324032565", "1241747373", "1241206398",
    "1255818251", "1257474940", "1265436682", "1189209373", "1259610954",
    "1324021924", "1201341268", "1241204289", "1253252152", "1289076022",
    "1296556665", "1194107128", "1217101137"
]

for card in cards:
    if str(card.get("id")) in IDS_PROBLEMAS:
        print(f"\n=== {card['id']} | {card['title']} ===")
        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name", "")
            valor = campo.get("value")
            print(f"  [{label}] = {valor}")
