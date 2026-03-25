import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Finanças Pessoais",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif;
}

/* Background */
.stApp {
    background: #0d0f14;
    color: #e8e4dc;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #131620 !important;
    border-right: 1px solid #1e2230;
}
section[data-testid="stSidebar"] .stMarkdown p {
    color: #8891a8;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: #131620;
    border: 1px solid #1e2230;
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
}
div[data-testid="metric-container"] label {
    color: #8891a8 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #e8e4dc !important;
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem !important;
    font-weight: 700;
}

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input {
    background-color: #131620 !important;
    border: 1px solid #1e2230 !important;
    border-radius: 10px !important;
    color: #e8e4dc !important;
}
.stSelectbox > div > div > div {
    color: #e8e4dc !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4f7cff, #7c4fff);
    color: white;
    border: none;
    border-radius: 10px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 0.5rem 1.5rem;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(79,124,255,0.35);
}

/* Dataframe */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

/* Section headers */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e8e4dc;
    letter-spacing: 0.03em;
    margin-bottom: 0.3rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1e2230, transparent);
    margin-left: 0.5rem;
}

/* Category badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-receita { background: rgba(72,199,116,0.15); color: #48c774; }
.badge-despesa { background: rgba(255,99,99,0.15); color: #ff6363; }

/* Alert boxes */
.alert-success {
    background: rgba(72,199,116,0.1);
    border: 1px solid rgba(72,199,116,0.3);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    color: #48c774;
}
.alert-danger {
    background: rgba(255,99,99,0.1);
    border: 1px solid rgba(255,99,99,0.3);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    color: #ff6363;
}
</style>
""", unsafe_allow_html=True)

# ── Session State / Persistence ───────────────────────────────────────────────
DATA_FILE = "/tmp/financas_data.json"

CATEGORIAS_DESPESA = [
    "🏠 Moradia", "🍔 Alimentação", "🚗 Transporte", "💊 Saúde",
    "🎓 Educação", "🎭 Lazer", "👔 Vestuário", "💡 Contas / Serviços",
    "💳 Dívidas", "📦 Outros"
]
CATEGORIAS_RECEITA = [
    "💼 Salário", "💰 Freelance", "📈 Investimentos", "🏦 Rendimentos",
    "🎁 Presente / Doação", "🏪 Venda", "📦 Outros"
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            d = json.load(f)
        return pd.DataFrame(d) if d else empty_df()
    return empty_df()

def save_data(df):
    with open(DATA_FILE, "w") as f:
        json.dump(df.to_dict(orient="records"), f, default=str)

def empty_df():
    return pd.DataFrame(columns=["data", "tipo", "categoria", "descricao", "valor"])

if "df" not in st.session_state:
    st.session_state.df = load_data()
if "tab" not in st.session_state:
    st.session_state.tab = "Dashboard"

# ── Helper ────────────────────────────────────────────────────────────────────
def fmt_brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_df_typed():
    df = st.session_state.df.copy()
    if df.empty:
        return df
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    return df

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 FinanControl")
    st.markdown("---")

    st.markdown("NAVEGAÇÃO")
    pages = {"📊 Dashboard": "Dashboard", "➕ Lançamentos": "Lancamentos",
             "📋 Histórico": "Historico", "🎯 Orçamento": "Orcamento"}
    for label, key in pages.items():
        active = st.session_state.tab == key
        if st.button(label, key=f"nav_{key}",
                     use_container_width=True,
                     type="primary" if active else "secondary"):
            st.session_state.tab = key
            st.rerun()

    st.markdown("---")

    # Quick summary
    df = get_df_typed()
    if not df.empty:
        receitas = df[df["tipo"] == "Receita"]["valor"].sum()
        despesas = df[df["tipo"] == "Despesa"]["valor"].sum()
        saldo = receitas - despesas
        color = "#48c774" if saldo >= 0 else "#ff6363"
        st.markdown(f"""
        <div style='background:#0d0f14;border:1px solid #1e2230;border-radius:12px;padding:1rem;'>
            <div style='color:#8891a8;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;'>Saldo Atual</div>
            <div style='color:{color};font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;margin-top:4px;'>{fmt_brl(saldo)}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Pages ─────────────────────────────────────────────────────────────────────
tab = st.session_state.tab
df = get_df_typed()

