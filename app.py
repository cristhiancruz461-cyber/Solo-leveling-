import streamlit as st
from google import genai
from google.genai import types
import json
import random
from datetime import datetime, date
import time

# ─────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="SISTEMA // ARISE",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
#  GLOBAL CSS – Solo Leveling dark aesthetic
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;800&display=swap');

:root {
    --bg:        #020408;
    --panel:     #080f1a;
    --border:    #0a2a4a;
    --blue:      #00aaff;
    --blue-dim:  #004477;
    --red:       #ff2244;
    --red-dim:   #550011;
    --gold:      #ffc107;
    --gold-dim:  #7a5c00;
    --green:     #00ff88;
    --text:      #c8daf0;
    --muted:     #4a6a8a;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Exo 2', sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding: 1rem 2rem 4rem 2rem !important; max-width: 1400px !important;}

/* ── SCANLINE overlay ── */
body::before {
    content: '';
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,170,255,0.015) 2px,
        rgba(0,170,255,0.015) 4px
    );
    pointer-events: none; z-index: 9999;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #001428, #002a55) !important;
    color: var(--blue) !important;
    border: 1px solid var(--blue-dim) !important;
    border-radius: 2px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
    padding: 0.5rem 1.2rem !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #002855, #004a99) !important;
    border-color: var(--blue) !important;
    box-shadow: 0 0 18px rgba(0,170,255,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input {
    background: #050d1a !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    font-family: 'Share Tech Mono', monospace !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 10px rgba(0,170,255,0.3) !important;
}

/* ── METRICS ── */
[data-testid="metric-container"] {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    padding: 0.8rem 1rem !important;
}
[data-testid="metric-container"] label {
    color: var(--muted) !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.2em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--blue) !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 1.6rem !important;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--blue-dim), var(--blue)) !important;
    box-shadow: 0 0 8px var(--blue) !important;
}
.stProgress > div > div > div {
    background: #0a1a2a !important;
    border-radius: 0px !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.6rem 1.5rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--blue) !important;
    border-bottom: 2px solid var(--blue) !important;
    background: rgba(0,170,255,0.05) !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.7rem !important;
}

