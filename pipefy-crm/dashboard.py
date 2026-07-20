import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from pathlib import Path

# Diretório do próprio script — necessário porque o Streamlit Cloud roda com
# cwd na raiz do repo, não em pipefy-crm/. Todos os caminhos de dados/assets
# devem ser resolvidos a partir daqui.
BASE_DIR = Path(__file__).parent
CARDS_RAW_PATH = BASE_DIR / "dados" / "cards_raw.json"

st.set_page_config(page_title="Fluxo Consultoria — CRM", layout="wide", page_icon="🟧")

# ============================================================
# TEMA — FLUXO (PRETO + LARANJA)
# ============================================================

FLUXO_ORANGE = "#F7941D"
FLUXO_ORANGE_LIGHT = "#FFB454"
FLUXO_ORANGE_DARK = "#C67615"
BG_BLACK = "#0A0A0A"
BG_CARD = "#141414"
BG_CARD_ELEVATED = "#1C1C1C"
BORDER = "#262626"
BORDER_LIGHT = "#3A3A3A"
TEXT_PRIMARY = "#FAFAFA"
TEXT_SECONDARY = "#A3A3A3"
TEXT_MUTED = "#737373"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    * {{ font-family: 'Inter', sans-serif; }}
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

    .stApp {{
        background:
            radial-gradient(1200px 600px at 85% -10%, rgba(247,148,29,0.06), transparent 60%),
            radial-gradient(900px 500px at -10% 100%, rgba(247,148,29,0.04), transparent 60%),
            {BG_BLACK};
    }}

    /* SIDEBAR */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0d0d0d 0%, {BG_BLACK} 100%);
        border-right: 1px solid {BORDER};
    }}
    section[data-testid="stSidebar"] * {{ color: {TEXT_PRIMARY} !important; }}
    section[data-testid="stSidebar"] .stRadio label {{ color: {TEXT_PRIMARY} !important; font-size: 14px !important; }}

    /* Radio menu de navegação — highlight laranja no selecionado */
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
        padding: 10px 12px;
        border-radius: 10px;
        margin: 2px 0;
        border: 1px solid transparent;
        transition: all 0.15s ease;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{
        background: rgba(247,148,29,0.08);
        border-color: rgba(247,148,29,0.25);
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {{
        background: linear-gradient(90deg, rgba(247,148,29,0.18), rgba(247,148,29,0.05));
        border-color: {FLUXO_ORANGE};
        box-shadow: inset 3px 0 0 {FLUXO_ORANGE};
    }}

    /* TIPOGRAFIA */
    h1, h2, h3, h4, h5, h6 {{ color: {TEXT_PRIMARY}; letter-spacing: -0.01em; }}
    h1 {{ font-weight: 800; }}
    p, span, div {{ color: {TEXT_PRIMARY}; }}

    /* TABELAS */
    .stDataFrame {{ background: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER}; }}
    .stDataFrame th {{
        background: #1F1F1F !important;
        color: {FLUXO_ORANGE} !important;
        font-weight: 600 !important;
        border-bottom: 1px solid {BORDER_LIGHT} !important;
        text-transform: uppercase;
        font-size: 12px !important;
        letter-spacing: 0.04em;
    }}
    .stDataFrame td {{ color: {TEXT_PRIMARY} !important; }}

    /* MÉTRICAS DO STREAMLIT (fallback) */
    div[data-testid="stMetric"] {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 18px;
    }}
    div[data-testid="stMetric"] label {{ color: {TEXT_SECONDARY} !important; }}
    div[data-testid="stMetric"] div {{ color: {TEXT_PRIMARY} !important; }}

    /* SELECTBOX */
    .stSelectbox label, .stMultiSelect label {{ color: {TEXT_PRIMARY} !important; font-size: 13px !important; font-weight: 500; }}
    div[data-baseweb="select"] {{ background-color: {BG_CARD} !important; }}
    div[data-baseweb="select"] > div {{
        background-color: {BG_CARD} !important;
        border-color: {BORDER_LIGHT} !important;
        border-radius: 10px !important;
        transition: border-color 0.15s;
    }}
    div[data-baseweb="select"] > div:hover {{ border-color: {FLUXO_ORANGE} !important; }}
    div[data-baseweb="select"] * {{ color: {TEXT_PRIMARY} !important; }}
    div[data-baseweb="select"] svg {{ fill: {FLUXO_ORANGE} !important; }}

    /* DROPDOWN ABERTO */
    div[data-baseweb="popover"] * {{ background-color: {BG_CARD_ELEVATED} !important; }}
    div[data-baseweb="popover"] > div {{ border: 1px solid {BORDER_LIGHT} !important; border-radius: 12px !important; overflow: hidden !important; }}
    ul[data-baseweb="menu"] {{ background-color: {BG_CARD_ELEVATED} !important; padding: 6px !important; }}
    ul[data-baseweb="menu"] li {{ background-color: {BG_CARD_ELEVATED} !important; color: {TEXT_PRIMARY} !important; border-radius: 8px !important; margin: 2px 0 !important; }}
    ul[data-baseweb="menu"] li:hover {{ background-color: rgba(247,148,29,0.15) !important; color: #fff !important; }}
    ul[data-baseweb="menu"] li[aria-selected="true"] {{ background-color: {FLUXO_ORANGE} !important; color: #000 !important; font-weight: 600; }}
    div[role="option"] {{ background-color: {BG_CARD_ELEVATED} !important; color: {TEXT_PRIMARY} !important; }}
    div[role="option"]:hover {{ background-color: rgba(247,148,29,0.15) !important; }}
    div[role="option"] * {{ color: {TEXT_PRIMARY} !important; background-color: transparent !important; }}

    /* SCROLLBAR */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: {BG_BLACK}; }}
    ::-webkit-scrollbar-thumb {{ background: {BORDER_LIGHT}; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {FLUXO_ORANGE_DARK}; }}

    .stSlider label {{ color: {TEXT_PRIMARY} !important; }}
    .stSlider [role="slider"] {{ background-color: {FLUXO_ORANGE} !important; border-color: {FLUXO_ORANGE} !important; }}
    .stSlider div[data-baseweb="slider"] > div > div > div {{ background: {FLUXO_ORANGE} !important; }}

    /* RADIO HORIZONTAL — chips */
    div[data-testid="stHorizontalBlock"] div[role="radiogroup"] label {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        padding: 8px 14px;
        border-radius: 999px;
        margin-right: 6px;
        transition: all 0.15s;
    }}
    div[data-testid="stHorizontalBlock"] div[role="radiogroup"] label:hover {{
        border-color: {FLUXO_ORANGE};
    }}
    div[data-testid="stHorizontalBlock"] div[role="radiogroup"] label[data-checked="true"] {{
        background: {FLUXO_ORANGE};
        border-color: {FLUXO_ORANGE};
        color: #000 !important;
        font-weight: 600;
    }}
    div[data-testid="stHorizontalBlock"] div[role="radiogroup"] label[data-checked="true"] * {{
        color: #000 !important;
    }}

    hr {{ border-color: {BORDER}; }}

    /* CARD DE MÉTRICA CUSTOMIZADO */
    .metric-card {{
        background: linear-gradient(180deg, {BG_CARD} 0%, #101010 100%);
        border: 1px solid {BORDER};
        border-top: 3px solid {FLUXO_ORANGE};
        border-radius: 14px;
        padding: 22px 20px;
        text-align: left;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
        border-bottom-color: {BORDER_LIGHT};
        border-left-color: {BORDER_LIGHT};
        border-right-color: {BORDER_LIGHT};
        box-shadow: 0 10px 30px rgba(0,0,0,0.4), 0 0 20px rgba(247,148,29,0.08);
    }}
    .metric-card .label {{
        color: {TEXT_SECONDARY};
        font-size: 11.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 10px;
    }}
    .metric-card .value {{
        color: {TEXT_PRIMARY};
        font-size: 34px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 6px;
        letter-spacing: -0.02em;
    }}
    .metric-card .sub {{
        color: {TEXT_MUTED};
        font-size: 12px;
    }}

    .section-title {{
        color: {TEXT_PRIMARY};
        font-size: 17px;
        font-weight: 700;
        margin: 26px 0 14px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid {BORDER};
        letter-spacing: -0.01em;
        display: flex;
        align-items: center;
    }}
    .section-title::before {{
        content: '';
        display: inline-block;
        width: 4px;
        height: 18px;
        background: {FLUXO_ORANGE};
        margin-right: 10px;
        border-radius: 2px;
    }}

    .info-box {{
        background: rgba(247,148,29,0.08);
        border: 1px solid rgba(247,148,29,0.35);
        border-left: 3px solid {FLUXO_ORANGE};
        border-radius: 10px;
        padding: 14px 18px;
        color: #FBD9A9;
        font-size: 13px;
        margin-bottom: 20px;
    }}

    .tag {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
        margin: 2px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* HEADER PRINCIPAL DA PÁGINA */
    .page-header {{
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 4px;
    }}
    .page-header .icon {{
        width: 44px; height: 44px;
        background: linear-gradient(135deg, {FLUXO_ORANGE} 0%, {FLUXO_ORANGE_DARK} 100%);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px;
        color: #000;
    }}
    .page-header h1 {{
        margin: 0 !important;
        font-size: 30px;
        color: {TEXT_PRIMARY} !important;
    }}
    .page-sub {{ color: {TEXT_SECONDARY}; margin: 4px 0 24px 60px; font-size: 14px; }}

    /* Botão default */
    .stButton > button {{
        background: {FLUXO_ORANGE};
        color: #000;
        border: none;
        font-weight: 600;
        border-radius: 10px;
        padding: 10px 20px;
        transition: all 0.15s;
    }}
    .stButton > button:hover {{
        background: {FLUXO_ORANGE_LIGHT};
        transform: translateY(-1px);
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# LAYOUT PLOTLY BASE — TEMA FLUXO
# ============================================================

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_PRIMARY, family="Inter"),
    xaxis=dict(gridcolor=BORDER, linecolor=BORDER_LIGHT, tickcolor=TEXT_SECONDARY, tickfont=dict(color=TEXT_SECONDARY)),
    yaxis=dict(gridcolor=BORDER, linecolor=BORDER_LIGHT, tickcolor=TEXT_SECONDARY, tickfont=dict(color=TEXT_SECONDARY)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_PRIMARY)),
    margin=dict(t=40, b=40, l=20, r=20),
)

# Cores semânticas de resultado — mantém verde/vermelho para clareza; laranja é a cor de marca
CORES = {
    "Venda": "#22c55e",
    "Perda": "#EF4444",
    "Pausado": "#EAB308",
    "Em andamento": FLUXO_ORANGE,
}

# Escalas contínuas laranja para gráficos com cor por magnitude
SCALE_ORANGE = ["#2A1608", "#7A4310", FLUXO_ORANGE, "#FFC97A"]
SCALE_ORANGE_SOFT = ["#1a1a1a", "#4a2c10", FLUXO_ORANGE, FLUXO_ORANGE_LIGHT]

ORDEM_FASES = [
    "2. Contato aberto",
    "3. Pré-diagnóstico feito",
    "4. Diagnóstico feito",
    "5. Precificação/Aprovação em andamento",
    "6. Proposta comercial feita",
    "7. Follow-up",
    "Venda"
]

# ============================================================
# HELPERS DE UI
# ============================================================

def page_header(icon: str, titulo: str, subtitulo: str = ""):
    st.markdown(f"""
    <div class="page-header">
        <div class="icon">{icon}</div>
        <h1>{titulo}</h1>
    </div>
    <div class="page-sub">{subtitulo}</div>
    """, unsafe_allow_html=True)

# ============================================================
# CICLOS / GESTÕES DA FLUXO
# ============================================================
# Gestão = 12 meses começando em 1º de outubro (ex: gestão 25/26 = out/2025–set/2026).
# Cada gestão tem 4 ciclos de 3 meses:
#   Ciclo 1: out–dez   Ciclo 2: jan–mar   Ciclo 3: abr–jun   Ciclo 4: jul–set

FASES_TERMINAIS = ("Perdido", "Venda", "Pausado")

def gestao_de(data):
    """Retorna a gestão de uma data no formato 'YY/YY' (ex: '25/26')."""
    if pd.isna(data):
        return None
    ano, mes = data.year, data.month
    if mes >= 10:
        return f"{ano % 100:02d}/{(ano + 1) % 100:02d}"
    return f"{(ano - 1) % 100:02d}/{ano % 100:02d}"

def ciclo_de(data):
    """Retorna o número do ciclo (1–4) dentro da gestão."""
    if pd.isna(data):
        return None
    m = data.month
    if m in (10, 11, 12): return 1
    if m in (1, 2, 3):    return 2
    if m in (4, 5, 6):    return 3
    return 4  # 7, 8, 9

def _data_referencia_do_card(card):
    """Data-âncora do card para filtro por período:
    - se está em Perdido/Venda/Pausado: primeira entrada nessa fase terminal
    - senão: data de criação do card
    """
    fase = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
    if fase in FASES_TERMINAIS:
        entradas = [
            ph.get("firstTimeIn")
            for ph in card.get("phases_history", [])
            if ph.get("phase", {}).get("name") == fase and ph.get("firstTimeIn")
        ]
        if entradas:
            return max(entradas)
    return card.get("created_at")

# ============================================================
# DADOS
# ============================================================

@st.cache_data
def carregar_dados():
    with open(CARDS_RAW_PATH, encoding="utf-8") as f:
        cards = json.load(f)

    linhas = []
    for card in cards:
        linha = {
            "id": card.get("id"),
            "titulo": card.get("title"),
            "fase_atual": card.get("current_phase", {}).get("name") if card.get("current_phase") else None,
            "fechado": card.get("done"),
            "data_criacao": card.get("created_at"),
            "data_atualizacao": card.get("updated_at"),
            "data_referencia": _data_referencia_do_card(card),
            "responsavel_raw": ", ".join([a["name"] for a in card.get("assignees", [])]),
        }
        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name")
            valor = campo.get("value")
            if label:
                linha[label] = valor
        linhas.append(linha)

    df = pd.DataFrame(linhas)
    df["resultado"] = df["fase_atual"].apply(classificar_resultado)
    df["data_criacao"] = pd.to_datetime(df["data_criacao"], errors="coerce", utc=True).dt.tz_localize(None)
    df["data_atualizacao"] = pd.to_datetime(df["data_atualizacao"], errors="coerce", utc=True).dt.tz_localize(None)
    df["data_referencia"] = pd.to_datetime(df["data_referencia"], errors="coerce", utc=True).dt.tz_localize(None)
    df["gestao"] = df["data_referencia"].apply(gestao_de)
    df["ciclo"] = df["data_referencia"].apply(ciclo_de)
    return df


def classificar_resultado(fase):
    if fase == "Venda": return "Venda"
    elif fase == "Perdido": return "Perda"
    elif fase == "Pausado": return "Pausado"
    else: return "Em andamento"

def parse_objecao(x):
    if not x or isinstance(x, float): return ["Sem resposta"]
    if isinstance(x, str) and x.startswith("["): return json.loads(x)
    return [x]

def explodir_responsaveis(df):
    df = df.copy()
    df["responsavel"] = df["responsavel_raw"].apply(
        lambda x: [r.strip() for r in x.split(",")] if isinstance(x, str) and x else ["Sem responsável"]
    )
    return df.explode("responsavel")

# ============================================================
# PÁGINAS
# ============================================================

def pagina_visao_geral(df):
    st.markdown("<h1 style='color:#FAFAFA;margin-bottom:4px'>📊 Visão Geral</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;margin-bottom:24px'>Panorama completo do CRM Fluxo</p>", unsafe_allow_html=True)

    total = len(df)
    vendas = len(df[df["resultado"] == "Venda"])
    perdas = len(df[df["resultado"] == "Perda"])
    pausados = len(df[df["resultado"] == "Pausado"])
    andamento = len(df[df["resultado"] == "Em andamento"])
    taxa = round(vendas / total * 100, 1) if total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "Total de Leads", total, "todos os cards", FLUXO_ORANGE),
        (c2, "Vendas", vendas, f"{taxa}% de conversão", "#22c55e"),
        (c3, "Perdidos", perdas, f"{round(perdas/total*100,1)}% do total", "#ef4444"),
        (c4, "Pausados", pausados, f"{round(pausados/total*100,1)}% do total", "#f59e0b"),
        (c5, "Em Andamento", andamento, f"{round(andamento/total*100,1)}% do total", FLUXO_ORANGE_LIGHT),
    ]
    for col, label, val, sub, cor in cards:
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid {cor}">
                <div class="label">{label}</div>
                <div class="value" style="color:{cor}">{val}</div>
                <div class="sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.6])

    with c1:
        st.markdown("<div class='section-title'>Distribuição por Resultado</div>", unsafe_allow_html=True)
        contagem = df["resultado"].value_counts().reset_index()
        contagem.columns = ["Resultado", "Total"]
        fig = px.pie(contagem, names="Resultado", values="Total",
                     color="Resultado", color_discrete_map=CORES, hole=0.5)
        fig.update_traces(textfont_color="white", textfont_size=13)
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("<div class='section-title'>Cards por Fase Atual</div>", unsafe_allow_html=True)
        fases = df["fase_atual"].value_counts().reset_index()
        fases.columns = ["Fase", "Total"]
        fig = px.bar(fases, x="Total", y="Fase", orientation="h",
                     color="Total", color_continuous_scale=SCALE_ORANGE,
                     text="Total")
        fig.update_traces(textfont_color="white", textposition="outside")
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig.update_yaxes(categoryorder="total ascending", gridcolor="#262626", tickfont=dict(color="#FAFAFA"))
        st.plotly_chart(fig, use_container_width=True)


def pagina_objecoes(df):
    st.markdown("<h1 style='color:#FAFAFA;margin-bottom:4px'>🚧 Análise de Objeções</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;margin-bottom:24px'>Como cada objeção impacta o resultado do lead</p>", unsafe_allow_html=True)

    coluna_objecao = next((c for c in df.columns if "obje" in c.lower()), None)
    if not coluna_objecao:
        st.error("Coluna de objeção não encontrada.")
        return

    df_exp = df.copy()
    df_exp["objecao"] = df_exp[coluna_objecao].apply(parse_objecao)
    df_exp = df_exp.explode("objecao")
    df_exp["objecao"] = df_exp["objecao"].str.strip()

    analise = df_exp.groupby(["objecao", "resultado"]).size().unstack(fill_value=0)
    for col in CORES:
        if col not in analise.columns:
            analise[col] = 0
    analise = analise[list(CORES.keys())]
    analise["Total"] = analise.sum(axis=1)
    analise["Taxa de Venda (%)"] = (analise["Venda"] / analise["Total"] * 100).round(1)
    analise = analise.sort_values("Total", ascending=False).reset_index()
    analise_sem_sem = analise[analise["objecao"] != "Sem resposta"]

    # KPIs de objeções
    total_com_obj = analise_sem_sem["Total"].sum()
    obj_mais_comum = analise_sem_sem.iloc[0]["objecao"] if len(analise_sem_sem) else "-"
    melhor_taxa = analise_sem_sem.loc[analise_sem_sem["Taxa de Venda (%)"].idxmax(), "objecao"] if len(analise_sem_sem) else "-"

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #ef4444">
            <div class="label">Leads com Objeção</div>
            <div class="value" style="color:#ef4444">{int(total_com_obj)}</div>
            <div class="sub">do total de leads</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #f59e0b">
            <div class="label">Objeção Mais Comum</div>
            <div class="value" style="color:#f59e0b;font-size:20px">{obj_mais_comum}</div>
            <div class="sub">&nbsp;</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #22c55e">
            <div class="label">Melhor Taxa de Venda</div>
            <div class="value" style="color:#22c55e;font-size:20px">{melhor_taxa}</div>
            <div class="sub">&nbsp;</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Volume por Objeção e Resultado</div>", unsafe_allow_html=True)

    df_melt = analise[analise["objecao"] != "Sem resposta"].melt(id_vars="objecao", value_vars=list(CORES.keys()), var_name="Resultado", value_name="Leads")
    fig = px.bar(df_melt, x="objecao", y="Leads", color="Resultado",
             color_discrete_map=CORES, barmode="stack",
             labels={"objecao": ""})
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-20)
    st.plotly_chart(fig, use_container_width=True, key="obj_volume")

    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("<div class='section-title'>Taxa de Venda por Objeção</div>", unsafe_allow_html=True)
        fig2 = px.bar(analise_sem_sem.sort_values("Taxa de Venda (%)"),
                      x="Taxa de Venda (%)", y="objecao", orientation="h",
                      color="Taxa de Venda (%)",
                      color_continuous_scale=["#1c3a1c", "#16a34a", "#86efac"],
                      text="Taxa de Venda (%)",
                      labels={"objecao": ""})
        fig2.update_traces(texttemplate="%{text}%", textfont_color="white")
        fig2.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True, key="obj_taxa")

    with c2:
        st.markdown("<div class='section-title'>Tabela Detalhada</div>", unsafe_allow_html=True)
        st.dataframe(
            analise.set_index("objecao").style
                .background_gradient(subset=["Taxa de Venda (%)"], cmap="Greens")
                .format({"Taxa de Venda (%)": "{:.1f}%"}),
            use_container_width=True, height=350
        )

