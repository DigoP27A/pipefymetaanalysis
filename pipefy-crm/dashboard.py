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
    st.plotly_chart(fig, use_container_width=True)

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
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.markdown("<div class='section-title'>Tabela Detalhada</div>", unsafe_allow_html=True)
        st.dataframe(
            analise.set_index("objecao").style
                .background_gradient(subset=["Taxa de Venda (%)"], cmap="Greens")
                .format({"Taxa de Venda (%)": "{:.1f}%"}),
            use_container_width=True, height=350
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
            "🔻  Funil de Conversão",
            "🚧  Objeções",
            "👤  Responsáveis",
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
    elif "Tempo" in pagina:
        pagina_tempo_fases(df)

if __name__ == "__main__":
    main()