# ──────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────
if tab == "Dashboard":
    st.markdown("# 📊 Dashboard")

    if df.empty:
        st.info("Nenhum lançamento ainda. Vá em **➕ Lançamentos** para começar!")
    else:
        receitas = df[df["tipo"] == "Receita"]["valor"].sum()
        despesas = df[df["tipo"] == "Despesa"]["valor"].sum()
        saldo = receitas - despesas
        num_lancamentos = len(df)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💚 Total Receitas", fmt_brl(receitas))
        c2.metric("🔴 Total Despesas", fmt_brl(despesas))
        delta_label = "Positivo ✅" if saldo >= 0 else "Negativo ⚠️"
        c3.metric("💰 Saldo", fmt_brl(saldo), delta_label)
        c4.metric("📄 Lançamentos", num_lancamentos)

        st.markdown("<br>", unsafe_allow_html=True)
        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown('<div class="section-title">📈 Evolução Mensal</div>', unsafe_allow_html=True)
            df_m = df.copy()
            df_m["mes"] = df_m["data"].dt.to_period("M").astype(str)
            monthly = df_m.groupby(["mes", "tipo"])["valor"].sum().reset_index()
            if not monthly.empty:
                fig = px.bar(monthly, x="mes", y="valor", color="tipo",
                             barmode="group",
                             color_discrete_map={"Receita": "#4f7cff", "Despesa": "#ff6363"},
                             labels={"mes": "Mês", "valor": "Valor (R$)", "tipo": ""},
                             template="plotly_dark")
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans", color="#8891a8"),
                    legend=dict(orientation="h", y=1.1),
                    margin=dict(l=0, r=0, t=10, b=0),
                )
                fig.update_yaxes(gridcolor="#1e2230", tickprefix="R$ ")
                fig.update_xaxes(gridcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.markdown('<div class="section-title">🍕 Despesas por Categoria</div>', unsafe_allow_html=True)
            desp = df[df["tipo"] == "Despesa"]
            if not desp.empty:
                cat_sum = desp.groupby("categoria")["valor"].sum().reset_index()
                fig2 = px.pie(cat_sum, names="categoria", values="valor",
                              hole=0.55, template="plotly_dark",
                              color_discrete_sequence=px.colors.sequential.Plasma_r)
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans", color="#8891a8"),
                    showlegend=True,
                    legend=dict(font=dict(size=11)),
                    margin=dict(l=0, r=0, t=10, b=0),
                )
                fig2.update_traces(textinfo="percent", textfont_size=12)
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">🕐 Últimos Lançamentos</div>', unsafe_allow_html=True)
        recent = df.sort_values("data", ascending=False).head(8).copy()
        recent["data"] = recent["data"].dt.strftime("%d/%m/%Y")
        recent["valor_fmt"] = recent.apply(
            lambda r: f"{'+ ' if r['tipo']=='Receita' else '- '}{fmt_brl(r['valor'])}", axis=1)
        st.dataframe(
            recent[["data", "tipo", "categoria", "descricao", "valor_fmt"]].rename(columns={
                "data": "Data", "tipo": "Tipo", "categoria": "Categoria",
                "descricao": "Descrição", "valor_fmt": "Valor"
            }),
            use_container_width=True, hide_index=True
        )

