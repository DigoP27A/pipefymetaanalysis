import requests
import json
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# CONFIGURAÇÃO
# ============================================================

class PipefyConfig:
    """Centraliza todas as configurações da conexão com o Pipefy."""

    API_URL = "https://api.pipefy.com/graphql"

    def __init__(self):
        self.token = os.getenv("PIPEFY_TOKEN")
        self.pipe_id = os.getenv("PIPE_ID")

        if not self.token:
            raise ValueError("PIPEFY_TOKEN não encontrado no .env")
        if not self.pipe_id:
            raise ValueError("PIPE_ID não encontrado no .env")

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }


# ============================================================
# EXTRATOR — responsável por buscar dados da API
# ============================================================

class PipefyExtractor:
    """Busca cards do Pipefy via GraphQL com paginação automática."""

    def __init__(self, config: PipefyConfig):
        self.config = config

    def _build_query(self, pipe_id, cursor=None):
        after = f', after: "{cursor}"' if cursor else ""
        return """
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
        """ % (pipe_id, after)

    def _fetch_page(self, pipe_id, cursor=None):
        query = self._build_query(pipe_id, cursor)
        response = requests.post(
            self.config.API_URL,
            json={"query": query},
            headers=self.config.headers
        )
        return response.json()

    def fetch_all_cards(self):
        """Busca todos os cards do pipe com paginação automática."""
        todos_cards = []
        cursor = None
        pagina = 1

        while True:
            print(f"Buscando página {pagina}...")
            data = self._fetch_page(self.config.pipe_id, cursor)

            if "errors" in data:
                print("Erro na API:", data["errors"])
                break

            resultado = data["data"]["allCards"]
            cards = [edge["node"] for edge in resultado["edges"]]
            todos_cards.extend(cards)

            print(f"  → {len(cards)} cards | Total acumulado: {len(todos_cards)}")

            if not resultado["pageInfo"]["hasNextPage"]:
                break

            cursor = resultado["pageInfo"]["endCursor"]
            pagina += 1

        print(f"\n✅ Total extraído: {len(todos_cards)} cards")
        return todos_cards


# ============================================================
# PROCESSADOR — transforma dados brutos em DataFrame
# ============================================================

class PipefyProcessor:
    """Transforma os cards brutos da API em um DataFrame estruturado."""

    FASES_VENDA = ["Venda"]
    FASES_PERDA = ["Perdido"]
    FASES_PAUSADO = ["Pausado"]

    def build_dataframe(self, cards: list) -> pd.DataFrame:
        """Converte lista de cards em DataFrame com todos os campos."""
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

        df = pd.DataFrame(linhas)
        df["resultado"] = df["fase_atual"].apply(self.classificar_resultado)
        return df

    def classificar_resultado(self, fase: str) -> str:
        """Classifica a fase do card em Venda, Perda, Pausado ou Em andamento."""
        if fase in self.FASES_VENDA:
            return "Venda"
        elif fase in self.FASES_PERDA:
            return "Perda"
        elif fase in self.FASES_PAUSADO:
            return "Pausado"
        else:
            return "Em andamento"

    @staticmethod
    def parse_campo_lista(valor) -> list:
        """Converte campos de seleção múltipla (JSON array) em lista Python."""
        if not valor or isinstance(valor, float):
            return ["Sem resposta"]
        if isinstance(valor, str) and valor.startswith("["):
            return json.loads(valor)
        return [valor]

    def explodir_coluna(self, df: pd.DataFrame, coluna: str) -> pd.DataFrame:
        """Expande uma coluna de listas em múltiplas linhas (uma por item)."""
        df = df.copy()
        df[coluna] = df[coluna].apply(self.parse_campo_lista)
        df = df.explode(coluna)
        df[coluna] = df[coluna].str.strip()
        return df


# ============================================================
# ANALISADOR — gera análises e relatórios
# ============================================================

