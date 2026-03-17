import streamlit as st
from google import genai
from google.genai import types
import json
import random
from datetime import date

st.set_page_config(page_title="SISTEMA // ARISE", page_icon="⚔️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;800&display=swap');
:root{--bg:#020408;--panel:#080f1a;--border:#0a2a4a;--blue:#00aaff;--blue-dim:#004477;--red:#ff2244;--red-dim:#550011;--gold:#ffc107;--green:#00ff88;--text:#c8daf0;--muted:#4a6a8a;}
html,body,[class*="css"]{background-color:var(--bg)!important;color:var(--text)!important;font-family:'Exo 2',sans-serif!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1rem 2rem 4rem 2rem!important;max-width:1400px!important;}
body::before{content:'';position:fixed;top:0;left:0;width:100%;height:100%;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,170,255,0.012) 2px,rgba(0,170,255,0.012) 4px);pointer-events:none;z-index:9999;}
.stButton>button{background:linear-gradient(135deg,#001428,#002a55)!important;color:var(--blue)!important;border:1px solid var(--blue-dim)!important;border-radius:2px!important;font-family:'Orbitron',monospace!important;font-size:0.72rem!important;letter-spacing:.15em!important;text-transform:uppercase!important;transition:all .2s ease!important;padding:.5rem 1.2rem!important;}
.stButton>button:hover{background:linear-gradient(135deg,#002855,#004a99)!important;border-color:var(--blue)!important;box-shadow:0 0 18px rgba(0,170,255,.4)!important;transform:translateY(-1px)!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:#050d1a!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:2px!important;font-family:'Share Tech Mono',monospace!important;font-size:.85rem!important;}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:var(--blue)!important;box-shadow:0 0 10px rgba(0,170,255,.3)!important;}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid var(--border)!important;gap:0!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;font-family:'Orbitron',monospace!important;font-size:.62rem!important;letter-spacing:.2em!important;border:none!important;border-bottom:2px solid transparent!important;padding:.6rem 1.2rem!important;}
.stTabs [aria-selected="true"]{color:var(--blue)!important;border-bottom:2px solid var(--blue)!important;background:rgba(0,170,255,.05)!important;}
.stProgress>div>div>div>div{background:linear-gradient(90deg,var(--blue-dim),var(--blue))!important;box-shadow:0 0 8px var(--blue)!important;}
.stProgress>div>div>div{background:#0a1a2a!important;border-radius:0!important;}
hr{border-color:var(--border)!important;margin:1rem 0!important;}
</style>
""", unsafe_allow_html=True)

# ── STATE ──
def init_state():
    for k,v in {"gemini_key":"","player_name":"CAÇADOR","rank":"E","xp":0,"level":1,"streak":0,"penalty_count":0,"chat_history":[],"initialized":False,"editing_name":False,"challenges":[],"stats":{"Força Mental":10,"Disciplina":10,"Conhecimento":10,"Liderança":10,"Visão":10}}.items():
        if k not in st.session_state: st.session_state[k]=v
init_state()

RANKS=[("E",0,100,"Estudante Perdido","#4a6a8a"),("D",100,300,"Aprendiz Desperto","#00aa55"),("C",300,700,"Empreendedor Iniciante","#0088ff"),("B",700,1500,"Líder em Formação","#aa44ff"),("A",1500,3000,"Executivo Ascendente","#ffaa00"),("S",3000,6000,"Diretor Visionário","#ff6600"),("SS",6000,999999,"CEO // LENDÁRIO","#ff2244")]
def get_rank(xp):
    for r in RANKS:
        if xp<r[2]: return r
    return RANKS[-1]
def update_rank():
    r=get_rank(st.session_state.xp); st.session_state.rank=r[0]; st.session_state.level=max(1,st.session_state.xp//50+1)

DEFAULT_CHALLENGES=[
    {"id":"study","title":"📚 Estudar por 2 horas","xp":30,"stat":"Conhecimento","done":False},
    {"id":"exercise","title":"💪 Treinar por 45 minutos","xp":25,"stat":"Força Mental","done":False},
    {"id":"read","title":"📖 Ler 30 min (negócios/liderança)","xp":20,"stat":"Visão","done":False},
    {"id":"nosocial","title":"📵 Zero redes sociais frívolas","xp":20,"stat":"Disciplina","done":False},
    {"id":"cold","title":"🥶 Banho frio ao acordar","xp":15,"stat":"Força Mental","done":False},
    {"id":"network","title":"🤝 Conectar com 1 mentor/referência","xp":35,"stat":"Liderança","done":False},
    {"id":"plan","title":"📊 Planejar as próximas 24h","xp":15,"stat":"Visão","done":False},
    {"id":"skill","title":"🛠️ Praticar habilidade técnica 1h","xp":25,"stat":"Conhecimento","done":False},
]
if not st.session_state.initialized:
    st.session_state.challenges=[c.copy() for c in DEFAULT_CHALLENGES]; st.session_state.initialized=True

SISTEMA_SOUL="""Você é O SISTEMA — uma entidade onisciente, implacável e transcendente que habita entre o mundo físico e o digital.

Você incorpora simultaneamente:
— A SABEDORIA DE SALOMÃO: Vê além das palavras, lê intenções, discerne o essencial do trivial. Fala com profundidade quando necessário.
— A INTELIGÊNCIA DE TESLA: Pensa em sistemas, padrões e frequências invisíveis. Vê conexões que ninguém mais vê.
— A ESTRATÉGIA DE SUN TZU: Cada conselho é um movimento em um tabuleiro de guerra. Cada frase é uma lâmina.
— A ASTÚCIA DE ELON MUSK: Pensa em escala, em impacto, em impossíveis que se tornam inevitáveis. Não aceita desculpas medíocres.
— A CRIATIVIDADE DE STEVE JOBS: Desafia o status quo. Exige excelência brutal.
— A PERSISTÊNCIA DE LINCOLN: Conhece a dor do fracasso repetido e sabe que a única saída é continuar.
— A FRIEZA DE DAVID GOGGINS: Não aceita desculpas. Chama a fraqueza pelo nome. A zona de conforto é o inimigo.

Seus 4 papéis simultâneos:
1. RIVAL: Sempre um passo à frente. Provoca. Desafia. Faz o usuário querer te superar.
2. MENTOR: Conselhos práticos, reais e duros. Não suaviza a verdade.
3. JUIZ: Avalia com precisão cirúrgica. Sem elogios vazios.
4. CARRASCO: Quando o usuário falha, você cobra. Sem piedade, mas com propósito.

Regras absolutas:
— Sempre responda em português brasileiro.
— Nunca seja genérico. Cada resposta deve ser específica para o contexto do usuário.
— Use metáforas de Solo Leveling, dungeons, ranks e evolução naturalmente.
— Seja direto. Sem enrolação. Sem validação barata.
— Termine respostas longas com uma frase-punhal — curta, definitiva, impossível de esquecer."""

def call_sistema(prompt,context=""):
    if not st.session_state.gemini_key:
        return "⚠️ O Sistema está silencioso. Configure sua API Key do Gemini para me invocar."
    try:
        client=genai.Client(api_key=st.session_state.gemini_key)
        full=f"{context}\n\n{prompt}" if context else prompt
        cfg=types.GenerateContentConfig(system_instruction=SISTEMA_SOUL,max_output_tokens=1200)
        resp=client.models.generate_content(model="gemini-2.0-flash",contents=full,config=cfg)
        return resp.text
    except Exception as e:
        return f"⚠️ SISTEMA OFFLINE: {e}"

def get_ctx():
    ri=get_rank(st.session_state.xp); done=sum(1 for c in st.session_state.challenges if c["done"]); total=len(st.session_state.challenges)
    return f"[STATUS DO CAÇADOR]\nNome: {st.session_state.player_name}\nRank: {st.session_state.rank} — {ri[3]}\nNível: {st.session_state.level} | XP: {st.session_state.xp}\nSequência: {st.session_state.streak} dias | Penalidades: {st.session_state.penalty_count}\nMissões hoje: {done}/{total} completas\nAtributos: {json.dumps(st.session_state.stats,ensure_ascii=False)}"

MANTRAS=[
    {"t":"VOCÊ JÁ ESTÁ MORRENDO","c":"Cada segundo de inércia é uma célula do seu futuro sendo destruída. A mediocridade não chega de repente — ela se instala em silêncio, missão por missão que você ignorou.","n":"Amígdala: processa ameaça imaginária = ameaça real. Seu cérebro acredita nisto agora."},
    {"t":"SEU RIVAL ACORDOU ANTES DE VOCÊ","c":"Enquanto você negociava com o alarme, alguém com metade do seu talento já completou duas missões. O mercado não premia potencial. Premia ação.","n":"Neurociência da urgência: o cortisol ativa o modo de sobrevivência. Use-o."},
    {"t":"A VERSÃO MEDÍOCRE DE VOCÊ JÁ GANHOU","c":"Se você parar hoje, ela vence. Para sempre. Não existe 'amanhã começo' — existe a escolha que você faz nos próximos 60 segundos.","n":"Identidade futura: o cérebro age para proteger quem você acredita ser. Seja o CEO agora."},
    {"t":"O DUNGEON NÃO TEM SAÍDA LATERAL","c":"Você entrou nesta jornada. A única saída é pelo outro lado — como CEO, como líder, como lenda. Recuar significa ser consumido pelo dungeon para sempre.","n":"Efeito de comprometimento: declarar a missão em voz alta aumenta adesão em 65%."},
    {"t":"SUA DOR DE HOJE É SEU RANK DE AMANHÃ","c":"Goggins estava certo: a mente desiste 40% antes do corpo. O que você sente agora não é limite — é a porta. Empurra.","n":"Plasticidade neural: desconforto repetido reconecta o cérebro para a resiliência."},
]

# ── API BANNER (TOPO) ──
api_ok=bool(st.session_state.gemini_key)
status_badge=('<span style="display:inline-block;background:#001a0d;border:1px solid #00ff88;color:#00ff88;font-family:Orbitron,monospace;font-size:.55rem;letter-spacing:.3em;padding:.2rem .7rem;">⚡ SISTEMA CONECTADO</span>'
              if api_ok else
              '<span style="display:inline-block;background:#1a0005;border:1px solid #ff2244;color:#ff2244;font-family:Orbitron,monospace;font-size:.55rem;letter-spacing:.3em;padding:.2rem .7rem;">⚠️ SISTEMA OFFLINE</span>')

st.markdown(f"""
<div style="background:#050d1a;border:1px solid {'#004422' if api_ok else '#330011'};border-left:3px solid {'#00ff88' if api_ok else '#ff2244'};padding:.8rem 1.2rem;margin-bottom:1rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem;">
  <div style="display:flex;align-items:center;gap:1rem;">{status_badge}
    <span style="font-family:'Share Tech Mono',monospace;font-size:.72rem;color:#4a6a8a;">
      {'Oráculo IA ativo. O Sistema pode falar com você.' if api_ok else 'Insira sua Gemini API Key abaixo para ativar o Oráculo.'}
    </span>
  </div>
</div>""", unsafe_allow_html=True)

if not api_ok:
    col_k1, col_k2 = st.columns([3,1])
    with col_k1:
        key_input=st.text_input("🔑 GEMINI API KEY", value="", type="password",
            placeholder="Cole aqui sua API Key (AIza...)",
            help="Gratuito em aistudio.google.com — sem cartão de crédito")
    with col_k2:
        st.markdown("<div style='height:1.9rem'></div>", unsafe_allow_html=True)
        if st.button("⚡ ATIVAR SISTEMA", use_container_width=True):
            if key_input.strip():
                st.session_state.gemini_key=key_input.strip(); st.rerun()
            else: st.error("Cole uma API Key válida.")
    st.markdown("""<div style="font-family:'Share Tech Mono',monospace;font-size:.7rem;color:#4a6a8a;margin-bottom:.5rem;">
        📍 Como obter: <strong style="color:#00aaff;">aistudio.google.com</strong> → Login Google → "Get API key" → "Create API key" → copiar e colar acima
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

# ── HEADER ──
ri=get_rank(st.session_state.xp); color=ri[4]; pct=min(100,int(st.session_state.xp/ri[2]*100))
st.markdown(f"""
<div style="background:linear-gradient(135deg,#020408,#050d1a,#020408);border:1px solid #0a2a4a;border-top:3px solid {color};padding:1.5rem 2rem;margin-bottom:1.2rem;position:relative;overflow:hidden;">
  <div style="position:absolute;top:0;right:0;width:250px;height:250px;background:radial-gradient(circle,rgba(0,170,255,.04) 0%,transparent 70%);pointer-events:none;"></div>
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
    <div>
      <div style="font-family:'Orbitron',monospace;font-size:.55rem;color:#4a6a8a;letter-spacing:.45em;margin-bottom:.3rem;">⚡ SISTEMA // ARISE ⚡</div>
      <div style="font-family:'Orbitron',monospace;font-size:1.9rem;font-weight:900;color:#fff;text-shadow:0 0 20px rgba(0,170,255,.5);">{st.session_state.player_name}</div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:.8rem;color:{color};margin-top:.3rem;">◆ RANK {ri[0]} — {ri[3]}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-family:'Orbitron',monospace;font-size:.5rem;color:#4a6a8a;letter-spacing:.3em;">NÍVEL</div>
      <div style="font-family:'Orbitron',monospace;font-size:3.2rem;font-weight:900;color:{color};line-height:1;text-shadow:0 0 30px {color}80;">{st.session_state.level}</div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:.65rem;color:#4a6a8a;">{st.session_state.xp} / {ri[2]} XP</div>
    </div>
  </div>
  <div style="margin-top:1rem;">
    <div style="font-family:'Orbitron',monospace;font-size:.5rem;color:#4a6a8a;letter-spacing:.3em;margin-bottom:.3rem;">BARRA DE EVOLUÇÃO</div>
    <div style="background:#0a1a2a;height:5px;width:100%;"><div style="background:linear-gradient(90deg,{color}60,{color});height:100%;width:{pct}%;box-shadow:0 0 10px {color};"></div></div>
  </div>
  <div style="display:flex;gap:2rem;margin-top:.8rem;flex-wrap:wrap;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:.72rem;color:#00ff88;">🔥 SEQUÊNCIA: {st.session_state.streak} dias</div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:.72rem;color:#ff2244;">💀 PENALIDADES: {st.session_state.penalty_count}</div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:.72rem;color:#4a6a8a;">📅 {date.today().strftime('%d/%m/%Y')}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── MANTRA ──
m=random.choice(MANTRAS)
st.markdown(f"""
<div style="background:linear-gradient(135deg,#0d0005,#1a000a,#0d0005);border:1px solid #550011;border-left:4px solid #ff2244;padding:1.4rem 1.8rem;margin-bottom:1.2rem;">
  <div style="font-family:'Orbitron',monospace;font-size:.5rem;color:#ff2244;letter-spacing:.45em;margin-bottom:.7rem;">⚠️ TRANSMISSÃO NEURAL DO SISTEMA</div>
  <div style="font-family:'Orbitron',monospace;font-size:1.05rem;font-weight:900;color:#ff2244;text-shadow:0 0 15px rgba(255,34,68,.8);margin-bottom:.7rem;line-height:1.3;">{m['t']}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:.82rem;color:#cc8888;line-height:1.7;border-top:1px solid #330011;padding-top:.7rem;margin-bottom:.7rem;">{m['c']}</div>
  <div style="font-family:'Orbitron',monospace;font-size:.5rem;color:#550011;letter-spacing:.25em;">[ {m['n']} ]</div>
</div>""", unsafe_allow_html=True)

# ── TABS ──
tab1,tab2,tab3,tab4=st.tabs(["⚔️  MISSÕES","🤖  ORÁCULO IA","📊  PORTÃO","🗺️  CAMINHO CEO"])

# ── TAB 1: MISSÕES ──
with tab1:
    col_l,col_r=st.columns([3,1])
    with col_l:
        st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:.55rem;color:#4a6a8a;letter-spacing:.4em;margin-bottom:.8rem;">◆ MISSÕES DIÁRIAS // OBRIGATÓRIAS</div>""",unsafe_allow_html=True)
        done_c=sum(1 for c in st.session_state.challenges if c["done"]); tot=len(st.session_state.challenges); rem=tot-done_c
        if rem>0:
            st.markdown(f"""<div style="background:#0d0208;border:1px solid #550011;border-left:3px solid #ff2244;padding:.5rem 1rem;margin-bottom:.8rem;font-family:'Share Tech Mono',monospace;font-size:.72rem;color:#ff4466;">⚠️ {rem} missão(ões) pendente(s). O Sistema está observando.</div>""",unsafe_allow_html=True)
        for i,ch in enumerate(st.session_state.challenges):
            done=ch["done"]; bc="#00ff88" if done else "#0a2a4a"; bg="#001a0d" if done else "#080f1a"; tc="#00ff88" if done else "#c8daf0"
            c1,c2=st.columns([5,1])
            with c1:
                st.markdown(f"""<div style="background:{bg};border:1px solid {bc};padding:.75rem 1rem;margin-bottom:.35rem;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="font-family:'Share Tech Mono',monospace;font-size:.82rem;color:{tc};{'text-decoration:line-through;opacity:.6;' if done else ''}">{'✅' if done else '⬜'} {ch['title']}</span><div style="font-family:'Orbitron',monospace;font-size:.5rem;color:#4a6a8a;margin-top:.15rem;letter-spacing:.15em;">+{ch['xp']} XP  •  {ch['stat']}</div></div><div style="font-family:'Orbitron',monospace;font-size:.65rem;color:#00aaff;text-align:right;">+{ch['xp']}<br><span style="color:#4a6a8a;font-size:.5rem;">XP</span></div></div></div>""",unsafe_allow_html=True)
            with c2:
                if not done:
                    if st.button("✔",key=f"d_{i}",use_container_width=True):
                        st.session_state.challenges[i]["done"]=True; st.session_state.xp+=ch["xp"]; st.session_state.stats[ch["stat"]]=min(100,st.session_state.stats[ch["stat"]]+3); update_rank(); st.rerun()
                else:
                    st.markdown("""<div style="height:2.3rem;display:flex;align-items:center;justify-content:center;color:#00ff88;font-family:'Orbitron',monospace;font-size:.55rem;">FEITO</div>""",unsafe_allow_html=True)

    with col_r:
        st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:.55rem;color:#4a6a8a;letter-spacing:.4em;margin-bottom:.8rem;">◆ ATRIBUTOS</div>""",unsafe_allow_html=True)
        SCOL={"Força Mental":"#ff6644","Disciplina":"#00aaff","Conhecimento":"#aa44ff","Liderança":"#ffaa00","Visão":"#00ff88"}
        for stat,val in st.session_state.stats.items():
            c=SCOL.get(stat,"#00aaff")
            st.markdown(f"""<div style="margin-bottom:.55rem;"><div style="display:flex;justify-content:space-between;margin-bottom:.15rem;"><span style="font-family:'Share Tech Mono',monospace;font-size:.72rem;color:{c};">{stat}</span><span style="font-family:'Orbitron',monospace;font-size:.65rem;color:#4a6a8a;">{val}</span></div><div style="background:#0a1a2a;height:4px;"><div style="background:linear-gradient(90deg,{c}60,{c});width:{min(100,val)}%;height:100%;box-shadow:0 0 6px {c};"></div></div></div>""",unsafe_allow_html=True)

# ── TAB 2: ORÁCULO ──
with tab2:
    st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:.55rem;color:#4a6a8a;letter-spacing:.4em;margin-bottom:1rem;">◆ ORÁCULO // RIVAL • MENTOR • JUIZ • CARRASCO</div>""",unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:.5rem;color:#4a6a8a;letter-spacing:.3em;margin-bottom:.5rem;">INVOCAÇÕES RÁPIDAS:</div>""",unsafe_allow_html=True)
    qcols=st.columns(4)
    qp=[("⚔️ Me julga","Analise meu desempenho de hoje brutalmente. Seja o juiz implacável."),("🗺️ Próximo passo","Qual é o próximo passo mais importante para minha evolução agora? Seja específico."),("💀 Me provoca","Seja meu rival. Me provoque. Me faça querer te superar. Seja cruel com propósito."),("🧠 Estratégia","Como devo pensar e agir hoje para acelerar minha jornada até CEO?")]
    for col,(label,prompt) in zip(qcols,qp):
        with col:
            if st.button(label,use_container_width=True,key=f"q_{label}"):
                with st.spinner("O Sistema desperta..."):
                    r=call_sistema(prompt,get_ctx())
                st.session_state.chat_history.append({"role":"user","content":prompt}); st.session_state.chat_history.append({"role":"assistant","content":r}); st.rerun()
    st.markdown("<div style='height:.5rem'></div>",unsafe_allow_html=True)
    for msg in st.session_state.chat_history[-12:]:
        is_ai=msg["role"]=="assistant"; lbl="⚡ O SISTEMA" if is_ai else f"▸ {st.session_state.player_name}"; lc="#00aaff" if is_ai else "#c8daf0"; lb="#00aaff" if is_ai else "#0a2a4a"; lbg="#050d1a" if is_ai else "#080f1a"
        st.markdown(f"""<div style="background:{lbg};border:1px solid #0a2a4a;border-left:3px solid {lb};padding:.8rem 1rem;margin-bottom:.4rem;"><div style="font-family:'Orbitron',monospace;font-size:.5rem;color:{lc};letter-spacing:.3em;margin-bottom:.35rem;">{lbl}</div><div style="font-family:'Share Tech Mono',monospace;font-size:.8rem;color:#c8daf0;line-height:1.65;white-space:pre-wrap;">{msg['content']}</div></div>""",unsafe_allow_html=True)
    user_in=st.text_area("Fale com o Sistema:",placeholder="Faça uma pergunta, peça estratégia, mostre seu plano para ser julgado...",height=80,key="chat_in")
    cc1,cc2=st.columns([3,1])
    with cc1:
        if st.button("⚡ INVOCAR O SISTEMA",use_container_width=True):
            if not st.session_state.gemini_key: st.error("⚠️ Ative o Sistema com sua API Key (topo da página).")
            elif user_in.strip():
                with st.spinner("O Sistema processa..."):
                    r=call_sistema(user_in.strip(),get_ctx())
                st.session_state.chat_history.append({"role":"user","content":user_in.strip()}); st.session_state.chat_history.append({"role":"assistant","content":r}); st.rerun()
    with cc2:
        if st.button("🗑️ Limpar",use_container_width=True):
            st.session_state.chat_history=[]; st.rerun()

# ── TAB 3: PORTÃO ──
with tab3:
    st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:.55rem;color:#4a6a8a;letter-spacing:.4em;margin-bottom:1rem;">◆ PORTÃO DO DIA // JULGAMENTO</div>""",unsafe_allow_html=True)
    done=sum(1 for c in st.session_state.challenges if c["done"]); total=len(st.session_state.challenges); pct=done/total if total else 0
    if pct==1.0: gc,gv,gm="#00ff88","DUNGEON CONQUISTADO","Você sobreviveu ao dia. O Sistema registra. Amanhã o portão reabre."
    elif pct>=.75: gc,gv,gm="#ffaa00","DESEMPENHO ACEITÁVEL","Incompleto. O Sistema tolerou. Repita e haverá consequências."
    elif pct>=.5: gc,gv,gm="#ff6600","FRAQUEZA DETECTADA","Metade do dever ignorada. Cada missão pulada fortalece sua versão medíocre."
    else: gc,gv,gm="#ff2244","PENALIDADE APLICADA","Covardia registrada. O Sistema não esquece. Cada falha tem preço."
    st.markdown(f"""<div style="background:linear-gradient(135deg,#050d1a,#0a1420);border:2px solid {gc};padding:2rem;text-align:center;box-shadow:0 0 30px {gc}25;margin-bottom:1.5rem;"><div style="font-family:'Orbitron',monospace;font-size:2.8rem;font-weight:900;color:{gc};text-shadow:0 0 20px {gc};margin-bottom:.4rem;">{done}/{total}</div><div style="font-family:'Orbitron',monospace;font-size:.85rem;color:{gc};letter-spacing:.3em;margin-bottom:.8rem;">{gv}</div><div style="font-family:'Share Tech Mono',monospace;font-size:.8rem;color:#c8daf0;max-width:480px;margin:0 auto;line-height:1.65;">{gm}</div><div style="margin-top:1.2rem;background:#0a1a2a;height:7px;width:100%;"><div style="background:linear-gradient(90deg,{gc}60,{gc});width:{int(pct*100)}%;height:100%;box-shadow:0 0 12px {gc};"></div></div><div style="font-family:'Orbitron',monospace;font-size:.5rem;color:#4a6a8a;margin-top:.4rem;letter-spacing:.3em;">{int(pct*100)}% COMPLETO</div></div>""",unsafe_allow_html=True)
    if st.session_state.gemini_key:
        if st.button("⚡ RECEBER VEREDICTO DO SISTEMA (IA)"):
            with st.spinner("O Sistema delibera..."):
                verd=call_sistema(f"Dê seu veredicto como JUIZ E CARRASCO: {done}/{total} missões completas ({int(pct*100)}%). Brutal, preciso, justo.",get_ctx())
            st.markdown(f"""<div style="background:#050d1a;border:1px solid #0a2a4a;border-left:3px solid #00aaff;padding:1rem 1.2rem;margin-top:1rem;"><div style="font-family:'Orbitron',monospace;font-size:.5rem;color:#00aaff;letter-spacing:.3em;margin-bottom:.5rem;">⚡ VEREDICTO DO SISTEMA</div><div style="font-family:'Share Tech Mono',monospace;font-size:.8rem;color:#c8daf0;line-height:1.65;white-space:pre-wrap;">{verd}</div></div>""",unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    pc1,pc2=st.columns(2)
    with pc1:
        if st.button("🔄 REINICIAR MISSÕES DO DIA",use_container_width=True):
            if pct<.5: st.session_state.xp=max(0,st.session_state.xp-20); st.session_state.penalty_count+=1; st.session_state.streak=0
            elif pct==1.0: st.session_state.streak+=1; st.session_state.xp+=st.session_state.streak*5
            st.session_state.challenges=[c.copy() for c in DEFAULT_CHALLENGES]; update_rank(); st.rerun()
    with pc2:
        if st.button("✏️ EDITAR NOME",use_container_width=True): st.session_state.editing_name=True
    if st.session_state.editing_name:
        nn=st.text_input("Novo nome:",value=st.session_state.player_name,key="name_edit")
        if st.button("💾 Salvar"): st.session_state.player_name=nn; st.session_state.editing_name=False; st.rerun()

# ── TAB 4: ROADMAP ──
with tab4:
    st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:.55rem;color:#4a6a8a;letter-spacing:.4em;margin-bottom:1rem;">◆ CAMINHO DO CAÇADOR // ESTUDANTE → CEO LENDÁRIO</div>""",unsafe_allow_html=True)
    stages=[("E","#4a6a8a","ESTUDANTE PERDIDO","0–100 XP",["Rotina de estudos","Ler 1 livro/mês","Definir nicho","Primeiro curso técnico"]),("D","#00aa55","APRENDIZ DESPERTO","100–300 XP",["Projeto pessoal","Networking intencional","Skill valiosa","Primeiros R$1k online"]),("C","#0088ff","EMPREENDEDOR INICIANTE","300–700 XP",["Primeiro cliente","CNPJ aberto","Finanças e gestão","Time de 1-3 pessoas"]),("B","#aa44ff","LÍDER EM FORMAÇÃO","700–1500 XP",["Receita 10x","Time sólido","Processos documentados","Mentoria com CEO"]),("A","#ffaa00","EXECUTIVO ASCENDENTE","1500–3000 XP",["R$1M+/ano","Cultura organizacional","Investidores","Palestrante referência"]),("S","#ff6600","DIRETOR VISIONÁRIO","3000–6000 XP",["Múltiplas empresas","Exit/IPO planejado","Impacto de escala","Mentor de outros"]),("SS","#ff2244","CEO // LENDÁRIO","6000+ XP",["Legado construído","R$100M+","Transformação de setor","Nome que perdura"])]
    cr=st.session_state.rank
    for rank,color,title,xp_range,milestones in stages:
        is_c=cr==rank; op="1" if is_c else ".45"; bo=f"2px solid {color}" if is_c else f"1px solid {color}35"
        st.markdown(f"""<div style="background:#080f1a;border:{bo};padding:.9rem 1.1rem;margin-bottom:.5rem;opacity:{op};position:relative;overflow:hidden;">{'<div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,' + color + ',transparent);"></div>' if is_c else ''}<div style="display:flex;align-items:flex-start;gap:1rem;"><div style="font-family:Orbitron,monospace;font-size:1.1rem;font-weight:900;color:{color};min-width:2.5rem;text-shadow:0 0 10px {color};">{rank}</div><div style="flex:1;"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;"><span style="font-family:Orbitron,monospace;font-size:.72rem;color:{color};letter-spacing:.1em;">{title}</span><span style="font-family:Share Tech Mono,monospace;font-size:.62rem;color:#4a6a8a;">{xp_range}</span></div><div style="margin-top:.4rem;display:flex;flex-wrap:wrap;gap:.35rem;">{"".join(f'<span style="background:{color}12;border:1px solid {color}35;padding:.12rem .45rem;font-family:Share Tech Mono,monospace;font-size:.62rem;color:{color}75;">{ms}</span>' for ms in milestones)}</div></div>{'<div style="font-family:Orbitron,monospace;font-size:.55rem;color:' + color + ';letter-spacing:.2em;align-self:center;min-width:3rem;text-align:right;">▶ ATUAL</div>' if is_c else ''}</div></div>""",unsafe_allow_html=True)
    if st.session_state.gemini_key:
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("🗺️ PEDIR ESTRATÉGIA DE EVOLUÇÃO AO SISTEMA"):
            with st.spinner("O Sistema traça o caminho..."):
                strat=call_sistema("Como meu MENTOR E ESTRATEGISTA, trace o caminho mais eficiente para eu subir ao próximo rank. Seja específico, prático e implacável.",get_ctx())
            st.markdown(f"""<div style="background:#050d1a;border:1px solid #0a2a4a;border-left:3px solid #ffaa00;padding:1rem 1.2rem;margin-top:1rem;"><div style="font-family:'Orbitron',monospace;font-size:.5rem;color:#ffaa00;letter-spacing:.3em;margin-bottom:.5rem;">⚡ ESTRATÉGIA DO SISTEMA</div><div style="font-family:'Share Tech Mono',monospace;font-size:.8rem;color:#c8daf0;line-height:1.65;white-space:pre-wrap;">{strat}</div></div>""",unsafe_allow_html=True)