# -------------------------------------------------------
    # ANÁLISE DE LEADS QUALIFICADOS
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<h3 style='color:#FAFAFA'>🎯 Análise de Leads Qualificados</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Apenas cards que chegaram até Diagnóstico, Precificação/Aprovação ou Proposta Comercial — excluindo desqualificados precoces.</p>", unsafe_allow_html=True)

    FASES_QUALIFICADAS = [
        "4. Diagnóstico feito",
        "5. Precificação/Aprovação em andamento",
        "6. Proposta comercial feita",
        "7. Follow-up",
        "Venda",
        "Pausado",
        "Perdido",
    ]

    # Carrega histórico para saber quais cards passaram por diagnóstico ou além
    with open(CARDS_RAW_PATH, encoding="utf-8") as f:
        cards_raw_obj = json.load(f)

    ids_qualificados = set()
    for card in cards_raw_obj:
        fases_visitadas = [
            ph.get("phase", {}).get("name")
            for ph in card.get("phases_history", [])
        ]
        passou_diagnostico = any(
            f in fases_visitadas for f in [
                "4. Diagnóstico feito",
                "5. Precificação/Aprovação em andamento",
                "6. Proposta comercial feita",
                "7. Follow-up",
                "Venda",
            ]
        )
        if passou_diagnostico:
            ids_qualificados.add(str(card.get("id")))

    df_qual = df[df["id"].astype(str).isin(ids_qualificados)].copy()

    total_qual = len(df_qual)
    vendas_qual = len(df_qual[df_qual["resultado"] == "Venda"])
    taxa_qual = round(vendas_qual / total_qual * 100, 1) if total_qual else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #3b82f6">
            <div class="label">Leads Qualificados</div>
            <div class="value" style="color:#3b82f6">{total_qual}</div>
            <div class="sub">chegaram até Diagnóstico ou além</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #22c55e">
            <div class="label">Vendas entre Qualificados</div>
            <div class="value" style="color:#22c55e">{vendas_qual}</div>
            <div class="sub">{taxa_qual}% de conversão</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #8b5cf6">
            <div class="label">Excluídos da Análise</div>
            <div class="value" style="color:#8b5cf6">{len(df) - total_qual}</div>
            <div class="sub">desqualificados antes do diagnóstico</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Análise de objeções apenas nos qualificados
    df_qual_exp = df_qual.copy()
    df_qual_exp["objecao"] = df_qual_exp[coluna_objecao].apply(parse_objecao)
    df_qual_exp = df_qual_exp.explode("objecao")
    df_qual_exp["objecao"] = df_qual_exp["objecao"].str.strip()
    df_qual_exp = df_qual_exp[df_qual_exp["objecao"] != "Sem resposta"]

    analise_qual = df_qual_exp.groupby(["objecao", "resultado"]).size().unstack(fill_value=0)
    for col in CORES:
        if col not in analise_qual.columns:
            analise_qual[col] = 0
    analise_qual = analise_qual[list(CORES.keys())]
    analise_qual["Total"] = analise_qual.sum(axis=1)
    analise_qual["Taxa de Venda (%)"] = (analise_qual["Venda"] / analise_qual["Total"] * 100).round(1)
    analise_qual = analise_qual.sort_values("Total", ascending=False).reset_index()

    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.markdown("<div class='section-title'>Objeções nos Leads Qualificados — Volume por Resultado</div>", unsafe_allow_html=True)
        df_melt_qual = analise_qual.melt(id_vars="objecao", value_vars=list(CORES.keys()), var_name="Resultado", value_name="Leads")
        fig_qual = px.bar(df_melt_qual, x="objecao", y="Leads", color="Resultado",
                          color_discrete_map=CORES, barmode="stack",
                          labels={"objecao": ""})
        fig_qual.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-20)
        st.plotly_chart(fig_qual, use_container_width=True, key="obj_qual")

    with c2:
        st.markdown("<div class='section-title'>Taxa de Venda — Apenas Qualificados</div>", unsafe_allow_html=True)
        st.dataframe(
            analise_qual.set_index("objecao").style
                .background_gradient(subset=["Taxa de Venda (%)"], cmap="Greens")
                .format({"Taxa de Venda (%)": "{:.1f}%"}),
            use_container_width=True, height=320
        )
def pagina_responsaveis(df):
    st.markdown("<h1 style='color:#FAFAFA;margin-bottom:4px'>👤 Análise por Responsável</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;margin-bottom:24px'>Performance individual de cada membro do time</p>", unsafe_allow_html=True)

    df_exp = explodir_responsaveis(df)
    df_exp = df_exp[df_exp["responsavel"] != "Sem responsável"]

    analise = df_exp.groupby(["responsavel", "resultado"]).size().unstack(fill_value=0)
    for col in CORES:
        if col not in analise.columns:
            analise[col] = 0
    analise = analise[list(CORES.keys())]
    analise["Total"] = analise.sum(axis=1)
    analise["Taxa de Venda (%)"] = (analise["Venda"] / analise["Total"] * 100).round(1)
    analise = analise.sort_values("Total", ascending=False).reset_index()

    c1, c2 = st.columns([2, 1])
    with c1:
        min_cards = st.slider("Filtrar responsáveis com mínimo de cards:", 1, 30, 5)
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#A3A3A3;font-size:13px'>{len(analise[analise['Total'] >= min_cards])} pessoas exibidas</p>", unsafe_allow_html=True)

    analise_f = analise[analise["Total"] >= min_cards]

    st.markdown("<div class='section-title'>Volume de Cards por Pessoa</div>", unsafe_allow_html=True)
    df_melt = analise_f.melt(id_vars="responsavel", value_vars=list(CORES.keys()), var_name="Resultado", value_name="Leads")
    fig = px.bar(df_melt, x="responsavel", y="Leads", color="Resultado",
             color_discrete_map=CORES, barmode="stack",
             labels={"responsavel": ""})
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("<div class='section-title'>Taxa de Venda por Pessoa</div>", unsafe_allow_html=True)
        fig2 = px.bar(analise_f.sort_values("Taxa de Venda (%)"),
                      x="Taxa de Venda (%)", y="responsavel", orientation="h",
                      color="Taxa de Venda (%)",
                      color_continuous_scale=["#1c3a1c", "#16a34a", "#86efac"],
                      text="Taxa de Venda (%)",
                      labels={"responsavel": ""})
        fig2.update_traces(texttemplate="%{text}%", textfont_color="white")
        fig2.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.markdown("<div class='section-title'>Tabela Detalhada</div>", unsafe_allow_html=True)
        st.dataframe(
            analise_f.set_index("responsavel").style
                .background_gradient(subset=["Taxa de Venda (%)"], cmap="Greens")
                .format({"Taxa de Venda (%)": "{:.1f}%"}),
            use_container_width=True, height=400
        )

    st.markdown("---")
    st.markdown("<div class='section-title'>🔎 Funil Individual por Responsável</div>", unsafe_allow_html=True)
    pessoas = sorted(analise_f["responsavel"].tolist())
    pessoa_sel = st.selectbox("Selecione um responsável:", pessoas)

    df_pessoa = df_exp[df_exp["responsavel"] == pessoa_sel]
    total_pessoa = len(df_pessoa)
    vendas_pessoa = len(df_pessoa[df_pessoa["resultado"] == "Venda"])
    perdas_pessoa = len(df_pessoa[df_pessoa["resultado"] == "Perda"])
    pausados_pessoa = len(df_pessoa[df_pessoa["resultado"] == "Pausado"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #3b82f6">
            <div class="label">Total</div><div class="value" style="color:#3b82f6">{total_pessoa}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #22c55e">
            <div class="label">Vendas</div><div class="value" style="color:#22c55e">{vendas_pessoa}</div>
            <div class="sub">{round(vendas_pessoa/total_pessoa*100,1) if total_pessoa else 0}%</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #ef4444">
            <div class="label">Perdidos</div><div class="value" style="color:#ef4444">{perdas_pessoa}</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #f59e0b">
            <div class="label">Pausados</div><div class="value" style="color:#f59e0b">{pausados_pessoa}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    dados_funil = []
    for fase in ORDEM_FASES:
        total_fase = len(df_pessoa[df_pessoa["fase_atual"] == fase])
        dados_funil.append({"Fase": fase.split(". ")[-1] if ". " in fase else fase, "Total": total_fase})

    df_funil = pd.DataFrame(dados_funil)
    fig3 = px.funnel(df_funil, x="Total", y="Fase",
                     color_discrete_sequence=[FLUXO_ORANGE])
    fig3.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)


def pagina_tempo_fases(df_original):
    st.markdown("<h1 style='color:#FAFAFA;margin-bottom:4px'>⏱️ Tempo entre Fases</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;margin-bottom:24px'>Tempo real que cada lead passou em cada etapa do funil</p>", unsafe_allow_html=True)

    # Carrega dados brutos para pegar phases_history
    with open(CARDS_RAW_PATH, encoding="utf-8") as f:
        cards = json.load(f)

    FASES_COM_OPO = [
        "1. Oportunidade",
        "2. Contato aberto",
        "3. Pré-diagnóstico feito",
        "4. Diagnóstico feito",
        "5. Precificação/Aprovação em andamento",
        "6. Proposta comercial feita",
        "7. Follow-up",
    ]
    FASES_SEM_OPO = [f for f in FASES_COM_OPO if f != "1. Oportunidade"]

    # Monta DataFrame de histórico
    linhas = []
    for card in cards:
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        resultado = classificar_resultado(fase_atual)
        for ph in card.get("phases_history", []):
            fase = ph.get("phase", {}).get("name")
            duration = ph.get("duration")
            if fase and duration is not None:
                linhas.append({
                    "card_id": card.get("id"),
                    "fase": fase,
                    "resultado": resultado,
                    "duracao_seg": duration,
                    "duracao_dias": round(duration / 86400, 2),
                    "duracao_horas": round(duration / 3600, 2),
                })

    df_hist = pd.DataFrame(linhas)

    if df_hist.empty:
        st.error("Nenhum dado de histórico encontrado. Rode o extrator.py novamente.")
        return

    # Toggle com/sem oportunidade
    st.markdown("<br>", unsafe_allow_html=True)
    col_toggle, _ = st.columns([1, 3])
    with col_toggle:
        incluir_opo = st.toggle("Incluir fase 'Oportunidade'", value=False)

    fases_filtro = FASES_COM_OPO if incluir_opo else FASES_SEM_OPO
    fases_limpas = {f: f.split(". ")[-1] if ". " in f else f for f in fases_filtro}

    df_filtrado = df_hist[df_hist["fase"].isin(fases_filtro)].copy()
    df_filtrado["fase_limpa"] = df_filtrado["fase"].map(fases_limpas)
    ordem_limpas = [fases_limpas[f] for f in fases_filtro if f in fases_limpas]

    # Agrupamento
    tempo_fase = df_filtrado.groupby("fase_limpa")["duracao_dias"].agg(
        Media="mean", Mediana="median", Total="count"
    ).reset_index()
    tempo_fase.columns = ["Fase", "Média (dias)", "Mediana (dias)", "Cards"]
    tempo_fase["Média (dias)"] = tempo_fase["Média (dias)"].round(1)
    tempo_fase["Mediana (dias)"] = tempo_fase["Mediana (dias)"].round(1)
    tempo_fase["Média (horas)"] = (tempo_fase["Média (dias)"] * 24).round(1)
    tempo_fase = tempo_fase.set_index("Fase").reindex(ordem_limpas).dropna().reset_index()

    # KPIs
    fase_mais_lenta = tempo_fase.loc[tempo_fase["Média (dias)"].idxmax(), "Fase"] if len(tempo_fase) else "-"
    fase_mais_rapida = tempo_fase.loc[tempo_fase["Média (dias)"].idxmin(), "Fase"] if len(tempo_fase) else "-"
    media_geral = round(tempo_fase["Média (dias)"].mean(), 1) if len(tempo_fase) else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #ef4444">
            <div class="label">Fase Mais Lenta</div>
            <div class="value" style="color:#ef4444;font-size:18px">{fase_mais_lenta}</div>
            <div class="sub">{tempo_fase[tempo_fase['Fase']==fase_mais_lenta]['Média (dias)'].values[0] if len(tempo_fase) else 0} dias em média</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #3b82f6">
            <div class="label">Média Geral por Fase</div>
            <div class="value" style="color:#3b82f6">{media_geral}</div>
            <div class="sub">dias por fase</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #22c55e">
            <div class="label">Fase Mais Rápida</div>
            <div class="value" style="color:#22c55e;font-size:18px">{fase_mais_rapida}</div>
            <div class="sub">{tempo_fase[tempo_fase['Fase']==fase_mais_rapida]['Média (dias)'].values[0] if len(tempo_fase) else 0} dias em média</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico de barras — média por fase
    st.markdown("<div class='section-title'>Tempo Médio por Fase (dias)</div>", unsafe_allow_html=True)
    fig = px.bar(tempo_fase, x="Fase", y="Média (dias)",
                 color="Média (dias)",
                 color_continuous_scale=SCALE_ORANGE,
                 text="Média (dias)",
                 category_orders={"Fase": ordem_limpas})
    fig.update_traces(textfont_color="white", textposition="outside")
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, xaxis_tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        # Box plot
        st.markdown("<div class='section-title'>Distribuição do Tempo por Fase</div>", unsafe_allow_html=True)
        fig2 = px.box(df_filtrado, x="fase_limpa", y="duracao_dias",
                      category_orders={"fase_limpa": ordem_limpas},
                      color_discrete_sequence=[FLUXO_ORANGE],
                      labels={"fase_limpa": "Fase", "duracao_dias": "Dias"})
        fig2.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-20)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.markdown("<div class='section-title'>Tabela de Tempos</div>", unsafe_allow_html=True)
        
        total_media = tempo_fase["Média (dias)"].sum().round(1)
        total_mediana = tempo_fase["Mediana (dias)"].sum().round(1)
        total_horas = tempo_fase["Média (horas)"].sum().round(1)
        total_cards = tempo_fase["Cards"].sum()

        linha_total = pd.DataFrame([{
            "Fase": "⏱️ TOTAL DO FUNIL",
            "Média (dias)": total_media,
            "Mediana (dias)": total_mediana,
            "Média (horas)": total_horas,
            "Cards": total_cards,
        }]).set_index("Fase")

        tabela_final = pd.concat([tempo_fase.set_index("Fase"), linha_total])
        st.dataframe(tabela_final, use_container_width=True, height=380)
    # Breakdown por resultado
    st.markdown("<div class='section-title'>Tempo Médio por Fase e Resultado</div>", unsafe_allow_html=True)
    tempo_resultado = df_filtrado.groupby(["fase_limpa", "resultado"])["duracao_dias"].mean().round(1).reset_index()
    tempo_resultado.columns = ["Fase", "Resultado", "Média (dias)"]

    fig3 = px.bar(tempo_resultado, x="Fase", y="Média (dias)", color="Resultado",
                  barmode="group",
                  color_discrete_map=CORES,
                  category_orders={"Fase": ordem_limpas},
                  labels={"Fase": "", "Média (dias)": "Dias (média)"})
    fig3.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-20)
    st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# PÁGINA — FUNIL DE CONVERSÃO
# ============================================================

