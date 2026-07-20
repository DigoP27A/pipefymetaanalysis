# Deploy do Dashboard Fluxo

Este documento mostra 3 formas de colocar o dashboard no ar. A recomendada é **Streamlit Community Cloud** (gratuito, ~10 min).

---

## Opção 1 — Streamlit Community Cloud (recomendado, grátis)

Você terá uma URL pública do tipo `https://fluxo-crm.streamlit.app` que qualquer pessoa com o link pode abrir.

### Pré-requisitos
- Uma conta no [GitHub](https://github.com)
- Uma conta no [Streamlit Cloud](https://share.streamlit.io) (login com o próprio GitHub)

### Passo 1 — Subir o código pro GitHub

Na pasta `pipefy-crm/`, abra um terminal e rode:

```bash
git init
git add dashboard.py requirements.txt .gitignore .streamlit/config.toml extrator.py dados/cards_raw.json
git commit -m "Dashboard Fluxo pronto para deploy"
```

Crie um repositório novo em https://github.com/new (pode ser **privado** — o Streamlit Cloud consegue acessar). Depois:

```bash
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/fluxo-crm.git
git push -u origin main
```

> **Importante:** o `.gitignore` já bloqueia o `.env` (com seu token do Pipefy). Nunca envie ele pro GitHub.

### Passo 2 — Publicar no Streamlit Cloud

1. Vá em https://share.streamlit.io e clique em **"New app"**.
2. Escolha o repositório que você acabou de criar.
3. Preencha:
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
   - **App URL:** escolha algo como `fluxo-crm` (a URL final vai ser `fluxo-crm.streamlit.app`)
4. Clique em **"Deploy!"**. Em ~2 min o app fica no ar.

### Passo 3 — Compartilhar

Copie o link (`https://fluxo-crm.streamlit.app`) e mande no grupo da empresa. Qualquer pessoa com o link consegue abrir.

Se quiser proteger com senha (para restringir a membros da Fluxo):
- No Streamlit Cloud → **Settings → Sharing** → marque **"Password"** e defina uma senha.

### Atualizar os dados

Sempre que quiser puxar os cards mais recentes do Pipefy:

```bash
# Na sua máquina local
python extrator.py
git add dados/cards_raw.json
git commit -m "Atualiza dados"
git push
```

O Streamlit Cloud detecta o push e re-deploya automaticamente em ~30s.

**Automação opcional:** dá pra criar um GitHub Action que roda o `extrator.py` todo dia às 8h. Se quiser, me peça pra criar o workflow.

---

## Opção 2 — Ngrok (mais rápido, só pra testes)

Se quiser mostrar o dashboard *agora* pro time sem colocar no GitHub:

1. Instale o [Ngrok](https://ngrok.com/download)
2. Rode o dashboard local:
   ```bash
   streamlit run dashboard.py
   ```
3. Em outro terminal:
   ```bash
   ngrok http 8501
   ```
4. Ele vai gerar uma URL pública tipo `https://abc123.ngrok-free.app` — mande esse link.

**Limitação:** só funciona enquanto seu PC estiver ligado e o `ngrok` rodando. Bom pra reunião, ruim pra uso contínuo.

---

## Opção 3 — Render.com (gratuito, sempre online)

Se preferir não usar o Streamlit Cloud:

1. Suba o código no GitHub (mesmo passo 1 acima).
2. Vá em https://render.com → **"New Web Service"** → conecte o repositório.
3. Configure:
   - **Environment:** Python
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0`
4. Deploy. URL final: `https://fluxo-crm.onrender.com`

**Ponto de atenção:** o plano free do Render "hiberna" após 15 min sem uso — a primeira requisição do dia demora ~30s pra acordar.

---

## Recomendação final

Para uso interno da Fluxo, use **Streamlit Cloud** com senha. É o setup mais simples, o app fica sempre online, e a atualização dos dados é `git push`.