# ──────────────────────────────────────────────────────────────────────────────
# LANÇAMENTOS
# ──────────────────────────────────────────────────────────────────────────────
elif tab == "Lancamentos":
    st.markdown("# ➕ Novo Lançamento")

    with st.form("form_lancamento", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Tipo *", ["Despesa", "Receita"])
            valor = st.number_input("Valor (R$) *", min_value=0.01, step=0.01, format="%.2f")
            data_input = st.date_input("Data *", value=date.today())
        with c2:
            categorias = CATEGORIAS_DESPESA if tipo == "Despesa" else CATEGORIAS_RECEITA
            categoria = st.selectbox("Categoria *", categorias)
            descricao = st.text_input("Descrição", placeholder="Ex: Conta de luz, Salário mensal...")

        submitted = st.form_submit_button("💾 Salvar Lançamento", use_container_width=True)

        if submitted:
            if valor <= 0:
                st.error("O valor deve ser maior que zero.")
            else:
                new_row = pd.DataFrame([{
                    "data": str(data_input),
                    "tipo": tipo,
                    "categoria": categoria,
                    "descricao": descricao or "—",
                    "valor": valor,
                }])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df)
                color = "badge-receita" if tipo == "Receita" else "badge-despesa"
                st.markdown(f"""
                <div class="alert-{'success' if tipo=='Receita' else 'danger'}">
                    ✅ Lançamento de <strong>{fmt_brl(valor)}</strong> em
                    <strong>{categoria}</strong> adicionado com sucesso!
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📥 Importar CSV")
    st.caption("O arquivo deve ter as colunas: `data`, `tipo`, `categoria`, `descricao`, `valor`")
    uploaded = st.file_uploader("Escolha um CSV", type="csv")
    if uploaded:
        try:
            imported = pd.read_csv(uploaded)
            required = {"data", "tipo", "categoria", "descricao", "valor"}
            if required.issubset(set(imported.columns)):
                st.session_state.df = pd.concat([st.session_state.df, imported], ignore_index=True)
                save_data(st.session_state.df)
                st.success(f"✅ {len(imported)} lançamentos importados!")
            else:
                st.error(f"Colunas necessárias: {required}")
        except Exception as e:
            st.error(f"Erro ao importar: {e}")

# ──────────────────────────────────────────────────────────────────────────────
# HISTÓRICO
# ──────────────────────────────────────────────────────────────────────────────
elif tab == "Historico":
    st.markdown("# 📋 Histórico de Lançamentos")

    if df.empty:
        st.info("Nenhum lançamento encontrado.")
    else:
        # Filters
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            tipos = ["Todos"] + list(df["tipo"].unique())
            filtro_tipo = st.selectbox("Tipo", tipos)
        with fc2:
            cats = ["Todas"] + sorted(df["categoria"].unique().tolist())
            filtro_cat = st.selectbox("Categoria", cats)
        with fc3:
            meses = ["Todos"] + sorted(df["data"].dt.to_period("M").astype(str).unique().tolist(), reverse=True)
            filtro_mes = st.selectbox("Mês", meses)

        filtered = df.copy()
        if filtro_tipo != "Todos":
            filtered = filtered[filtered["tipo"] == filtro_tipo]
        if filtro_cat != "Todas":
            filtered = filtered[filtered["categoria"] == filtro_cat]
        if filtro_mes != "Todos":
            filtered = filtered[filtered["data"].dt.to_period("M").astype(str) == filtro_mes]

        filtered = filtered.sort_values("data", ascending=False)

        st.markdown(f"**{len(filtered)}** registros encontrados.")

        display = filtered.copy()
        display["data"] = display["data"].dt.strftime("%d/%m/%Y")
        display["valor"] = display["valor"].apply(fmt_brl)

        edited = st.data_editor(
            display[["data", "tipo", "categoria", "descricao", "valor"]].rename(columns={
                "data": "Data", "tipo": "Tipo", "categoria": "Categoria",
                "descricao": "Descrição", "valor": "Valor"
            }),
            use_container_width=True,
            hide_index=False,
            num_rows="dynamic"
        )

        col_del, col_exp = st.columns([1, 3])
        with col_del:
            if st.button("🗑️ Limpar TODOS os dados", type="secondary"):
                st.session_state.df = empty_df()
                save_data(st.session_state.df)
                st.rerun()
        with col_exp:
            csv = filtered.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Exportar CSV", csv, "lancamentos.csv", "text/csv",
                               use_container_width=False)

# ──────────────────────────────────────────────────────────────────────────────
# ORÇAMENTO
# ──────────────────────────────────────────────────────────────────────────────
elif tab == "Orcamento":
    st.markdown("# 🎯 Controle de Orçamento")
    st.caption("Defina metas mensais por categoria e acompanhe seu progresso.")

    if "orcamento" not in st.session_state:
        st.session_state.orcamento = {}

    st.markdown("### Definir Metas")
    cols = st.columns(2)
    for i, cat in enumerate(CATEGORIAS_DESPESA):
        with cols[i % 2]:
            val = st.number_input(
                cat, min_value=0.0, step=50.0, format="%.2f",
                value=float(st.session_state.orcamento.get(cat, 0)),
                key=f"orc_{cat}"
            )
            st.session_state.orcamento[cat] = val

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Progresso do Mês Atual")

    if df.empty:
        st.info("Nenhum lançamento para comparar.")
    else:
        mes_atual = date.today().strftime("%Y-%m")
        df_mes = df[df["data"].dt.to_period("M").astype(str) == mes_atual]
        desp_mes = df_mes[df_mes["tipo"] == "Despesa"].groupby("categoria")["valor"].sum()

        for cat in CATEGORIAS_DESPESA:
            meta = st.session_state.orcamento.get(cat, 0)
            gasto = float(desp_mes.get(cat, 0))
            if meta > 0 or gasto > 0:
                pct = min(gasto / meta, 1.0) if meta > 0 else 1.0
                cor = "#48c774" if pct < 0.7 else ("#f5a623" if pct < 1.0 else "#ff6363")
                status = "✅" if pct < 0.7 else ("⚠️" if pct < 1.0 else "🚨")
                st.markdown(f"""
                <div style='margin-bottom:1rem;'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                        <span style='font-size:0.9rem;color:#e8e4dc;'>{status} {cat}</span>
                        <span style='font-size:0.85rem;color:#8891a8;'>{fmt_brl(gasto)} / {fmt_brl(meta) if meta>0 else "sem meta"}</span>
                    </div>
                    <div style='background:#1e2230;border-radius:20px;height:8px;overflow:hidden;'>
                        <div style='width:{pct*100:.1f}%;background:{cor};height:100%;border-radius:20px;transition:width 0.4s ease;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
