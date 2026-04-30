"""
Gerador de Relatório ICP — Fluxo Consultoria
Usa fpdf2 para criar um PDF profissional com a análise completa de ICP.
"""

import csv
import re
import ast
from collections import Counter, defaultdict
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")

# ── Paleta de cores ──────────────────────────────────────────────
AZUL_ESCURO  = (15,  40,  80)
AZUL_MEDIO   = (30,  90, 160)
AZUL_CLARO   = (210, 230, 255)
CINZA_ESCURO = (50,  50,  50)
CINZA_CLARO  = (245, 245, 245)
BRANCO       = (255, 255, 255)
VERDE        = (34, 139,  34)
VERMELHO     = (180,  30,  30)
LARANJA      = (200, 100,   0)
AMARELO_BG   = (255, 250, 220)

# ── Dados calculados (replicados do script de análise) ────────────
DATA_PATH = r"c:\Users\Rodrigo\Desktop\site\pipefymetaanalysis\pipefy-crm\dados\cards.csv"

def parse_valor(s):
    s = s.replace(".", "").replace(",", ".").strip()
    try:
        return float(re.sub(r"[^\d.]", "", s))
    except:
        return None

def parse_coord(s):
    try:
        return [x.strip() for x in ast.literal_eval(s)]
    except:
        return [s.strip()] if s.strip() else []