class PipefyAnalyzer:
    """Gera análises e relatórios a partir do DataFrame processado."""

    RESULTADOS = ["Venda", "Perda", "Pausado", "Em andamento"]

    def __init__(self, processor: PipefyProcessor):
        self.processor = processor

    def _encontrar_coluna(self, df: pd.DataFrame, termo: str) -> str:
        """Busca uma coluna pelo nome aproximado."""
        for col in df.columns:
            if termo.lower() in col.lower():
                return col
        return None

    def _montar_tabela(self, df_exploded: pd.DataFrame, coluna: str) -> pd.DataFrame:
        """Monta tabela cruzada entre coluna e resultado."""
        analise = df_exploded.groupby([coluna, "resultado"]).size().unstack(fill_value=0)

        for col in self.RESULTADOS:
            if col not in analise.columns:
                analise[col] = 0

        analise = analise[self.RESULTADOS]
        analise["Total"] = analise.sum(axis=1)
        analise["Taxa de Venda (%)"] = (analise["Venda"] / analise["Total"] * 100).round(1)
        return analise.sort_values("Total", ascending=False)

    def analisar_objecoes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analisa objeções por resultado (Venda, Perda, Pausado, Em andamento)."""
        coluna = self._encontrar_coluna(df, "obje")
        if not coluna:
            print("⚠️ Coluna de objeção não encontrada.")
            return None

        df_exp = self.processor.explodir_coluna(df, coluna)
        analise = self._montar_tabela(df_exp, coluna)

        print("\n📊 Análise de Objeções por Resultado")
        print("=" * 70)
        print(analise.to_string())
        return analise

    def analisar_por_responsavel(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analisa resultados agrupados por responsável individual."""
        df = df.copy()
        
        # Separa múltiplos responsáveis em linhas individuais
        df["responsavel"] = df["responsavel"].apply(
            lambda x: [r.strip() for r in x.split(",")] if isinstance(x, str) and x else ["Sem responsável"]
        )
        df = df.explode("responsavel")
        df["responsavel"] = df["responsavel"].str.strip()

        analise = df.groupby(["responsavel", "resultado"]).size().unstack(fill_value=0)

        for col in self.RESULTADOS:
            if col not in analise.columns:
                analise[col] = 0

        analise = analise[self.RESULTADOS]
        analise["Total"] = analise.sum(axis=1)
        analise["Taxa de Venda (%)"] = (analise["Venda"] / analise["Total"] * 100).round(1)
        analise = analise.sort_values("Total", ascending=False)

        print("\n👤 Análise por Responsável Individual")
        print("=" * 70)
        print(analise.to_string())
        return analise
    def analisar_por_fase(self, df: pd.DataFrame) -> pd.DataFrame:
        """Conta quantos cards estão em cada fase."""
        analise = df.groupby("fase_atual").size().reset_index(name="total")
        analise = analise.sort_values("total", ascending=False)

        print("\n🔄 Distribuição por Fase")
        print("=" * 70)
        print(analise.to_string(index=False))
        return analise

    def analisar_coluna_personalizada(self, df: pd.DataFrame, termo: str) -> pd.DataFrame:
        """Analisa qualquer coluna do CRM por resultado. Passe parte do nome da coluna."""
        coluna = self._encontrar_coluna(df, termo)
        if not coluna:
            print(f"⚠️ Coluna com termo '{termo}' não encontrada.")
            print("Colunas disponíveis:", list(df.columns))
            return None

        df_exp = self.processor.explodir_coluna(df, coluna)
        analise = self._montar_tabela(df_exp, coluna)

        print(f"\n📊 Análise por '{coluna}'")
        print("=" * 70)
        print(analise.to_string())
        return analise


# ============================================================
# EXPORTADOR — salva arquivos
# ============================================================

class PipefyExporter:
    """Salva os dados e relatórios em diferentes formatos."""

    def __init__(self, pasta_saida: str = "dados"):
        self.pasta_saida = pasta_saida
        os.makedirs(pasta_saida, exist_ok=True)

    def salvar_json(self, cards: list, nome: str = "cards_raw.json"):
        caminho = os.path.join(self.pasta_saida, nome)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(cards, f, ensure_ascii=False, indent=2)
        print(f"💾 JSON salvo em {caminho}")

    def salvar_csv(self, df: pd.DataFrame, nome: str = "cards.csv"):
        caminho = os.path.join(self.pasta_saida, nome)
        df.to_csv(caminho, index=False, encoding="utf-8-sig")
        print(f"💾 CSV salvo em {caminho} ({len(df)} linhas, {len(df.columns)} colunas)")

    def salvar_excel(self, df: pd.DataFrame, nome: str = "relatorio.xlsx"):
        caminho = os.path.join(self.pasta_saida, nome)
        df.to_excel(caminho)
        print(f"💾 Excel salvo em {caminho}")

    def salvar_multiplas_abas(self, relatorios: dict, nome: str = "relatorio_completo.xlsx"):
        """Salva múltiplos DataFrames em abas diferentes de um mesmo Excel."""
        caminho = os.path.join(self.pasta_saida, nome)
        with pd.ExcelWriter(caminho, engine="openpyxl") as writer:
            for aba, df in relatorios.items():
                if df is not None:
                    df.to_excel(writer, sheet_name=aba)
        print(f"💾 Relatório completo salvo em {caminho}")


# ============================================================
# PIPELINE PRINCIPAL
# ============================================================

def main():
    # Inicializa componentes
    config = PipefyConfig()
    extractor = PipefyExtractor(config)
    processor = PipefyProcessor()
    analyzer = PipefyAnalyzer(processor)
    exporter = PipefyExporter()

    # 1. Extrai todos os cards
    print(f"🚀 Iniciando extração do pipe {config.pipe_id}...\n")
    cards = extractor.fetch_all_cards()

    # 2. Salva dados brutos
    exporter.salvar_json(cards)

    # 3. Processa em DataFrame
    df = processor.build_dataframe(cards)
    exporter.salvar_csv(df)

    # 4. Análises
    analise_objecoes = analyzer.analisar_objecoes(df)
    analise_responsavel = analyzer.analisar_por_responsavel(df)
    analise_fases = analyzer.analisar_por_fase(df)

    # 5. Salva relatório completo com múltiplas abas
    exporter.salvar_multiplas_abas({
        "Objeções": analise_objecoes,
        "Por Responsável": analise_responsavel,
        "Por Fase": analise_fases,
    }, nome="relatorio_completo.xlsx")


if __name__ == "__main__":
    main()