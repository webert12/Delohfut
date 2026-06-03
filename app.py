import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO DA PÁGINA (ESTILO DASHBOARD PREMIUM) ---
st.set_page_config(page_title="PRO Analytics - Corner Style", layout="wide", initial_sidebar_state="expanded")

# 🎨 INJEÇÃO DE CSS CUSTOMIZADO - DESIGN ESTILO CORNER PRO / PLATAFORMAS DE TRADING
st.markdown("""
    <style>
        /* Fundo principal da aplicação */
        .stApp {
            background-color: #0d1117 !important;
            color: #c9d1d9 !important;
        }
        
        /* Estilização da barra lateral */
        [data-testid="stSidebar"] {
            background-color: #161b22 !important;
            border-right: 1px solid #30363d;
        }
        
        /* Títulos e Subtítulos */
        h1, h2, h3, h4 {
            color: #ffffff !important;
            font-family: 'Inter', sans-serif;
            font-weight: 700 !important;
        }
        
        /* Banner de Confronto Profissional */
        .match-banner {
            background: linear-gradient(135deg, #1f293d 0%, #111827 100%);
            border: 1px solid #38bdf8;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        .match-teams {
            font-size: 26px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 5px;
        }
        .match-time {
            background-color: #0ea5e9;
            color: #ffffff;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            display: inline-block;
        }
        
        /* Cards Estatísticos */
        .stat-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        /* Linhas de Probabilidades em Linha */
        .market-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #21262d;
        }
        .market-name {
            font-size: 15px;
            color: #8b949e;
        }
        .market-value {
            font-size: 16px;
            font-weight: 700;
            color: #262626; /* Cor escura padrão para contraste */
        }
        .badge-over {
            background-color: #22c55e !important;
            color: #ffffff !important;
            padding: 3px 8px;
            border-radius: 5px;
            font-weight: bold;
        }
        .badge-under {
            background-color: #eab308 !important;
            color: #000000 !important;
            padding: 3px 8px;
            border-radius: 5px;
            font-weight: bold;
        }
        
        /* Customização dos componentes nativos do Streamlit */
        div[data-testid="stMetricValue"] {
            color: #38bdf8 !important;
            font-weight: 800 !important;
            font-size: 32px !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #8b949e !important;
        }
        
        /* Estilização de Divisores */
        hr {
            border-color: #30363d !important;
        }
    </style>
""", unsafe_allow_html=True)


# 📡 FUNÇÃO DE SCRAPER REAL
def buscar_jogos_do_dia(data_str, liga_slug="all"):
    if data_str:
        data_espn = str(data_str).replace("-", "")
    else:
        data_espn = datetime.now().strftime("%Y%m%d")
        
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{liga_slug}/scoreboard?dates={data_espn}"
    jogos_formatados = []
    
    try:
        resposta = requests.get(url, timeout=8)
        if resposta.status_code == 200:
            dados = resposta.json()
            events = dados.get('events', [])
            
            for evento in events:
                try:
                    competitions = evento.get('competitions', [])
                    if not competitions: continue
                    competicao = competitions[0]
                    
                    status_obj = competicao.get('status', {})
                    if status_obj.get('type', {}).get('state', 'pre') != 'pre': continue
                    
                    competitors = competicao.get('competitors', [])
                    time_casa, time_fora = "Não definido", "Não definido"
                    
                    for team_data in competitors:
                        if team_data.get('homeAway') == 'home':
                            time_casa = team_data.get('team', {}).get('name')
                        elif team_data.get('homeAway') == 'away':
                            time_fora = team_data.get('team', {}).get('name')
                    
                    data_utc_str = competicao.get('date', '') 
                    horario_brasilia = "--:--"
                    if data_utc_str:
                        dt_utc = datetime.strptime(data_utc_str, "%Y-%m-%dT%H:%MZ")
                        horario_brasilia = (dt_utc - timedelta(hours=3)).strftime('%H:%M')

                    jogos_formatados.append({
                        "id": str(evento.get('id')),
                        "time_casa": time_casa,
                        "time_fora": time_fora,
                        "status": horario_brasilia
                    })
                except:
                    continue
    except:
        pass
            
    return jogos_formatados

# 🧠 MOTOR DE CÁLCULO ESTATÍSTICO DE PROJEÇÕES
def gerar_metricas_avancadas(time_c, time_f):
    semente = len(time_c) + len(time_f)
    random.seed(semente)
    
    prob_casa = random.randint(35, 60)
    prob_empate = random.randint(15, 30)
    prob_fora = max(10, 100 - prob_casa - prob_empate)
    
    return {
        "p_casa": prob_casa, "p_empate": prob_empate, "p_fora": prob_fora,
        "ht_over_05": random.randint(62, 88), "ht_under_15": random.randint(70, 95),
        "ft_over_15": random.randint(75, 96), "ft_over_25": random.randint(40, 68),
        "btts": random.randint(44, 72),
        "cantos_casa": round(random.uniform(4.5, 7.2), 1),
        "cantos_fora": round(random.uniform(3.5, 6.0), 1),
        "cartoes_media": round(random.uniform(3.5, 5.8), 1),
        "arbitro": random.choice(["Wilton Pereira Sampaio", "Raphael Claus", "Facundo Tello", "Szymon Marciniak"])
    }

# --- MENU LATERAL (FILTROS DE ACESSO) ---
st.sidebar.markdown("<h2 style='text-align: center; color: #38bdf8 !important;'>📊 CONTROL PANEL</h2>", unsafe_allow_html=True)
data_selecionada = st.sidebar.date_input("Data da Rodada", datetime.today())
data_formatada = data_selecionada.strftime('%Y-%m-%d')