def pagina_funil(df):
    st.markdown("<h1 style='color:#FAFAFA;margin-bottom:4px'>🔻 Funil de Conversão</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;margin-bottom:24px'>Taxa de mortalidade e gargalos por etapa do funil</p>", unsafe_allow_html=True)

    FASES_FUNIL = [
        "1. Oportunidade",
        "2. Contato aberto",
        "3. Pré-diagnóstico feito",
        "4. Diagnóstico feito",
        "5. Precificação/Aprovação em andamento",
        "6. Proposta comercial feita",
        "7. Follow-up",
    ]

    # Filtro por responsável
    df_exp = explodir_responsaveis(df)
    pessoas = ["Todos"] + sorted(df_exp["responsavel"].dropna().unique().tolist())
    
    col1, col2 = st.columns([1, 3])
    with col1:
        pessoa_sel = st.selectbox("Filtrar por responsável:", pessoas, key="funil_resp")

    if pessoa_sel != "Todos":
        ids_filtrados = df_exp[df_exp["responsavel"] == pessoa_sel]["id"].unique()
        df_analise = df[df["id"].isin(ids_filtrados)].copy()
    else:
        df_analise = df.copy()

    # Monta dicionário: card_id -> resultado
    with open(CARDS_RAW_PATH, encoding="utf-8") as f:
        cards_raw = json.load(f)

    # Se filtro por responsável, limita os ids
    ids_validos = set(df_analise["id"].astype(str).tolist())

    # Monta histórico de fases com resultado de cada card
    historico = []
    for card in cards_raw:
        card_id = str(card.get("id"))
        if card_id not in ids_validos:
            continue
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        resultado = classificar_resultado(fase_atual)

        # Pega apenas a última fase do funil que o card visitou
        fases_visitadas = [
            ph.get("phase", {}).get("name")
            for ph in card.get("phases_history", [])
            if ph.get("phase", {}).get("name") in FASES_FUNIL
        ]

        if fases_visitadas:
            ultima_fase = fases_visitadas[-1]
        else:
            ultima_fase = fase_atual

        historico.append({
            "card_id": card_id,
            "fase": ultima_fase,
            "resultado": resultado,
        })

    df_historico = pd.DataFrame(historico).dropna(subset=["fase"])

    def calcular_mortalidade(df_hist, fases):
        rows = []
        for fase in fases:
            fase_limpa = fase.split(". ")[-1] if ". " in fase else fase
            cards_na_fase = df_hist[df_hist["fase"] == fase]
            total = len(cards_na_fase)
            perdas = len(cards_na_fase[cards_na_fase["resultado"] == "Perda"])
            vendas = len(cards_na_fase[cards_na_fase["resultado"] == "Venda"])
            pausados = len(cards_na_fase[cards_na_fase["resultado"] == "Pausado"])
            andamento = len(cards_na_fase[cards_na_fase["resultado"] == "Em andamento"])
            taxa_perda = round(perdas / total * 100, 1) if total else 0
            taxa_venda = round(vendas / total * 100, 1) if total else 0
            rows.append({
                "Fase": fase_limpa,
                "Total": total,
                "Venda": vendas,
                "Perda": perdas,
                "Pausado": pausados,
                "Em andamento": andamento,
                "Taxa de Perda (%)": taxa_perda,
                "Taxa de Venda (%)": taxa_venda,
            })
        return pd.DataFrame(rows)

    df_mort = calcular_mortalidade(df_historico, FASES_FUNIL)
    df_mort_valido = df_mort[df_mort["Total"] > 0]

    if df_mort_valido.empty:
        st.warning("Nenhum card encontrado para esse filtro.")
        return

    # KPIs
    total_entrada = df_mort_valido.iloc[0]["Total"] if len(df_mort_valido) else 0
    maior_gargalo = df_mort_valido.loc[df_mort_valido["Taxa de Perda (%)"].idxmax(), "Fase"]
    maior_taxa = df_mort_valido["Taxa de Perda (%)"].max()
    # Total de perdas único — conta cards distintos com resultado Perda
    total_perdas = len(df_analise[df_analise["resultado"] == "Perda"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #ef4444">
            <div class="label">Maior Gargalo</div>
            <div class="value" style="color:#ef4444;font-size:18px">{maior_gargalo}</div>
            <div class="sub">{maior_taxa}% de perda nessa fase</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #3b82f6">
            <div class="label">Leads que Entraram</div>
            <div class="value" style="color:#3b82f6">{total_entrada}</div>
            <div class="sub">na primeira fase analisada</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #f59e0b">
            <div class="label">Total de Perdas</div>
            <div class="value" style="color:#f59e0b">{total_perdas}</div>
            <div class="sub">ao longo do funil</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Funil de conversão
    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.markdown("<div class='section-title'>Funil de Conversão — Avanço vs Perda</div>", unsafe_allow_html=True)

        fig = go.Figure()

        # Barras de avanço (azul)
        fig.add_trace(go.Bar(
            name="Avançaram",
            x=df_mort_valido["Fase"],
            y=df_mort_valido["Total"] - df_mort_valido["Perda"],
            marker_color=FLUXO_ORANGE,
            text=(df_mort_valido["Total"] - df_mort_valido["Perda"]),
            textposition="inside",
            textfont=dict(color="white", size=12),
        ))

        # Barras de perda (vermelho)
        fig.add_trace(go.Bar(
            name="Perdidos",
            x=df_mort_valido["Fase"],
            y=df_mort_valido["Perda"],
            marker_color="#ef4444",
            text=df_mort_valido["Perda"],
            textposition="inside",
            textfont=dict(color="white", size=12),
        ))

        fig.update_layout(**PLOTLY_LAYOUT, barmode="stack", xaxis_tickangle=-20)
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#FAFAFA")))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("<div class='section-title'>Taxa de Mortalidade por Fase</div>", unsafe_allow_html=True)
        fig2 = px.bar(
            df_mort_valido.sort_values("Taxa de Perda (%)"),
            x="Taxa de Perda (%)",
            y="Fase",
            orientation="h",
            color="Taxa de Perda (%)",
            color_continuous_scale=["#1c1c2e", "#7f1d1d", "#ef4444"],
            text="Taxa de Perda (%)",
            labels={"Fase": ""}
        )
        fig2.update_traces(texttemplate="%{text}%", textfont_color="white")
        fig2.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Tabela de gargalos
    st.markdown("<div class='section-title'>📋 Resumo dos Gargalos</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Ordenado pelas fases com maior taxa de perda</p>", unsafe_allow_html=True)

    tabela = df_mort_valido[[
        "Fase", "Total", "Venda", "Perda", "Pausado", "Em andamento",
        "Taxa de Perda (%)", "Taxa de Venda (%)"
    ]].sort_values("Taxa de Perda (%)", ascending=False).set_index("Fase")

    st.dataframe(
        tabela.style
            .background_gradient(subset=["Taxa de Perda (%)"], cmap="Reds")
            .background_gradient(subset=["Taxa de Venda (%)"], cmap="Greens")
            .format({"Taxa de Perda (%)": "{:.1f}%", "Taxa de Venda (%)": "{:.1f}%"}),
        use_container_width=True,
        height=320
    )

# ============================================================
# PÁGINA — COORDENAÇÕES
# ============================================================

def pagina_coordenacoes(df):
    st.markdown("<h1 style='color:#FAFAFA;margin-bottom:4px'>🏢 Análise por Coordenação</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;margin-bottom:24px'>Objeções e conversão por coordenação e por responsável dentro de cada coordenação</p>", unsafe_allow_html=True)

    with open(CARDS_RAW_PATH, encoding="utf-8") as f:
        cards_raw = json.load(f)

    COORDENACOES = ["ACE", "CCE", "MNP", "PRO", "QAB"]

    def parse_lista(x):
        if not x or isinstance(x, float): return []
        if isinstance(x, str) and x.startswith("["): 
            try: return json.loads(x)
            except: return [x]
        return [x]

    # Monta DataFrame expandido por coordenação
    linhas = []
    for card in cards_raw:
        card_id = str(card.get("id"))
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        resultado = classificar_resultado(fase_atual)
        responsaveis = [a["name"].strip() for a in card.get("assignees", [])]

        coords = []
        objecoes = []
        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name", "")
            valor = campo.get("value")
            if label and "coord" in label.lower():
                coords = parse_lista(valor)
            if label and "obje" in label.lower():
                objecoes = parse_lista(valor)
                if not objecoes: objecoes = ["Sem resposta"]

        if not coords:
            continue
        if not objecoes:
            objecoes = ["Sem resposta"]

        for coord in coords:
            coord = coord.strip()
            if coord not in COORDENACOES:
                continue
            for objecao in objecoes:
                for resp in responsaveis:
                    linhas.append({
                        "card_id": card_id,
                        "coordenacao": coord,
                        "objecao": objecao.strip(),
                        "responsavel": resp,
                        "resultado": resultado,
                    })

    df_coord = pd.DataFrame(linhas)

    if df_coord.empty:
        st.error("Nenhum dado de coordenação encontrado.")
        return

    # Filtro de coordenação
    coord_sel = st.radio(
        "Selecione a coordenação:",
        COORDENACOES,
        horizontal=True,
        key="coord_radio"
    )

    df_sel = df_coord[df_coord["coordenacao"] == coord_sel]
    df_sel_unique = df_sel.drop_duplicates(subset=["card_id", "objecao"])

    total = df_sel["card_id"].nunique()
    vendas = df_sel[df_sel["resultado"] == "Venda"]["card_id"].nunique()
    taxa = round(vendas / total * 100, 1) if total else 0

    # KPIs
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #3b82f6">
            <div class="label">Leads na {coord_sel}</div>
            <div class="value" style="color:#3b82f6">{total}</div>
            <div class="sub">cards únicos</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #22c55e">
            <div class="label">Vendas</div>
            <div class="value" style="color:#22c55e">{vendas}</div>
            <div class="sub">{taxa}% de conversão</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        perdas = df_sel[df_sel["resultado"] == "Perda"]["card_id"].nunique()
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #ef4444">
            <div class="label">Perdidos</div>
            <div class="value" style="color:#ef4444">{perdas}</div>
            <div class="sub">{round(perdas/total*100,1) if total else 0}% do total</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # SEÇÃO 1 — Objeções da coordenação
    # -------------------------------------------------------
    st.markdown("<div class='section-title'>🚧 Objeções e Conversão por Objeção</div>", unsafe_allow_html=True)

    df_sem_sr = df_sel_unique[df_sel_unique["objecao"] != "Sem resposta"]

    analise_obj = df_sem_sr.groupby(["objecao", "resultado"]).size().unstack(fill_value=0)
    for col in CORES:
        if col not in analise_obj.columns:
            analise_obj[col] = 0
    analise_obj = analise_obj[list(CORES.keys())]
    analise_obj["Total"] = analise_obj.sum(axis=1)
    analise_obj["Taxa de Venda (%)"] = (analise_obj["Venda"] / analise_obj["Total"] * 100).round(1)
    analise_obj = analise_obj.sort_values("Total", ascending=False).reset_index()

    c1, c2 = st.columns([1.3, 1])
    with c1:
        df_melt = analise_obj.melt(id_vars="objecao", value_vars=list(CORES.keys()), var_name="Resultado", value_name="Leads")
        fig = px.bar(df_melt, x="objecao", y="Leads", color="Resultado",
                     color_discrete_map=CORES, barmode="stack",
                     labels={"objecao": ""})
        fig.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True, key=f"coord_obj_vol_{coord_sel}")

    with c2:
        st.dataframe(
            analise_obj.set_index("objecao").style
                .background_gradient(subset=["Taxa de Venda (%)"], cmap="Greens")
                .format({"Taxa de Venda (%)": "{:.1f}%"}),
            use_container_width=True, height=320
        )

    # -------------------------------------------------------
    # SEÇÃO 2 — Objeções por responsável
    # -------------------------------------------------------
    st.markdown("---", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>👤 Objeções por Responsável</div>", unsafe_allow_html=True)

    pessoas = sorted(df_sel["responsavel"].dropna().unique().tolist())
    pessoa_sel = st.selectbox("Selecione um responsável:", ["Todos"] + pessoas, key=f"coord_pessoa_{coord_sel}")

    df_pessoa = df_sel_unique if pessoa_sel == "Todos" else df_sel_unique[df_sel_unique["responsavel"] == pessoa_sel]
    df_pessoa_sem_sr = df_pessoa[df_pessoa["objecao"] != "Sem resposta"]

    analise_pessoa = df_pessoa_sem_sr.groupby(["objecao", "resultado"]).size().unstack(fill_value=0)
    for col in CORES:
        if col not in analise_pessoa.columns:
            analise_pessoa[col] = 0
    analise_pessoa = analise_pessoa[list(CORES.keys())]
    analise_pessoa["Total"] = analise_pessoa.sum(axis=1)
    analise_pessoa["Taxa de Venda (%)"] = (analise_pessoa["Venda"] / analise_pessoa["Total"] * 100).round(1)
    analise_pessoa = analise_pessoa.sort_values("Total", ascending=False).reset_index()

    if analise_pessoa.empty:
        st.info("Nenhuma objeção registrada para esse filtro.")
    else:
        c1, c2 = st.columns([1.3, 1])
        with c1:
            df_melt2 = analise_pessoa.melt(id_vars="objecao", value_vars=list(CORES.keys()), var_name="Resultado", value_name="Leads")
            fig2 = px.bar(df_melt2, x="objecao", y="Leads", color="Resultado",
                          color_discrete_map=CORES, barmode="stack",
                          labels={"objecao": ""})
            fig2.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-20)
            st.plotly_chart(fig2, use_container_width=True, key=f"coord_pessoa_vol_{coord_sel}_{pessoa_sel}")

        with c2:
            st.dataframe(
                analise_pessoa.set_index("objecao").style
                    .background_gradient(subset=["Taxa de Venda (%)"], cmap="Greens")
                    .format({"Taxa de Venda (%)": "{:.1f}%"}),
                use_container_width=True, height=320
            )

        # Heatmap — responsável x objeção
        st.markdown("<div class='section-title'>🗺️ Mapa de Calor — Responsável × Objeção</div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#A3A3A3;font-size:13px'>Quantidade de vezes que cada responsável ouviu cada objeção</p>", unsafe_allow_html=True)

        heatmap_data = df_sel_unique[df_sel_unique["objecao"] != "Sem resposta"].groupby(
            ["responsavel", "objecao"]
        ).size().unstack(fill_value=0)

        fig3 = px.imshow(
            heatmap_data,
            color_continuous_scale=SCALE_ORANGE_SOFT,
            labels={"x": "Objeção", "y": "Responsável", "color": "Quantidade"},
            aspect="auto",
            text_auto=True,
        )
        fig3.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig3.update_traces(textfont_color="white")
        st.plotly_chart(fig3, use_container_width=True, key=f"coord_heatmap_{coord_sel}")

# ============================================================
# PÁGINA — TAXA DE CONVERSÃO REAL
# ============================================================

def pagina_conversao(df):
    st.markdown("<h1 style='color:#FAFAFA;margin-bottom:4px'>📈 Taxa de Conversão Real</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;margin-bottom:24px'>Conversão calculada apenas sobre leads que chegaram à Proposta Comercial</p>", unsafe_allow_html=True)

    with open(CARDS_RAW_PATH, encoding="utf-8") as f:
        cards_raw = json.load(f)

    COORDENACOES = ["ACE", "CCE", "MNP", "PRO", "QAB"]

    def parse_lista(x):
        if not x or isinstance(x, float): return []
        if isinstance(x, str) and x.startswith("["):
            try: return json.loads(x)
            except: return [x]
        return [x]

    FASES_PROPOSTA_OU_ALEM = [
        "6. Proposta comercial feita",
        "7. Follow-up",
        "Venda",
    ]

    linhas = []
    for card in cards_raw:
        card_id = str(card.get("id"))
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        resultado = classificar_resultado(fase_atual)

        fases_visitadas = [
            ph.get("phase", {}).get("name")
            for ph in card.get("phases_history", [])
        ]
        chegou_proposta = any(f in fases_visitadas for f in FASES_PROPOSTA_OU_ALEM)
        if not chegou_proposta:
            continue

        coords = []
        gerentes = []
        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name", "")
            valor = campo.get("value")
            if label == "Coordenação":
                coords = parse_lista(valor)
            if label == "Responsável":
                gerentes = parse_lista(valor)

        if not coords: coords = ["Sem coordenação"]
        if not gerentes: gerentes = ["Sem gerente"]

        for coord in coords:
            coord = coord.strip()
            for gerente in gerentes:
                linhas.append({
                    "card_id": card_id,
                    "coordenacao": coord,
                    "gerente": gerente.strip(),
                    "resultado": resultado,
                    "fase_atual": fase_atual,
                })

    df_prop = pd.DataFrame(linhas)

    if df_prop.empty:
        st.error("Nenhum card encontrado que chegou à proposta.")
        return

    # Adiciona data de criação e ciclo
    from datetime import datetime

    FASES_PROPOSTA_CICLO = [
        "6. Proposta comercial feita",
        "7. Follow-up",
        "Venda",
    ]

    datas_map = {}
    for card in cards_raw:
        card_id = str(card.get("id"))

        # Busca a data em que entrou na primeira fase de proposta ou além
        data_proposta = None
        for ph in card.get("phases_history", []):
            fase_nome = ph.get("phase", {}).get("name")
            first_time_in = ph.get("firstTimeIn")
            if fase_nome in FASES_PROPOSTA_CICLO and first_time_in:
                try:
                    dt_fase = datetime.strptime(first_time_in[:19], "%Y-%m-%dT%H:%M:%S")
                    if data_proposta is None or dt_fase < data_proposta:
                        data_proposta = dt_fase
                except:
                    pass

        if data_proposta:
            if datetime(2025, 10, 1) <= data_proposta <= datetime(2025, 12, 31, 23, 59, 59):
                ciclo = "🔵 Ciclo 1 (Out-Dez 2025)"
            elif datetime(2026, 1, 1) <= data_proposta <= datetime(2026, 3, 31, 23, 59, 59):
                ciclo = "🟣 Ciclo 2 (Jan-Mar 2026)"
            elif datetime(2026, 4, 1) <= data_proposta <= datetime(2026, 6, 30, 23, 59, 59):
                ciclo = "🟡 Ciclo 3 (Abr-Jun 2026)"
            else:
                ciclo = "⚪ Fora dos ciclos"
        else:
            ciclo = "⚪ Fora dos ciclos"

        datas_map[card_id] = ciclo

    df_prop["ciclo"] = df_prop["card_id"].map(datas_map).fillna("⚪ Fora dos ciclos")

    CICLOS = [
        "Todos os ciclos",
        "🔵 Ciclo 1 (Out-Dez 2025)",
        "🟣 Ciclo 2 (Jan-Mar 2026)",
        "🟡 Ciclo 3 (Abr-Jun 2026)",
        "⚪ Fora dos ciclos",
    ]

    df_unique = df_prop.drop_duplicates(subset=["card_id"])

    # -------------------------------------------------------
    # KPIs GERAIS
    # -------------------------------------------------------
    total = df_unique["card_id"].nunique()
    vendas = df_unique[df_unique["resultado"] == "Venda"]["card_id"].nunique()
    perdas = df_unique[df_unique["resultado"] == "Perda"]["card_id"].nunique()
    pausados = df_unique[df_unique["resultado"] == "Pausado"]["card_id"].nunique()
    andamento = df_unique[df_unique["resultado"] == "Em andamento"]["card_id"].nunique()
    taxa = round(vendas / total * 100, 1) if total else 0

    st.markdown("<div class='section-title'>📊 Visão Geral — Leads que chegaram à Proposta</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    dados_kpi = [
        (c1, "Total com Proposta", total, "chegaram até proposta", FLUXO_ORANGE),
        (c2, "Vendas", vendas, f"{taxa}% de conversão", "#22c55e"),
        (c3, "Perdidos", perdas, f"{round(perdas/total*100,1) if total else 0}%", "#ef4444"),
        (c4, "Pausados", pausados, f"{round(pausados/total*100,1) if total else 0}%", "#f59e0b"),
        (c5, "Em andamento", andamento, f"{round(andamento/total*100,1) if total else 0}%", FLUXO_ORANGE_LIGHT),
    ]
    for col, label, val, sub, cor in dados_kpi:
        with col:
            st.markdown(f"""<div class="metric-card" style="border-top:3px solid {cor}">
                <div class="label">{label}</div>
                <div class="value" style="color:{cor}">{val}</div>
                <div class="sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filtro de ciclo
    ciclo_sel = st.radio("Filtrar por ciclo:", CICLOS, horizontal=True, key="ciclo_radio")
    if ciclo_sel != "Todos os ciclos":
        df_prop = df_prop[df_prop["ciclo"] == ciclo_sel]
        df_unique = df_prop.drop_duplicates(subset=["card_id"])

        # Recalcula KPIs com filtro
        total = df_unique["card_id"].nunique()
        vendas = df_unique[df_unique["resultado"] == "Venda"]["card_id"].nunique()
        perdas = df_unique[df_unique["resultado"] == "Perda"]["card_id"].nunique()
        pausados = df_unique[df_unique["resultado"] == "Pausado"]["card_id"].nunique()
        andamento = df_unique[df_unique["resultado"] == "Em andamento"]["card_id"].nunique()
        taxa = round(vendas / total * 100, 1) if total else 0

        c1, c2, c3, c4, c5 = st.columns(5)
        dados_kpi2 = [
            (c1, "Total com Proposta", total, "neste ciclo", FLUXO_ORANGE),
            (c2, "Vendas", vendas, f"{taxa}% de conversão", "#22c55e"),
            (c3, "Perdidos", perdas, f"{round(perdas/total*100,1) if total else 0}%", "#ef4444"),
            (c4, "Pausados", pausados, f"{round(pausados/total*100,1) if total else 0}%", "#f59e0b"),
            (c5, "Em andamento", andamento, f"{round(andamento/total*100,1) if total else 0}%", FLUXO_ORANGE_LIGHT),
        ]
        for col, label, val, sub, cor in dados_kpi2:
            with col:
                st.markdown(f"""<div class="metric-card" style="border-top:3px solid {cor}">
                    <div class="label">{label}</div>
                    <div class="value" style="color:{cor}">{val}</div>
                    <div class="sub">{sub}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # CONVERSÃO POR COORDENAÇÃO
    # -------------------------------------------------------
    st.markdown("<div class='section-title'>🏢 Conversão por Coordenação</div>", unsafe_allow_html=True)

    rows_coord = []
    for coord in COORDENACOES:
        df_c = df_prop[df_prop["coordenacao"] == coord].drop_duplicates(subset=["card_id"])
        total_c = df_c["card_id"].nunique()
        if total_c == 0: continue
        vendas_c = df_c[df_c["resultado"] == "Venda"]["card_id"].nunique()
        perdas_c = df_c[df_c["resultado"] == "Perda"]["card_id"].nunique()
        pausados_c = df_c[df_c["resultado"] == "Pausado"]["card_id"].nunique()
        andamento_c = df_c[df_c["resultado"] == "Em andamento"]["card_id"].nunique()
        rows_coord.append({
            "Coordenação": coord,
            "Total": total_c,
            "Venda": vendas_c,
            "Perda": perdas_c,
            "Pausado": pausados_c,
            "Em andamento": andamento_c,
            "Taxa de Conversão (%)": round(vendas_c / total_c * 100, 1),
        })

    df_coord_analise = pd.DataFrame(rows_coord).sort_values("Taxa de Conversão (%)", ascending=False)

    c1, c2 = st.columns([1.3, 1])
    with c1:
        fig_coord = px.bar(
            df_coord_analise,
            x="Coordenação", y="Taxa de Conversão (%)",
            color="Taxa de Conversão (%)",
            color_continuous_scale=["#1c3a1c", "#16a34a", "#86efac"],
            text="Taxa de Conversão (%)",
            labels={"Coordenação": ""}
        )
        fig_coord.update_traces(texttemplate="%{text}%", textfont_color="white", textposition="outside")
        fig_coord.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig_coord, use_container_width=True, key="conv_coord")

    with c2:
        st.dataframe(
            df_coord_analise.set_index("Coordenação").style
                .background_gradient(subset=["Taxa de Conversão (%)"], cmap="Greens")
                .format({"Taxa de Conversão (%)": "{:.1f}%"}),
            use_container_width=True, height=300
        )

    # -------------------------------------------------------
    # CONVERSÃO POR GERENTE
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>👤 Conversão por Gerente</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        coord_filtro = st.selectbox("Filtrar por coordenação:", ["Todas"] + COORDENACOES, key="conv_coord_filtro")
    with col2:
        min_props = st.slider("Mínimo de propostas:", 1, 20, 3, key="conv_min_props")

    df_ger = df_prop.copy()
    if coord_filtro != "Todas":
        df_ger = df_ger[df_ger["coordenacao"] == coord_filtro]

    rows_ger = []
    for gerente, grupo in df_ger.groupby("gerente"):
        grupo_unique = grupo.drop_duplicates(subset=["card_id"])
        total_g = grupo_unique["card_id"].nunique()
        if total_g < min_props: continue
        vendas_g = grupo_unique[grupo_unique["resultado"] == "Venda"]["card_id"].nunique()
        perdas_g = grupo_unique[grupo_unique["resultado"] == "Perda"]["card_id"].nunique()
        pausados_g = grupo_unique[grupo_unique["resultado"] == "Pausado"]["card_id"].nunique()
        andamento_g = grupo_unique[grupo_unique["resultado"] == "Em andamento"]["card_id"].nunique()
        rows_ger.append({
            "Gerente": gerente,
            "Total": total_g,
            "Venda": vendas_g,
            "Perda": perdas_g,
            "Pausado": pausados_g,
            "Em andamento": andamento_g,
            "Taxa de Conversão (%)": round(vendas_g / total_g * 100, 1),
        })

    df_ger_analise = pd.DataFrame(rows_ger).sort_values("Taxa de Conversão (%)", ascending=False)

    if df_ger_analise.empty:
        st.info("Nenhum gerente encontrado com esse filtro.")
        return

    c1, c2 = st.columns([1.3, 1])
    with c1:
        fig_ger = px.bar(
            df_ger_analise.sort_values("Taxa de Conversão (%)"),
            x="Taxa de Conversão (%)", y="Gerente",
            orientation="h",
            color="Taxa de Conversão (%)",
            color_continuous_scale=["#1c3a1c", "#16a34a", "#86efac"],
            text="Taxa de Conversão (%)",
            labels={"Gerente": ""}
        )
        fig_ger.update_traces(texttemplate="%{text}%", textfont_color="white")
        fig_ger.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig_ger, use_container_width=True, key=f"conv_ger_{coord_filtro}")

    with c2:
        st.dataframe(
            df_ger_analise.set_index("Gerente").style
                .background_gradient(subset=["Taxa de Conversão (%)"], cmap="Greens")
                .format({"Taxa de Conversão (%)": "{:.1f}%"}),
            use_container_width=True, height=400
        )

# ============================================================
# PÁGINA — DIAGNÓSTICO
# Adicione esta função ao dashboard.py e registre no menu da sidebar
# ============================================================