def load_data():
    with open(DATA_PATH, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    return rows

rows = load_data()
sample_keys = list(rows[0].keys())
coord_key = next(k for k in sample_keys if "Coordena" in k)
mnp_key   = next(k for k in sample_keys if "MNP" in k and "Enviar" in k)
qab_key   = next(k for k in sample_keys if "QAB" in k and "Enviar" in k)
ace_key   = next(k for k in sample_keys if "ACE" in k and "Enviar" in k)
cce_key   = next(k for k in sample_keys if "CCE" in k and "Enviar" in k)

proposta = [r for r in rows if r.get("Valor da proposta", "").strip()]

def coord_stats_calc():
    stats = defaultdict(lambda: {"n": 0, "v": 0, "p": 0, "val_v": 0, "prazo": []})
    prazo_key = next(k for k in sample_keys if "Prazo" in k and "teis" in k)
    for r in proposta:
        coords = parse_coord(r.get(coord_key, ""))
        val = parse_valor(r.get("Valor da proposta", ""))
        res = r["resultado"].strip()
        prazo_raw = r.get(prazo_key, "").strip()
        for c in coords:
            stats[c]["n"] += 1
            if res == "Venda":
                stats[c]["v"] += 1
                if val: stats[c]["val_v"] += val
            elif res == "Perda":
                stats[c]["p"] += 1
            try:
                stats[c]["prazo"].append(float(prazo_raw))
            except:
                pass
    return stats

def canal_stats_calc():
    stats = defaultdict(lambda: {"n": 0, "v": 0, "p": 0, "val_v": 0})
    for r in proposta:
        canal = r.get("Canal de aquisição", "").strip() or "(não informado)"
        # Normalizar variantes
        canal_norm = canal.lower()
        if "indica" in canal_norm and ("membro" in canal_norm or "alumni" in canal_norm or "ex" in canal_norm):
            canal = "Indicação (membros/alumni)"
        elif "indica" in canal_norm:
            canal = "Indicação"
        elif "fideliza" in canal_norm:
            canal = "Fidelização"
        elif "paga" in canal_norm and "google" in canal_norm:
            canal = "Busca Paga | Google"
        elif "org" in canal_norm and "google" in canal_norm:
            canal = "Busca Orgânica | Google"
        elif "direto" in canal_norm or "trafego" in canal_norm:
            canal = "Tráfego Direto"
        elif "outbound" in canal_norm:
            canal = "Outbound"
        elif "referencia" in canal_norm or "ufrj" in canal_norm:
            canal = "Referência UFRJ"
        val = parse_valor(r.get("Valor da proposta", ""))
        res = r["resultado"].strip()
        stats[canal]["n"] += 1
        if res == "Venda":
            stats[canal]["v"] += 1
            if val: stats[canal]["val_v"] += val
        elif res == "Perda":
            stats[canal]["p"] += 1
    return stats

coord_s = coord_stats_calc()
canal_s  = canal_stats_calc()

total_proposto = sum(parse_valor(r.get("Valor da proposta","")) or 0 for r in proposta)
vendas_list    = [r for r in proposta if r["resultado"].strip() == "Venda"]
perdas_list    = [r for r in proposta if r["resultado"].strip() == "Perda"]
total_vendido  = sum(parse_valor(r.get("Valor da proposta","")) or 0 for r in vendas_list)
total_perdido  = sum(parse_valor(r.get("Valor da proposta","")) or 0 for r in perdas_list)
total_pipe     = sum(parse_valor(r.get("Valor da proposta","")) or 0
                     for r in proposta if r["resultado"].strip() in ("Em andamento","Pausado"))
conv_vol = len(vendas_list)/(len(vendas_list)+len(perdas_list))*100
conv_val = total_vendido/(total_vendido+total_perdido)*100
tv_list  = [parse_valor(r.get("Valor da proposta","")) for r in vendas_list]
tv_list  = [v for v in tv_list if v]
tp_list  = [parse_valor(r.get("Valor da proposta","")) for r in perdas_list]
tp_list  = [v for v in tp_list if v]
ticket_medio_v = sum(tv_list)/len(tv_list)
ticket_medio_p = sum(tp_list)/len(tp_list)


# ── Classe PDF ────────────────────────────────────────────────────
class FluxoPDF(FPDF):

    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.add_font("Arial", fname="C:/Windows/Fonts/arial.ttf")
        self.add_font("Arial", "B", "C:/Windows/Fonts/arialbd.ttf")
        self.add_font("Arial", "I", "C:/Windows/Fonts/ariali.ttf")
        self.add_font("Arial", "BI", "C:/Windows/Fonts/arialbi.ttf")
        self.set_auto_page_break(auto=True, margin=20)
        self.add_page()

    # ── cabeçalho / rodapé ──────────────────────────────────────
    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*AZUL_ESCURO)
        self.rect(0, 0, 210, 12, "F")
        self.set_xy(10, 3)
        self.set_font("Arial", "B", 8)
        self.set_text_color(*BRANCO)
        self.cell(0, 6, "Fluxo Consultoria — Análise de ICP", align="L")
        self.set_xy(10, 3)
        self.cell(0, 6, f"Pág. {self.page_no()}", align="R")
        self.set_text_color(*CINZA_ESCURO)
        self.ln(10)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-12)
        self.set_font("Arial", "", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, "Confidencial — Fluxo Consultoria / POLI-UFRJ  •  Análise gerada com Claude Sonnet 4.6", align="C")

    # ── helpers ─────────────────────────────────────────────────
    def titulo_secao(self, txt, cor=AZUL_ESCURO):
        self.ln(4)
        self.set_fill_color(*cor)
        self.set_text_color(*BRANCO)
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, f"  {txt}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.set_text_color(*CINZA_ESCURO)
        self.ln(3)

    def subtitulo(self, txt):
        self.set_font("Arial", "B", 10)
        self.set_text_color(*AZUL_MEDIO)
        self.cell(0, 6, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*CINZA_ESCURO)
        self.ln(1)

    def corpo(self, txt, size=9):
        self.set_font("Arial", "", size)
        self.set_text_color(*CINZA_ESCURO)
        self.multi_cell(0, 5, txt)
        self.ln(1)

    def linha_tabela(self, colunas, larguras, header=False, fill=False, fill_color=CINZA_CLARO):
        if header:
            self.set_font("Arial", "B", 8)
            self.set_fill_color(*AZUL_ESCURO)
            self.set_text_color(*BRANCO)
        else:
            self.set_font("Arial", "", 8)
            self.set_text_color(*CINZA_ESCURO)
            if fill:
                self.set_fill_color(*fill_color)
            else:
                self.set_fill_color(*BRANCO)

        x0 = self.get_x()
        y0 = self.get_y()
        h  = 6

        for i, (col, larg) in enumerate(zip(colunas, larguras)):
            align = "R" if i > 0 and not header else "L"
            self.cell(larg, h, str(col), border=1, fill=True, align=align)

        self.ln(h)
        self.set_text_color(*CINZA_ESCURO)

    def kpi_box(self, label, value, sub="", cor=AZUL_MEDIO, w=42, h=22):
        x, y = self.get_x(), self.get_y()
        self.set_fill_color(*cor)
        self.rect(x, y, w, h, "F")
        self.set_text_color(*BRANCO)
        self.set_font("Arial", "B", 14)
        self.set_xy(x, y+3)
        self.cell(w, 7, value, align="C")
        self.set_font("Arial", "", 7)
        self.set_xy(x, y+10)
        self.cell(w, 5, label, align="C")
        if sub:
            self.set_xy(x, y+15)
            self.cell(w, 5, sub, align="C")
        self.set_text_color(*CINZA_ESCURO)
        self.set_xy(x + w + 2, y)

    def bullet(self, txt, indent=5):
        self.set_font("Arial", "", 9)
        self.set_text_color(*CINZA_ESCURO)
        self.set_x(self.l_margin + indent)
        self.multi_cell(0, 5, f"•  {txt}")
        self.ln(0.5)

    def tag(self, txt, cor_bg=AZUL_CLARO, cor_txt=AZUL_ESCURO):
        self.set_font("Arial", "B", 8)
        self.set_fill_color(*cor_bg)
        self.set_text_color(*cor_txt)
        w = self.get_string_width(txt) + 4
        self.cell(w, 5, txt, fill=True)
        self.set_text_color(*CINZA_ESCURO)
        self.cell(2, 5, "")

    def perfil_icp(self, num, titulo, combo, exemplos, quem_e,
                    dores, por_que, como_abordar, ticket, prioridade):
        self.add_page()
        # Cabeçalho do perfil
        self.set_fill_color(*AZUL_ESCURO)
        self.rect(10, self.get_y(), 190, 14, "F")
        self.set_xy(13, self.get_y()+2)
        self.set_font("Arial", "B", 13)
        self.set_text_color(*BRANCO)
        self.cell(0, 5, f"ICP {num} — {titulo}")
        self.ln(7)
        self.set_xy(13, self.get_y())
        self.set_font("Arial", "", 9)
        self.cell(0, 5, f"Combo: {combo}   |   Ticket potencial: {ticket}   |   Prioridade: {prioridade}")
        self.set_text_color(*CINZA_ESCURO)
        self.ln(10)

        # Exemplos reais
        self.subtitulo("Exemplos reais nos dados")
        for ex in exemplos:
            self.bullet(ex)
        self.ln(2)

        # Quem é
        self.subtitulo("Quem é esse cliente")
        for q in quem_e:
            self.bullet(q)
        self.ln(2)

        # Dores
        self.subtitulo("Dores e motivações")
        for d in dores:
            self.bullet(d, indent=5)
        self.ln(2)

        # Por que Fluxo
        self.subtitulo("Por que a Fluxo é única aqui")
        self.corpo(por_que)

        # Como abordar
        self.subtitulo("Como abordar comercialmente")
        self.corpo(como_abordar)


# ═══════════════════════════════════════════════════════════════
# GERAÇÃO DO PDF
# ═══════════════════════════════════════════════════════════════
pdf = FluxoPDF()
pdf.set_margins(10, 10, 10)

# ── Capa ──────────────────────────────────────────────────────
pdf.set_fill_color(*AZUL_ESCURO)
pdf.rect(0, 0, 210, 297, "F")