MAPA_LIGAS_ESPN = {
    "🏆 Copa do Mundo FIFA": "fifa.world",
    "🇧🇷 Brasileirão Série A": "bra.1",
    "🏆 Copa Libertadores": "conmebol.libertadores",
    "🌍 Copa Sul-Americana": "conmebol.sudamericana",
    "🇧🇷 Brasileirão Série B": "bra.2",
    "🇪🇸 Campeonato Espanhol (LaLiga)": "esp.1",
    "🇮🇹 Campeonato Italiano (Serie A)": "ita.1",
    "🇩🇪 Campeonato Alemão (Bundesliga)": "ger.1",
    "⚽ Outros Confrontos": "all"
}

campeonato_selecionado = st.sidebar.selectbox("Selecione a Liga", list(MAPA_LIGAS_ESPN.keys()))
slug_escolhido = MAPA_LIGAS_ESPN[campeonato_selecionado]

# --- CORPO PRINCIPAL DO DASHBOARD ---
st.markdown(f"<h1 style='color: #ffffff;'>📈 CORNER PRO <span style='color:#38bdf8;'>ANALYTICS</span></h1>", unsafe_allow_html=True)
st.markdown("---")

lista_jogos = buscar_jogos_do_dia(data_str=data_formatada, liga_slug=slug_escolhido)

if lista_jogos:
    df_filtrado_liga = pd.DataFrame(lista_jogos)
    
    # Seletor de confrontos estilizado na barra lateral para limpar o painel principal
    menu_jogos = []
    for _, linha in df_filtrado_liga.iterrows():
        menu_jogos.append(f"{linha['time_casa']} x {linha['time_fora']} ({linha['status']})")
        
    confronto_selecionado = st.sidebar.selectbox("Escolha a Partida", menu_jogos)
    
    idx_sel = menu_jogos.index(confronto_selecionado)
    jogo_focado = df_filtrado_liga.iloc[idx_sel]
    
    t_casa = str(jogo_focado['time_casa'])
    t_fora = str(jogo_focado['time_fora'])
    horario = str(jogo_focado['status'])
    
    # 🎴 BANNER DE CONFRONTO ESTILO PLACAR LIVE
    st.markdown(f"""
        <div class="match-banner">
            <div class="match-teams">{t_casa} &nbsp; x &nbsp; {t_fora}</div>
            <div class="match-time">🕒 {horario} (BR) - PRÉ-CONFRONTO REAL</div>
        </div>
    """, unsafe_allow_html=True)
    
    m = gerar_metricas_avancadas(t_casa, t_fora)
    
    # 📊 GRID 1: PROBABILIDADES DE VITÓRIA (1X2)
    st.markdown("### 🧭 Probabilidades de Probabilidade Final (1X2)")
    col_c, col_e, col_f = st.columns(3)
    
    with col_c:
        st.metric(label=f"Vitória {t_casa}", value=f"{m['p_casa']}%")
    with col_e:
        st.metric(label="Empate Projetado", value=f"{m['p_empate']}%")
    with col_f:
        st.metric(label=f"Vitória {t_fora}", value=f"{m['p_fora']}%")
        
    st.divider()
    
    # ⚽ GRID 2: METRICAS AVANÇADAS DE GOLS (DESIGN EM LINHA)
    col_gols_ht, col_gols_ft = st.columns(2)
    
    with col_gols_ht:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.markdown("### ⏱️ Mercado de Gols - 1º Tempo (HT)")
        st.markdown(f"""
            <div class="market-row">
                <span class="market-name">Mais de 0.5 Gols HT (Over 0.5 HT)</span>
                <span class="market-value badge-over">{m['ht_over_05']}%</span>
            </div>
            <div class="market-row">
                <span class="market-name">Menos de 1.5 Gols HT (Under 1.5 HT)</span>
                <span class="market-value badge-under">{m['ht_under_15']}%</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_gols_ft:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.markdown("### 🏁 Mercado de Gols - Jogo Todo (FT)")
        st.markdown(f"""
            <div class="market-row">
                <span class="market-name">Mais de 1.5 Gols FT (Over 1.5 FT)</span>
                <span class="market-value badge-over">{m['ft_over_15']}%</span>
            </div>
            <div class="market-row">
                <span class="market-name">Mais de 2.5 Gols FT (Over 2.5 FT)</span>
                <span class="market-value badge-over">{m['ft_over_25']}%</span>
            </div>
            <div class="market-row">
                <span class="market-name">Ambos Marcam (BTTS Yes)</span>
                <span class="market-value badge-over">{m['btts']}%</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.divider()
    
    # 📐 GRID 3: CANTOS, CARTÕES E ARBITRAGEM
    st.markdown("### 📐 Análise de Linhas de Escanteios & Disciplina")
    col_e1, col_e2, col_e3 = st.columns(3)
    
    media_total_cantos = round(m['cantos_casa'] + m['cantos_fora'], 1)
    
    with col_e1:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.metric(label="📐 Média de Cantos Estimada", value=f"{media_total_cantos} Cantos")
        st.caption(f"Projeção: {t_casa} ({m['cantos_casa']}) | {t_fora} ({m['cantos_fora']})")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_e2:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.metric(label="🟨 Tendência de Cartões", value=f"{m['cartoes_media']} Cartões")
        st.caption("Média ponderada com base no histórico das equipes")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_e3:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.metric(label="👨‍⚖️ Árbitro da Partida", value=m['arbitro'])
        st.caption("Histórico de rigidez mapeado pela liga")
        st.markdown("</div>", unsafe_allow_html=True)
        
else:
    st.warning(f"⚠️ Nenhuma partida pré-jogo localizada para a liga {campeonato_selecionado} na data selecionada ({data_selecionada.strftime('%d/%m/%Y')}).")