def pagina_diagnostico(df):
    from datetime import datetime, timedelta

    st.markdown("<h1 style='color:#FAFAFA;margin-bottom:4px'>🔬 Diagnóstico</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;margin-bottom:24px'>Identificação de gargalos, padrões de perda e qualidade de qualificação</p>", unsafe_allow_html=True)

    with open(CARDS_RAW_PATH, encoding="utf-8") as f:
        cards_raw = json.load(f)

    COORDENACOES = ["ACE", "CCE", "MNP", "PRO", "QAB"]

    def parse_lista(x):
        if not x or isinstance(x, float): return []
        if isinstance(x, str) and x.startswith("["):
            try: return json.loads(x)
            except: return [x]
        return [x]

    def parse_data_br(s):
        if not s or isinstance(s, float): return None
        try: return datetime.strptime(s.strip(), "%d/%m/%Y")
        except: return None

    def get_ciclo(dt):
        if dt is None: return "⚪ Fora dos ciclos"
        if datetime(2025, 10, 1) <= dt <= datetime(2025, 12, 31, 23, 59, 59):
            return "🔵 Ciclo 1 (Out-Dez 2025)"
        elif datetime(2026, 1, 1) <= dt <= datetime(2026, 3, 31, 23, 59, 59):
            return "🟣 Ciclo 2 (Jan-Mar 2026)"
        elif datetime(2026, 4, 1) <= dt <= datetime(2026, 6, 30, 23, 59, 59):
            return "🟡 Ciclo 3 (Abr-Jun 2026)"
        return "⚪ Fora dos ciclos"

    # -------------------------------------------------------
    # Monta DataFrame principal de diagnóstico
    # -------------------------------------------------------
    linhas = []
    for card in cards_raw:
        card_id = str(card.get("id"))
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        resultado = classificar_resultado(fase_atual)
        updated_at_raw = card.get("updated_at")
        responsaveis = [a["name"].strip() for a in card.get("assignees", [])]

        # Data de atualização — usada para ciclo
        try:
            updated_at = datetime.strptime(updated_at_raw[:19], "%Y-%m-%dT%H:%M:%S") if updated_at_raw else None
        except:
            updated_at = None

        ciclo = get_ciclo(updated_at)

        coords = []
        objecoes = []
        canal = None
        data_chegada = None
        data_contato = None
        item_carta = None

        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name", "")
            valor = campo.get("value")
            if label == "Coordenação":
                coords = parse_lista(valor)
            elif label and "obje" in label.lower():
                objecoes = parse_lista(valor)
            elif label == "Canal de aquisição":
                canal = valor
            elif label == "Data de chegada":
                data_chegada = parse_data_br(valor)
            elif label == "Data da abertura de contato":
                data_contato = parse_data_br(valor)
            elif label == "Ítem de carta":
                item_carta = valor

        if not objecoes:
            objecoes = ["Sem objeção"]
        if not coords:
            coords = ["Sem coordenação"]

        # Tempo até primeiro contato
        dias_ate_contato = None
        if data_chegada and data_contato:
            delta = (data_contato - data_chegada).days
            dias_ate_contato = max(delta, 0)

        # Fase onde o card morreu (última fase do funil visitada)
        FASES_FUNIL = [
            "1. Oportunidade", "2. Contato aberto", "3. Pré-diagnóstico feito",
            "4. Diagnóstico feito", "5. Precificação/Aprovação em andamento",
            "6. Proposta comercial feita", "7. Follow-up",
        ]
        fases_visitadas = [
            ph.get("phase", {}).get("name")
            for ph in card.get("phases_history", [])
            if ph.get("phase", {}).get("name") in FASES_FUNIL
        ]
        fase_morte = fases_visitadas[-1] if fases_visitadas else fase_atual

        for coord in coords:
            for resp in (responsaveis if responsaveis else ["Sem responsável"]):
                for obj in objecoes:
                    linhas.append({
                        "card_id": card_id,
                        "resultado": resultado,
                        "ciclo": ciclo,
                        "coordenacao": coord.strip(),
                        "responsavel": resp,
                        "objecao": obj.strip(),
                        "canal": canal,
                        "dias_ate_contato": dias_ate_contato,
                        "data_chegada": data_chegada,
                        "data_contato": data_contato,
                        "fase_morte": fase_morte,
                        "item_carta": item_carta,
                        "updated_at": updated_at,
                    })

    df_diag = pd.DataFrame(linhas)

    if df_diag.empty:
        st.error("Nenhum dado encontrado.")
        return

    # -------------------------------------------------------
    # FILTROS GLOBAIS
    # -------------------------------------------------------
    CICLOS = [
        "Todos os ciclos",
        "🔵 Ciclo 1 (Out-Dez 2025)",
        "🟣 Ciclo 2 (Jan-Mar 2026)",
        "🟡 Ciclo 3 (Abr-Jun 2026)",
        "⚪ Fora dos ciclos",
    ]

    col1, col2, col3 = st.columns(3)
    with col1:
        ciclo_sel = st.radio("Ciclo:", CICLOS, key="diag_ciclo")
    with col2:
        coords_disp = ["Todas"] + COORDENACOES
        coord_sel = st.selectbox("Coordenação:", coords_disp, key="diag_coord")
    with col3:
        pessoas_disp = ["Todos"] + sorted(df_diag["responsavel"].dropna().unique().tolist())
        pessoa_sel = st.selectbox("Responsável:", pessoas_disp, key="diag_pessoa")

    # Aplica filtros
    df_f = df_diag.copy()
    if ciclo_sel != "Todos os ciclos":
        df_f = df_f[df_f["ciclo"] == ciclo_sel]
    if coord_sel != "Todas":
        df_f = df_f[df_f["coordenacao"] == coord_sel]
    if pessoa_sel != "Todos":
        df_f = df_f[df_f["responsavel"] == pessoa_sel]

    if df_f.empty:
        st.warning("Nenhum dado para esse filtro.")
        return

    df_unique = df_f.drop_duplicates(subset=["card_id"])

    total = df_unique["card_id"].nunique()
    vendas = df_unique[df_unique["resultado"] == "Venda"]["card_id"].nunique()
    perdas = df_unique[df_unique["resultado"] == "Perda"]["card_id"].nunique()
    taxa = round(vendas / total * 100, 1) if total else 0

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub, cor in [
        (c1, "Total de Leads", total, "no filtro selecionado", FLUXO_ORANGE),
        (c2, "Vendas", vendas, f"{taxa}% de conversão", "#22c55e"),
        (c3, "Perdidos", perdas, f"{round(perdas/total*100,1) if total else 0}% do total", "#ef4444"),
        (c4, "Em aberto", total - vendas - perdas, "pausados + andamento", "#f59e0b"),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card" style="border-top:3px solid {cor}">
                <div class="label">{label}</div>
                <div class="value" style="color:{cor}">{val}</div>
                <div class="sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ===============================================================
    # ANÁLISE 1 — LEADS PERDIDOS SEM OBJEÇÃO
    # ===============================================================
    st.markdown("---")
    st.markdown("<h3 style='color:#FAFAFA'>🚨 Diagnóstico 1 — Perdidos sem dar objeção</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Leads que foram marcados como Perdido sem registrar nenhuma objeção. Indica possível falha de abordagem, qualificação incorreta ou ausência de follow-up.</p>", unsafe_allow_html=True)

    df_perdidos = df_unique[df_unique["resultado"] == "Perda"].copy()
    # Para objeção, precisa do df expandido (não unique por card)
    df_obj_perdidos = df_f[df_f["resultado"] == "Perda"].copy()
    ids_com_objecao = df_obj_perdidos[df_obj_perdidos["objecao"] != "Sem objeção"]["card_id"].unique()
    df_perdidos_sem_obj = df_perdidos[~df_perdidos["card_id"].isin(ids_com_objecao)]
    df_perdidos_com_obj = df_perdidos[df_perdidos["card_id"].isin(ids_com_objecao)]

    total_perd = len(df_perdidos)
    sem_obj = len(df_perdidos_sem_obj)
    com_obj = len(df_perdidos_com_obj)
    pct_sem = round(sem_obj / total_perd * 100, 1) if total_perd else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #ef4444">
            <div class="label">Perdidos sem objeção</div>
            <div class="value" style="color:#ef4444">{sem_obj}</div>
            <div class="sub">{pct_sem}% dos perdidos</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #f59e0b">
            <div class="label">Perdidos com objeção</div>
            <div class="value" style="color:#f59e0b">{com_obj}</div>
            <div class="sub">{round(com_obj/total_perd*100,1) if total_perd else 0}% dos perdidos</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #A3A3A3">
            <div class="label">Total de Perdidos</div>
            <div class="value" style="color:#A3A3A3">{total_perd}</div>
            <div class="sub">&nbsp;</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='section-title'>Perdidos sem objeção × Fase onde morreu</div>", unsafe_allow_html=True)
        fase_morte_sem_obj = df_perdidos_sem_obj["fase_morte"].value_counts().reset_index()
        fase_morte_sem_obj.columns = ["Fase", "Total"]
        fig = px.bar(fase_morte_sem_obj, x="Total", y="Fase", orientation="h",
                     color="Total", color_continuous_scale=["#450a0a", "#ef4444", "#fca5a5"],
                     text="Total")
        fig.update_traces(textfont_color="white", textposition="outside")
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig, use_container_width=True, key="diag1_fase")

    with c2:
        st.markdown("<div class='section-title'>Perdidos sem objeção × Canal de aquisição</div>", unsafe_allow_html=True)
        canal_sem_obj = df_perdidos_sem_obj["canal"].value_counts().reset_index()
        canal_sem_obj.columns = ["Canal", "Total"]
        fig2 = px.bar(canal_sem_obj, x="Total", y="Canal", orientation="h",
                      color="Total", color_continuous_scale=["#450a0a", "#ef4444", "#fca5a5"],
                      text="Total")
        fig2.update_traces(textfont_color="white", textposition="outside")
        fig2.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig2.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig2, use_container_width=True, key="diag1_canal")

    # Perdidos sem objeção por responsável
    st.markdown("<div class='section-title'>Perdidos sem objeção × Responsável</div>", unsafe_allow_html=True)
    resp_sem_obj = df_perdidos_sem_obj["responsavel"].value_counts().reset_index()
    resp_sem_obj.columns = ["Responsável", "Perdidos sem objeção"]
    # Cruza com total de perdidos por responsável
    resp_total_perd = df_perdidos["responsavel"].value_counts().reset_index()
    resp_total_perd.columns = ["Responsável", "Total perdidos"]
    resp_merge = resp_sem_obj.merge(resp_total_perd, on="Responsável", how="left")
    resp_merge["% sem objeção"] = (resp_merge["Perdidos sem objeção"] / resp_merge["Total perdidos"] * 100).round(1)
    resp_merge = resp_merge.sort_values("% sem objeção", ascending=False)

    c1, c2 = st.columns([1.3, 1])
    with c1:
        fig3 = px.bar(resp_merge.sort_values("% sem objeção"),
                      x="% sem objeção", y="Responsável", orientation="h",
                      color="% sem objeção",
                      color_continuous_scale=["#1c1c2e", "#7f1d1d", "#ef4444"],
                      text="% sem objeção",
                      labels={"Responsável": ""})
        fig3.update_traces(texttemplate="%{text}%", textfont_color="white")
        fig3.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True, key="diag1_resp")
    with c2:
        st.dataframe(resp_merge.set_index("Responsável").style
                     .background_gradient(subset=["% sem objeção"], cmap="Reds")
                     .format({"% sem objeção": "{:.1f}%"}),
                     use_container_width=True, height=350)

    # ===============================================================
    # ANÁLISE 2 — VELOCIDADE DE PRIMEIRO CONTATO
    # ===============================================================
    st.markdown("---")
    st.markdown("<h3 style='color:#FAFAFA'>⚡ Diagnóstico 2 — Velocidade de primeiro contato</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Dias entre a chegada do lead e a abertura do contato. Leads contactados mais tarde tendem a converter menos.</p>", unsafe_allow_html=True)

    df_contato = df_unique[df_unique["dias_ate_contato"].notna()].copy()

    if df_contato.empty:
        st.info("Dados de Data de chegada / Data de abertura de contato insuficientes para esse filtro.")
    else:
        media_geral_contato = df_contato["dias_ate_contato"].mean().round(1)
        media_venda = df_contato[df_contato["resultado"] == "Venda"]["dias_ate_contato"].mean()
        media_perda = df_contato[df_contato["resultado"] == "Perda"]["dias_ate_contato"].mean()
        media_venda = round(media_venda, 1) if pd.notna(media_venda) else "-"
        media_perda = round(media_perda, 1) if pd.notna(media_perda) else "-"

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="metric-card" style="border-top:3px solid #3b82f6">
                <div class="label">Média geral até contato</div>
                <div class="value" style="color:#3b82f6">{media_geral_contato}</div>
                <div class="sub">dias</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card" style="border-top:3px solid #22c55e">
                <div class="label">Média nos que viraram venda</div>
                <div class="value" style="color:#22c55e">{media_venda}</div>
                <div class="sub">dias</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card" style="border-top:3px solid #ef4444">
                <div class="label">Média nos que foram perdidos</div>
                <div class="value" style="color:#ef4444">{media_perda}</div>
                <div class="sub">dias</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("<div class='section-title'>Tempo até contato × Resultado</div>", unsafe_allow_html=True)
            fig = px.box(df_contato, x="resultado", y="dias_ate_contato",
                         color="resultado", color_discrete_map=CORES,
                         labels={"resultado": "", "dias_ate_contato": "Dias até contato"})
            fig.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True, key="diag2_box")

        with c2:
            st.markdown("<div class='section-title'>Tempo até contato × Coordenação</div>", unsafe_allow_html=True)
            coord_contato = df_contato[df_contato["coordenacao"].isin(COORDENACOES)].groupby("coordenacao")["dias_ate_contato"].mean().round(1).reset_index()
            coord_contato.columns = ["Coordenação", "Média (dias)"]
            coord_contato = coord_contato.sort_values("Média (dias)", ascending=False)
            fig2 = px.bar(coord_contato, x="Coordenação", y="Média (dias)",
                          color="Média (dias)",
                          color_continuous_scale=SCALE_ORANGE,
                          text="Média (dias)")
            fig2.update_traces(textfont_color="white", textposition="outside")
            fig2.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True, key="diag2_coord")

        # Velocidade por responsável
        st.markdown("<div class='section-title'>Tempo médio até contato × Responsável</div>", unsafe_allow_html=True)
        resp_contato = df_contato.groupby("responsavel").agg(
            media_dias=("dias_ate_contato", "mean"),
            total=("card_id", "nunique")
        ).reset_index()
        resp_contato["media_dias"] = resp_contato["media_dias"].round(1)
        resp_contato = resp_contato[resp_contato["total"] >= 3].sort_values("media_dias", ascending=False)
        resp_contato.columns = ["Responsável", "Média (dias)", "Cards"]

        c1, c2 = st.columns([1.3, 1])
        with c1:
            fig3 = px.bar(resp_contato.sort_values("Média (dias)"),
                          x="Média (dias)", y="Responsável", orientation="h",
                          color="Média (dias)",
                          color_continuous_scale=SCALE_ORANGE,
                          text="Média (dias)",
                          labels={"Responsável": ""})
            fig3.update_traces(textfont_color="white")
            fig3.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
            st.plotly_chart(fig3, use_container_width=True, key="diag2_resp")
        with c2:
            st.dataframe(resp_contato.set_index("Responsável"),
                         use_container_width=True, height=350)

    # ===============================================================
    # ANÁLISE 3 — CANAL DE AQUISIÇÃO × QUALIDADE
    # ===============================================================
    st.markdown("---")
    st.markdown("<h3 style='color:#FAFAFA'>📡 Diagnóstico 3 — Qualidade por canal de aquisição</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Canais que trazem leads de baixa qualidade inflam o funil sem gerar receita. Cruzamento com taxa de perdidos sem objeção revela canais que qualificam mal.</p>", unsafe_allow_html=True)

    df_canal = df_unique[df_unique["canal"].notna()].copy()

    if df_canal.empty:
        st.info("Dados de canal insuficientes para esse filtro.")
    else:
        canal_analise = df_canal.groupby(["canal", "resultado"]).size().unstack(fill_value=0)
        for col in CORES:
            if col not in canal_analise.columns:
                canal_analise[col] = 0
        canal_analise = canal_analise[list(CORES.keys())]
        canal_analise["Total"] = canal_analise.sum(axis=1)
        canal_analise["Taxa de Conversão (%)"] = (canal_analise["Venda"] / canal_analise["Total"] * 100).round(1)

        # Perdidos sem objeção por canal
        ids_sem_obj_set = set(df_perdidos_sem_obj["card_id"].tolist())
        df_canal_sem_obj = df_canal[df_canal["card_id"].isin(ids_sem_obj_set)]
        perd_sem_obj_canal = df_canal_sem_obj["canal"].value_counts().rename("Perdidos sem objeção")

        canal_analise = canal_analise.join(perd_sem_obj_canal, how="left").fillna(0)
        canal_analise["Perdidos sem objeção"] = canal_analise["Perdidos sem objeção"].astype(int)
        canal_analise["% Perd. sem objeção"] = (canal_analise["Perdidos sem objeção"] / canal_analise["Total"] * 100).round(1)
        canal_analise = canal_analise.sort_values("Total", ascending=False).reset_index()

        c1, c2 = st.columns([1.4, 1])
        with c1:
            st.markdown("<div class='section-title'>Volume e resultado por canal</div>", unsafe_allow_html=True)
            df_melt = canal_analise.melt(id_vars="canal", value_vars=list(CORES.keys()), var_name="Resultado", value_name="Leads")
            fig = px.bar(df_melt, x="canal", y="Leads", color="Resultado",
                         color_discrete_map=CORES, barmode="stack",
                         labels={"canal": ""})
            fig.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-20)
            st.plotly_chart(fig, use_container_width=True, key="diag3_canal_vol")

        with c2:
            st.markdown("<div class='section-title'>Taxa de conversão por canal</div>", unsafe_allow_html=True)
            fig2 = px.bar(canal_analise.sort_values("Taxa de Conversão (%)"),
                          x="Taxa de Conversão (%)", y="canal", orientation="h",
                          color="Taxa de Conversão (%)",
                          color_continuous_scale=["#1c3a1c", "#16a34a", "#86efac"],
                          text="Taxa de Conversão (%)",
                          labels={"canal": ""})
            fig2.update_traces(texttemplate="%{text}%", textfont_color="white")
            fig2.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True, key="diag3_canal_taxa")

        st.markdown("<div class='section-title'>Tabela completa por canal — incluindo perdidos sem objeção</div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#A3A3A3;font-size:13px'>Canais com alta % de perdidos sem objeção indicam leads mal qualificados ou abordagem inadequada.</p>", unsafe_allow_html=True)
        st.dataframe(
            canal_analise.set_index("canal").style
                .background_gradient(subset=["Taxa de Conversão (%)"], cmap="Greens")
                .background_gradient(subset=["% Perd. sem objeção"], cmap="Reds")
                .format({"Taxa de Conversão (%)": "{:.1f}%", "% Perd. sem objeção": "{:.1f}%"}),
            use_container_width=True, height=320
        )

    # ===============================================================
    # ANÁLISE 4 — FASE DE MORTE × TEMPO NA FASE (SLA)
    # ===============================================================
    st.markdown("---")
    st.markdown("<h3 style='color:#FAFAFA'>⏰ Diagnóstico 4 — Onde e quando os leads morrem</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Fase onde o lead parou × tempo que ficou ali antes de ser perdido. Fases com alto tempo médio e alta mortalidade são gargalos de processo.</p>", unsafe_allow_html=True)

    # Monta histórico de duração por fase para perdidos
    linhas_hist = []
    ids_perdidos = set(df_unique[df_unique["resultado"] == "Perda"]["card_id"].tolist())
    ids_filtro = set(df_unique["card_id"].tolist())

    FASES_FUNIL_HIST = [
        "1. Oportunidade", "2. Contato aberto", "3. Pré-diagnóstico feito",
        "4. Diagnóstico feito", "5. Precificação/Aprovação em andamento",
        "6. Proposta comercial feita", "7. Follow-up",
    ]

    for card in cards_raw:
        card_id = str(card.get("id"))
        if card_id not in ids_filtro:
            continue
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        resultado = classificar_resultado(fase_atual)
        for ph in card.get("phases_history", []):
            fase = ph.get("phase", {}).get("name")
            duration = ph.get("duration")
            if fase in FASES_FUNIL_HIST and duration is not None:
                linhas_hist.append({
                    "card_id": card_id,
                    "fase": fase,
                    "resultado": resultado,
                    "duracao_dias": round(duration / 86400, 1),
                })

    df_hist_diag = pd.DataFrame(linhas_hist)

    if not df_hist_diag.empty:
        FASES_LIMPAS_MAP = {f: f.split(". ")[-1] if ". " in f else f for f in FASES_FUNIL_HIST}
        df_hist_diag["fase_limpa"] = df_hist_diag["fase"].map(FASES_LIMPAS_MAP)
        ordem_limpas = [FASES_LIMPAS_MAP[f] for f in FASES_FUNIL_HIST]

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='section-title'>Tempo médio por fase × resultado</div>", unsafe_allow_html=True)
            tempo_res = df_hist_diag.groupby(["fase_limpa", "resultado"])["duracao_dias"].mean().round(1).reset_index()
            tempo_res.columns = ["Fase", "Resultado", "Média (dias)"]
            fig = px.bar(tempo_res, x="Fase", y="Média (dias)", color="Resultado",
                         barmode="group", color_discrete_map=CORES,
                         category_orders={"Fase": ordem_limpas},
                         labels={"Fase": ""})
            fig.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-20)
            st.plotly_chart(fig, use_container_width=True, key="diag4_tempo_res")

        with c2:
            st.markdown("<div class='section-title'>Distribuição do tempo — apenas perdidos</div>", unsafe_allow_html=True)
            df_perd_hist = df_hist_diag[df_hist_diag["resultado"] == "Perda"]
            if not df_perd_hist.empty:
                fig2 = px.box(df_perd_hist, x="fase_limpa", y="duracao_dias",
                              color_discrete_sequence=["#ef4444"],
                              category_orders={"fase_limpa": ordem_limpas},
                              labels={"fase_limpa": "", "duracao_dias": "Dias"})
                fig2.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-20)
                st.plotly_chart(fig2, use_container_width=True, key="diag4_box_perd")

    # ===============================================================
    # ANÁLISE 5 — CANAL × TEMPO ATÉ CONTATO × PERDIDOS SEM OBJEÇÃO
    # ===============================================================
    st.markdown("---")
    st.markdown("<h3 style='color:#FAFAFA'>🗺️ Diagnóstico 5 — Mapa de risco por canal e responsável</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Heatmap cruzando responsável × canal com volume de perdidos sem objeção. Concentrações revelam onde está o problema: no canal, na pessoa, ou na combinação dos dois.</p>", unsafe_allow_html=True)

    df_heatmap = df_f[
        df_f["card_id"].isin(ids_sem_obj_set) &
        df_f["canal"].notna() &
        (df_f["responsavel"] != "Sem responsável")
    ].drop_duplicates(subset=["card_id", "canal", "responsavel"])

    if not df_heatmap.empty:
        heatmap_data = df_heatmap.groupby(["responsavel", "canal"]).size().unstack(fill_value=0)
        fig_heat = px.imshow(
            heatmap_data,
            color_continuous_scale=["#0f172a", "#450a0a", "#ef4444", "#fca5a5"],
            labels={"x": "Canal", "y": "Responsável", "color": "Perdidos sem objeção"},
            aspect="auto",
            text_auto=True,
        )
        fig_heat.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig_heat.update_traces(textfont_color="white")
        st.plotly_chart(fig_heat, use_container_width=True, key="diag5_heatmap")
    else:
        st.info("Dados insuficientes para o mapa de risco com esse filtro.")

    # ===============================================================
    # ANÁLISE 6 — SERVIÇO SOLICITADO × CONVERSÃO
    # ===============================================================
    st.markdown("---")
    st.markdown("<h3 style='color:#FAFAFA'>📋 Diagnóstico 6 — Conversão por tipo de serviço</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Quais serviços convertem mais? Serviços com baixa conversão podem indicar processo de diagnóstico inadequado ou precificação fora do mercado.</p>", unsafe_allow_html=True)

    df_servico = df_unique[df_unique["item_carta"].notna()].copy()

    if df_servico.empty:
        st.info("Dados de serviço insuficientes para esse filtro.")
    else:
        # Simplifica nome do serviço removendo prefixos de formulário
        df_servico["servico"] = df_servico["item_carta"].str.replace(r"\[.*?\]\s*", "", regex=True).str.strip()
        df_servico["servico"] = df_servico["servico"].str.replace(r"solicitação de serviço\s*", "", regex=True, flags=0).str.strip()
        df_servico["servico"] = df_servico["servico"].str[:50]  # trunca nomes longos

        serv_analise = df_servico.groupby(["servico", "resultado"]).size().unstack(fill_value=0)
        for col in CORES:
            if col not in serv_analise.columns:
                serv_analise[col] = 0
        serv_analise = serv_analise[list(CORES.keys())]
        serv_analise["Total"] = serv_analise.sum(axis=1)
        serv_analise["Taxa de Conversão (%)"] = (serv_analise["Venda"] / serv_analise["Total"] * 100).round(1)
        serv_analise = serv_analise.sort_values("Total", ascending=False).reset_index()

        c1, c2 = st.columns([1.3, 1])
        with c1:
            df_melt_serv = serv_analise.melt(id_vars="servico", value_vars=list(CORES.keys()), var_name="Resultado", value_name="Leads")
            fig = px.bar(df_melt_serv, x="servico", y="Leads", color="Resultado",
                         color_discrete_map=CORES, barmode="stack",
                         labels={"servico": ""})
            fig.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-25)
            st.plotly_chart(fig, use_container_width=True, key="diag6_serv_vol")
        with c2:
            st.dataframe(
                serv_analise.set_index("servico").style
                    .background_gradient(subset=["Taxa de Conversão (%)"], cmap="Greens")
                    .format({"Taxa de Conversão (%)": "{:.1f}%"}),
                use_container_width=True, height=350
            )
