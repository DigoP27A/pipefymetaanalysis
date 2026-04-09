import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

st.set_page_config(page_title="CRM Fluxo", layout="wide", page_icon="📊")

# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #0f172a; }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    
    .stRadio label { color: #e2e8f0 !important; font-size: 14px !important; }
    
    h1, h2, h3, h4, h5, h6, p, span, div { color: #f1f5f9; }
    
    .stDataFrame { background: #1e293b; border-radius: 12px; }
    .stDataFrame th { background: #334155 !important; color: #f1f5f9 !important; }
    .stDataFrame td { color: #e2e8f0 !important; }
    
    div[data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
    }
    div[data-testid="stMetric"] label { color: #94a3b8 !important; }
    div[data-testid="stMetric"] div { color: #f1f5f9 !important; }
    
    /* Selectbox - campo fechado */
    .stSelectbox label { color: #e2e8f0 !important; font-size: 14px !important; }
    div[data-baseweb="select"] { background-color: #1e293b !important; }
    div[data-baseweb="select"] > div { background-color: #1e293b !important; border-color: #475569 !important; border-radius: 8px !important; }
    div[data-baseweb="select"] * { color: #f1f5f9 !important; }
    div[data-baseweb="select"] svg { fill: #94a3b8 !important; }

    /* Dropdown aberto - container */
    div[data-baseweb="popover"] * { background-color: #1e293b !important; }
    div[data-baseweb="popover"] > div { border: 1px solid #475569 !important; border-radius: 10px !important; overflow: hidden !important; }
    
    /* Itens da lista */
    ul[data-baseweb="menu"] { background-color: #1e293b !important; padding: 4px !important; }
    ul[data-baseweb="menu"] li { background-color: #1e293b !important; color: #f1f5f9 !important; border-radius: 6px !important; margin: 2px 0 !important; }
    ul[data-baseweb="menu"] li:hover { background-color: #334155 !important; color: #ffffff !important; }
    ul[data-baseweb="menu"] li[aria-selected="true"] { background-color: #2563eb !important; color: #ffffff !important; }
    
    /* Texto dentro dos itens */
    div[role="option"] { background-color: #1e293b !important; color: #f1f5f9 !important; }
    div[role="option"]:hover { background-color: #334155 !important; }
    div[role="option"] * { color: #f1f5f9 !important; background-color: transparent !important; }
    div[role="option"]:hover * { color: #ffffff !important; }
    
    /* Scrollbar do dropdown */
    div[data-baseweb="popover"] ::-webkit-scrollbar { width: 6px; }
    div[data-baseweb="popover"] ::-webkit-scrollbar-track { background: #1e293b; }
    div[data-baseweb="popover"] ::-webkit-scrollbar-thumb { background: #475569; border-radius: 3px; }
    
    .stSlider label { color: #e2e8f0 !important; }
    
    hr { border-color: #334155; }

    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); border-color: #475569; }
    .metric-card .label { color: #94a3b8; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
    .metric-card .value { color: #f1f5f9; font-size: 36px; font-weight: 700; line-height: 1; margin-bottom: 6px; }
    .metric-card .sub { color: #64748b; font-size: 12px; }

    .section-title {
        color: #f1f5f9;
        font-size: 18px;
        font-weight: 600;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #334155;
    }

    .info-box {
        background: #1e3a5f;
        border: 1px solid #2563eb;
        border-radius: 10px;
        padding: 14px 18px;
        color: #93c5fd;
        font-size: 13px;
        margin-bottom: 20px;
    }

    .tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LAYOUT PLOTLY BASE
# ============================================================

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", family="Inter"),
    xaxis=dict(gridcolor="#334155", linecolor="#475569", tickcolor="#94a3b8"),
    yaxis=dict(gridcolor="#334155", linecolor="#475569", tickcolor="#94a3b8"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")),
    margin=dict(t=40, b=40, l=20, r=20),
)

CORES = {
    "Venda": "#22c55e",
    "Perda": "#ef4444",
    "Pausado": "#f59e0b",
    "Em andamento": "#3b82f6"
}

ORDEM_FASES = [
    "2. Contato aberto",
    "3. Pré-diagnóstico feito",
    "4. Dignóstico feito",
    "5. Precificação/Aprovação em andamento",
    "6. Proposta comercial feita",
    "7. Follow-up",
    "Venda"
]

# ============================================================
# DADOS
# ============================================================

@st.cache_data
def carregar_dados():
    with open("dados/cards_raw.json", encoding="utf-8") as f:
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
    df["data_criacao"] = pd.to_datetime(df["data_criacao"], unit="s", errors="coerce")
    df["data_atualizacao"] = pd.to_datetime(df["data_atualizacao"], unit="s", errors="coerce")
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
    st.markdown("<h1 style='color:#f1f5f9;margin-bottom:4px'>📊 Visão Geral</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;margin-bottom:24px'>Panorama completo do CRM Fluxo</p>", unsafe_allow_html=True)

    total = len(df)
    vendas = len(df[df["resultado"] == "Venda"])
    perdas = len(df[df["resultado"] == "Perda"])
    pausados = len(df[df["resultado"] == "Pausado"])
    andamento = len(df[df["resultado"] == "Em andamento"])
    taxa = round(vendas / total * 100, 1) if total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "Total de Leads", total, "todos os cards", "#3b82f6"),
        (c2, "Vendas", vendas, f"{taxa}% de conversão", "#22c55e"),
        (c3, "Perdidos", perdas, f"{round(perdas/total*100,1)}% do total", "#ef4444"),
        (c4, "Pausados", pausados, f"{round(pausados/total*100,1)}% do total", "#f59e0b"),
        (c5, "Em Andamento", andamento, f"{round(andamento/total*100,1)}% do total", "#8b5cf6"),
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
                     color="Total", color_continuous_scale=["#1e3a5f", "#3b82f6", "#60a5fa"],
                     text="Total")
        fig.update_traces(textfont_color="white", textposition="outside")
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig.update_yaxes(categoryorder="total ascending", gridcolor="#334155", tickfont=dict(color="#e2e8f0"))
        st.plotly_chart(fig, use_container_width=True)


def pagina_objecoes(df):
    st.markdown("<h1 style='color:#f1f5f9;margin-bottom:4px'>🚧 Análise de Objeções</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;margin-bottom:24px'>Como cada objeção impacta o resultado do lead</p>", unsafe_allow_html=True)

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
    st.markdown("<h3 style='color:#f1f5f9'>🎯 Análise de Leads Qualificados</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;font-size:13px'>Apenas cards que chegaram até Diagnóstico, Precificação/Aprovação ou Proposta Comercial — excluindo desqualificados precoces.</p>", unsafe_allow_html=True)

    FASES_QUALIFICADAS = [
        "4. Dignóstico feito",
        "5. Precificação/Aprovação em andamento",
        "6. Proposta comercial feita",
        "7. Follow-up",
        "Venda",
        "Pausado",
        "Perdido",
    ]

    # Carrega histórico para saber quais cards passaram por diagnóstico ou além
    with open("dados/cards_raw.json", encoding="utf-8") as f:
        cards_raw_obj = json.load(f)

    ids_qualificados = set()
    for card in cards_raw_obj:
        fases_visitadas = [
            ph.get("phase", {}).get("name")
            for ph in card.get("phases_history", [])
        ]
        passou_diagnostico = any(
            f in fases_visitadas for f in [
                "4. Dignóstico feito",
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
    st.markdown("<h1 style='color:#f1f5f9;margin-bottom:4px'>👤 Análise por Responsável</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;margin-bottom:24px'>Performance individual de cada membro do time</p>", unsafe_allow_html=True)

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
        st.markdown(f"<p style='color:#94a3b8;font-size:13px'>{len(analise[analise['Total'] >= min_cards])} pessoas exibidas</p>", unsafe_allow_html=True)

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
                     color_discrete_sequence=["#3b82f6"])
    fig3.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)


def pagina_tempo_fases(df_original):
    st.markdown("<h1 style='color:#f1f5f9;margin-bottom:4px'>⏱️ Tempo entre Fases</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;margin-bottom:24px'>Tempo real que cada lead passou em cada etapa do funil</p>", unsafe_allow_html=True)

    # Carrega dados brutos para pegar phases_history
    with open("dados/cards_raw.json", encoding="utf-8") as f:
        cards = json.load(f)

    FASES_COM_OPO = [
        "1. Oportunidade",
        "2. Contato aberto",
        "3. Pré-diagnóstico feito",
        "4. Dignóstico feito",
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
                 color_continuous_scale=["#1e3a5f", "#7c3aed", "#c4b5fd"],
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
                      color_discrete_sequence=["#8b5cf6"],
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
    st.markdown("<h1 style='color:#f1f5f9;margin-bottom:4px'>🔻 Funil de Conversão</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;margin-bottom:24px'>Taxa de mortalidade e gargalos por etapa do funil</p>", unsafe_allow_html=True)

    FASES_FUNIL = [
        "1. Oportunidade",
        "2. Contato aberto",
        "3. Pré-diagnóstico feito",
        "4. Dignóstico feito",
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
    with open("dados/cards_raw.json", encoding="utf-8") as f:
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
            marker_color="#3b82f6",
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
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#e2e8f0")))
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
    st.markdown("<p style='color:#64748b;font-size:13px'>Ordenado pelas fases com maior taxa de perda</p>", unsafe_allow_html=True)

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
    st.markdown("<h1 style='color:#f1f5f9;margin-bottom:4px'>🏢 Análise por Coordenação</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;margin-bottom:24px'>Objeções e conversão por coordenação e por responsável dentro de cada coordenação</p>", unsafe_allow_html=True)

    with open("dados/cards_raw.json", encoding="utf-8") as f:
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
        st.markdown("<p style='color:#64748b;font-size:13px'>Quantidade de vezes que cada responsável ouviu cada objeção</p>", unsafe_allow_html=True)

        heatmap_data = df_sel_unique[df_sel_unique["objecao"] != "Sem resposta"].groupby(
            ["responsavel", "objecao"]
        ).size().unstack(fill_value=0)

        fig3 = px.imshow(
            heatmap_data,
            color_continuous_scale=["#0f172a", "#1e3a5f", "#3b82f6", "#93c5fd"],
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
    st.markdown("<h1 style='color:#f1f5f9;margin-bottom:4px'>📈 Taxa de Conversão Real</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;margin-bottom:24px'>Conversão calculada apenas sobre leads que chegaram à Proposta Comercial</p>", unsafe_allow_html=True)

    with open("dados/cards_raw.json", encoding="utf-8") as f:
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
        (c1, "Total com Proposta", total, "chegaram até proposta", "#3b82f6"),
        (c2, "Vendas", vendas, f"{taxa}% de conversão", "#22c55e"),
        (c3, "Perdidos", perdas, f"{round(perdas/total*100,1) if total else 0}%", "#ef4444"),
        (c4, "Pausados", pausados, f"{round(pausados/total*100,1) if total else 0}%", "#f59e0b"),
        (c5, "Em andamento", andamento, f"{round(andamento/total*100,1) if total else 0}%", "#8b5cf6"),
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
            (c1, "Total com Proposta", total, "neste ciclo", "#3b82f6"),
            (c2, "Vendas", vendas, f"{taxa}% de conversão", "#22c55e"),
            (c3, "Perdidos", perdas, f"{round(perdas/total*100,1) if total else 0}%", "#ef4444"),
            (c4, "Pausados", pausados, f"{round(pausados/total*100,1) if total else 0}%", "#f59e0b"),
            (c5, "Em andamento", andamento, f"{round(andamento/total*100,1) if total else 0}%", "#8b5cf6"),
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

    st.markdown("<h1 style='color:#f1f5f9;margin-bottom:4px'>🔬 Diagnóstico</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;margin-bottom:24px'>Identificação de gargalos, padrões de perda e qualidade de qualificação</p>", unsafe_allow_html=True)

    with open("dados/cards_raw.json", encoding="utf-8") as f:
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
            "4. Dignóstico feito", "5. Precificação/Aprovação em andamento",
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
        (c1, "Total de Leads", total, "no filtro selecionado", "#3b82f6"),
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
    st.markdown("<h3 style='color:#f1f5f9'>🚨 Diagnóstico 1 — Perdidos sem dar objeção</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;font-size:13px'>Leads que foram marcados como Perdido sem registrar nenhuma objeção. Indica possível falha de abordagem, qualificação incorreta ou ausência de follow-up.</p>", unsafe_allow_html=True)

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
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #64748b">
            <div class="label">Total de Perdidos</div>
            <div class="value" style="color:#94a3b8">{total_perd}</div>
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
    st.markdown("<h3 style='color:#f1f5f9'>⚡ Diagnóstico 2 — Velocidade de primeiro contato</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;font-size:13px'>Dias entre a chegada do lead e a abertura do contato. Leads contactados mais tarde tendem a converter menos.</p>", unsafe_allow_html=True)

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
                          color_continuous_scale=["#1e3a5f", "#7c3aed", "#c4b5fd"],
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
                          color_continuous_scale=["#1e3a5f", "#7c3aed", "#c4b5fd"],
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
    st.markdown("<h3 style='color:#f1f5f9'>📡 Diagnóstico 3 — Qualidade por canal de aquisição</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;font-size:13px'>Canais que trazem leads de baixa qualidade inflam o funil sem gerar receita. Cruzamento com taxa de perdidos sem objeção revela canais que qualificam mal.</p>", unsafe_allow_html=True)

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
        st.markdown("<p style='color:#64748b;font-size:13px'>Canais com alta % de perdidos sem objeção indicam leads mal qualificados ou abordagem inadequada.</p>", unsafe_allow_html=True)
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
    st.markdown("<h3 style='color:#f1f5f9'>⏰ Diagnóstico 4 — Onde e quando os leads morrem</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;font-size:13px'>Fase onde o lead parou × tempo que ficou ali antes de ser perdido. Fases com alto tempo médio e alta mortalidade são gargalos de processo.</p>", unsafe_allow_html=True)

    # Monta histórico de duração por fase para perdidos
    linhas_hist = []
    ids_perdidos = set(df_unique[df_unique["resultado"] == "Perda"]["card_id"].tolist())
    ids_filtro = set(df_unique["card_id"].tolist())

    FASES_FUNIL_HIST = [
        "1. Oportunidade", "2. Contato aberto", "3. Pré-diagnóstico feito",
        "4. Dignóstico feito", "5. Precificação/Aprovação em andamento",
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
    st.markdown("<h3 style='color:#f1f5f9'>🗺️ Diagnóstico 5 — Mapa de risco por canal e responsável</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;font-size:13px'>Heatmap cruzando responsável × canal com volume de perdidos sem objeção. Concentrações revelam onde está o problema: no canal, na pessoa, ou na combinação dos dois.</p>", unsafe_allow_html=True)

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
    st.markdown("<h3 style='color:#f1f5f9'>📋 Diagnóstico 6 — Conversão por tipo de serviço</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;font-size:13px'>Quais serviços convertem mais? Serviços com baixa conversão podem indicar processo de diagnóstico inadequado ou precificação fora do mercado.</p>", unsafe_allow_html=True)

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
    st.markdown("<h1 style='color:#f1f5f9;margin-bottom:4px'>🔀 Situação do Cross Selling</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;margin-bottom:24px'>Análise de leads qualificados por etapa do funil e quantos foram designados a mais de uma coordenação</p>", unsafe_allow_html=True)

    with open("dados/cards_raw.json", encoding="utf-8") as f:
        cards_raw = json.load(f)

    COORDENACOES = ["ACE", "CCE", "MNP", "PRO", "QAB"]

    def parse_lista(x):
        if not x or isinstance(x, float): return []
        if isinstance(x, str) and x.startswith("["):
            try: return json.loads(x)
            except: return [x]
        return [x]

    GRUPOS = {
        "Diagnóstico": ["4. Dignóstico feito"],
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
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #64748b">
            <div class="label">Sem Coordenação</div>
            <div class="value" style="color:#64748b">{sem}</div>
            <div class="sub">{round(sem/total*100,1) if total else 0}% dos qualificados</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # ANÁLISE POR GRUPO
    # -------------------------------------------------------
    ORDEM_GRUPOS = ["Diagnóstico", "Precificação/Aprovação", "Proposta"]
    CORES_GRUPOS = {
        "1 Coordenação": "#22c55e",
        "Múltiplas Coordenações": "#8b5cf6",
        "Sem coordenação": "#64748b",
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
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #64748b">
            <div class="label">Sem Coordenação</div>
            <div class="value" style="color:#64748b">{sem_g}</div>
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
                          color_continuous_scale=["#2e1065", "#7c3aed", "#c4b5fd"],
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
# SIDEBAR + MAIN
# ============================================================

def main():
    if not os.path.exists("dados/cards_raw.json"):
        st.error("❌ Arquivo dados/cards_raw.json não encontrado. Rode o extrator.py primeiro.")
        return

    df = carregar_dados()

    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:20px 0 10px 0'>
            <div style='font-size:32px'>📊</div>
            <div style='font-size:20px;font-weight:700;color:#f1f5f9'>CRM Fluxo</div>
            <div style='font-size:12px;color:#64748b'>Dashboard de Análise</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:#334155;margin:10px 0'>", unsafe_allow_html=True)

        pagina = st.radio("", [
            "📊  Visão Geral",
            "📈  Conversão Real",
            "🔻  Funil de Conversão",
            "🚧  Objeções",
            "👤  Responsáveis",
            "🏢  Coordenações",
            "🔀  Cross Selling",
            "🔬  Diagnóstico",
            "⏱️  Tempo entre Fases"
        ], label_visibility="collapsed")

        st.markdown("<hr style='border-color:#334155;margin:10px 0'>", unsafe_allow_html=True)

        ultima = df["data_atualizacao"].max()
        st.markdown(f"""
        <div style='padding:12px;background:#0f172a;border-radius:10px'>
            <div style='color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:0.05em'>Total de cards</div>
            <div style='color:#f1f5f9;font-size:22px;font-weight:700'>{len(df)}</div>
            <div style='color:#64748b;font-size:11px;margin-top:8px'>Última atualização</div>
            <div style='color:#94a3b8;font-size:12px'>{ultima.strftime('%d/%m/%Y') if pd.notna(ultima) else 'N/A'}</div>
        </div>
        """, unsafe_allow_html=True)

    if "Visão Geral" in pagina:
        pagina_visao_geral(df)
    elif "Funil" in pagina:
        pagina_funil(df)
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