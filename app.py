import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from analises import calcular_analise_completa

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard Pro Analytics", layout="wide")

st.title("📊 Painel de Análise Estatística Pré-Jogo")
st.markdown("Filtro Ativo: **Apenas confrontos futuros** | Conexão Direta por Banco de Dados")

# 📡 FUNÇÃO DE SCRAPER INTEGRADA (Evita erros de sincronização de arquivos no celular)
def buscar_jogos_do_dia(data_str, liga_slug="all"):
    if data_str:
        data_espn = str(data_str).replace("-", "")
    else:
        data_espn = datetime.now().strftime("%Y%m%d")
        
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{liga_slug}/scoreboard?dates={data_espn}"
    jogos_formatados = []
    
    try:
        resposta = requests.get(url, timeout=10)
        if resposta.status_code != 200:
            return []
            
        dados = resposta.json()
        events = dados.get('events', [])
        
        for evento in events:
            try:
                competitions = evento.get('competitions', [])
                if not competitions:
                    continue
                competicao = competitions[0]
                
                # Filtra apenas partidas que não começaram (pré-jogo)
                status_obj = competicao.get('status', {})
                estado_jogo = status_obj.get('type', {}).get('state', 'pre') 
                if estado_jogo != 'pre':
                    continue
                
                competitors = competicao.get('competitors', [])
                time_casa = "Não definido"
                time_fora = "Não definido"
                
                for team_data in competitors:
                    if team_data.get('homeAway') == 'home':
                        time_casa = team_data.get('team', {}).get('name')
                    elif team_data.get('homeAway') == 'away':
                        time_fora = team_data.get('team', {}).get('name')
                
                # Ajuste Fuso Horário UTC -> Brasília
                data_utc_str = competicao.get('date', '') 
                horario_brasilia = "--:--"
                if data_utc_str:
                    try:
                        dt_utc = datetime.strptime(data_utc_str, "%Y-%m-%dT%H:%MZ")
                        dt_br = dt_utc - timedelta(hours=3)
                        horario_brasilia = dt_br.strftime('%H:%M')
                    except:
                        horario_brasilia = status_obj.get('type', {}).get('shortDetail', '--:--')

                jogos_formatados.append({
                    "id": str(evento.get('id')),
                    "time_casa": time_casa,
                    "time_fora": time_fora,
                    "status": horario_brasilia
                })
            except Exception:
                continue
                
        return jogos_formatados
    except Exception:
        return []

# --- DICIONÁRIO DE CONEXÕES DIRETAS DA ESPN ---
MAPA_LIGAS_ESPN = {
    "🏆 Copa do Mundo FIFA": "fifa.world",
    "🏆 Copa Libertadores": "conmebol.libertadores",
    "🌍 Copa Sul-Americana": "conmebol.sudamericana",
    "🇧🇷 Brasileirão Série A": "bra.1",
    "🇧🇷 Brasileirão Série B": "bra.2",
    "🇧🇷 Copa do Brasil": "bra.copa_do_brasil",
    "🇸🇦 Liga Saudita (Arábia Saudita)": "sau.1",
    "🇪🇸 Campeonato Espanhol (LaLiga)": "esp.1",
    "🇮🇹 Campeonato Italiano (Serie A)": "ita.1",
    "🇩🇪 Campeonato Alemão (Bundesliga)": "ger.1",
    "🇫🇷 Campeonato Francês (Ligue 1)": "fra.1",
    "🇵🇹 Campeonato Português (Liga Portugal)": "por.1",
    "🇦🇷 Campeonato Argentino": "arg.1",
    "🇳🇴 Campeonato Norueguês (Eliteserien)": "nor.1",
    "⚽ Outros Confrontos": "all"
}

# --- FILTROS DE SELEÇÃO LATERAL ---
st.sidebar.header("🔍 Configurações")
data_selecionada = st.sidebar.date_input("Escolha a Data da Rodada", datetime.today())
data_formatada = data_selecionada.strftime('%Y-%m-%d')

# 🧱 PASSO 1: Escolher o Campeonato
st.subheader("🏆 Passo 1: Selecione o Campeonato")
campeonato_selecionado = st.selectbox("Escolha a liga que deseja analisar:", list(MAPA_LIGAS_ESPN.keys()))

slug_escolhido = MAPA_LIGAS_ESPN[campeonato_selecionado]

# Executa a busca usando a função local do próprio arquivo
lista_jogos = buscar_jogos_do_dia(data_str=data_formatada, liga_slug=slug_escolhido)

st.divider()

if lista_jogos:
    df_filtrado_liga = pd.DataFrame(lista_jogos)
    
    # 🧱 PASSO 2: Escolher o Time
    st.subheader("⚽ Passo 2: Selecione o Time")
    times_disponiveis = sorted(list(set(df_filtrado_liga['time_casa'].tolist() + df_filtrado_liga['time_fora'].tolist())))
    time_selecionado = st.selectbox("Escolha a equipe para focar a análise pré-jogo:", times_disponiveis)
    
    linha_jogo = df_filtrado_liga[(df_filtrado_liga['time_casa'] == time_selecionado) | (df_filtrado_liga['time_fora'] == time_selecionado)].iloc[0]
    
    id_jogo = str(linha_jogo['id'])
    t_casa = str(linha_jogo['time_casa'])
    t_fora = str(linha_jogo['time_fora'])
    horario = str(linha_jogo['status'])
    
    st.divider()
    
    st.success(f"🎯 **Confronto Localizado:** {t_casa} x {t_fora} | 🕒 **Horário:** {horario} (Brasília)")
    
    with st.spinner(f"Processando métricas oficiais de {t_casa} x {t_fora}..."):
        res = calcular_analise_completa(id_jogo, t_casa, t_fora)
        
    st.subheader(f"🛠️ Painel Analítico")
    analisar_tudo = st.checkbox("🔥 EXIBIR TODOS OS MERCADOS DE ANÁLISE", value=True)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        quero_probabilidades = st.checkbox("📈 Probabilidades / Odds", value=True if analisar_tudo else False)
    with col_m2:
        quero_gols = st.checkbox("⚽ Histórico H2H / Gols", value=True if analisar_tudo else False)
    with col_m3:
        quero_cartoes = st.checkbox("🟨 Juiz e Escalação", value=True if analisar_tudo else False)
        
    st.divider()
    
    if quero_probabilidades:
        st.markdown("### 📈 Previsões de Força do Confronto")
        st.info(f"**Projeção Algorítmica das Ligas:** {res['probabilidade_vitoria']}")
        st.metric("⭐ Tendência de Favoritismo Técnico", res['time_favorito'])
        st.write("---")

    if quero_gols:
        st.markdown("### ⚽ Retrospecto de Jogos e Confrontos Reais em Campo")
        st.markdown(res['tendencia_gols'])
        st.write("---")
        
    if quero_cartoes:
        st.markdown("### 🟨 Informações sobre a Escala de Arbitragem")
        st.metric("👨‍⚖️ Árbitro Escalado", res['juiz_nome'])
        st.markdown(res['tendencia_cartoes'])
        st.write("---")
else:
    st.warning(f"⚠️ Não existem jogos pré-confronto agendados para o campeonato **{campeonato_selecionado}** na data selecionada ({data_selecionada.strftime('%d/%m/%Y')}).")