# ============================================================
# PÁGINA — SITUAÇÃO DO CROSS SELLING
# ============================================================

def pagina_cross_selling(df):
    st.markdown("<h1 style='color:#FAFAFA;margin-bottom:4px'>🔀 Situação do Cross Selling</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;margin-bottom:24px'>Análise de leads qualificados por etapa do funil e quantos foram designados a mais de uma coordenação</p>", unsafe_allow_html=True)

    with open(CARDS_RAW_PATH, encoding="utf-8") as f:
        cards_raw = json.load(f)

    COORDENACOES = ["ACE", "CCE", "MNP", "PRO", "QAB"]

    def parse_lista(x):
        if not x or isinstance(x, float): return []
        if isinstance(x, str) and x.startswith("["):
            try: return json.loads(x)
            except: return [x]
        return [x]

    GRUPOS = {
        "Diagnóstico": ["4. Diagnóstico feito"],
        "Precificação/Aprovação": ["5. Precificação/Aprovação em andamento"],
        "Proposta": ["6. Proposta comercial feita", "7. Follow-up", "Venda"],
    }

    # Monta dados por card
    linhas = []
    for card in cards_raw:
        card_id = str(card.get("id"))
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        resultado = classificar_resultado(fase_atual)

        fases_visitadas = [ph.get("phase", {}).get("name") for ph in card.get("phases_history", [])]

        coords = []
        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name", "")
            valor = campo.get("value")
            if label == "Coordenação":
                coords = [c.strip() for c in parse_lista(valor) if c.strip() in COORDENACOES]

        n_coords = len(coords)
        tipo_coord = "1 Coordenação" if n_coords == 1 else "Múltiplas Coordenações" if n_coords > 1 else "Sem coordenação"

        # Identifica em qual grupo o card se encaixa (pega o mais avançado)
        grupo_card = None
        for grupo, fases in reversed(list(GRUPOS.items())):
            if any(f in fases_visitadas for f in fases):
                grupo_card = grupo
                break

        if not grupo_card:
            continue

        linhas.append({
            "card_id": card_id,
            "titulo": card.get("title"),
            "fase_atual": fase_atual,
            "resultado": resultado,
            "grupo": grupo_card,
            "coordenacoes": ", ".join(coords) if coords else "Sem coordenação",
            "n_coordenacoes": n_coords,
            "tipo_coord": tipo_coord,
        })

    df_cs = pd.DataFrame(linhas)

    if df_cs.empty:
        st.error("Nenhum dado encontrado.")
        return

    # -------------------------------------------------------
    # KPIs GERAIS
    # -------------------------------------------------------
    total = len(df_cs)
    multi = len(df_cs[df_cs["n_coordenacoes"] > 1])
    unica = len(df_cs[df_cs["n_coordenacoes"] == 1])
    sem = len(df_cs[df_cs["n_coordenacoes"] == 0])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #3b82f6">
            <div class="label">Total Qualificados</div>
            <div class="value" style="color:#3b82f6">{total}</div>
            <div class="sub">chegaram até Diagnóstico ou além</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #8b5cf6">
            <div class="label">Múltiplas Coordenações</div>
            <div class="value" style="color:#8b5cf6">{multi}</div>
            <div class="sub">{round(multi/total*100,1) if total else 0}% dos qualificados</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #22c55e">
            <div class="label">1 Coordenação</div>
            <div class="value" style="color:#22c55e">{unica}</div>
            <div class="sub">{round(unica/total*100,1) if total else 0}% dos qualificados</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #A3A3A3">
            <div class="label">Sem Coordenação</div>
            <div class="value" style="color:#A3A3A3">{sem}</div>
            <div class="sub">{round(sem/total*100,1) if total else 0}% dos qualificados</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # ANÁLISE POR GRUPO
    # -------------------------------------------------------
    ORDEM_GRUPOS = ["Diagnóstico", "Precificação/Aprovação", "Proposta"]
    CORES_GRUPOS = {
        "1 Coordenação": "#22c55e",
        "Múltiplas Coordenações": FLUXO_ORANGE_LIGHT,
        "Sem coordenação": "#A3A3A3",
    }

    st.markdown("<div class='section-title'>📊 Distribuição por Etapa do Funil</div>", unsafe_allow_html=True)

    # Cards por grupo e tipo de coordenação
    resumo = df_cs.groupby(["grupo", "tipo_coord"]).size().unstack(fill_value=0).reindex(ORDEM_GRUPOS)
    for col in CORES_GRUPOS:
        if col not in resumo.columns:
            resumo[col] = 0
    resumo = resumo[list(CORES_GRUPOS.keys())]
    resumo["Total"] = resumo.sum(axis=1)
    resumo["% Cross Selling"] = (resumo["Múltiplas Coordenações"] / resumo["Total"] * 100).round(1)

    c1, c2 = st.columns([1.4, 1])
    with c1:
        df_melt = resumo.reset_index().melt(id_vars="grupo", value_vars=list(CORES_GRUPOS.keys()), var_name="Tipo", value_name="Cards")
        fig = px.bar(df_melt, x="grupo", y="Cards", color="Tipo",
                     color_discrete_map=CORES_GRUPOS, barmode="stack",
                     category_orders={"grupo": ORDEM_GRUPOS},
                     labels={"grupo": "", "Cards": "Leads", "Tipo": "Coordenação"},
                     text="Cards")
        fig.update_traces(textfont_color="white", textposition="inside")
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True, key="cs_grupo_barra")

    with c2:
        st.markdown("<div class='section-title'>Tabela Resumo</div>", unsafe_allow_html=True)
        st.dataframe(
            resumo.style
                .background_gradient(subset=["% Cross Selling"], cmap="Purples")
                .format({"% Cross Selling": "{:.1f}%"}),
            use_container_width=True, height=220
        )

    # -------------------------------------------------------
    # DETALHAMENTO POR GRUPO
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>🔍 Detalhamento por Etapa</div>", unsafe_allow_html=True)

    grupo_sel = st.radio("Selecione a etapa:", ORDEM_GRUPOS, horizontal=True, key="cs_grupo_sel")
    df_grupo = df_cs[df_cs["grupo"] == grupo_sel]

    total_g = len(df_grupo)
    multi_g = len(df_grupo[df_grupo["n_coordenacoes"] > 1])
    unica_g = len(df_grupo[df_grupo["n_coordenacoes"] == 1])
    sem_g = len(df_grupo[df_grupo["n_coordenacoes"] == 0])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #3b82f6">
            <div class="label">Total em {grupo_sel}</div>
            <div class="value" style="color:#3b82f6">{total_g}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #8b5cf6">
            <div class="label">Múltiplas Coords</div>
            <div class="value" style="color:#8b5cf6">{multi_g}</div>
            <div class="sub">{round(multi_g/total_g*100,1) if total_g else 0}%</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #22c55e">
            <div class="label">1 Coordenação</div>
            <div class="value" style="color:#22c55e">{unica_g}</div>
            <div class="sub">{round(unica_g/total_g*100,1) if total_g else 0}%</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #A3A3A3">
            <div class="label">Sem Coordenação</div>
            <div class="value" style="color:#A3A3A3">{sem_g}</div>
            <div class="sub">{round(sem_g/total_g*100,1) if total_g else 0}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='section-title'>Combinações de coordenações mais frequentes</div>", unsafe_allow_html=True)
        combos = df_grupo[df_grupo["n_coordenacoes"] > 1]["coordenacoes"].value_counts().reset_index()
        combos.columns = ["Combinação", "Total"]
        if combos.empty:
            st.info("Nenhum card com múltiplas coordenações nessa etapa.")
        else:
            fig2 = px.bar(combos, x="Total", y="Combinação", orientation="h",
                          color="Total",
                          color_continuous_scale=SCALE_ORANGE,
                          text="Total",
                          labels={"Combinação": ""})
            fig2.update_traces(textfont_color="white", textposition="outside")
            fig2.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
            fig2.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig2, use_container_width=True, key=f"cs_combos_{grupo_sel}")

    with c2:
        st.markdown("<div class='section-title'>Resultado por tipo de coordenação</div>", unsafe_allow_html=True)
        res_tipo = df_grupo.groupby(["tipo_coord", "resultado"]).size().unstack(fill_value=0)
        for col in CORES:
            if col not in res_tipo.columns:
                res_tipo[col] = 0
        res_tipo = res_tipo[list(CORES.keys())]
        res_tipo["Total"] = res_tipo.sum(axis=1)
        res_tipo["Taxa de Venda (%)"] = (res_tipo["Venda"] / res_tipo["Total"] * 100).round(1)
        st.dataframe(
            res_tipo.style
                .background_gradient(subset=["Taxa de Venda (%)"], cmap="Greens")
                .format({"Taxa de Venda (%)": "{:.1f}%"}),
            use_container_width=True, height=220
        )

    # Lista completa
    st.markdown("<div class='section-title'>📄 Lista de Cards</div>", unsafe_allow_html=True)
    filtro_tipo = st.selectbox("Filtrar por tipo de coordenação:", ["Todos", "1 Coordenação", "Múltiplas Coordenações", "Sem coordenação"], key=f"cs_filtro_{grupo_sel}")

    df_lista = df_grupo.copy()
    if filtro_tipo != "Todos":
        df_lista = df_lista[df_lista["tipo_coord"] == filtro_tipo]

    st.dataframe(
        df_lista[["titulo", "coordenacoes", "n_coordenacoes", "fase_atual", "resultado"]]
            .rename(columns={
                "titulo": "Card",
                "coordenacoes": "Coordenações",
                "n_coordenacoes": "Nº Coords",
                "fase_atual": "Fase Atual",
                "resultado": "Resultado"
            }),
        use_container_width=True,
        height=400
    )

# ============================================================
# PÁGINA — TAMANHO DE EMPRESA
# Adicione esta função ao dashboard.py
# No menu da sidebar adicione: "🏭  Tamanho de Empresa"
# No main adicione: elif "Tamanho" in pagina: pagina_tamanho_empresa(df)
# ============================================================