pdf.set_y(60)
pdf.set_font("Arial", "B", 28)
pdf.set_text_color(*BRANCO)
pdf.cell(0, 12, "Análise de ICP", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("Arial", "B", 18)
pdf.cell(0, 10, "Ideal Customer Profile", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(6)
pdf.set_font("Arial", "", 13)
pdf.set_text_color(180, 210, 255)
pdf.cell(0, 7, "Fluxo Consultoria — POLI/UFRJ", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(3)
pdf.set_font("Arial", "", 10)
pdf.cell(0, 6, "Baseado em 792 cards extraídos do Pipefy", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.cell(0, 6, "Abril / 2026", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

pdf.set_y(200)
pdf.set_fill_color(30, 70, 130)
pdf.rect(0, 195, 210, 40, "F")
pdf.set_font("Arial", "B", 9)
pdf.set_text_color(180, 210, 255)
pdf.cell(0, 6, "Gerado com Claude Sonnet 4.6  •  Análise de dados: Python / fpdf2", align="C",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("Arial", "", 8)
pdf.set_text_color(140, 170, 210)
pdf.cell(0, 5, "Confidencial — uso interno", align="C")

# ── Sumário Executivo ──────────────────────────────────────────
pdf.add_page()
pdf.titulo_secao("1. Sumário Executivo")

pdf.corpo(
    "Esta análise consolida 187 propostas comerciais enviadas pela Fluxo Consultoria "
    "entre julho/2025 e abril/2026, identificando padrões de conversão, perfis de cliente ideal (ICP) "
    "e as combinações de coordenação com maior potencial de receita. Os dados foram extraídos "
    "diretamente do CRM Pipefy e processados com Python."
)

# KPIs
pdf.ln(3)
pdf.subtitulo("Indicadores-chave do funil de propostas")
pdf.ln(2)

kpis = [
    ("187", "Propostas\nenviadas", ""),
    ("56", "Vendas\nfechadas", "30%"),
    ("70", "Perdas", "37%"),
    ("44%", "Conv. volume\n(V / V+P)", ""),
    ("18%", "Conv. valor\n(R$ / R$)", "alerta"),
]
cores = [AZUL_MEDIO, VERDE, VERMELHO, AZUL_MEDIO, LARANJA]
y_kpi = pdf.get_y()
x_kpi = pdf.l_margin
for (val, lab, sub), cor in zip(kpis, cores):
    pdf.set_xy(x_kpi, y_kpi)
    pdf.kpi_box(lab, val, sub, cor=cor, w=35, h=22)
    x_kpi += 37

pdf.set_y(y_kpi + 26)

pdf.ln(2)
# Segunda linha de KPIs
kpis2 = [
    (f"R$ {total_proposto/1e6:.2f}M", "Total proposto", ""),
    (f"R$ {total_vendido/1e3:.0f}k", "Receita gerada", ""),
    (f"R$ {total_perdido/1e6:.2f}M", "Receita perdida", ""),
    (f"R$ {total_pipe/1e3:.0f}k", "Pipeline ativo", "61 cards"),
    (f"R$ {ticket_medio_v/1e3:.0f}k", "Ticket médio V", ""),
]
cores2 = [AZUL_MEDIO, VERDE, VERMELHO, LARANJA, AZUL_MEDIO]
y_kpi2 = pdf.get_y()
x_kpi2 = pdf.l_margin
for (val, lab, sub), cor in zip(kpis2, cores2):
    pdf.set_xy(x_kpi2, y_kpi2)
    pdf.kpi_box(lab, val, sub, cor=cor, w=35, h=22)
    x_kpi2 += 37
pdf.set_y(y_kpi2 + 26)

pdf.ln(4)
pdf.set_fill_color(*AMARELO_BG)
pdf.set_draw_color(*LARANJA)
pdf.rect(pdf.l_margin, pdf.get_y(), 190, 18, "FD")
pdf.set_xy(pdf.l_margin + 3, pdf.get_y() + 3)
pdf.set_font("Arial", "B", 9)
pdf.set_text_color(*LARANJA)
pdf.cell(0, 5, "Insight central: gap entre conversão por volume (44%) e por valor (18%)")
pdf.ln(5)
pdf.set_x(pdf.l_margin + 3)
pdf.set_font("Arial", "", 8)
pdf.set_text_color(*CINZA_ESCURO)
pdf.cell(0, 5,
    f"Ticket médio Venda: R$ {ticket_medio_v:,.0f}  vs  Ticket médio Perda: R$ {ticket_medio_p:,.0f}  "
    f"(Fluxo ganha os pequenos e perde os grandes — razão 3,6x)"
)
pdf.ln(8)

# ── Performance por Coordenação ───────────────────────────────
pdf.titulo_secao("2. Performance por Coordenação de Serviço")

headers = ["Área", "Propostas", "Vendas", "Perdas", "Conv.%", "Ticket V", "Receita Gerada", "Prazo médio"]
widths  = [22, 22, 18, 18, 18, 28, 34, 30]
pdf.linha_tabela(headers, widths, header=True)

linhas_coord = [
    ("CCE", 70),
    ("MNP", 48),
    ("QAB", 41),
    ("PRO", 42),
    ("ACE", 35),
]
nomes = {"CCE":"CCE — Software", "MNP":"MNP — Mecatrônica",
         "QAB":"QAB — Químico/Alim.", "PRO":"PRO — Estratégia", "ACE":"ACE — Arquitetura"}
prazo_map = {"ACE":43,"CCE":62,"MNP":62,"PRO":57,"QAB":90}
for i, (c, _) in enumerate(sorted(coord_s.items(), key=lambda x: -(x[1]["v"]/(x[1]["v"]+x[1]["p"])*100 if (x[1]["v"]+x[1]["p"])>0 else 0))):
    s = coord_s[c]
    td = s["v"]+s["p"]
    conv = s["v"]/td*100 if td else 0
    tm = s["val_v"]/s["v"] if s["v"] else 0
    prazo = prazo_map.get(c, 0)
    vals = [nomes.get(c,c), s["n"], s["v"], s["p"],
            f"{conv:.0f}%", f'R$ {tm:,.0f}', f'R$ {s["val_v"]:,.0f}', f"{prazo} du"]
    pdf.linha_tabela(vals, widths, fill=(i%2==0))

pdf.ln(4)
pdf.corpo(
    "CCE (Software/Computação) lidera com 70% de conversão. PRO (Estratégia) gera a maior receita absoluta. "
    "ACE tem o maior volume de propostas mas a menor conversão (35%) e menor ticket médio — "
    "relação esforço/retorno mais fraca entre todas as coordenações."
)

# ── Performance por Canal ─────────────────────────────────────
pdf.titulo_secao("3. Performance por Canal de Aquisição")

# Filtrar canais principais
canais_principais = {
    "Indicação (membros/alumni)": canal_s.get("Indicação (membros/alumni)", {"n":0,"v":0,"p":0,"val_v":0}),
    "Fidelização": {k: canal_s.get("Fidelização",{"n":0,"v":0,"p":0,"val_v":0})[k] +
                      canal_s.get("fidelização MNP",{"n":0,"v":0,"p":0,"val_v":0}).get(k,0) +
                      canal_s.get("Fidelização AR",{"n":0,"v":0,"p":0,"val_v":0}).get(k,0)
                   for k in ["n","v","p","val_v"]},
    "Busca Orgânica | Google": canal_s.get("Busca Orgânica | Google", {"n":0,"v":0,"p":0,"val_v":0}),
    "Tráfego Direto": canal_s.get("Tráfego Direto", {"n":0,"v":0,"p":0,"val_v":0}),
    "Outbound": canal_s.get("Outbound", {"n":0,"v":0,"p":0,"val_v":0}),
    "Busca Paga | Google": canal_s.get("Busca Paga | Google", {"n":0,"v":0,"p":0,"val_v":0}),
    "Referência UFRJ": canal_s.get("Referência UFRJ", {"n":0,"v":0,"p":0,"val_v":0}),
}

hc = ["Canal", "Props.", "V", "P", "Conv.%", "Ticket V"]
wc = [65, 18, 12, 12, 22, 30]
pdf.linha_tabela(hc, wc, header=True)
for i, (canal, s) in enumerate(canais_principais.items()):
    td = s["v"]+s["p"]
    conv = s["v"]/td*100 if td else 0
    tm = s["val_v"]/s["v"] if s["v"] else 0
    pdf.linha_tabela([canal, s["n"], s["v"], s["p"], f"{conv:.0f}%", f'R$ {tm:,.0f}'],
                     wc, fill=(i%2==0))

pdf.ln(4)
pdf.corpo(
    "Indicação converte 3× mais que Google Pago. Fidelização entrega o maior ticket médio. "
    "Busca Paga no Google representa alto volume mas apenas 26% de conversão, "
    "gerando custo de aquisição elevado com retorno desproporcional."
)

# ── Tamanho e Faixa de Ticket ─────────────────────────────────
pdf.add_page()
pdf.titulo_secao("4. Conversão por Porte de Empresa e Faixa de Ticket")

pdf.subtitulo("Por porte de empresa")
ht = ["Porte", "Props.", "V", "P", "Conv.%", "Ticket V"]
wt = [40, 20, 14, 14, 24, 30]
pdf.linha_tabela(ht, wt, header=True)
portes = [
    ("Grande",       25, 7,  5,  58, 14247),
    ("Pessoa física",52, 20, 21, 49, 11955),
    ("Pequena",      54, 18, 20, 47, 9739),
    ("Média",        54, 10, 24, 29, 8490),
]
for i, (p, n, v, pe, conv, tm) in enumerate(portes):
    pdf.linha_tabela([p, n, v, pe, f"{conv}%", f"R$ {tm:,.0f}"], wt, fill=(i%2==0))

pdf.ln(4)
pdf.corpo(
    "Empresa Grande tem a maior conversão (58%) E o maior ticket (R$ 14.247). "
    "Empresa Média apresenta o pior resultado (29%) — processos de compra burocráticos "
    "sem orçamento proporcional ao esforço de venda."
)

pdf.ln(3)
pdf.subtitulo("Por faixa de ticket")
hf = ["Faixa de Ticket", "Props.", "V", "P", "Conv.%", "Observação"]
wf = [38, 18, 12, 12, 22, 58]
pdf.linha_tabela(hf, wf, header=True)
faixas = [
    ("Até R$ 3k",       20, 7,  11, 39, "Abaixo do ideal"),
    ("R$ 3k – R$ 8k",   58, 24, 17, 59, "Sweet spot de conversão"),
    ("R$ 8k – R$ 15k",  47, 13, 15, 46, "Zona produtiva"),
    ("R$ 15k – R$ 25k", 34,  7, 13, 35, "Conversão cai"),
    ("R$ 25k – R$ 50k", 22,  4, 10, 29, "Alta dificuldade"),
    ("Acima de R$ 50k",  6,  1,  4, 20, "Tickets grandes, low conv."),
]
for i, (f, n, v, p, conv, obs) in enumerate(faixas):
    cor = CINZA_CLARO if i%2==0 else BRANCO
    pdf.linha_tabela([f, n, v, p, f"{conv}%", obs], wf, fill=(i%2==0), fill_color=cor)

pdf.ln(4)
pdf.corpo(
    "O sistema de avaliação por estrelas confirma a predição: todos os leads com 4 estrelas "
    "converteram (45/45 = 100%). Leads com 1–2 estrelas tiveram 0% de conversão em 75 propostas, "
    "representando desperdício massivo de capacidade da equipe."
)

# ── Motivos de Perda ─────────────────────────────────────────
pdf.titulo_secao("5. Motivos de Perda e Objeções")

pdf.subtitulo("Motivos de perda em propostas")
hm = ["Motivo", "Ocorrências", "% do total"]
wm = [90, 30, 30]
pdf.linha_tabela(hm, wm, header=True)
motivos = [
    ("Concorrência", 13, 19),
    ("Não respondeu (ghost pós-proposta)", 12, 17),
    ("Preço elevado", 9, 13),
    ("Preferiu deixar para depois", 8, 11),
    ("Proposta recusada", 6, 9),
    ("Não executamos o serviço", 5, 7),
    ("Não informado", 13, 19),
]
for i, (m, n, pct) in enumerate(motivos):
    pdf.linha_tabela([m, n, f"{pct}%"], wm, fill=(i%2==0))

pdf.ln(4)
pdf.subtitulo("Objeções mais frequentes")
ho = ["Objeção", "Ocorrências"]
wo = [100, 30]
pdf.linha_tabela(ho, wo, header=True)
objecoes = [
    ("Preço", 33),
    ("Coletando outros orçamentos", 22),
    ("Validade da proposta", 12),
    ("Prazo", 11),
    ("Outros", 11),
    ("Autoridade / decisor não envolvido", 7),
    ("Parcelamento", 7),
]
for i, (o, n) in enumerate(objecoes):
    pdf.linha_tabela([o, n], wo, fill=(i%2==0))


# ══════════════════════════════════════════════════════════════
# ICPs INDIVIDUAIS (páginas próprias)
# ══════════════════════════════════════════════════════════════

perfis = [
    dict(
        num=1,
        titulo="Corporações e Grandes Empresas (B2B Enterprise)",
        combo="PRO + CCE + MNP (conforme demanda)",
        exemplos=[
            "Ambev (PE + Otimização Operacional) — R$ 22.000 — Canal: desconhecido",
            "OceanPact (PE + Sustentabilidade) — R$ 25.160 — Fidelização",
            "Segmedic (MPOP) — R$ 14.282 — Busca Paga Google",
            "Beep Saúde (Assessoria) — R$ 30.000 — Indicação de membro",
            "Casas Pedro (EVDFMC Temperos) — R$ 11.998 — Grande empresa alimentícia",
        ],
        quem_e=[
            "Empresa com 100+ funcionários, CNPJ estabelecido, operação formal",
            "Múltiplos decisores: gerente de área + diretoria",
            "Tem orçamento anual definido para projetos de melhoria",
            "Pressão interna por eficiência, ESG ou transformação digital",
        ],
        dores=[
            "Processos internos ineficientes gerando desperdício ou risco operacional",
            "Necessidade de metas e KPIs estruturados",
            "Pressão por digitalização e automação (BI, dashboards, PowerApps)",
            "Conformidade regulatória (BPF, PPCI, ESG, compliance)",
            "Geração de caixa e redução de custos operacionais",
        ],
        por_que=(
            "Credencial POLI/UFRJ como sinal de qualidade técnica. Custo 5–10× menor "
            "que grandes consultorias (McKinsey, Deloitte). Equipe multidisciplinar que "
            "resolve escopo amplo em um único fornecedor sem necessidade de coordenar "
            "múltiplos contratos."
        ),
        como_abordar=(
            "Canal prioritário: outbound via rede de alumni UFRJ. Abrir com reunião "
            "formal de diagnóstico com gerente de inovação ou operações. Proposta deve "
            "apresentar ROI estimado e benchmark setorial. Ciclo de venda: 6–12 semanas."
        ),
        ticket="R$ 10.000 – R$ 55.000+",
        prioridade="Alta"
    ),
    dict(
        num=2,
        titulo="Startups e PMEs de Tecnologia (B2B Tech)",
        combo="CCE + PRO (fidelização progressiva)",
        exemplos=[
            "Malvs Clean (AR → DEV → PN) — LTV R$ 83.458 — fidelização",
            "Tork One (CCE → DEV 2.0) — LTV R$ 29.348 — fidelização via MNP",
            "220 Decibéis (DEV sistema de eventos) — R$ 40.000",
            "PETREC (ER Rochas × 2 + DEV plataforma) — multi-projeto",
            "Brazil Sensations (automação receptivo turístico) — PRO + CCE",
        ],
        quem_e=[
            "PME já operante ou startup em fase de produto (2–50 pessoas)",
            "Sócio-fundador como decisor único — decisão ágil, sem burocracia",
            "Tem processo manual que precisa virar sistema digital",
            "Alta probabilidade de fidelização quando bem atendida na primeira entrega",
        ],
        dores=[
            "MVP que precisa ser lançado com prazo definido (edital, lançamento, mestrado)",
            "Integração de sistemas legados ou planilhas manuais com nova plataforma",
            "Automação de operações que consomem tempo do fundador",
            "Precisa de aplicativo mas não sabe como especificar o escopo",
        ],
        por_que=(
            "Equipe técnica atualizada (React, Flutter, IA, Bluetooth LE) com custo "
            "muito menor que software houses tradicionais. Flexibilidade para adaptar "
            "escopo durante o projeto. Relacionamento próximo — fator decisivo para "
            "que o cliente retorne para a segunda e terceira demanda."
        ),
        como_abordar=(
            "Porta de entrada ideal: Análise de Requisitos (AR) ou MPOP de baixo ticket. "
            "Após entrega, proativamente oferecer o DEV ou OP como fase 2. "
            "Nunca encerrar o projeto sem mapear a próxima demanda potencial do cliente. "
            "Canal mais eficaz: indicação de membros e presidência da EJ."
        ),
        ticket="R$ 3.000 – R$ 67.760 por projeto; LTV médio R$ 30k+",
        prioridade="Alta"
    ),
    dict(
        num=3,
        titulo="Empreendedores de Alimentos e Confeitaria",
        combo="QAB + MNP + PRO (escalonado por maturidade)",
        exemplos=[
            "Galo Doce (QAB + MNP + PRO simultâneos) — lead ativo de alto valor",
            "MC Onigiri (validade lonigiri) — R$ 11.600 — Facebook Ads",
            "Verônica Bolos (Bem Casado Pt2) — R$ 4.014 — fidelização",
            "Seven Green (PN Tangará) — R$ 9.700 — proposta em andamento",
            "EVDF Manchas Vinho (saneante premium) — R$ 21.000 — tráfego direto",
        ],
        quem_e=[
            "Microempresa ou MEI de confeitaria/alimentos/saneantes (1–10 pessoas)",
            "Dono do negócio é o decisor e o operador — tempo escasso",
            "Produto artesanal com demanda crescente mas produção limitada",
            "Presença ativa no Instagram; sensível a preço mas responde bem a resultados",
        ],
        dores=[
            "Produto endurece, perde cremosidade ou não aguentta temperatura do delivery",
            "Validade muito curta para o canal de vendas desejado (redes, e-commerce)",
            "Quer escalar produção mas sem fórmula estável não consegue",
            "Quer lançar versão fit/sem açúcar mas trava na formulação",
            "Produção 100% manual e dependente de uma única pessoa",
        ],
        por_que=(
            "Única opção acessível com respaldo científico (laboratório POLI/UFRJ). "
            "Custo muito menor que P&D corporativo. Consegue atender demandas "
            "específicas e artesanais que laboratórios comerciais recusam por "
            "volume insuficiente."
        ),
        como_abordar=(
            "Facebook Ads e Instagram Ads com copy focado no problema técnico "
            "(ex.: 'Seu produto perde a textura no delivery? A gente resolve.'). "
            "Formulário de entrada deve capturar número de pedidos/dia e principal dor "
            "para qualificação rápida. "
            "Clientes de QAB que estão crescendo devem receber oferta de PRO (PN) "
            "e MNP (maquinário) como expansão natural."
        ),
        ticket="R$ 4.000 – R$ 19.000 (QAB isolado); R$ 30.000–80.000 (multi-coord)",
        prioridade="Alta"
    ),
    dict(
        num=4,
        titulo="Inovadores em Engenharia e P&D de Equipamentos",
        combo="MNP + CCE ou MNP isolado com upsell",
        exemplos=[
            "Deseq Boia — FAPERJ/FINEP (alarme antipogamento) — R$ 19.700",
            "Techmedika (bolsa de sangue cirúrgica) — R$ 12.000 — busca orgânica",
            "ZM Surgical / ER Lente (ferramenta dental) — R$ 12.500",
            "GL Healthtech / EV Termoformadora — R$ 5.000 — busca paga",
            "PETREC (ER Amostra de Rochas × 2) — LTV R$ 20.260 — fidelização",
        ],
        quem_e=[
            "Startup de hardware ou pesquisador acadêmico com edital aprovado",
            "Empresa industrial que precisa de equipamento customizado inexistente no mercado",
            "Médico/cirurgião ou profissional técnico desenvolvendo produto para sua área",
            "Decisor único com expertise técnica — exige rigor de engenharia",
        ],
        dores=[
            "Tem protótipo ou ideia mas não tem equipe de engenharia para projeto formal",
            "Precisa de laudo/documento técnico para edital ou investimento",
            "Produto existente tem falsos positivos, imprecisão ou baixa eficiência",
            "Produção artesanal que precisa ser industrializada",
            "Tem verba de edital com prazo para gastar — menor objeção de preço",
        ],
        por_que=(
            "POLI/UFRJ tem credencial técnica forte para laudos e projetos de engenharia — "
            "barreira de entrada para concorrentes. Preço competitivo vs. escritórios de "
            "engenharia tradicionais. Atende o nicho de engenharia customizada que "
            "fornecedores de prateleira recusam."
        ),
        como_abordar=(
            "Prospecção ativa em chamadas públicas FAPERJ, FINEP e CNPq — pesquisadores "
            "agraciados têm orçamento definido e urgência de prazo. "
            "Google Search com palavras-chave técnicas ('desenvolvimento de equipamento "
            "médico', 'projeto de máquina industrial') já funciona (Techmedika veio assim). "
            "Proposta deve incluir um EV (Estudo de Viabilidade) como fase 1 "
            "antes do Desmaq completo."
        ),
        ticket="R$ 5.000 – R$ 25.000",
        prioridade="Alta"
    ),
    dict(
        num=5,
        titulo="Setor Offshore, Naval e Indústria Pesada",
        combo="MNP + PRO + CCE (projetos integrados)",
        exemplos=[
            "Oceânica Engenharia (visão computacional ROV) — R$ 8.000 — alumni",
            "OceanPact (PE + metas ESG) — R$ 25.160 — fidelização",
            "Navia Pipeline (garras para dutos submarinos) — R$ 13.000 — orgânico",
            "OceanInfinity (PowerApps plataforma operacional) — R$ 25.000 — relacionamento",
            "Bridge Log (neutralização de carbono) — R$ 12.590 — follow-up ativo",
        ],
        quem_e=[
            "Empresa de médio a grande porte nos setores de petróleo, gás, offshore, naval",
            "Gerente de Inovação ou Engenheiro Sênior como primeiro contato",
            "Diretoria como decisor final — processo de aprovação formal",
            "Tem demanda de inovação tecnológica em ambientes hostis (pressão, corrosão, submarino)",
        ],
        dores=[
            "Analisar imagens de ROV ou sensores para gerar banco histórico de dados",
            "Metas de ESG e neutralização de carbono exigidas por reguladores e investidores",
            "Digitalizar processos internos com low-code (PowerApps, Power BI)",
            "Desenvolver mecanismos mecânicos para ambientes extremos",
            "Plataformas de dados técnicos (geofísica, geologia) que precisam de evolução",
        ],
        por_que=(
            "O canal Alumni UFRJ é uma barreira de entrada quase intransponível: "
            "concorrentes não têm acesso à rede de engenheiros formados pela POLI "
            "que trabalham nessas empresas. A credencial acadêmica + capacidade de "
            "pesquisa aplicada é altamente valorizada neste setor. Custo 5× menor "
            "que consultorias especializadas offshore."
        ),
        como_abordar=(
            "Ativar sistematicamente a rede de ex-membros que trabalham no setor "
            "(newsletter mensal de casos técnicos + pedido direto de indicação). "
            "Criar uma landing page específica para o setor offshore com os casos "
            "Oceânica, OceanPact e Navia como âncoras de credibilidade. "
            "Não esperar o lead chegar — fazer outbound via LinkedIn targeting "
            "'Gerente de Inovação' em empresas de oil & gas no Brasil."
        ),
        ticket="R$ 8.000 – R$ 55.000+",
        prioridade="Alta"
    ),
]

for p in perfis:
    pdf.perfil_icp(**p)


# ── ICPs Multidisciplinares ────────────────────────────────────
pdf.add_page()
pdf.titulo_secao("7. Perfis Ideais para Abordagem Multidisciplinar")

pdf.corpo(
    "Os dados revelam 152 cards com envolvimento de 2 ou mais coordenações. "
    "O combo CCE+PRO tem 80% de conversão — o maior de qualquer segmento analisado. "
    "O caso Malvs Clean (LTV R$ 83.458) demonstra que o maior potencial de receita está "
    "em clientes que começam com um projeto pequeno e expandem para múltiplas coordenações. "
    "A regra de ouro: o cliente não chega pedindo multi — a Fluxo descobre no diagnóstico."
)

pdf.ln(3)
pdf.subtitulo("Combos com dados suficientes para análise")

hco = ["Combo", "Props.", "V", "P", "Conv.%", "Ticket V"]
wco = [55, 18, 12, 12, 25, 38]
pdf.linha_tabela(hco, wco, header=True)
combos_dados = [
    ("CCE + PRO", 8, 4, 1, "80%", "R$ 7.819"),
    ("QAB + MNP + PRO (Galo Doce, Brigadeiro)", 2, 0, 1, "—", "R$ 40.000 perdido"),
    ("PRO + QAB (químico/cosmético)", 1, 0, 0, "—", "R$ 23.000 pipeline"),
]
for i, row in enumerate(combos_dados):
    pdf.linha_tabela(list(row), wco, fill=(i%2==0))

pdf.ln(5)

# 5 perfis multi
multi_perfis = [
    ("M1", "Empreendedor Processo + Tecnologia", "PRO + CCE",
     "Alta — 80% conv.", "R$ 5k–30k / projeto; R$ 30k+ LTV",
     [
         "Malvs Clean: AR → DEV → PN = R$ 83.458 em LTV",
         "LiveMode: OP de IA + processos = R$ 5.000 (PRO+CCE)",
         "Cleber (bancas de jornal): OP + DEV integração = R$ 6.220",
         "Renata (personal chef): OP + software lista de compras = R$ 5.057",
     ],
     "Dono de PME com processo manual que quer automatizar. Decisão rápida, 1 decisor.",
     "Oferecer AR ou MPOP como entrada, propor DEV/OP após entrega. "
     "Nunca encerrar projeto sem mapear próxima demanda."),

    ("M2", "Inovador Hardware + Software", "MNP + CCE",
     "Alta — casos com LTV crescente", "R$ 15k–60k",
     [
         "Tork One (dispositivo automotivo + app Bluetooth): LTV R$ 29.348",
         "Deseq + DEV Oxigenius: R$ 43.000 em pipeline (MNP+CCE)",
         "Deseq Boia (FAPERJ/FINEP, circuito eletrônico + IA): R$ 19.700",
     ],
     "Startup de hardware ou pesquisador com edital. Produto físico que precisa de firmware/app.",
     "Prospectar editais FAPERJ/FINEP. Proposta integrada hardware+software "
     "numa única proposta — não dois módulos separados."),

    ("M3", "Fabricante de Alimentos Escalando", "QAB + MNP + PRO",
     "Muito alta — diferencial único", "R$ 30k–80k",
     [
         "Galo Doce (marca histórica): fórmula + maquinário + estratégia (ativo)",
         "EVDF Bebida Funcional: QAB+PRO = R$ 23.000 pausado",
         "Desmaq+MC Brigadeiro (perda): R$ 40.000 — grande demais para o momento",
     ],
     "Empresa alimentícia pequena/média, produto artesanal, produção manual, quer escalar.",
     "Diagnóstico conjunto das 3 coordenações na mesma reunião. "
     "Apresentar o 'antes e depois' completo: produto estável + máquina + estratégia."),

    ("M4", "Empreendedor de Produto Químico/Cosmético", "QAB + PRO",
     "Média-alta", "R$ 10k–30k",
     [
         "EVDF Manchas Vinho (saneante premium): R$ 21.000 convertido",
         "EVDF Drink sem Álcool: R$ 19.000 convertido",
         "AF Benuá / CORA Beauty (precificação): R$ 6.032 convertido",
         "EVDF Bebida Funcional: R$ 23.000 em pipeline",
     ],
     "Empreendedor com fórmula base buscando validação técnica + visão de mercado simultâneas.",
     "Toda proposta QAB deve incluir oferta PRO complementar. "
     "Apresentar como 'Programa de Lançamento de Produto' em 2 fases."),

    ("M5", "Empresa Industrial com Inovação + Estratégia", "MNP+PRO ou PRO+CCE",
     "Alta — maior ticket médio", "R$ 20k–60k",
     [
         "Ambev: otimização operacional + geração de caixa — R$ 22.000",
         "OceanInfinity (PowerApps): R$ 25.000 via relacionamento",
         "AR Oceânica (visão computacional): R$ 8.000 — alumni UFRJ",
         "MPOP+AR+MER CGIR: R$ 46.580 — maior pipeline ativo individual",
     ],
     "Médio/grande porte industrial, offshore ou serviços especializados. "
     "Quer inovar com IA, automação e análise de dados.",
     "Rede Alumni UFRJ como canal exclusivo. Outbound via LinkedIn "
     "targeting 'Gerente de Inovação' em oil & gas, offshore, manufatura."),
]

for mp in multi_perfis:
    num, titulo, combo, prioridade, ticket, exemplos, quem_e, como = mp
    pdf.ln(2)
    # mini-card colorido
    pdf.set_fill_color(*AZUL_MEDIO)
    pdf.rect(pdf.l_margin, pdf.get_y(), 190, 7, "F")
    pdf.set_xy(pdf.l_margin+3, pdf.get_y()+1)
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(*BRANCO)
    pdf.cell(60, 5, f"{num} — {titulo}")
    pdf.cell(40, 5, f"Combo: {combo}")
    pdf.cell(40, 5, f"Ticket: {ticket}")
    pdf.cell(0, 5, f"Prioridade: {prioridade}")
    pdf.set_text_color(*CINZA_ESCURO)
    pdf.ln(9)

    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(pdf.l_margin+3)
    pdf.cell(0, 5, quem_e[:110])
    pdf.ln(5)

    for ex in exemplos[:3]:
        pdf.set_font("Arial", "", 8)
        pdf.set_x(pdf.l_margin+5)
        pdf.cell(4, 4, "•")
        pdf.multi_cell(180, 4, ex)
    pdf.set_font("Arial", "B", 8)
    pdf.set_x(pdf.l_margin+3)
    pdf.set_text_color(*AZUL_ESCURO)
    pdf.cell(20, 5, "Abordar: ")
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(*CINZA_ESCURO)
    pdf.multi_cell(170, 4, como)
    pdf.ln(2)


# ── Recomendações Finais ──────────────────────────────────────
pdf.add_page()
pdf.titulo_secao("8. Recomendações Estratégicas Prioritárias")

recomendacoes = [
    ("1", "Não enviar proposta para leads com 1–2 estrelas",
     "Representam 75 propostas com 0% de conversão. Oferecer pré-diagnóstico "
     "rápido e encerrar o card. Libera ~40% da capacidade comercial da equipe.",
     VERMELHO),
    ("2", "Reativar os 46 Pausados (R$ 695.117 em pipeline latente)",
     "Uma campanha de reativação direcionada pode gerar receita imediata sem "
     "nenhum custo de aquisição. Priorizar: DS ViX (R$ 55k), CGIR (R$ 46k), "
     "Oxigenius (R$ 43k), Sabão e Amaciante (R$ 40k).",
     LARANJA),
    ("3", "Ativar sistematicamente o canal Alumni UFRJ",
     "Newsletter mensal com cases técnicos + pedido explícito de indicação. "
     "Canal com 80%+ de conversão quando utilizado. Offline: manter cadastro "
     "de ex-membros empregados em empresas-alvo.",
     VERDE),
    ("4", "Criar programa de pós-venda com oferta de próxima fase",
     "Após cada entrega, o responsável deve mapear e propor a demanda adjacente. "
     "Modelo Malvs Clean (AR → DEV → PN = R$ 83k LTV) deve ser o padrão, "
     "não a exceção. Montar playbook por tipo de cliente.",
     AZUL_MEDIO),
    ("5", "Reduzir Google Ads para ACE residencial (conv. 26%)",
     "Redirecionar verba para conteúdo técnico no Instagram/LinkedIn "
     "e para outbound B2B nos segmentos offshore e industrial.",
     AZUL_MEDIO),
    ("6", "Prospectar pesquisadores com editais FAPERJ/FINEP/CNPq ativos",
     "Leads com financiamento público têm orçamento definido, prazo de gasto "
     "e baixa objeção de preço. Monitorar chamadas públicas mensalmente e "
     "fazer outbound para pesquisadores agraciados.",
     VERDE),
    ("7", "Toda proposta QAB deve incluir oferta PRO complementar",
     "Empreendedores de alimentos/cosméticos que precisam de formulação "
     "também precisam de viabilidade de mercado e precificação. "
     "Apresentar como 'Programa de Lançamento' em 2 fases com desconto bundle.",
     AZUL_MEDIO),
]

for num, titulo, desc, cor in recomendacoes:
    # Badge numerado
    pdf.set_fill_color(*cor)
    x, y = pdf.l_margin, pdf.get_y()
    pdf.rect(x, y, 8, 8, "F")
    pdf.set_xy(x, y+1)
    pdf.set_font("Arial", "B", 8)
    pdf.set_text_color(*BRANCO)
    pdf.cell(8, 5, num, align="C")
    # Título
    pdf.set_xy(x+10, y)
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(*CINZA_ESCURO)
    pdf.cell(0, 5, titulo)
    pdf.ln(5)
    # Descrição
    pdf.set_x(x+10)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(178, 4, desc)
    pdf.ln(3)


# ── Limitações e Dados a Coletar ─────────────────────────────
pdf.titulo_secao("9. Limitações dos Dados e Melhorias Recomendadas")

pdf.corpo(
    "A análise foi realizada sobre dados reais do Pipefy com as seguintes limitações "
    "que impactam a precisão dos ICPs identificados:"
)

limitacoes = [
    ("Setor/Indústria", "Apenas 4 de 152 cards multidisciplinares têm setor preenchido",
     "Adicionar campo select obrigatório no formulário de entrada"),
    ("Cargo do decisor", "Ausente na maioria dos cards — impede análise de persona",
     "Campo obrigatório na fase de diagnóstico"),
    ("Canal de aquisição", "35 variantes distintas por falta de padronização",
     "Transformar em select com opções fixas"),
    ("Faturamento da empresa", "Não coletado — impede segmentação por maturidade financeira",
     "Perguntar indiretamente via budget disponível no formulário"),
    ("NPS pós-projeto", "Sem dados de satisfação para correlacionar com fidelização",
     "Criar pesquisa automática via Pipefy após fase 'Venda'"),
    ("Dados de tempo por fase", "Timestamps inconsistentes — impede calcular velocidade do funil",
     "Garantir preenchimento das datas em todas as fases"),
]

hl = ["Dado faltante", "Impacto", "Solução"]
wl = [42, 72, 66]
pdf.linha_tabela(hl, wl, header=True)
for i, (dado, impacto, solucao) in enumerate(limitacoes):
    pdf.linha_tabela([dado, impacto, solucao], wl, fill=(i%2==0))


# ── Salvar ───────────────────────────────────────────────────
output_path = r"c:\Users\Rodrigo\Desktop\site\pipefymetaanalysis\pipefy-crm\Relatorio_ICP_Fluxo.pdf"
pdf.output(output_path)
print(f"PDF gerado com sucesso: {output_path}")
print(f"Total de páginas: {pdf.page_no()}")
