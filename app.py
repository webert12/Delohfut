import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import buscar_jogos_do_dia
from analises import calcular_analise_completa

st.set_page_config(page_title="Dashboard Pro Analytics", layout="wide")

st.title("📊 Painel de Análise Estatística Pré-Jogo")
st.markdown("Filtro Ativo: **Apenas confrontos futuros**")

# --- FILTROS DE SELEÇÃO LATERAL ---
st.sidebar.header("🔍 Configurações")
data_selecionada = st.sidebar.date_input("Escolha a Data da Rodada", datetime.today())
data_formatada = data_selecionada.strftime('%Y-%m-%d')

CAMPEONATOS_FIXOS = [
    "🏆 Copa do Mundo FIFA",
    "🏆 Copa Libertadores",
    "🌍 Copa Sul-Americana",
    "🇧🇷 Brasileirão Série A",
    "🇧🇷 Brasileirão Série B",
    "🇧🇷 Copa do Brasil",
    "🇸🇦 Liga Saudita (Arábia Saudita)",
    "🇪🇸 Campeonato Espanhol (LaLiga)",
    "🇮🇹 Campeonato Italiano (Serie A)",
    "🇩🇪 Campeonato Alemão (Bundesliga)",
    "🇫🇷 Campeonato Francês (Ligue 1)",
    "🇵🇹 Campeonato Português (Liga Portugal)",
    "🇦🇷 Campeonato Argentino",
    "🇳🇴 Campeonato Norueguês (Eliteserien)",
    "⚽ Outros Confrontos"
]

# 🧱 PASSO 1: Escolher o Campeonato
st.subheader("🏆 Passo 1: Selecione o Campeonato")
campeonato_selecionado = st.selectbox("Escolha a liga que deseja analisar:", CAMPEONATOS_FIXOS)

# Coleta os dados do dia de forma segura
lista_jogos = buscar_jogos_do_dia(data_formatada)

df_filtrado_liga = pd.DataFrame()
if lista_jogos:
    df_jogos = pd.DataFrame(lista_jogos)
    df_filtrado_liga = df_jogos[df_jogos['campeonato'] == campeonato_selecionado]

st.divider()

# Exibição baseada no filtro
if not df_filtrado_liga.empty:
    
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
