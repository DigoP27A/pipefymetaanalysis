import requests
import json
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("PIPEFY_TOKEN")
PIPE_ID = os.getenv("PIPE_ID")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def buscar_cards(pipe_id):
    todos_cards = []
    cursor = None
    pagina = 1

    while True:
        print(f"Buscando página {pagina}...")
        after = f', after: "{cursor}"' if cursor else ""

        query = """
        {
          allCards(pipeId: %s, first: 50%s) {
            pageInfo {
              hasNextPage
              endCursor
            }
            edges {
              node {
                id
                title
                done
                expired
                due_date
                created_at
                updated_at
                current_phase {
                  name
                }
                assignees {
                  name
                  email
                }
                fields {
                  name
                  value
                  field {
                    label
                  }
                }
              }
            }
          }
        }
        """ % (pipe_id, after)

        response = requests.post(
            "https://api.pipefy.com/graphql",
            json={"query": query},
            headers=HEADERS
        )

        data = response.json()

        if "errors" in data:
            print("Erro na API:", data["errors"])
            break

        resultado = data["data"]["allCards"]
        cards = [edge["node"] for edge in resultado["edges"]]
        todos_cards.extend(cards)

        print(f"  → {len(cards)} cards encontrados nesta página | Total: {len(todos_cards)}")

        if not resultado["pageInfo"]["hasNextPage"]:
            break

        cursor = resultado["pageInfo"]["endCursor"]
        pagina += 1

    return todos_cards

def processar_cards(cards):
    linhas = []

    for card in cards:
        linha = {
            "id": card.get("id"),
            "titulo": card.get("title"),
            "fase_atual": card.get("current_phase", {}).get("name") if card.get("current_phase") else None,
            "fechado": card.get("done"),
            "expirado": card.get("expired"),
            "data_criacao": card.get("created_at"),
            "data_atualizacao": card.get("updated_at"),
            "data_vencimento": card.get("due_date"),
            "responsavel": ", ".join([a["name"] for a in card.get("assignees", [])]),
        }

        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name")
            valor = campo.get("value")
            if label:
                linha[label] = valor

        linhas.append(linha)

    return pd.DataFrame(linhas)

def classificar_fase(fase):
    if fase == "Venda":
        return "Venda"
    elif fase == "Perdido":
        return "Perda"
    elif fase == "Pausado":
        return "Pausado"
    else:
        return "Em andamento"

def analisar_objecoes(df):
    coluna_objecao = None
    for col in df.columns:
        if "obje" in col.lower():
            coluna_objecao = col
            break

    if not coluna_objecao:
        print("\n⚠️ Coluna de objeção não encontrada.")
        print("Colunas disponíveis:", list(df.columns))
        return

    # Classifica cada card
    df["resultado"] = df["fase_atual"].apply(classificar_fase)

    # Explode objeções múltiplas
    def parse_objecao(x):
        if not x or (isinstance(x, float)):
            return ["Sem objeção"]
        if isinstance(x, str) and x.startswith("["):
            return json.loads(x)
        return [x]

    df["objecao_lista"] = df[coluna_objecao].apply(parse_objecao)
    df_exploded = df.explode("objecao_lista")
    df_exploded["objecao_lista"] = df_exploded["objecao_lista"].str.strip()

    # Agrupa por objeção e resultado
    analise = df_exploded.groupby(["objecao_lista", "resultado"]).size().unstack(fill_value=0)

    # Garante que todas as colunas existam
    for col in ["Venda", "Perda", "Pausado", "Em andamento"]:
        if col not in analise.columns:
            analise[col] = 0

    analise = analise[["Venda", "Perda", "Pausado", "Em andamento"]]
    analise["Total"] = analise.sum(axis=1)
    analise["Taxa de Venda (%)"] = (analise["Venda"] / analise["Total"] * 100).round(1)
    analise = analise.sort_values("Total", ascending=False)

    print("\n📊 Análise de Objeções por Resultado")
    print("=" * 70)
    print(analise.to_string())

    analise.to_excel("dados/analise_objecoes.xlsx")
    print("\n✅ Relatório salvo em dados/analise_objecoes.xlsx")

def main():
    os.makedirs("dados", exist_ok=True)

    print(f"🚀 Iniciando extração do pipe {PIPE_ID}...\n")
    cards = buscar_cards(PIPE_ID)

    print(f"\n✅ Total de cards extraídos: {len(cards)}")

    with open("dados/cards_raw.json", "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print("💾 JSON salvo em dados/cards_raw.json")

    df = processar_cards(cards)
    df.to_csv("dados/cards.csv", index=False, encoding="utf-8-sig")
    print(f"💾 CSV salvo em dados/cards.csv ({len(df)} linhas, {len(df.columns)} colunas)")

    analisar_objecoes(df)

if __name__ == "__main__":
    main()