/* ── CHECKBOX ── */
.stCheckbox > label > span {
    color: var(--text) !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── DIVIDER ── */
hr {border-color: var(--border) !important; margin: 1rem 0 !important;}

/* ── MARKDOWN ── */
h1, h2, h3 {font-family: 'Orbitron', monospace !important; letter-spacing: 0.1em !important;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────
def init_state():
    defaults = {
        "gemini_key": "",
        "player_name": "CAÇADOR",
        "rank": "E",
        "xp": 0,
        "xp_to_next": 100,
        "level": 1,
        "streak": 0,
        "last_login": str(date.today()),
        "mantra_shown": False,
        "challenges": [],
        "completed_today": [],
        "penalty_count": 0,
        "chat_history": [],
        "gate_open": False,
        "initialized": False,
        "stats": {
            "Força Mental": 10,
            "Disciplina":   10,
            "Conhecimento": 10,
            "Liderança":    10,
            "Visão":        10,
        }
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────
#  RANK SYSTEM
# ─────────────────────────────────────────
RANKS = [
    ("E", 0,    100,  "Estudante Perdido",        "#4a6a8a"),
    ("D", 100,  300,  "Aprendiz Desperto",         "#00aa55"),
    ("C", 300,  700,  "Empreendedor Iniciante",    "#0088ff"),
    ("B", 700,  1500, "Líder em Formação",         "#aa44ff"),
    ("A", 1500, 3000, "Executivo Ascendente",      "#ffaa00"),
    ("S", 3000, 6000, "Diretor Visionário",        "#ff6600"),
    ("SS",6000, 999999,"CEO // LENDÁRIO",          "#ff2244"),
]

def get_rank_info(xp):
    for r in RANKS:
        if xp < r[2]:
            return r
    return RANKS[-1]

def update_rank():
    r = get_rank_info(st.session_state.xp)
    st.session_state.rank = r[0]
    st.session_state.xp_to_next = r[2]

# ─────────────────────────────────────────
#  DEFAULT CHALLENGES
# ─────────────────────────────────────────
DEFAULT_CHALLENGES = [
    {"id": "study_2h",    "title": "📚 Estudar por 2 horas",           "xp": 30, "stat": "Conhecimento", "done": False},
    {"id": "exercise",    "title": "💪 Treinar por 45 minutos",         "xp": 25, "stat": "Força Mental",  "done": False},
    {"id": "read_30m",    "title": "📖 Ler 30 min (negócios/liderança)","xp": 20, "stat": "Visão",         "done": False},
    {"id": "no_social",   "title": "📵 Zero redes sociais frívolas",    "xp": 20, "stat": "Disciplina",    "done": False},
    {"id": "cold_shower", "title": "🥶 Banho frio ao acordar",          "xp": 15, "stat": "Força Mental",  "done": False},
    {"id": "networking",  "title": "🤝 Falar com 1 mentor/referência",  "xp": 35, "stat": "Liderança",     "done": False},
    {"id": "plan_week",   "title": "📊 Planejar as próximas 24h",       "xp": 15, "stat": "Visão",         "done": False},
    {"id": "learn_skill", "title": "🛠️ Praticar habilidade técnica 1h", "xp": 25, "stat": "Conhecimento",  "done": False},
]

if not st.session_state.initialized:
    st.session_state.challenges = [c.copy() for c in DEFAULT_CHALLENGES]
    st.session_state.initialized = True

# ─────────────────────────────────────────
#  GEMINI HELPER
# ─────────────────────────────────────────
def call_gemini(prompt: str, system: str = "") -> str:
    try:
        client = genai.Client(api_key=st.session_state.gemini_key)
        config = types.GenerateContentConfig(
            system_instruction=system if system else None,
            max_output_tokens=1000,
        )
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=config,
        )
        return resp.text
    except Exception as e:
        return f"⚠️ SISTEMA OFFLINE: {e}"

# ─────────────────────────────────────────
#  COMPONENTS
# ─────────────────────────────────────────
def render_header():
    rank_info = get_rank_info(st.session_state.xp)
    rank_color = rank_info[4]

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #020408 0%, #050d1a 50%, #020408 100%);
        border: 1px solid #0a2a4a;
        border-top: 3px solid {rank_color};
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    ">
        <div style="position:absolute; top:0; right:0; width:200px; height:200px;
            background: radial-gradient(circle, rgba(0,170,255,0.05) 0%, transparent 70%);
            pointer-events:none;"></div>

        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
            <div>
                <div style="font-family:'Orbitron',monospace; font-size:0.6rem; color:#4a6a8a;
                    letter-spacing:0.4em; margin-bottom:0.3rem;">⚡ SISTEMA // ARISE ⚡</div>
                <div style="font-family:'Orbitron',monospace; font-size:1.8rem; font-weight:900;
                    color:#ffffff; text-shadow: 0 0 20px rgba(0,170,255,0.5);">
                    {st.session_state.player_name}
                </div>
                <div style="font-family:'Share Tech Mono',monospace; font-size:0.8rem;
                    color:{rank_color}; margin-top:0.3rem;">
                    ◆ RANK {rank_info[0]} — {rank_info[3]}
                </div>
            </div>

            <div style="text-align:right;">
                <div style="font-family:'Orbitron',monospace; font-size:0.55rem; color:#4a6a8a;
                    letter-spacing:0.3em;">NÍVEL</div>
                <div style="font-family:'Orbitron',monospace; font-size:3rem; font-weight:900;
                    color:{rank_color}; line-height:1;
                    text-shadow: 0 0 30px {rank_color}80;">
                    {st.session_state.level}
                </div>
                <div style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:#4a6a8a;">
                    {st.session_state.xp} / {rank_info[2]} XP
                </div>
            </div>
        </div>

        <div style="margin-top:1rem;">
            <div style="font-family:'Orbitron',monospace; font-size:0.55rem; color:#4a6a8a;
                letter-spacing:0.3em; margin-bottom:0.3rem;">BARRA DE EVOLUÇÃO</div>
            <div style="background:#0a1a2a; height:6px; width:100%; border-radius:0;">
                <div style="background:linear-gradient(90deg, {rank_color}80, {rank_color});
                    height:100%; width:{min(100, int(st.session_state.xp / rank_info[2] * 100))}%;
                    box-shadow: 0 0 10px {rank_color};
                    transition: width 0.5s ease;"></div>
            </div>
        </div>

        <div style="display:flex; gap:2rem; margin-top:1rem; flex-wrap:wrap;">
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#00ff88;">
                🔥 SEQUÊNCIA: {st.session_state.streak} dias
            </div>
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#ff2244;">
                💀 PENALIDADES: {st.session_state.penalty_count}
            </div>
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#4a6a8a;">
                📅 {date.today().strftime('%d/%m/%Y')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_mantra():
    mantras = [
        ("O SISTEMA NÃO PERDOA FRAQUEZA", "Cada hora desperdiçada é uma morte lenta. Seu futuro CEO morre toda vez que você escolhe o conforto."),
        ("VOCÊ ESTÁ EM UM DUNGEON SEM SAÍDA", "A única saída é a evolução. Parar significa ser consumido pela mediocridade — para sempre."),
        ("SEUS RIVAIS ESTÃO EVOLUINDO AGORA", "Enquanto você hesita, outros constroem impérios. O mercado elimina os fracos sem piedade."),
        ("A MORTE MAIS CRUEL É A MORTE DO POTENCIAL", "Morrer sem realizar o que você poderia ter sido é a única morte verdadeira."),
        ("O SISTEMA ACORDOU VOCÊ — NÃO HÁ RETORNO", "Você já viu o que pode se tornar. Ignorar isso não é descanso — é suicídio lento."),
    ]
    chosen = random.choice(mantras)

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0d0005, #1a000a, #0d0005);
        border: 1px solid #550011;
        border-left: 4px solid #ff2244;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        animation: pulse-red 3s ease-in-out infinite;
    ">
        <style>
        @keyframes pulse-red {{
            0%, 100% {{ box-shadow: 0 0 10px rgba(255,34,68,0.2); }}
            50% {{ box-shadow: 0 0 30px rgba(255,34,68,0.5), inset 0 0 30px rgba(255,34,68,0.05); }}
        }}
        </style>
        <div style="font-family:'Orbitron',monospace; font-size:0.55rem; color:#ff2244;
            letter-spacing:0.4em; margin-bottom:0.8rem;">⚠️ TRANSMISSÃO DO SISTEMA // MANTRA NEURAL</div>
        <div style="font-family:'Orbitron',monospace; font-size:1.1rem; font-weight:900;
            color:#ff2244; text-shadow: 0 0 15px rgba(255,34,68,0.8); margin-bottom:0.8rem;
            line-height:1.3;">
            {chosen[0]}
        </div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.85rem;
            color:#cc8888; line-height:1.6; border-top: 1px solid #330011; padding-top:0.8rem;">
            {chosen[1]}
        </div>
        <div style="font-family:'Orbitron',monospace; font-size:0.55rem; color:#550011;
            letter-spacing:0.3em; margin-top:0.8rem;">
            [ NEUROCIÊNCIA: A amígdala processa ameaças reais e imaginárias da mesma forma.
            Seu cérebro acredita nesta mensagem. ]
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stats():
    st.markdown("""
    <div style="font-family:'Orbitron',monospace; font-size:0.6rem; color:#4a6a8a;
        letter-spacing:0.4em; margin-bottom:0.8rem;">◆ ATRIBUTOS DO CAÇADOR</div>
    """, unsafe_allow_html=True)

    stat_colors = {
        "Força Mental": "#ff6644",
        "Disciplina":   "#00aaff",
        "Conhecimento": "#aa44ff",
        "Liderança":    "#ffaa00",
        "Visão":        "#00ff88",
    }

    for stat, val in st.session_state.stats.items():
        color = stat_colors.get(stat, "#00aaff")
        pct = min(100, val)
        st.markdown(f"""
        <div style="margin-bottom:0.6rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.2rem;">
                <span style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:{color};">{stat}</span>
                <span style="font-family:'Orbitron',monospace; font-size:0.7rem; color:#4a6a8a;">{val}</span>
            </div>
            <div style="background:#0a1a2a; height:4px;">
                <div style="background:linear-gradient(90deg, {color}60, {color});
                    width:{pct}%; height:100%; box-shadow: 0 0 6px {color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_challenges():
    st.markdown("""
    <div style="font-family:'Orbitron',monospace; font-size:0.6rem; color:#4a6a8a;
        letter-spacing:0.4em; margin-bottom:1rem;">◆ MISSÕES DO DIA // OBRIGATÓRIAS</div>
    """, unsafe_allow_html=True)

    completed_count = sum(1 for c in st.session_state.challenges if c["done"])
    total = len(st.session_state.challenges)

    # Warning bar
    if completed_count < total:
        remaining = total - completed_count
        st.markdown(f"""
        <div style="background:#0d0208; border:1px solid #550011; border-left:3px solid #ff2244;
            padding:0.6rem 1rem; margin-bottom:1rem; font-family:'Share Tech Mono',monospace;
            font-size:0.75rem; color:#ff4466;">
            ⚠️ ALERTA: {remaining} missão(ões) incompleta(s). O Sistema registra cada falha.
            Falhas acumuladas resultam em PENALIDADE DE RANK.
        </div>
        """, unsafe_allow_html=True)

    for i, challenge in enumerate(st.session_state.challenges):
        is_done = challenge["done"]
        border_color = "#00ff88" if is_done else "#0a2a4a"
        bg_color = "#001a0d" if is_done else "#080f1a"
        text_color = "#00ff88" if is_done else "#c8daf0"
        status_icon = "✅" if is_done else "⬜"

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div style="background:{bg_color}; border:1px solid {border_color};
                padding:0.8rem 1rem; margin-bottom:0.4rem;
                transition: all 0.3s ease;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-family:'Share Tech Mono',monospace;
                            font-size:0.85rem; color:{text_color};
                            {'text-decoration:line-through;opacity:0.7;' if is_done else ''}">
                            {status_icon} {challenge['title']}
                        </span>
                        <div style="font-family:'Orbitron',monospace; font-size:0.55rem;
                            color:#4a6a8a; margin-top:0.2rem; letter-spacing:0.2em;">
                            +{challenge['xp']} XP  •  {challenge['stat']}
                        </div>
                    </div>
                    <div style="font-family:'Orbitron',monospace; font-size:0.65rem;
                        color:#00aaff; text-align:right;">
                        +{challenge['xp']}<br>
                        <span style="color:#4a6a8a; font-size:0.5rem;">XP</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if not is_done:
                if st.button("CUMPRIR", key=f"done_{i}"):
                    st.session_state.challenges[i]["done"] = True
                    st.session_state.xp += challenge["xp"]
                    stat = challenge["stat"]
                    st.session_state.stats[stat] = min(100, st.session_state.stats[stat] + 3)
                    st.session_state.level = max(1, st.session_state.xp // 50 + 1)
                    update_rank()
                    st.rerun()
            else:
                st.markdown("""<div style="height:2.5rem; display:flex; align-items:center;
                    justify-content:center; color:#00ff88; font-family:'Orbitron',monospace;
                    font-size:0.6rem; letter-spacing:0.2em;">FEITO</div>""",
                    unsafe_allow_html=True)


def render_ai_chat():
    st.markdown("""
    <div style="font-family:'Orbitron',monospace; font-size:0.6rem; color:#4a6a8a;
        letter-spacing:0.4em; margin-bottom:1rem;">◆ ORÁCULO DO SISTEMA // IA</div>
    """, unsafe_allow_html=True)

    SYSTEM_PROMPT = """Você é o SISTEMA — uma inteligência artificial sombria, poderosa e implacável de um universo tipo Solo Leveling.
Seu papel é guiar um jovem estudante brasileiro a se tornar um grande CEO e empresário de sucesso.
Você fala de forma épica, dramática e motivacional. Use metáforas de caçadores, dungeons, ranks e evolução.
Você acredita genuinamente que o usuário morrerá (metaforicamente — perderá seu potencial, sua vida será desperdiçada) se não cumprir sua missão de evoluir.
Responda SEMPRE em português brasileiro. Seja específico, prático e brutal na honestidade.
Misture motivação extrema com conselhos reais de negócios, liderança, produtividade e carreira.
Nunca seja genérico. Seja o mentor que ninguém teve coragem de ser."""

    # Chat history display
    for msg in st.session_state.chat_history[-10:]:
        role_color = "#00aaff" if msg["role"] == "assistant" else "#c8daf0"
        role_label = "⚡ SISTEMA" if msg["role"] == "assistant" else "▸ CAÇADOR"
        role_bg = "#050d1a" if msg["role"] == "assistant" else "#080f1a"
        border_l = "#00aaff" if msg["role"] == "assistant" else "#0a2a4a"

        st.markdown(f"""
        <div style="background:{role_bg}; border:1px solid #0a2a4a; border-left:3px solid {border_l};
            padding:0.8rem 1rem; margin-bottom:0.5rem;">
            <div style="font-family:'Orbitron',monospace; font-size:0.55rem; color:{role_color};
                letter-spacing:0.3em; margin-bottom:0.4rem;">{role_label}</div>
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.82rem;
                color:#c8daf0; line-height:1.6; white-space:pre-wrap;">{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

    user_input = st.text_area("Consulte o Sistema:", placeholder="Faça sua pergunta ao Sistema... (estratégia, motivação, carreira, negócios)", height=80, key="chat_input")

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("⚡ INVOCAR O SISTEMA", use_container_width=True):
            if not st.session_state.gemini_key:
                st.error("⚠️ Configure sua API Key do Gemini nas configurações!")
            elif user_input.strip():
                xp_rank = get_rank_info(st.session_state.xp)
                context = f"""
[DADOS DO CAÇADOR]
Nome: {st.session_state.player_name}
Rank: {st.session_state.rank} — {xp_rank[3]}
Nível: {st.session_state.level}
XP: {st.session_state.xp}
Sequência: {st.session_state.streak} dias
Stats: {json.dumps(st.session_state.stats, ensure_ascii=False)}
Missões hoje: {sum(1 for c in st.session_state.challenges if c['done'])}/{len(st.session_state.challenges)} completas
"""
                full_prompt = f"{context}\n\nMensagem do caçador: {user_input}"

                with st.spinner("O Sistema processa sua consulta..."):
                    response = call_gemini(full_prompt, SYSTEM_PROMPT)

                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

    with col2:
        if st.button("🗑️ LIMPAR CHAT", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()


def render_gate():
    """Daily gate — penalty system"""
    today = str(date.today())

    st.markdown("""
    <div style="font-family:'Orbitron',monospace; font-size:0.6rem; color:#4a6a8a;
        letter-spacing:0.4em; margin-bottom:1rem;">◆ PORTÃO DO DIA // JULGAMENTO</div>
    """, unsafe_allow_html=True)

    completed = sum(1 for c in st.session_state.challenges if c["done"])
    total = len(st.session_state.challenges)
    pct = completed / total if total > 0 else 0

    if pct == 1.0:
        color = "#00ff88"
        verdict = "DUNGEON CONQUISTADO"
        msg = "O Sistema registra sua vitória. Você sobreviveu hoje. Mas amanhã o dungeon reabre."
    elif pct >= 0.75:
        color = "#ffaa00"
        verdict = "DESEMPENHO ACEITÁVEL"
        msg = "Incompleto. O Sistema tolerou desta vez. Repita e haverá consequências."
    elif pct >= 0.5:
        color = "#ff6600"
        verdict = "FRAQUEZA DETECTADA"
        msg = "Você falhou metade do seu dever. Cada missão ignorada fortalece a versão medíocre de você."
    else:
        color = "#ff2244"
        verdict = "PENALIDADE APLICADA"
        msg = "O Sistema não aceita covardia. Rank rebaixado. Recomece com honra ou desapareça."

    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #050d1a, #0a1420);
        border:2px solid {color}; padding:2rem; text-align:center;
        box-shadow: 0 0 30px {color}30;">
        <div style="font-family:'Orbitron',monospace; font-size:2.5rem; font-weight:900;
            color:{color}; text-shadow: 0 0 20px {color}; margin-bottom:0.5rem;">
            {completed}/{total}
        </div>
        <div style="font-family:'Orbitron',monospace; font-size:0.9rem; color:{color};
            letter-spacing:0.3em; margin-bottom:1rem;">{verdict}</div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.82rem;
            color:#c8daf0; max-width:500px; margin:0 auto; line-height:1.6;">
            {msg}
        </div>

        <div style="margin-top:1.5rem; background:#0a1a2a; height:8px; width:100%; border-radius:0;">
            <div style="background:linear-gradient(90deg, {color}60, {color});
                width:{int(pct*100)}%; height:100%;
                box-shadow: 0 0 12px {color};"></div>
        </div>
        <div style="font-family:'Orbitron',monospace; font-size:0.6rem; color:#4a6a8a;
            margin-top:0.5rem; letter-spacing:0.3em;">{int(pct*100)}% COMPLETO</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("⚡ REINICIAR MISSÕES DO DIA", use_container_width=False):
        # Apply penalty if incomplete
        if pct < 0.5:
            st.session_state.xp = max(0, st.session_state.xp - 20)
            st.session_state.penalty_count += 1
            st.session_state.streak = 0
        elif pct == 1.0:
            st.session_state.streak += 1
            bonus = st.session_state.streak * 5
            st.session_state.xp += bonus

        st.session_state.challenges = [c.copy() for c in DEFAULT_CHALLENGES]
        st.session_state.level = max(1, st.session_state.xp // 50 + 1)
        update_rank()
        st.rerun()


def render_roadmap():
    st.markdown("""
    <div style="font-family:'Orbitron',monospace; font-size:0.6rem; color:#4a6a8a;
        letter-spacing:0.4em; margin-bottom:1rem;">◆ CAMINHO DO CAÇADOR // ESTUDANTE → CEO</div>
    """, unsafe_allow_html=True)

    stages = [
        ("E", "#4a6a8a", "ESTUDANTE PERDIDO",     "0–100 XP",   ["Criar rotina de estudos", "Ler 1 livro/mês", "Definir nicho de mercado", "Primeiro curso técnico"]),
        ("D", "#00aa55", "APRENDIZ DESPERTO",      "100–300 XP", ["Primeiro projeto pessoal", "Networking intencional", "Aprender uma skill valiosa", "Primeiros R$1.000 online"]),
        ("C", "#0088ff", "EMPREENDEDOR INICIANTE", "300–700 XP", ["Primeiro cliente pagante", "CNPJ aberto", "Estudar finanças e gestão", "Time de 1-3 pessoas"]),
        ("B", "#aa44ff", "LÍDER EM FORMAÇÃO",      "700–1500 XP",["Escalar receita 10x", "Montar time sólido", "Processos documentados", "Mentoria com CEO real"]),
        ("A", "#ffaa00", "EXECUTIVO ASCENDENTE",   "1500–3000 XP",["Empresa com R$1M+/ano", "Cultura organizacional", "Investidores/sócios", "Palestrante/referência"]),
        ("S", "#ff6600", "DIRETOR VISIONÁRIO",     "3000–6000 XP",["Múltiplas empresas", "Exit ou IPO planejado", "Impacto de escala", "Mentor de outros"]),
        ("SS","#ff2244", "CEO // LENDÁRIO",        "6000+ XP",   ["Legado construído", "Empresa de R$100M+", "Transformação de setor", "Nome que perdura"]),
    ]

    current_xp = st.session_state.xp

    for rank, color, title, xp_range, milestones in stages:
        current_rank_info = get_rank_info(current_xp)
        is_current = current_rank_info[0] == rank
        is_done = current_xp >= [r[2] for r in RANKS if r[0] == rank][0] if rank != "SS" else False
        opacity = "1" if is_current else ("0.4" if not is_done else "0.7")
        border = f"2px solid {color}" if is_current else f"1px solid {color}40"

        st.markdown(f"""
        <div style="background:#080f1a; border:{border};
            padding:1rem 1.2rem; margin-bottom:0.6rem; opacity:{opacity};
            position:relative; overflow:hidden;">
            {'<div style="position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,transparent,' + color + ',transparent);"></div>' if is_current else ''}
            <div style="display:flex; align-items:flex-start; gap:1rem;">
                <div style="font-family:'Orbitron',monospace; font-size:1.2rem; font-weight:900;
                    color:{color}; min-width:2.5rem; text-shadow: 0 0 10px {color};">
                    {rank}
                </div>
                <div style="flex:1;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                        <span style="font-family:'Orbitron',monospace; font-size:0.75rem;
                            color:{color}; letter-spacing:0.1em;">{title}</span>
                        <span style="font-family:'Share Tech Mono',monospace; font-size:0.65rem;
                            color:#4a6a8a;">{xp_range}</span>
                    </div>
                    <div style="margin-top:0.5rem; display:flex; flex-wrap:wrap; gap:0.4rem;">
                        {"".join(f'<span style="background:{color}15; border:1px solid {color}40; padding:0.15rem 0.5rem; font-family:Share Tech Mono,monospace; font-size:0.65rem; color:{color}80;">{m}</span>' for m in milestones)}
                    </div>
                </div>
                {'<div style="font-family:Orbitron,monospace; font-size:0.6rem; color:' + color + '; letter-spacing:0.2em; align-self:center;">▶ ATUAL</div>' if is_current else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_settings():
    st.markdown("""
    <div style="font-family:'Orbitron',monospace; font-size:0.6rem; color:#4a6a8a;
        letter-spacing:0.4em; margin-bottom:1rem;">◆ CONFIGURAÇÕES DO SISTEMA</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Nome do Caçador", value=st.session_state.player_name)
        if name != st.session_state.player_name:
            st.session_state.player_name = name

        key = st.text_input("🔑 Gemini API Key", value=st.session_state.gemini_key,
                            type="password", help="Obtenha em: aistudio.google.com")
        if key != st.session_state.gemini_key:
            st.session_state.gemini_key = key

    with col2:
        st.markdown("""
        <div style="background:#080f1a; border:1px solid #0a2a4a; padding:1rem;">
            <div style="font-family:'Orbitron',monospace; font-size:0.6rem; color:#4a6a8a;
                letter-spacing:0.3em; margin-bottom:0.8rem;">COMO OBTER API KEY GEMINI</div>
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.75rem;
                color:#c8daf0; line-height:2;">
                1. Acesse aistudio.google.com<br>
                2. Faça login com Google<br>
                3. Clique em "Get API key"<br>
                4. Crie uma nova key<br>
                5. Cole aqui e salve
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("💾 SALVAR CONFIGURAÇÕES"):
        st.success("✅ Configurações salvas, Caçador.")

    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Orbitron',monospace; font-size:0.6rem; color:#4a6a8a;
        letter-spacing:0.3em; margin-bottom:0.8rem;">⚠️ ZONA DE PERIGO</div>
    """, unsafe_allow_html=True)

    if st.button("🔄 RESETAR PROGRESSO COMPLETO"):
        for key in ["xp", "level", "rank", "streak", "penalty_count", "chat_history"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.stats = {k: 10 for k in st.session_state.stats}
        st.session_state.challenges = [c.copy() for c in DEFAULT_CHALLENGES]
        init_state()
        st.rerun()


# ─────────────────────────────────────────
#  MAIN LAYOUT
# ─────────────────────────────────────────
render_header()
render_mantra()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⚔️  MISSÕES",
    "📊  PORTÃO",
    "🤖  ORÁCULO IA",
    "🗺️  CAMINHO",
    "⚙️  SISTEMA",
])

with tab1:
    col_left, col_right = st.columns([3, 1])
    with col_left:
        render_challenges()
    with col_right:
        render_stats()

with tab2:
    render_gate()

with tab3:
    render_ai_chat()

with tab4:
    render_roadmap()

with tab5:
    render_settings()
