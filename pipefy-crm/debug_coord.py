import json

with open('dados/cards_raw.json', encoding='utf-8') as f:
    cards = json.load(f)

COORDENACOES = ["ACE", "CCE", "MNP", "PRO", "QAB"]
FASES_PROPOSTA = ["6. Proposta comercial feita", "7. Follow-up", "Venda"]

def parse_lista(x):
    if not x or isinstance(x, float): return []
    if isinstance(x, str) and x.startswith("["):
        try: return json.loads(x)
        except: return [x]
    return [x]

sem_coord = []
for card in cards:
    fases_visitadas = [ph.get("phase", {}).get("name") for ph in card.get("phases_history", [])]
    chegou_proposta = any(f in fases_visitadas for f in FASES_PROPOSTA)
    if not chegou_proposta:
        continue

    # Busca todos os campos que possam ter coordenação
    coord_fields = {}
    for campo in card.get("fields", []):
        label = campo.get("field", {}).get("label") or campo.get("name", "")
        valor = campo.get("value")
        if valor and any(c in str(valor) for c in COORDENACOES):
            coord_fields[label] = valor

    # Verifica se o campo Coordenação existe e qual seu valor
    coord_valor = None
    for campo in card.get("fields", []):
        label = campo.get("field", {}).get("label") or campo.get("name", "")
        if label == "Coordenação":
            coord_valor = campo.get("value")
            break

    coords_encontradas = [c.strip() for c in parse_lista(coord_valor) if c.strip() in COORDENACOES]

    if not coords_encontradas:
        sem_coord.append({
            "id": card.get("id"),
            "titulo": card.get("title"),
            "coord_valor_raw": coord_valor,
            "campos_com_coord": coord_fields,
        })

print(f"Total sem coordenação válida: {len(sem_coord)}\n")
for c in sem_coord:
    print(f"ID: {c['id']} | {c['titulo']}")
    print(f"  coord_raw: {c['coord_valor_raw']}")
    print(f"  outros campos com coord: {c['campos_com_coord']}")
    print()