def pagina_tamanho_empresa(df):
    from datetime import datetime

    st.markdown("<h1 style='color:#FAFAFA;margin-bottom:4px'>🏭 Tamanho de Empresa</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;margin-bottom:24px'>Ticket médio, volume e conversão por tamanho de empresa</p>", unsafe_allow_html=True)

    with open(CARDS_RAW_PATH, encoding="utf-8") as f:
        cards_raw = json.load(f)

    COORDENACOES = ["ACE", "CCE", "MNP", "PRO", "QAB"]
    ORDEM_TAMANHO = ["Pessoa física", "Pequena", "Média", "Grande"]

    def parse_lista(x):
        if not x or isinstance(x, float): return []
        if isinstance(x, str) and x.startswith("["):
            try: return json.loads(x)
            except: return [x]
        return [x]

    def parse_valor(v):
        if not v: return None
        try:
            s = str(v).strip()
            # Formato BR: 3.985,00 → remove pontos, troca vírgula por ponto
            s = s.replace(".", "").replace(",", ".")
            return float(s)
        except:
            return None

    def get_ciclo(dt):
        if dt is None: return "⚪ Fora dos ciclos"
        if datetime(2025, 10, 1) <= dt <= datetime(2025, 12, 31, 23, 59, 59):
            return "🔵 Ciclo 1 (Out-Dez 2025)"
        elif datetime(2026, 1, 1) <= dt <= datetime(2026, 3, 31, 23, 59, 59):
            return "🟣 Ciclo 2 (Jan-Mar 2026)"
        elif datetime(2026, 4, 1) <= dt <= datetime(2026, 6, 30, 23, 59, 59):
            return "🟡 Ciclo 3 (Abr-Jun 2026)"
        return "⚪ Fora dos ciclos"

    # -------------------------------------------------------
    # Monta DataFrame com TODOS os cards (não só vendas)
    # para calcular conversão por tamanho
    # -------------------------------------------------------
    linhas = []
    for card in cards_raw:
        card_id = str(card.get("id"))
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        resultado = classificar_resultado(fase_atual)
        responsaveis = [a["name"].strip() for a in card.get("assignees", [])]

        tamanho = None
        valor_proposta = None
        coords = []
        canal = None
        item_carta = None

        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name", "")
            valor = campo.get("value")
            if label == "Tamanho da empresa":
                tamanho = valor
            elif label == "Valor da proposta":
                valor_proposta = parse_valor(valor)
            elif label == "Coordenação":
                coords = [c.strip() for c in parse_lista(valor) if c.strip() in COORDENACOES]
            elif label == "Canal de aquisição":
                canal = valor
            elif label == "Ítem de carta":
                item_carta = valor

        if not tamanho:
            continue

        # Data de venda para ciclo
        data_venda = None
        updated_at_raw = card.get("updated_at")
        try:
            updated_at = datetime.strptime(updated_at_raw[:19], "%Y-%m-%dT%H:%M:%S") if updated_at_raw else None
        except:
            updated_at = None

        if resultado == "Venda":
            for ph in card.get("phases_history", []):
                if ph.get("phase", {}).get("name") == "Venda":
                    fit = ph.get("firstTimeIn")
                    if fit:
                        try:
                            data_venda = datetime.strptime(fit[:19], "%Y-%m-%dT%H:%M:%S")
                        except:
                            pass

        ciclo = get_ciclo(data_venda if data_venda else updated_at)

        for resp in (responsaveis if responsaveis else ["Sem responsável"]):
            linhas.append({
                "card_id": card_id,
                "resultado": resultado,
                "tamanho": tamanho.strip(),
                "valor_proposta": valor_proposta,
                "coordenacoes": ", ".join(coords) if coords else "Sem coordenação",
                "canal": canal if canal else "Não informado",
                "item_carta": item_carta,
                "responsavel": resp,
                "ciclo": ciclo,
                "data_venda": data_venda,
            })

    df_tam = pd.DataFrame(linhas)

    if df_tam.empty:
        st.error("Nenhum dado de tamanho de empresa encontrado.")
        return

    # -------------------------------------------------------
    # FILTRO DE CICLO
    # -------------------------------------------------------
    CICLOS = [
        "Todos os ciclos",
        "🔵 Ciclo 1 (Out-Dez 2025)",
        "🟣 Ciclo 2 (Jan-Mar 2026)",
        "🟡 Ciclo 3 (Abr-Jun 2026)",
        "⚪ Fora dos ciclos",
    ]

    ciclo_sel = st.radio("Filtrar por ciclo:", CICLOS, horizontal=True, key="tam_ciclo")
    if ciclo_sel != "Todos os ciclos":
        df_tam = df_tam[df_tam["ciclo"] == ciclo_sel]

    if df_tam.empty:
        st.warning("Nenhum dado para esse ciclo.")
        return

    df_unique = df_tam.drop_duplicates(subset=["card_id"])

    # -------------------------------------------------------
    # KPIs GERAIS
    # -------------------------------------------------------
    df_vendas = df_unique[df_unique["resultado"] == "Venda"]
    total_vendas = len(df_vendas)
    ticket_medio_geral = df_vendas["valor_proposta"].mean()
    ticket_medio_fmt = f"R$ {ticket_medio_geral:,.0f}".replace(",", ".") if pd.notna(ticket_medio_geral) else "N/A"
    receita_total = df_vendas["valor_proposta"].sum()
    receita_fmt = f"R$ {receita_total:,.0f}".replace(",", ".") if pd.notna(receita_total) else "N/A"
    tamanho_mais_vendas = df_vendas["tamanho"].value_counts().idxmax() if not df_vendas.empty else "-"
    maior_ticket_tam = df_vendas.groupby("tamanho")["valor_proposta"].mean().idxmax() if not df_vendas["valor_proposta"].isna().all() else "-"

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub, cor in [
        (c1, "Total de Vendas", total_vendas, "com tamanho informado", "#22c55e"),
        (c2, "Ticket Médio Geral", ticket_medio_fmt, "média de todas as vendas", FLUXO_ORANGE),
        (c3, "Receita Total", receita_fmt, "soma das propostas", "#f59e0b"),
        (c4, "Maior Ticket Médio", maior_ticket_tam, "segmento com maior valor médio", FLUXO_ORANGE_LIGHT),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card" style="border-top:3px solid {cor}">
                <div class="label">{label}</div>
                <div class="value" style="color:{cor};font-size:{'28px' if len(str(val)) > 6 else '36px'}">{val}</div>
                <div class="sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # ANÁLISE PRINCIPAL — TICKET MÉDIO POR TAMANHO
    # -------------------------------------------------------
    st.markdown("<div class='section-title'>💰 Ticket Médio por Tamanho de Empresa</div>", unsafe_allow_html=True)

    ticket_tam = df_vendas.groupby("tamanho").agg(
        Vendas=("card_id", "count"),
        Ticket_Medio=("valor_proposta", "mean"),
        Receita_Total=("valor_proposta", "sum"),
        Com_Valor=("valor_proposta", lambda x: x.notna().sum()),
    ).reset_index()
    ticket_tam["Ticket_Medio"] = ticket_tam["Ticket_Medio"].round(0)
    ticket_tam["Receita_Total"] = ticket_tam["Receita_Total"].round(0)

    # Ordena pela ordem lógica de tamanho
    ticket_tam["ordem"] = ticket_tam["tamanho"].apply(
        lambda x: ORDEM_TAMANHO.index(x) if x in ORDEM_TAMANHO else 99
    )
    ticket_tam = ticket_tam.sort_values("ordem").drop(columns="ordem")

    c1, c2 = st.columns([1.4, 1])
    with c1:
        fig = px.bar(
            ticket_tam,
            x="tamanho",
            y="Ticket_Medio",
            color="Ticket_Medio",
            color_continuous_scale=["#1c3a1c", "#16a34a", "#86efac"],
            text="Ticket_Medio",
            labels={"tamanho": "", "Ticket_Medio": "Ticket Médio (R$)"},
            category_orders={"tamanho": ORDEM_TAMANHO},
        )
        fig.update_traces(
            texttemplate="R$ %{text:,.0f}",
            textfont_color="white",
            textposition="outside",
        )
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True, key="tam_ticket_bar")

    with c2:
        tabela_ticket = ticket_tam.copy()
        tabela_ticket["Ticket Médio"] = tabela_ticket["Ticket_Medio"].apply(
            lambda x: f"R$ {x:,.0f}".replace(",", ".") if pd.notna(x) else "N/A"
        )
        tabela_ticket["Receita Total"] = tabela_ticket["Receita_Total"].apply(
            lambda x: f"R$ {x:,.0f}".replace(",", ".") if pd.notna(x) else "N/A"
        )
        tabela_ticket["% Com Valor"] = (tabela_ticket["Com_Valor"] / tabela_ticket["Vendas"] * 100).round(1).astype(str) + "%"
        st.dataframe(
            tabela_ticket[["tamanho", "Vendas", "Ticket Médio", "Receita Total", "% Com Valor"]]
                .rename(columns={"tamanho": "Tamanho"}),
            use_container_width=True,
            height=250,
            hide_index=True,
        )

    # -------------------------------------------------------
    # VOLUME DE LEADS E CONVERSÃO POR TAMANHO
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>📊 Volume de Leads e Conversão por Tamanho</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Considera todos os leads com tamanho informado, não apenas os vendidos.</p>", unsafe_allow_html=True)

    conv_tam = df_unique.groupby(["tamanho", "resultado"]).size().unstack(fill_value=0)
    for col in CORES:
        if col not in conv_tam.columns:
            conv_tam[col] = 0
    conv_tam = conv_tam[list(CORES.keys())]
    conv_tam["Total"] = conv_tam.sum(axis=1)
    conv_tam["Taxa de Conversão (%)"] = (conv_tam["Venda"] / conv_tam["Total"] * 100).round(1)
    conv_tam = conv_tam.reset_index()
    conv_tam["ordem"] = conv_tam["tamanho"].apply(lambda x: ORDEM_TAMANHO.index(x) if x in ORDEM_TAMANHO else 99)
    conv_tam = conv_tam.sort_values("ordem").drop(columns="ordem")

    c1, c2 = st.columns(2)
    with c1:
        df_melt = conv_tam.melt(id_vars="tamanho", value_vars=list(CORES.keys()), var_name="Resultado", value_name="Leads")
        fig2 = px.bar(df_melt, x="tamanho", y="Leads", color="Resultado",
                      color_discrete_map=CORES, barmode="stack",
                      category_orders={"tamanho": ORDEM_TAMANHO},
                      labels={"tamanho": "", "Leads": "Leads"})
        fig2.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True, key="tam_volume_bar")

    with c2:
        fig3 = px.bar(
            conv_tam.sort_values("Taxa de Conversão (%)"),
            x="Taxa de Conversão (%)", y="tamanho", orientation="h",
            color="Taxa de Conversão (%)",
            color_continuous_scale=["#1c3a1c", "#16a34a", "#86efac"],
            text="Taxa de Conversão (%)",
            labels={"tamanho": ""}
        )
        fig3.update_traces(texttemplate="%{text}%", textfont_color="white")
        fig3.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True, key="tam_conv_bar")

    # -------------------------------------------------------
    # TICKET MÉDIO POR TAMANHO × COORDENAÇÃO
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>🏢 Ticket Médio por Tamanho × Coordenação</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Apenas vendas. Revela qual coordenação performa melhor em cada segmento.</p>", unsafe_allow_html=True)

    linhas_coord = []
    for _, row in df_vendas.iterrows():
        coords = [c.strip() for c in row["coordenacoes"].split(",") if c.strip() in COORDENACOES]
        if not coords:
            coords = ["Sem coordenação"]
        for coord in coords:
            linhas_coord.append({
                "tamanho": row["tamanho"],
                "coordenacao": coord,
                "valor_proposta": row["valor_proposta"],
            })

    df_coord_tam = pd.DataFrame(linhas_coord)
    df_coord_tam = df_coord_tam[df_coord_tam["coordenacao"].isin(COORDENACOES)]

    if not df_coord_tam.empty:
        pivot = df_coord_tam.groupby(["tamanho", "coordenacao"])["valor_proposta"].mean().round(0).unstack(fill_value=0)
        pivot = pivot.reindex([t for t in ORDEM_TAMANHO if t in pivot.index])

        fig4 = px.imshow(
            pivot,
            color_continuous_scale=["#0f172a", "#1c3a1c", "#16a34a", "#86efac"],
            labels={"x": "Coordenação", "y": "Tamanho", "color": "Ticket Médio (R$)"},
            aspect="auto",
            text_auto=True,
        )
        fig4.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=True)
        fig4.update_traces(textfont_color="white")
        st.plotly_chart(fig4, use_container_width=True, key="tam_coord_heatmap")

    # -------------------------------------------------------
    # DISTRIBUIÇÃO DE VALORES — BOX PLOT
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>📦 Distribuição dos Valores por Tamanho</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Dispersão dos valores de proposta dentro de cada segmento. Caixas largas indicam alta variação de preço.</p>", unsafe_allow_html=True)

    df_box = df_vendas[df_vendas["valor_proposta"].notna()].copy()
    if not df_box.empty:
        fig5 = px.box(
            df_box,
            x="tamanho",
            y="valor_proposta",
            color="tamanho",
            color_discrete_sequence=[FLUXO_ORANGE, "#22c55e", "#eab308", FLUXO_ORANGE_LIGHT],
            category_orders={"tamanho": ORDEM_TAMANHO},
            labels={"tamanho": "", "valor_proposta": "Valor da Proposta (R$)"},
            points="all",
        )
        fig5.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        st.plotly_chart(fig5, use_container_width=True, key="tam_box")

    # -------------------------------------------------------
    # CANAL DE AQUISIÇÃO × TAMANHO (só vendas)
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>📡 Canal de Aquisição × Tamanho de Empresa</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Quais canais trazem cada tipo de empresa para a venda.</p>", unsafe_allow_html=True)

    canal_tam = df_vendas.groupby(["canal", "tamanho"]).size().unstack(fill_value=0)
    canal_tam = canal_tam.reindex(columns=[t for t in ORDEM_TAMANHO if t in canal_tam.columns])
    canal_tam["Total"] = canal_tam.sum(axis=1)
    canal_tam = canal_tam.sort_values("Total", ascending=False).drop(columns="Total")

    if not canal_tam.empty:
        fig6 = px.imshow(
            canal_tam,
            color_continuous_scale=SCALE_ORANGE_SOFT,
            labels={"x": "Tamanho", "y": "Canal", "color": "Vendas"},
            aspect="auto",
            text_auto=True,
        )
        fig6.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig6.update_traces(textfont_color="white")
        st.plotly_chart(fig6, use_container_width=True, key="tam_canal_heatmap")

    # -------------------------------------------------------
    # TABELA COMPLETA DE VENDAS COM VALOR
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>📄 Lista de Vendas com Valor Informado</div>", unsafe_allow_html=True)

    filtro_tam = st.selectbox(
        "Filtrar por tamanho:",
        ["Todos"] + [t for t in ORDEM_TAMANHO if t in df_vendas["tamanho"].values],
        key="tam_filtro_lista"
    )

    df_lista = df_vendas[df_vendas["valor_proposta"].notna()].copy()
    if filtro_tam != "Todos":
        df_lista = df_lista[df_lista["tamanho"] == filtro_tam]

    df_lista = df_lista.sort_values("valor_proposta", ascending=False)
    df_lista["Valor"] = df_lista["valor_proposta"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    df_lista["Data Venda"] = df_lista["data_venda"].apply(lambda x: x.strftime("%d/%m/%Y") if x else "N/A")

    st.dataframe(
        df_lista[["tamanho", "canal", "coordenacoes", "Valor", "ciclo", "Data Venda", "responsavel"]]
            .rename(columns={
                "tamanho": "Tamanho",
                "canal": "Canal",
                "coordenacoes": "Coordenações",
                "ciclo": "Ciclo",
                "responsavel": "Responsável",
            }),
        use_container_width=True,
        height=420,
        hide_index=True,
    )

# ============================================================
# PÁGINA — PANORAMA DE VENDAS
# ============================================================

def pagina_vendas(df):
    st.markdown("<h1 style='color:#FAFAFA;margin-bottom:4px'>💰 Panorama de Vendas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;margin-bottom:24px'>Visão completa sobre todas as vendas realizadas</p>", unsafe_allow_html=True)

    with open(CARDS_RAW_PATH, encoding="utf-8") as f:
        cards_raw = json.load(f)

    from datetime import datetime

    def parse_lista(x):
        if not x or isinstance(x, float): return []
        if isinstance(x, str) and x.startswith("["):
            try: return json.loads(x)
            except: return [x]
        return [x]

    def get_ciclo(dt):
        if dt is None: return "⚪ Fora dos ciclos"
        if datetime(2025, 10, 1) <= dt <= datetime(2025, 12, 31, 23, 59, 59):
            return "🔵 Ciclo 1 (Out-Dez 2025)"
        elif datetime(2026, 1, 1) <= dt <= datetime(2026, 3, 31, 23, 59, 59):
            return "🟣 Ciclo 2 (Jan-Mar 2026)"
        elif datetime(2026, 4, 1) <= dt <= datetime(2026, 6, 30, 23, 59, 59):
            return "🟡 Ciclo 3 (Abr-Jun 2026)"
        return "⚪ Fora dos ciclos"

    COORDENACOES = ["ACE", "CCE", "MNP", "PRO", "QAB"]

    linhas = []
    for card in cards_raw:
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        if fase_atual != "Venda":
            continue

        card_id = str(card.get("id"))
        responsaveis = [a["name"].strip() for a in card.get("assignees", [])]

        canal = None
        coords = []
        valor_proposta = None
        item_carta = None
        nome_lead = None
        empresa = None
        tamanho = None

        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name", "")
            valor = campo.get("value")
            if label == "Canal de aquisição" and not canal:
                canal = valor
            elif label and "coord" in label.lower():
                coords = [c.strip() for c in parse_lista(valor)]
            elif label == "Valor da proposta" and not valor_proposta:
                valor_proposta = valor
            elif label == "Ítem de carta" and not item_carta:
                item_carta = valor
            elif label == "Nome do lead" and not nome_lead:
                nome_lead = valor
            elif label == "Empresa" and not empresa:
                empresa = valor
            elif label == "Tamanho da empresa" and not tamanho:
                tamanho = valor

        data_venda = None
        for ph in card.get("phases_history", []):
            if ph.get("phase", {}).get("name") == "Venda":
                fit = ph.get("firstTimeIn")
                if fit:
                    try:
                        data_venda = datetime.strptime(fit[:19], "%Y-%m-%dT%H:%M:%S")
                    except: pass

        ciclo = get_ciclo(data_venda)
        is_fidelizacao = canal and "fideliz" in canal.lower() if canal else False

        valor_num = None
        if valor_proposta:
            try:
                v = str(valor_proposta).replace(".", "").replace(",", ".").strip()
                valor_num = float(v)
            except: pass

        linhas.append({
            "card_id": card_id,
            "titulo": card.get("title"),
            "canal": canal if canal else "Não informado",
            "coordenacoes": ", ".join(coords) if coords else "Sem coordenação",
            "item_carta": item_carta,
            "valor_proposta": valor_num,
            "data_venda": data_venda,
            "ciclo": ciclo,
            "is_fidelizacao": is_fidelizacao,
            "responsavel": ", ".join(responsaveis),
        })

    df_vendas = pd.DataFrame(linhas)

    if df_vendas.empty:
        st.error("Nenhuma venda encontrada.")
        return

    # Filtro de ciclo
    CICLOS = ["Todos os ciclos", "🔵 Ciclo 1 (Out-Dez 2025)", "🟣 Ciclo 2 (Jan-Mar 2026)", "🟡 Ciclo 3 (Abr-Jun 2026)", "⚪ Fora dos ciclos"]
    ciclo_sel = st.radio("Filtrar por ciclo:", CICLOS, horizontal=True, key="vendas_ciclo")
    if ciclo_sel != "Todos os ciclos":
        df_vendas = df_vendas[df_vendas["ciclo"] == ciclo_sel]

    total = len(df_vendas)
    if total == 0:
        st.warning("Nenhuma venda neste ciclo.")
        return

    fidelizacoes = int(df_vendas["is_fidelizacao"].sum())
    nao_fidelizacoes = total - fidelizacoes
    pct_fidelizacao = round(fidelizacoes / total * 100, 1)
    valor_total = df_vendas["valor_proposta"].sum()
    valor_medio = df_vendas["valor_proposta"].mean()

    st.markdown("<br>", unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #22c55e">
            <div class="label">Total de Vendas</div>
            <div class="value" style="color:#22c55e">{total}</div>
            <div class="sub">cards na fase Venda</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #8b5cf6">
            <div class="label">Fidelizações</div>
            <div class="value" style="color:#8b5cf6">{fidelizacoes}</div>
            <div class="sub">{pct_fidelizacao}% das vendas</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #3b82f6">
            <div class="label">Novas Aquisições</div>
            <div class="value" style="color:#3b82f6">{nao_fidelizacoes}</div>
            <div class="sub">{round(nao_fidelizacoes/total*100,1)}% das vendas</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        valor_fmt = f"R$ {valor_total:,.0f}".replace(",", ".") if pd.notna(valor_total) else "N/A"
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #f59e0b">
            <div class="label">Receita Total</div>
            <div class="value" style="color:#f59e0b;font-size:22px">{valor_fmt}</div>
            <div class="sub">soma das propostas</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        medio_fmt = f"R$ {valor_medio:,.0f}".replace(",", ".") if pd.notna(valor_medio) else "N/A"
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #A3A3A3">
            <div class="label">Ticket Médio</div>
            <div class="value" style="color:#A3A3A3;font-size:22px">{medio_fmt}</div>
            <div class="sub">valor médio por venda</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Fidelização vs Nova Aquisição
    st.markdown("<div class='section-title'>🔄 Fidelização vs Nova Aquisição</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1.5])
    with c1:
        df_fid = pd.DataFrame({"Tipo": ["Fidelização", "Nova Aquisição"], "Total": [fidelizacoes, nao_fidelizacoes]})
        fig = px.pie(df_fid, names="Tipo", values="Total", hole=0.5,
                     color="Tipo", color_discrete_map={"Fidelização": FLUXO_ORANGE_LIGHT, "Nova Aquisição": FLUXO_ORANGE})
        fig.update_traces(textfont_color="white", textfont_size=13)
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True, key="vendas_fid_pizza")

    with c2:
        df_fid_canais = df_vendas[df_vendas["is_fidelizacao"]]["canal"].value_counts().reset_index()
        df_fid_canais.columns = ["Canal", "Total"]
        if not df_fid_canais.empty:
            fig2 = px.bar(df_fid_canais, x="Total", y="Canal", orientation="h",
                          color="Total", color_continuous_scale=SCALE_ORANGE,
                          text="Total", title="Tipos de Fidelização", labels={"Canal": ""})
            fig2.update_traces(textfont_color="white", textposition="outside")
            fig2.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
            fig2.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig2, use_container_width=True, key="vendas_fid_canais")

    with c3:
        st.markdown("<div class='section-title'>Detalhamento das Fidelizações</div>", unsafe_allow_html=True)
        df_fid_lista = df_vendas[df_vendas["is_fidelizacao"]][["titulo", "canal", "coordenacoes", "ciclo"]].rename(columns={
            "titulo": "Card", "canal": "Canal", "coordenacoes": "Coordenações", "ciclo": "Ciclo"})
        st.dataframe(df_fid_lista, use_container_width=True, height=280)

    # Canais de Aquisição
    st.markdown("---")
    st.markdown("<div class='section-title'>📡 Canais de Aquisição das Vendas</div>", unsafe_allow_html=True)
    canal_vendas = df_vendas.groupby("canal").agg(
        Total=("card_id", "count"),
        Fidelizacoes=("is_fidelizacao", "sum"),
    ).reset_index()
    canal_vendas["Novas Aquisições"] = canal_vendas["Total"] - canal_vendas["Fidelizacoes"]
    canal_vendas["% do Total"] = (canal_vendas["Total"] / canal_vendas["Total"].sum() * 100).round(1)
    canal_vendas = canal_vendas.sort_values("Total", ascending=False)

    c1, c2 = st.columns([1.4, 1])
    with c1:
        fig3 = px.bar(canal_vendas, x="canal", y="Total",
                      color="Total", color_continuous_scale=["#1c3a1c", "#16a34a", "#86efac"],
                      text="Total", labels={"canal": "", "Total": "Vendas"})
        fig3.update_traces(textfont_color="white", textposition="outside")
        fig3.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, xaxis_tickangle=-20)
        st.plotly_chart(fig3, use_container_width=True, key="vendas_canal_bar")
    with c2:
        st.dataframe(canal_vendas.set_index("canal").style
                     .background_gradient(subset=["Total"], cmap="Greens")
                     .format({"% do Total": "{:.1f}%", "Fidelizacoes": "{:.0f}"}),
                     use_container_width=True, height=320)

    # Vendas por Coordenação
    st.markdown("---")
    st.markdown("<div class='section-title'>🏢 Vendas por Coordenação</div>", unsafe_allow_html=True)
    linhas_coord = []
    for _, row in df_vendas.iterrows():
        coords = [c.strip() for c in row["coordenacoes"].split(",") if c.strip() in COORDENACOES]
        if not coords: coords = ["Sem coordenação"]
        for coord in coords:
            linhas_coord.append({"coordenacao": coord, "is_fidelizacao": row["is_fidelizacao"]})

    df_coord_vendas = pd.DataFrame(linhas_coord)
    coord_analise = df_coord_vendas.groupby("coordenacao").agg(
        Total=("coordenacao", "count"), Fidelizacoes=("is_fidelizacao", "sum")).reset_index()
    coord_analise["Novas"] = coord_analise["Total"] - coord_analise["Fidelizacoes"]
    coord_analise = coord_analise[coord_analise["coordenacao"].isin(COORDENACOES)].sort_values("Total", ascending=False)

    c1, c2 = st.columns([1.4, 1])
    with c1:
        df_melt_coord = coord_analise.melt(id_vars="coordenacao", value_vars=["Fidelizacoes", "Novas"],
                                            var_name="Tipo", value_name="Vendas")
        fig4 = px.bar(df_melt_coord, x="coordenacao", y="Vendas", color="Tipo",
                      color_discrete_map={"Fidelizacoes": FLUXO_ORANGE_LIGHT, "Novas": FLUXO_ORANGE},
                      barmode="stack", text="Vendas", labels={"coordenacao": ""})
        fig4.update_traces(textfont_color="white", textposition="inside")
        fig4.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig4, use_container_width=True, key="vendas_coord_bar")
    with c2:
        st.dataframe(coord_analise.set_index("coordenacao"), use_container_width=True, height=280)

    # Itens de Carta
    st.markdown("---")
    st.markdown("<div class='section-title'>📋 Itens de Carta — Vendas e Taxa de Conversão</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Quantidade de vendas por serviço e taxa de conversão proposta → venda</p>", unsafe_allow_html=True)

    itens_proposta = {}
    itens_venda = {}
    for card in cards_raw:
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        resultado = classificar_resultado(fase_atual)
        fases_visitadas = [ph.get("phase", {}).get("name") for ph in card.get("phases_history", [])]
        chegou_proposta = any(f in fases_visitadas for f in ["6. Proposta comercial feita", "7. Follow-up", "Venda"])
        if not chegou_proposta:
            continue
        item = None
        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name", "")
            valor = campo.get("value")
            if label == "Ítem de carta" and valor:
                item = str(valor).strip()
                break
        if not item:
            item = "Não informado"
        itens_proposta[item] = itens_proposta.get(item, 0) + 1
        if resultado == "Venda":
            itens_venda[item] = itens_venda.get(item, 0) + 1

    rows_itens = []
    for item, total_prop in itens_proposta.items():
        vendas_item = itens_venda.get(item, 0)
        rows_itens.append({
            "Item de Carta": item,
            "Propostas": total_prop,
            "Vendas": vendas_item,
            "Taxa de Conversão (%)": round(vendas_item / total_prop * 100, 1) if total_prop else 0,
        })

    df_itens = pd.DataFrame(rows_itens).sort_values("Vendas", ascending=False)

    c1, c2 = st.columns([1.4, 1])
    with c1:
        fig_itens = px.bar(df_itens.head(15).sort_values("Vendas"),
                           x="Vendas", y="Item de Carta", orientation="h",
                           color="Taxa de Conversão (%)",
                           color_continuous_scale=["#1c3a1c", "#16a34a", "#86efac"],
                           text="Vendas", labels={"Item de Carta": ""})
        fig_itens.update_traces(textfont_color="white", textposition="outside")
        fig_itens.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=True)
        st.plotly_chart(fig_itens, use_container_width=True, key="vendas_itens_bar")
    with c2:
        df_taxa_itens = df_itens[df_itens["Propostas"] >= 2].sort_values("Taxa de Conversão (%)", ascending=False).head(15)
        fig_taxa = px.bar(df_taxa_itens.sort_values("Taxa de Conversão (%)"),
                          x="Taxa de Conversão (%)", y="Item de Carta", orientation="h",
                          color="Taxa de Conversão (%)",
                          color_continuous_scale=["#1c3a1c", "#16a34a", "#86efac"],
                          text="Taxa de Conversão (%)", labels={"Item de Carta": ""})
        fig_taxa.update_traces(texttemplate="%{text}%", textfont_color="white")
        fig_taxa.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig_taxa, use_container_width=True, key="vendas_itens_taxa")

    st.markdown("<div class='section-title'>Tabela Completa de Itens</div>", unsafe_allow_html=True)
    st.dataframe(
        df_itens.set_index("Item de Carta").style
            .background_gradient(subset=["Vendas"], cmap="Greens")
            .background_gradient(subset=["Taxa de Conversão (%)"], cmap="Blues")
            .format({"Taxa de Conversão (%)": "{:.1f}%"}),
        use_container_width=True, height=400
    )

    # Lista completa de vendas
    st.markdown("---")
    st.markdown("<div class='section-title'>📄 Lista Completa de Vendas</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        filtro_canal = st.selectbox("Filtrar por canal:", ["Todos"] + sorted(df_vendas["canal"].unique().tolist()), key="vendas_filtro_canal")
    with col2:
        filtro_fid = st.selectbox("Filtrar por tipo:", ["Todos", "Fidelização", "Nova Aquisição"], key="vendas_filtro_fid")

    df_lista = df_vendas.copy()
    if filtro_canal != "Todos":
        df_lista = df_lista[df_lista["canal"] == filtro_canal]
    if filtro_fid == "Fidelização":
        df_lista = df_lista[df_lista["is_fidelizacao"]]
    elif filtro_fid == "Nova Aquisição":
        df_lista = df_lista[~df_lista["is_fidelizacao"]]

    df_lista["data_venda_fmt"] = df_lista["data_venda"].apply(lambda x: x.strftime("%d/%m/%Y") if x else "N/A")
    df_lista["valor_fmt"] = df_lista["valor_proposta"].apply(lambda x: f"R$ {x:,.0f}".replace(",", ".") if pd.notna(x) else "N/A")

    st.dataframe(
        df_lista[["titulo", "canal", "coordenacoes", "ciclo", "data_venda_fmt", "valor_fmt", "responsavel"]]
            .rename(columns={
                "titulo": "Card", "canal": "Canal", "coordenacoes": "Coordenações",
                "ciclo": "Ciclo", "data_venda_fmt": "Data da Venda",
                "valor_fmt": "Valor", "responsavel": "Responsável"}),
        use_container_width=True, height=450
    )

# ============================================================
# PÁGINA — TAMANHO DE EMPRESA
# Adicione esta função ao dashboard.py
# No menu da sidebar adicione: "🏭  Tamanho de Empresa"
# No main adicione: elif "Tamanho" in pagina: pagina_tamanho_empresa(df)
# ============================================================

def pagina_tamanho_empresa(df):
    from datetime import datetime

    st.markdown("<h1 style='color:#FAFAFA;margin-bottom:4px'>🏭 Tamanho de Empresa</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;margin-bottom:24px'>Ticket médio, volume e conversão por tamanho de empresa</p>", unsafe_allow_html=True)

    with open(CARDS_RAW_PATH, encoding="utf-8") as f:
        cards_raw = json.load(f)

    COORDENACOES = ["ACE", "CCE", "MNP", "PRO", "QAB"]
    ORDEM_TAMANHO = ["Pessoa física", "Pequena", "Média", "Grande"]

    def parse_lista(x):
        if not x or isinstance(x, float): return []
        if isinstance(x, str) and x.startswith("["):
            try: return json.loads(x)
            except: return [x]
        return [x]

    def parse_valor(v):
        if not v: return None
        try:
            s = str(v).strip()
            # Formato BR: 3.985,00 → remove pontos, troca vírgula por ponto
            s = s.replace(".", "").replace(",", ".")
            return float(s)
        except:
            return None

    def get_ciclo(dt):
        if dt is None: return "⚪ Fora dos ciclos"
        if datetime(2025, 10, 1) <= dt <= datetime(2025, 12, 31, 23, 59, 59):
            return "🔵 Ciclo 1 (Out-Dez 2025)"
        elif datetime(2026, 1, 1) <= dt <= datetime(2026, 3, 31, 23, 59, 59):
            return "🟣 Ciclo 2 (Jan-Mar 2026)"
        elif datetime(2026, 4, 1) <= dt <= datetime(2026, 6, 30, 23, 59, 59):
            return "🟡 Ciclo 3 (Abr-Jun 2026)"
        return "⚪ Fora dos ciclos"

    # -------------------------------------------------------
    # Monta DataFrame com TODOS os cards (não só vendas)
    # para calcular conversão por tamanho
    # -------------------------------------------------------
    linhas = []
    for card in cards_raw:
        card_id = str(card.get("id"))
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        resultado = classificar_resultado(fase_atual)
        responsaveis = [a["name"].strip() for a in card.get("assignees", [])]

        tamanho = None
        valor_proposta = None
        coords = []
        canal = None
        item_carta = None

        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name", "")
            valor = campo.get("value")
            if label == "Tamanho da empresa":
                tamanho = valor
            elif label == "Valor da proposta":
                valor_proposta = parse_valor(valor)
            elif label == "Coordenação":
                coords = [c.strip() for c in parse_lista(valor) if c.strip() in COORDENACOES]
            elif label == "Canal de aquisição":
                canal = valor
            elif label == "Ítem de carta":
                item_carta = valor

        if not tamanho:
            continue

        # Data de venda para ciclo
        data_venda = None
        updated_at_raw = card.get("updated_at")
        try:
            updated_at = datetime.strptime(updated_at_raw[:19], "%Y-%m-%dT%H:%M:%S") if updated_at_raw else None
        except:
            updated_at = None

        if resultado == "Venda":
            for ph in card.get("phases_history", []):
                if ph.get("phase", {}).get("name") == "Venda":
                    fit = ph.get("firstTimeIn")
                    if fit:
                        try:
                            data_venda = datetime.strptime(fit[:19], "%Y-%m-%dT%H:%M:%S")
                        except:
                            pass

        ciclo = get_ciclo(data_venda if data_venda else updated_at)

        for resp in (responsaveis if responsaveis else ["Sem responsável"]):
            linhas.append({
                "card_id": card_id,
                "resultado": resultado,
                "tamanho": tamanho.strip(),
                "valor_proposta": valor_proposta,
                "coordenacoes": ", ".join(coords) if coords else "Sem coordenação",
                "canal": canal if canal else "Não informado",
                "item_carta": item_carta,
                "responsavel": resp,
                "ciclo": ciclo,
                "data_venda": data_venda,
            })

    df_tam = pd.DataFrame(linhas)

    if df_tam.empty:
        st.error("Nenhum dado de tamanho de empresa encontrado.")
        return

    # -------------------------------------------------------
    # FILTRO DE CICLO
    # -------------------------------------------------------
    CICLOS = [
        "Todos os ciclos",
        "🔵 Ciclo 1 (Out-Dez 2025)",
        "🟣 Ciclo 2 (Jan-Mar 2026)",
        "🟡 Ciclo 3 (Abr-Jun 2026)",
        "⚪ Fora dos ciclos",
    ]

    ciclo_sel = st.radio("Filtrar por ciclo:", CICLOS, horizontal=True, key="tam_ciclo")
    if ciclo_sel != "Todos os ciclos":
        df_tam = df_tam[df_tam["ciclo"] == ciclo_sel]

    if df_tam.empty:
        st.warning("Nenhum dado para esse ciclo.")
        return

    df_unique = df_tam.drop_duplicates(subset=["card_id"])

    # -------------------------------------------------------
    # KPIs GERAIS
    # -------------------------------------------------------
    df_vendas = df_unique[df_unique["resultado"] == "Venda"]
    total_vendas = len(df_vendas)
    ticket_medio_geral = df_vendas["valor_proposta"].mean()
    ticket_medio_fmt = f"R$ {ticket_medio_geral:,.0f}".replace(",", ".") if pd.notna(ticket_medio_geral) else "N/A"
    receita_total = df_vendas["valor_proposta"].sum()
    receita_fmt = f"R$ {receita_total:,.0f}".replace(",", ".") if pd.notna(receita_total) else "N/A"
    tamanho_mais_vendas = df_vendas["tamanho"].value_counts().idxmax() if not df_vendas.empty else "-"
    maior_ticket_tam = df_vendas.groupby("tamanho")["valor_proposta"].mean().idxmax() if not df_vendas["valor_proposta"].isna().all() else "-"

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub, cor in [
        (c1, "Total de Vendas", total_vendas, "com tamanho informado", "#22c55e"),
        (c2, "Ticket Médio Geral", ticket_medio_fmt, "média de todas as vendas", FLUXO_ORANGE),
        (c3, "Receita Total", receita_fmt, "soma das propostas", "#f59e0b"),
        (c4, "Maior Ticket Médio", maior_ticket_tam, "segmento com maior valor médio", FLUXO_ORANGE_LIGHT),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card" style="border-top:3px solid {cor}">
                <div class="label">{label}</div>
                <div class="value" style="color:{cor};font-size:{'28px' if len(str(val)) > 6 else '36px'}">{val}</div>
                <div class="sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # ANÁLISE PRINCIPAL — TICKET MÉDIO POR TAMANHO
    # -------------------------------------------------------
    st.markdown("<div class='section-title'>💰 Ticket Médio por Tamanho de Empresa</div>", unsafe_allow_html=True)

    ticket_tam = df_vendas.groupby("tamanho").agg(
        Vendas=("card_id", "count"),
        Ticket_Medio=("valor_proposta", "mean"),
        Receita_Total=("valor_proposta", "sum"),
        Com_Valor=("valor_proposta", lambda x: x.notna().sum()),
    ).reset_index()
    ticket_tam["Ticket_Medio"] = ticket_tam["Ticket_Medio"].round(0)
    ticket_tam["Receita_Total"] = ticket_tam["Receita_Total"].round(0)

    # Ordena pela ordem lógica de tamanho
    ticket_tam["ordem"] = ticket_tam["tamanho"].apply(
        lambda x: ORDEM_TAMANHO.index(x) if x in ORDEM_TAMANHO else 99
    )
    ticket_tam = ticket_tam.sort_values("ordem").drop(columns="ordem")

    c1, c2 = st.columns([1.4, 1])
    with c1:
        fig = px.bar(
            ticket_tam,
            x="tamanho",
            y="Ticket_Medio",
            color="Ticket_Medio",
            color_continuous_scale=["#1c3a1c", "#16a34a", "#86efac"],
            text="Ticket_Medio",
            labels={"tamanho": "", "Ticket_Medio": "Ticket Médio (R$)"},
            category_orders={"tamanho": ORDEM_TAMANHO},
        )
        fig.update_traces(
            texttemplate="R$ %{text:,.0f}",
            textfont_color="white",
            textposition="outside",
        )
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True, key="tam_ticket_bar")

    with c2:
        tabela_ticket = ticket_tam.copy()
        tabela_ticket["Ticket Médio"] = tabela_ticket["Ticket_Medio"].apply(
            lambda x: f"R$ {x:,.0f}".replace(",", ".") if pd.notna(x) else "N/A"
        )
        tabela_ticket["Receita Total"] = tabela_ticket["Receita_Total"].apply(
            lambda x: f"R$ {x:,.0f}".replace(",", ".") if pd.notna(x) else "N/A"
        )
        tabela_ticket["% Com Valor"] = (tabela_ticket["Com_Valor"] / tabela_ticket["Vendas"] * 100).round(1).astype(str) + "%"
        st.dataframe(
            tabela_ticket[["tamanho", "Vendas", "Ticket Médio", "Receita Total", "% Com Valor"]]
                .rename(columns={"tamanho": "Tamanho"}),
            use_container_width=True,
            height=250,
            hide_index=True,
        )

    # -------------------------------------------------------
    # VOLUME DE LEADS E CONVERSÃO POR TAMANHO
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>📊 Volume de Leads e Conversão por Tamanho</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Considera todos os leads com tamanho informado, não apenas os vendidos.</p>", unsafe_allow_html=True)

    conv_tam = df_unique.groupby(["tamanho", "resultado"]).size().unstack(fill_value=0)
    for col in CORES:
        if col not in conv_tam.columns:
            conv_tam[col] = 0
    conv_tam = conv_tam[list(CORES.keys())]
    conv_tam["Total"] = conv_tam.sum(axis=1)
    conv_tam["Taxa de Conversão (%)"] = (conv_tam["Venda"] / conv_tam["Total"] * 100).round(1)
    conv_tam = conv_tam.reset_index()
    conv_tam["ordem"] = conv_tam["tamanho"].apply(lambda x: ORDEM_TAMANHO.index(x) if x in ORDEM_TAMANHO else 99)
    conv_tam = conv_tam.sort_values("ordem").drop(columns="ordem")

    c1, c2 = st.columns(2)
    with c1:
        df_melt = conv_tam.melt(id_vars="tamanho", value_vars=list(CORES.keys()), var_name="Resultado", value_name="Leads")
        fig2 = px.bar(df_melt, x="tamanho", y="Leads", color="Resultado",
                      color_discrete_map=CORES, barmode="stack",
                      category_orders={"tamanho": ORDEM_TAMANHO},
                      labels={"tamanho": "", "Leads": "Leads"})
        fig2.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True, key="tam_volume_bar")

    with c2:
        fig3 = px.bar(
            conv_tam.sort_values("Taxa de Conversão (%)"),
            x="Taxa de Conversão (%)", y="tamanho", orientation="h",
            color="Taxa de Conversão (%)",
            color_continuous_scale=["#1c3a1c", "#16a34a", "#86efac"],
            text="Taxa de Conversão (%)",
            labels={"tamanho": ""}
        )
        fig3.update_traces(texttemplate="%{text}%", textfont_color="white")
        fig3.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True, key="tam_conv_bar")

    # -------------------------------------------------------
    # TICKET MÉDIO POR TAMANHO × COORDENAÇÃO
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>🏢 Ticket Médio por Tamanho × Coordenação</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Apenas vendas. Revela qual coordenação performa melhor em cada segmento.</p>", unsafe_allow_html=True)

    linhas_coord = []
    for _, row in df_vendas.iterrows():
        coords = [c.strip() for c in row["coordenacoes"].split(",") if c.strip() in COORDENACOES]
        if not coords:
            coords = ["Sem coordenação"]
        for coord in coords:
            linhas_coord.append({
                "tamanho": row["tamanho"],
                "coordenacao": coord,
                "valor_proposta": row["valor_proposta"],
            })

    df_coord_tam = pd.DataFrame(linhas_coord)
    df_coord_tam = df_coord_tam[df_coord_tam["coordenacao"].isin(COORDENACOES)]

    if not df_coord_tam.empty:
        pivot = df_coord_tam.groupby(["tamanho", "coordenacao"])["valor_proposta"].mean().round(0).unstack(fill_value=0)
        pivot = pivot.reindex([t for t in ORDEM_TAMANHO if t in pivot.index])

        fig4 = px.imshow(
            pivot,
            color_continuous_scale=["#0f172a", "#1c3a1c", "#16a34a", "#86efac"],
            labels={"x": "Coordenação", "y": "Tamanho", "color": "Ticket Médio (R$)"},
            aspect="auto",
            text_auto=True,
        )
        fig4.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=True)
        fig4.update_traces(textfont_color="white")
        st.plotly_chart(fig4, use_container_width=True, key="tam_coord_heatmap")

    # -------------------------------------------------------
    # DISTRIBUIÇÃO DE VALORES — BOX PLOT
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>📦 Distribuição dos Valores por Tamanho</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Dispersão dos valores de proposta dentro de cada segmento. Caixas largas indicam alta variação de preço.</p>", unsafe_allow_html=True)

    df_box = df_vendas[df_vendas["valor_proposta"].notna()].copy()
    if not df_box.empty:
        fig5 = px.box(
            df_box,
            x="tamanho",
            y="valor_proposta",
            color="tamanho",
            color_discrete_sequence=[FLUXO_ORANGE, "#22c55e", "#eab308", FLUXO_ORANGE_LIGHT],
            category_orders={"tamanho": ORDEM_TAMANHO},
            labels={"tamanho": "", "valor_proposta": "Valor da Proposta (R$)"},
            points="all",
        )
        fig5.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        st.plotly_chart(fig5, use_container_width=True, key="tam_box")

    # -------------------------------------------------------
    # CANAL DE AQUISIÇÃO × TAMANHO (só vendas)
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>📡 Canal de Aquisição × Tamanho de Empresa</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A3A3A3;font-size:13px'>Quais canais trazem cada tipo de empresa para a venda.</p>", unsafe_allow_html=True)

    canal_tam = df_vendas.groupby(["canal", "tamanho"]).size().unstack(fill_value=0)
    canal_tam = canal_tam.reindex(columns=[t for t in ORDEM_TAMANHO if t in canal_tam.columns])
    canal_tam["Total"] = canal_tam.sum(axis=1)
    canal_tam = canal_tam.sort_values("Total", ascending=False).drop(columns="Total")

    if not canal_tam.empty:
        fig6 = px.imshow(
            canal_tam,
            color_continuous_scale=SCALE_ORANGE_SOFT,
            labels={"x": "Tamanho", "y": "Canal", "color": "Vendas"},
            aspect="auto",
            text_auto=True,
        )
        fig6.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig6.update_traces(textfont_color="white")
        st.plotly_chart(fig6, use_container_width=True, key="tam_canal_heatmap")

    # -------------------------------------------------------
    # TABELA COMPLETA DE VENDAS COM VALOR
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>📄 Lista de Vendas com Valor Informado</div>", unsafe_allow_html=True)

    filtro_tam = st.selectbox(
        "Filtrar por tamanho:",
        ["Todos"] + [t for t in ORDEM_TAMANHO if t in df_vendas["tamanho"].values],
        key="tam_filtro_lista"
    )

    df_lista = df_vendas[df_vendas["valor_proposta"].notna()].copy()
    if filtro_tam != "Todos":
        df_lista = df_lista[df_lista["tamanho"] == filtro_tam]

    df_lista = df_lista.sort_values("valor_proposta", ascending=False)
    df_lista["Valor"] = df_lista["valor_proposta"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    df_lista["Data Venda"] = df_lista["data_venda"].apply(lambda x: x.strftime("%d/%m/%Y") if x else "N/A")

    st.dataframe(
        df_lista[["tamanho", "canal", "coordenacoes", "Valor", "ciclo", "Data Venda", "responsavel"]]
            .rename(columns={
                "tamanho": "Tamanho",
                "canal": "Canal",
                "coordenacoes": "Coordenações",
                "ciclo": "Ciclo",
                "responsavel": "Responsável",
            }),
        use_container_width=True,
        height=420,
        hide_index=True,
    )

# ============================================================
# PÁGINA — MOTIVO DA PERDA
# ============================================================

def pagina_motivo_perda(df):
    st.markdown(f"""
    <div class="page-header">
        <div class="icon">💔</div>
        <h1>Motivo da Perda</h1>
    </div>
    <div class="page-sub">Diagnóstico completo dos motivos que fizeram o lead ser perdido</div>
    """, unsafe_allow_html=True)

    with open(CARDS_RAW_PATH, encoding="utf-8") as f:
        cards_raw = json.load(f)

    # -------------------------------------------------------
    # FILTRO POR GESTÃO E CICLO (ancorado na data em que virou Perdido)
    # -------------------------------------------------------
    gestoes_presentes = sorted(
        {g for g in df.loc[df["resultado"] == "Perda", "gestao"].dropna().unique()},
        key=lambda s: int(s.split("/")[0]),
        reverse=True,
    )
    opcoes_gestao = ["Todas as gestões"] + gestoes_presentes
    default_gestao = "25/26" if "25/26" in gestoes_presentes else opcoes_gestao[0]

    gcol1, gcol2 = st.columns(2)
    with gcol1:
        st.selectbox(
            "Gestão",
            opcoes_gestao,
            index=opcoes_gestao.index(default_gestao) if default_gestao in opcoes_gestao else 0,
            key="mp_gestao_sel",
            help="Filtra pelas perdas cujo lead entrou na fase Perdido dentro da gestão selecionada. Gestão vai de out–set.",
        )
    with gcol2:
        if st.session_state["mp_gestao_sel"] != "Todas as gestões":
            st.selectbox(
                "Ciclo",
                ["Toda a gestão", "Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4"],
                key="mp_ciclo_sel",
                help="Ciclo 1 out–dez · Ciclo 2 jan–mar · Ciclo 3 abr–jun · Ciclo 4 jul–set.",
            )
        else:
            st.markdown("<div style='color:#737373;font-size:12px;margin-top:34px'>Ciclo indisponível quando 'Todas as gestões' está selecionado</div>", unsafe_allow_html=True)
            st.session_state.pop("mp_ciclo_sel", None)

    gestao_sel = st.session_state["mp_gestao_sel"]
    ciclo_sel = st.session_state.get("mp_ciclo_sel", "Toda a gestão")

    df_periodo = df[df["resultado"] == "Perda"].copy()
    if gestao_sel != "Todas as gestões":
        df_periodo = df_periodo[df_periodo["gestao"] == gestao_sel]
        if ciclo_sel != "Toda a gestão":
            df_periodo = df_periodo[df_periodo["ciclo"] == int(ciclo_sel.split()[-1])]

    ids_permitidos = set(df_periodo["id"].astype(str))

    COORDENACOES = ["ACE", "CCE", "MNP", "PRO", "QAB"]

    def parse_lista(x):
        if not x or isinstance(x, float): return []
        if isinstance(x, str) and x.startswith("["):
            try: return json.loads(x)
            except: return [x]
        return [x]

    # Monta DataFrame apenas com perdidos
    linhas = []
    for card in cards_raw:
        fase_atual = card.get("current_phase", {}).get("name") if card.get("current_phase") else None
        if fase_atual != "Perdido":
            continue

        card_id = str(card.get("id"))
        if card_id not in ids_permitidos:
            continue
        responsaveis = [a["name"].strip() for a in card.get("assignees", [])]

        motivo = None
        descricao_perda = None
        coords = []
        canal = None
        objecoes = []
        tamanho = None
        valor_proposta = None
        fases_visitadas = [ph.get("phase", {}).get("name") for ph in card.get("phases_history", [])]

        for campo in card.get("fields", []):
            label = campo.get("field", {}).get("label") or campo.get("name", "")
            valor = campo.get("value")
            if "motivo" in label.lower() and "perda" in label.lower():
                motivo = valor
            elif "descri" in label.lower() and "perda" in label.lower():
                descricao_perda = valor
            elif label == "Coordenação":
                coords = [c.strip() for c in parse_lista(valor) if c.strip() in COORDENACOES]
            elif label == "Canal de aquisição":
                canal = valor
            elif "obje" in label.lower():
                objecoes = parse_lista(valor)
            elif label == "Tamanho da empresa":
                tamanho = valor
            elif label == "Valor da proposta":
                try:
                    valor_proposta = float(str(valor).replace(".", "").replace(",", "."))
                except:
                    valor_proposta = None

        motivos_list = parse_lista(motivo) if motivo else ["Sem motivo informado"]
        if not motivos_list:
            motivos_list = ["Sem motivo informado"]

        # Fase onde o card morreu
        FASES_FUNIL = [
            "1. Oportunidade", "2. Contato aberto", "3. Pré-diagnóstico feito",
            "4. Diagnóstico feito", "5. Precificação/Aprovação em andamento",
            "6. Proposta comercial feita", "7. Follow-up",
        ]
        fases_no_funil = [f for f in fases_visitadas if f in FASES_FUNIL]
        fase_morte = fases_no_funil[-1] if fases_no_funil else "Não visitou funil"
        fase_morte_curta = fase_morte.split(". ")[-1] if ". " in fase_morte else fase_morte

        passou_diagnostico = "4. Diagnóstico feito" in fases_visitadas
        passou_precificacao = "5. Precificação/Aprovação em andamento" in fases_visitadas
        passou_proposta = "6. Proposta comercial feita" in fases_visitadas
        chegou_proposta = any(f in fases_visitadas for f in ["6. Proposta comercial feita", "7. Follow-up"])

        for m in motivos_list:
            linhas.append({
                "card_id": card_id,
                "titulo": card.get("title"),
                "motivo": m.strip() if isinstance(m, str) else "Sem motivo informado",
                "descricao": descricao_perda,
                "coordenacao": ", ".join(coords) if coords else "Sem coordenação",
                "coords_list": coords,
                "canal": canal if canal else "Não informado",
                "responsavel": ", ".join(responsaveis) if responsaveis else "Sem responsável",
                "resp_list": responsaveis if responsaveis else ["Sem responsável"],
                "fase_morte": fase_morte_curta,
                "chegou_proposta": chegou_proposta,
                "passou_diagnostico": passou_diagnostico,
                "passou_precificacao": passou_precificacao,
                "passou_proposta": passou_proposta,
                "tamanho": tamanho if tamanho else "Não informado",
                "valor_proposta": valor_proposta,
                "objecoes": objecoes,
            })

    df_perda = pd.DataFrame(linhas)

    if df_perda.empty:
        st.warning("Nenhum lead perdido encontrado.")
        return

    # -------------------------------------------------------
    # FILTRO POR ETAPA ATÉ ONDE O LEAD CHEGOU ANTES DE MORRER
    # -------------------------------------------------------
    FILTROS_ETAPA = {
        "Todos os perdidos": None,
        "Perdas pós-Diagnóstico": "passou_diagnostico",
        "Perdas pós-Precificação": "passou_precificacao",
        "Perdas pós-Proposta": "passou_proposta",
    }
    total_geral_cards = df_perda["card_id"].nunique()

    fcol1, fcol2 = st.columns([2, 1])
    with fcol1:
        etapa_sel = st.radio(
            "Recorte da análise",
            list(FILTROS_ETAPA.keys()),
            horizontal=True,
            key="mp_filtro_etapa",
            help="Filtra a página inteira para leads perdidos que passaram por determinada etapa antes de morrer.",
        )
    flag = FILTROS_ETAPA[etapa_sel]
    if flag is not None:
        df_perda = df_perda[df_perda[flag]].copy()

    if df_perda.empty:
        st.info(f"Nenhum lead perdido se encaixa no recorte '{etapa_sel}'.")
        return

    cards_no_recorte = df_perda["card_id"].nunique()
    with fcol2:
        st.markdown(
            f"<div style='padding:10px 14px;background:{BG_CARD};border:1px solid {BORDER};"
            f"border-radius:10px;text-align:right'>"
            f"<span style='color:{TEXT_SECONDARY};font-size:12px'>Cards no recorte</span><br>"
            f"<span style='color:{FLUXO_ORANGE};font-size:20px;font-weight:700'>{cards_no_recorte}</span>"
            f"<span style='color:{TEXT_MUTED};font-size:12px'> de {total_geral_cards}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    df_unique = df_perda.drop_duplicates(subset=["card_id"])
    total_perdidos = df_unique["card_id"].nunique()
    com_motivo = df_unique[df_unique["motivo"] != "Sem motivo informado"]["card_id"].nunique()
    sem_motivo = total_perdidos - com_motivo
    pct_documentado = round(com_motivo / total_perdidos * 100, 1) if total_perdidos else 0
    motivo_mais_comum = (
        df_perda[df_perda["motivo"] != "Sem motivo informado"]["motivo"].value_counts().idxmax()
        if not df_perda[df_perda["motivo"] != "Sem motivo informado"].empty else "-"
    )

    # -------------------------------------------------------
    # KPIs GERAIS
    # -------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub, cor in [
        (c1, "Total de Perdidos", total_perdidos, "cards na fase Perdido", "#EF4444"),
        (c2, "Com motivo documentado", com_motivo, f"{pct_documentado}% do total", FLUXO_ORANGE),
        (c3, "Sem motivo", sem_motivo, f"{round(sem_motivo/total_perdidos*100,1) if total_perdidos else 0}% do total", "#EAB308"),
        (c4, "Motivo mais frequente", motivo_mais_comum, "principal razão de perda", FLUXO_ORANGE_LIGHT),
    ]:
        with col:
            font_size = "22px" if isinstance(val, str) and len(val) > 8 else "34px"
            st.markdown(f"""<div class="metric-card" style="border-top: 3px solid {cor}">
                <div class="label">{label}</div>
                <div class="value" style="color:{cor};font-size:{font_size}">{val}</div>
                <div class="sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # RANKING DE MOTIVOS
    # -------------------------------------------------------
    st.markdown("<div class='section-title'>Ranking dos Motivos de Perda</div>", unsafe_allow_html=True)

    ranking = df_perda["motivo"].value_counts().reset_index()
    ranking.columns = ["Motivo", "Total"]
    ranking["% do total"] = (ranking["Total"] / ranking["Total"].sum() * 100).round(1)

    c1, c2 = st.columns([1.4, 1])
    with c1:
        fig = px.bar(
            ranking.sort_values("Total"),
            x="Total", y="Motivo", orientation="h",
            color="Total", color_continuous_scale=SCALE_ORANGE,
            text="Total", labels={"Motivo": ""}
        )
        fig.update_traces(textfont_color=TEXT_PRIMARY, textposition="outside")
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, height=440)
        st.plotly_chart(fig, use_container_width=True, key="mp_ranking")

    with c2:
        fig_pie = px.pie(
            ranking, names="Motivo", values="Total", hole=0.55,
            color_discrete_sequence=[
                FLUXO_ORANGE, "#EF4444", "#EAB308", "#22c55e",
                FLUXO_ORANGE_LIGHT, "#A855F7", "#0EA5E9", "#EC4899", "#94A3B8"
            ]
        )
        fig_pie.update_traces(textfont_color="#000", textfont_size=12, textinfo="percent")
        fig_pie.update_layout(**PLOTLY_LAYOUT, height=440)
        fig_pie.update_layout(legend=dict(orientation="v", x=1.05, y=0.5,
                                          font=dict(color=TEXT_PRIMARY, size=11)))
        st.plotly_chart(fig_pie, use_container_width=True, key="mp_pie")

    # -------------------------------------------------------
    # MOTIVO × FASE ONDE MORREU
    # -------------------------------------------------------
    st.markdown("<div class='section-title'>Motivo × Fase onde o lead morreu</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{TEXT_SECONDARY};font-size:13px'>Mostra em qual etapa do funil cada motivo mais aparece — permite ver se o problema é qualificação (fases iniciais) ou proposta (fases finais).</p>", unsafe_allow_html=True)

    matriz_fase = df_perda.groupby(["motivo", "fase_morte"]).size().unstack(fill_value=0)
    ordem_fases_curtas = [f.split(". ")[-1] if ". " in f else f for f in [
        "1. Oportunidade", "2. Contato aberto", "3. Pré-diagnóstico feito",
        "4. Diagnóstico feito", "5. Precificação/Aprovação em andamento",
        "6. Proposta comercial feita", "7. Follow-up",
    ]]
    ordem_presentes = [f for f in ordem_fases_curtas if f in matriz_fase.columns]
    if ordem_presentes:
        matriz_fase = matriz_fase[ordem_presentes]

    if not matriz_fase.empty:
        fig_heat = px.imshow(
            matriz_fase,
            color_continuous_scale=SCALE_ORANGE_SOFT,
            labels={"x": "Fase", "y": "Motivo", "color": "Perdidos"},
            aspect="auto", text_auto=True,
        )
        fig_heat.update_layout(**PLOTLY_LAYOUT, height=460)
        fig_heat.update_traces(textfont_color="#000")
        st.plotly_chart(fig_heat, use_container_width=True, key="mp_fase_heatmap")

    # -------------------------------------------------------
    # FILTROS E CRUZAMENTOS
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>Cruzamentos — Motivo por segmento</div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Coordenação", "Canal", "Responsável", "Tamanho de Empresa"])

    with tab1:
        df_coord = df_perda.explode("coords_list").dropna(subset=["coords_list"])
        df_coord = df_coord[df_coord["coords_list"].isin(COORDENACOES)]
        if not df_coord.empty:
            matriz = df_coord.groupby(["motivo", "coords_list"]).size().unstack(fill_value=0)
            fig = px.imshow(matriz, color_continuous_scale=SCALE_ORANGE_SOFT,
                            labels={"x": "Coordenação", "y": "Motivo", "color": "Perdidos"},
                            aspect="auto", text_auto=True)
            fig.update_layout(**PLOTLY_LAYOUT, height=420)
            fig.update_traces(textfont_color="#000")
            st.plotly_chart(fig, use_container_width=True, key="mp_coord_heat")

            st.markdown("<div class='section-title'>Tabela — Motivos por Coordenação</div>", unsafe_allow_html=True)
            tabela_coord = matriz.copy()
            tabela_coord["Total"] = tabela_coord.sum(axis=1)
            tabela_coord = tabela_coord.sort_values("Total", ascending=False)
            st.dataframe(
                tabela_coord.style.background_gradient(cmap="Oranges"),
                use_container_width=True, height=320
            )

    with tab2:
        df_canal_x = df_perda[df_perda["canal"] != "Não informado"]
        if not df_canal_x.empty:
            matriz_canal = df_canal_x.groupby(["motivo", "canal"]).size().unstack(fill_value=0)
            fig = px.imshow(matriz_canal, color_continuous_scale=SCALE_ORANGE_SOFT,
                            labels={"x": "Canal", "y": "Motivo", "color": "Perdidos"},
                            aspect="auto", text_auto=True)
            fig.update_layout(**PLOTLY_LAYOUT, height=460)
            fig.update_traces(textfont_color="#000")
            st.plotly_chart(fig, use_container_width=True, key="mp_canal_heat")

    with tab3:
        df_resp = df_perda.explode("resp_list")
        df_resp = df_resp[df_resp["resp_list"] != "Sem responsável"]
        # Top responsáveis por volume de perdas
        top_resp = df_resp.drop_duplicates(["card_id", "resp_list"])["resp_list"].value_counts().head(15).index.tolist()
        df_resp = df_resp[df_resp["resp_list"].isin(top_resp)]
        if not df_resp.empty:
            matriz_resp = df_resp.groupby(["resp_list", "motivo"]).size().unstack(fill_value=0)
            fig = px.imshow(matriz_resp, color_continuous_scale=SCALE_ORANGE_SOFT,
                            labels={"x": "Motivo", "y": "Responsável", "color": "Perdidos"},
                            aspect="auto", text_auto=True)
            fig.update_layout(**PLOTLY_LAYOUT, height=500)
            fig.update_traces(textfont_color="#000")
            st.plotly_chart(fig, use_container_width=True, key="mp_resp_heat")

    with tab4:
        df_tam_x = df_perda[df_perda["tamanho"] != "Não informado"]
        if not df_tam_x.empty:
            matriz_tam = df_tam_x.groupby(["motivo", "tamanho"]).size().unstack(fill_value=0)
            fig = px.imshow(matriz_tam, color_continuous_scale=SCALE_ORANGE_SOFT,
                            labels={"x": "Tamanho", "y": "Motivo", "color": "Perdidos"},
                            aspect="auto", text_auto=True)
            fig.update_layout(**PLOTLY_LAYOUT, height=420)
            fig.update_traces(textfont_color="#000")
            st.plotly_chart(fig, use_container_width=True, key="mp_tam_heat")

    # -------------------------------------------------------
    # PERDAS COM PROPOSTA — MOTIVO DE ALTO VALOR
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>Perdas após envio de proposta</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{TEXT_SECONDARY};font-size:13px'>Leads que chegaram até proposta comercial ou follow-up e foram perdidos — perdas mais caras, pois consumiram esforço comercial completo.</p>", unsafe_allow_html=True)

    df_pos_prop = df_perda[df_perda["chegou_proposta"]]
    df_pos_prop_unique = df_pos_prop.drop_duplicates(subset=["card_id"])

    total_pos = df_pos_prop_unique["card_id"].nunique()
    valor_perdido = df_pos_prop_unique["valor_proposta"].sum()
    valor_perdido_fmt = f"R$ {valor_perdido:,.0f}".replace(",", ".") if pd.notna(valor_perdido) and valor_perdido > 0 else "N/A"

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #EF4444">
            <div class="label">Perdidos após proposta</div>
            <div class="value" style="color:#EF4444">{total_pos}</div>
            <div class="sub">{round(total_pos/total_perdidos*100,1) if total_perdidos else 0}% do total de perdas</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid {FLUXO_ORANGE}">
            <div class="label">Valor não convertido</div>
            <div class="value" style="color:{FLUXO_ORANGE};font-size:22px">{valor_perdido_fmt}</div>
            <div class="sub">soma das propostas perdidas</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        motivo_pos_top = df_pos_prop["motivo"].value_counts().idxmax() if not df_pos_prop.empty else "-"
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid {FLUXO_ORANGE_LIGHT}">
            <div class="label">Principal motivo pós-proposta</div>
            <div class="value" style="color:{FLUXO_ORANGE_LIGHT};font-size:20px">{motivo_pos_top}</div>
            <div class="sub">motivo mais comum após proposta</div>
        </div>""", unsafe_allow_html=True)

    if not df_pos_prop.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        motivos_pos = df_pos_prop["motivo"].value_counts().reset_index()
        motivos_pos.columns = ["Motivo", "Perdas pós-proposta"]
        fig = px.bar(motivos_pos.sort_values("Perdas pós-proposta"),
                     x="Perdas pós-proposta", y="Motivo", orientation="h",
                     color="Perdas pós-proposta", color_continuous_scale=SCALE_ORANGE,
                     text="Perdas pós-proposta", labels={"Motivo": ""})
        fig.update_traces(textfont_color=TEXT_PRIMARY, textposition="outside")
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, height=380)
        st.plotly_chart(fig, use_container_width=True, key="mp_pos_prop")

    # -------------------------------------------------------
    # DETALHAMENTO POR MOTIVO
    # -------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>Explorar leads por motivo</div>", unsafe_allow_html=True)

    motivos_disp = ["Todos"] + sorted(df_perda["motivo"].unique().tolist())
    motivo_sel = st.selectbox("Filtrar por motivo:", motivos_disp, key="mp_motivo_sel")

    df_lista = df_perda.drop_duplicates(subset=["card_id"]).copy()
    if motivo_sel != "Todos":
        ids_com_motivo = df_perda[df_perda["motivo"] == motivo_sel]["card_id"].unique()
        df_lista = df_lista[df_lista["card_id"].isin(ids_com_motivo)]

    df_lista["Valor"] = df_lista["valor_proposta"].apply(
        lambda x: f"R$ {x:,.0f}".replace(",", ".") if pd.notna(x) and x > 0 else "-"
    )
    df_lista["Descrição"] = df_lista["descricao"].fillna("").apply(
        lambda x: (x[:80] + "…") if isinstance(x, str) and len(x) > 80 else (x or "-")
    )

    st.dataframe(
        df_lista[["titulo", "motivo", "coordenacao", "canal", "fase_morte", "responsavel", "Valor", "Descrição"]]
            .rename(columns={
                "titulo": "Card",
                "motivo": "Motivo",
                "coordenacao": "Coordenação",
                "canal": "Canal",
                "fase_morte": "Morreu em",
                "responsavel": "Responsável",
            }),
        use_container_width=True, height=460, hide_index=True
    )


