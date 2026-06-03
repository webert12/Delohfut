import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO DA PÁGINA (ESTILO DASHBOARD PREMIUM) ---
st.set_page_config(page_title="PRO Analytics - Corner Style", layout="wide", initial_sidebar_state="expanded")

# 🎨 DESIGN PROFISSIONAL ESCURO (ESTILO CORNER PRO / TRADING)
st.markdown("""
    <style>
        .stApp { background-color: #0d1117 !important; color: #c9d1d9 !important; }
        [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
        h1, h2, h3, h4 { color: #ffffff !important; font-family: 'Inter', sans-serif; font-weight: 700 !important; }
        
        .match-banner {
            background: linear-gradient(135deg, #1f293d 0%, #111827 100%);
            border: 1px solid #38bdf8;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        .match-teams { font-size: 26px; font-weight: 800; color: #ffffff; margin-bottom: 5px; }
        .match-time { background-color: #0ea5e9; color: #ffffff; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; display: inline-block; }
        
        .stat-card { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 10px; margin-bottom: 15px; }
        .market-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #21262d; }
        .market-name { font-size: 15px; color: #8b949e; }
        .market-value { font-size: 16px; font-weight: 700; }
        
        .badge-over { background-color: #22c55e !important; color: #ffffff !important; padding: 3px 8px; border-radius: 5px; font-weight: bold; }
        .badge-under { background-color: #eab308 !important; color: #000000 !important; padding: 3px 8px; border-radius: 5px; font-weight: bold; }
        
        div[data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: 800 !important; font-size: 32px !important; }
        div[data-testid="stMetricLabel"] { color: #8b949e !important; }
        hr { border-color: #30363d !important; }
    </style>
""", unsafe_allow_html=True)

# 📊 BANCO DE DADOS DE FORÇA TÉCNICA (Power Ratings)
TABELA_FORCA = {
    "Germany": 88, "Brazil": 90, "Argentina": 91, "France": 92, "Spain": 89, 
    "England": 89, "Portugal": 88, "Italy": 86, "Netherlands": 86, "Ivory Coast": 76,
    "Real Madrid": 94, "Barcelona": 89, "Manchester City": 94, "Bayern Munich": 91,
    "Flamengo": 82, "Palmeiras": 82, "River Plate": 80, "Boca Juniors": 77
}

# 📡 SCRAPER DA API COM CAPTURA DE DADOS REAIS
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
            for evento in dados.get('events', []):
                try:
                    competicao = evento.get('competitions', [{}])[0]
                    if competicao.get('status', {}).get('type', {}).get('state', 'pre') != 'pre': continue
                    
                    # Captura de Árbitro Real
                    referees = competicao.get('referees', [])
                    juiz_real = referees[0].get('displayName') if referees else "Escala pendente pela Liga"
                    
                    # Captura de Linhas de Gols/Odds Reais
                    odds_list = competicao.get('odds', [])
                    linha_gols_real = odds_list[0].get('overUnder') if odds_list else None
                    odds_detalhe_real = odds_list[0].get('details') if odds_list else None
                    
                    time_casa, time_fora = "Não definido", "Não definido"
                    for team_data in competicao.get('competitors', []):
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
                        "status": horario_brasilia,
                        "juiz": juiz_real,
                        "linha_gols": linha_gols_real,
                        "odds_detalhe": odds_detalhe_real
                    })
                except: continue
    except: pass
    return jogos_formatados

# 🧠 MOTOR ANALÍTICO CONFIGURADO POR DISPARIDADE TÉCNICA
def calcular_analise_real(time_c, time_f, linha_gols_api):
    f_casa = TABELA_FORCA.get(time_c, 75)
    f_fora = TABELA_FORCA.get(time_f, 75)
    
    peso_casa = f_casa + 3
    peso_fora = f_fora
    total_peso = peso_casa + peso_fora
    
    diff = peso_casa - peso_fora
    
    prob_casa = int(max(15, min(85, 45 + (diff * 2.5))))
    prob_fora = int(max(10, min(80, 35 - (diff * 2.5))))
    prob_empate = max(5, 100 - prob_casa - prob_fora)
    
    nivel_gols = (f_casa + f_fora) / 2
    ht_over = int(max(40, min(92, nivel_gols * 0.85 + (diff if diff > 0 else 0))))
    ft_over_25 = int(max(30, min(85, nivel_gols * 0.70)))
    btts = int(max(35, min(78, (100 - prob_empate) * 0.8)))
    
    cantos_c = round(max(3.5, min(8.5, (f_casa / 12) + 1)), 1)
    cantos_f = round(max(3.0, min(7.5, (f_fora / 14))), 1)
    
    proximidade = 20 - abs(prob_casa - prob_fora)
    cartoes = round(max(2.5, min(6.5, 3.0 + (proximidade * 0.15))), 1)
    
    return {
        "p_casa": prob_casa, "p_empate": prob_empate, "p_fora": prob_fora,
        "ht_05": ht_over, "ht_15_under": int(100 - (ht_over * 0.4)),
        "ft_15": int(max(65, ft_over_25 + 15)), "ft_25": ft_over_25, "btts": btts,
        "cantos_c": cantos_c, "cantos_f": cantos_f, "cartoes": cartoes
    }