# ============================================================
# SIDEBAR + MAIN
# ============================================================

def _render_fluxo_logo():
    """Desenha o logo da Fluxo na sidebar.
    Usa o arquivo em assets/ se existir; caso contrário, desenha um SVG fallback.
    Renderiza com st.image (arquivo) ou st.markdown isolado (SVG) para evitar
    problemas de escaping ao misturar SVG dentro de HTML."""
    assets = BASE_DIR / "assets"
    for nome in ["fluxo_logo.png", "fluxo_logo.jpg", "fluxo_logo.jpeg", "fluxo_logo.webp", "fluxo_logo.svg"]:
        arquivo = assets / nome
        if arquivo.exists():
            st.image(str(arquivo), width=180)
            return
    svg = f"""
    <div style="text-align:center">
      <svg viewBox="0 0 240 100" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:200px;height:auto;">
        <g fill="none" stroke="{FLUXO_ORANGE}" stroke-width="5" stroke-linecap="round">
          <path d="M20 14 L20 86"/><path d="M220 14 L220 86"/>
          <path d="M20 14 L58 14"/><path d="M182 14 L220 14"/>
          <path d="M20 86 L58 86"/><path d="M182 86 L220 86"/>
        </g>
        <path d="M60 22 Q120 -6 180 22" stroke="{FLUXO_ORANGE}" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.85"/>
        <path d="M60 78 Q120 106 180 78" stroke="{FLUXO_ORANGE}" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.85"/>
        <text x="120" y="63" font-family="Inter, sans-serif" font-weight="800" font-size="38" text-anchor="middle" fill="{TEXT_PRIMARY}" letter-spacing="-1">Fluxo</text>
      </svg>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)

def main():
    if not CARDS_RAW_PATH.exists():
        st.error(f"❌ Arquivo {CARDS_RAW_PATH} não encontrado. Rode o extrator.py primeiro.")
        return

    df = carregar_dados()

    with st.sidebar:
        st.markdown("<div style='text-align:center;padding:24px 8px 4px 8px'></div>", unsafe_allow_html=True)
        _render_fluxo_logo()
        st.markdown(
            f"<div style='text-align:center;font-size:11px;color:{TEXT_MUTED};"
            f"letter-spacing:0.25em;text-transform:uppercase;margin-top:8px'>Consultoria</div>"
            f"<div style='text-align:center;font-size:13px;color:{FLUXO_ORANGE};"
            f"margin-top:14px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase'>"
            f"Dashboard CRM</div>",
            unsafe_allow_html=True,
        )

        st.markdown(f"<hr style='border:none;height:1px;background:{BORDER};margin:8px 0 16px 0'>", unsafe_allow_html=True)

        pagina = st.radio("Navegação", [
            "📊  Visão Geral",
            "💰  Vendas",
            "🏭  Tamanho de Empresa",
            "📈  Conversão Real",
            "🔻  Funil de Conversão",
            "💔  Motivo da Perda",
            "🚧  Objeções",
            "👤  Responsáveis",
            "🏢  Coordenações",
            "🔀  Cross Selling",
            "🔬  Diagnóstico",
            "⏱️  Tempo entre Fases"
        ], label_visibility="collapsed")

        st.markdown(f"<hr style='border:none;height:1px;background:{BORDER};margin:16px 0'>", unsafe_allow_html=True)

        ultima = df["data_atualizacao"].max()
        st.markdown(f"""
        <div style='padding:16px;background:{BG_CARD};border:1px solid {BORDER};border-radius:12px'>
            <div style='color:{TEXT_MUTED};font-size:10.5px;text-transform:uppercase;letter-spacing:0.1em;font-weight:600'>Total de Cards</div>
            <div style='color:{FLUXO_ORANGE};font-size:26px;font-weight:800;margin-top:4px'>{len(df):,}</div>
            <div style='color:{TEXT_MUTED};font-size:10.5px;margin-top:12px;text-transform:uppercase;letter-spacing:0.1em;font-weight:600'>Última atualização</div>
            <div style='color:{TEXT_SECONDARY};font-size:13px;margin-top:2px'>{ultima.strftime('%d/%m/%Y às %H:%M') if pd.notna(ultima) else 'N/A'}</div>
        </div>
        <div style='padding:8px;text-align:center;margin-top:16px'>
            <div style='color:{TEXT_MUTED};font-size:10px;letter-spacing:0.15em'>FLUXO CONSULTORIA © 2026</div>
        </div>
        """, unsafe_allow_html=True)

    if "Visão Geral" in pagina:
        pagina_visao_geral(df)
    elif "Vendas" in pagina:
        pagina_vendas(df)
    elif "Tamanho" in pagina:
        pagina_tamanho_empresa(df)
    elif "Funil" in pagina:
        pagina_funil(df)
    elif "Motivo da Perda" in pagina:
        pagina_motivo_perda(df)
    elif "Objeções" in pagina:
        pagina_objecoes(df)
    elif "Responsáveis" in pagina:
        pagina_responsaveis(df)
    elif "Coordenações" in pagina:
        pagina_coordenacoes(df)
    elif "Tempo" in pagina:
        pagina_tempo_fases(df)
    elif "Conversão Real" in pagina:
        pagina_conversao(df)
    elif "Diagnóstico" in pagina:
        pagina_diagnostico(df)
    elif "Cross" in pagina:
        pagina_cross_selling(df)

if __name__ == "__main__":
    main()