# --- CONTROL PANEL LATERAL ---
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

# --- PAINEL CENTRAL PRINCIPAL ---
st.markdown(f"<h1>📈 CORNER PRO <span style='color:#38bdf8;'>ANALYTICS</span></h1>", unsafe_allow_html=True)
st.markdown("---")

lista_jogos = buscar_jogos_do_dia(data_str=data_formatada, liga_slug=slug_escolhido)

if lista_jogos:
    df_filtrado_liga = pd.DataFrame(lista_jogos)
    
    menu_jogos = [f"{r['time_casa']} x {r['time_fora']} ({r['status']})" for _, r in df_filtrado_liga.iterrows()]
    confronto_selecionado = st.sidebar.selectbox("Escolha a Partida Real", menu_jogos)
    
    idx_sel = menu_jogos.index(confronto_selecionado)
    jogo_focado = df_filtrado_liga.iloc[idx_sel]
    
    t_casa = str(jogo_focado['time_casa'])
    t_fora = str(jogo_focado['time_fora'])
    horario = str(jogo_focado['status'])
    juiz_do_jogo = str(jogo_focado['juiz'])
    linha_gols_api = jogo_focado['linha_gols']
    linha_odds_api = jogo_focado['odds_detalhe']
    
    # 🎴 BANNER DE CONFRONTO ESTILO PLACAR LIVE
    st.markdown(f"""
        <div class="match-banner">
            <div class="match-teams">{t_casa} &nbsp; x &nbsp; {t_fora}</div>
            <div class="match-time">🕒 {horario} (BR) - CONFRONTO REAL AGENDADO</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Processa as métricas
    m = calcular_analise_real(t_casa, t_fora, linha_gols_api)
    
    # 📊 SEÇÃO 1: PROBABILIDADES DE VITÓRIA (1X2)
    st.markdown("### 🧭 Probabilidades de Resultado Final (1X2)")
    col_c, col_e, col_f = st.columns(3)
    
    with col_c: st.metric(label=f"Vitória {t_casa}", value=f"{m['p_casa']}%")
    with col_e: st.metric(label="Empates", value=f"{m['p_empate']}%")
    with col_f: st.metric(label=f"Vitória {t_fora}", value=f"{m['p_fora']}%")
    
    if linha_odds_api:
        st.info(f"💵 **Linha de Abertura do Mercado:** {linha_odds_api}")
        
    st.divider()
    
    # ⚽ SEÇÃO 2: MERCADO DE GOLS HT E FT
    col_gols_ht, col_gols_ft = st.columns(2)
    
    with col_gols_ht:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.markdown("<h4>⏱️ Mercado de Gols - 1º Tempo (HT)</h4>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="market-row"><span class="market-name">Mais de 0.5 Gols HT</span><span class="market-value badge-over">{m['ht_05']}%</span></div>
            <div class="market-row"><span class="market-name">Menos de 1.5 Gols HT</span><span class="market-value badge-under">{m['ht_15_under']}%</span></div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_gols_ft:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.markdown("<h4>🏁 Mercado de Gols - Jogo Todo (FT)</h4>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="market-row"><span class="market-name">Mais de 1.5 Gols FT</span><span class="market-value badge-over">{m['ft_15']}%</span></div>
            <div class="market-row"><span class="market-name">Mais de 2.5 Gols FT</span><span class="market-value badge-over">{m['ft_25']}%</span></div>
            <div class="market-row"><span class="market-name">Ambos Marcam (BTTS Yes)</span><span class="market-value badge-over">{m['btts']}%</span></div>
        """, unsafe_allow_html=True)
        if linha_gols_api:
            st.caption(f"🎯 Linha de Gols recomendada pelas Casas: {linha_gols_api}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.divider()
    
    # 📐 SEÇÃO 3: ESCANTEIOS, CARTÕES E JUÍZ REAL
    st.markdown("### 📐 Linhas Avançadas de Escanteios & Disciplina")
    col_e1, col_e2, col_e3 = st.columns(3)
    
    total_cantos = round(m['cantos_c'] + m['cantos_f'], 1)
    
    with col_e1:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.metric(label="📐 Média de Cantos Projetada", value=f"{total_cantos} Cantos")
        st.caption(f"Projeção por Força: {t_casa} ({m['cantos_c']}) | {t_fora} ({m['cantos_f']})")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_e2:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.metric(label="🟨 Média de Cartões", value=f"{m['cartoes']} Cartões")
        st.caption("Baseado na intensidade esperada do duelo")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_e3:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.metric(label="👨‍⚖️ Árbitro Escalado", value=juiz_do_jogo)
        st.caption("Dado oficial extraído da súmula da Liga")
        st.markdown("</div>", unsafe_allow_html=True)
        
else:
    st.warning(f"⚠️ Nenhuma partida pré-jogo real localizada para a liga {campeonato_selecionado} na data selecionada ({data_selecionada.strftime('%d/%m/%Y')}).")
