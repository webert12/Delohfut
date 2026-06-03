import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import buscar_jogos_do_dia
from analises import calcular_analise_completa

st.set_page_config(page_title="Dashboard Pro Analytics", layout="wide")

st.title("📊 Dashboard de Análise Esportiva Avançada")
st.markdown("Fontes de Coleta Integrada: *ESPN Global Server (Dados 100% Reais e Livres de Bloqueio)*")

# --- FILTROS DE SELEÇÃO LATERAL ---
st.sidebar.header("🔍 Filtros de Busca")

data_selecionada = st.sidebar.date_input("1. Escolha a Data", datetime.today())
data_formatada = data_selecionada.strftime('%Y-%m-%d')

lista_jogos = []
try:
    with st.spinner("Conectando à API Oficial da ESPN..."):
        lista_jogos = buscar_jogos_do_dia(data_formatada)
except Exception as e:
    st.error(f"⚠️ {str(e)}")

if lista_jogos:
    df_jogos = pd.DataFrame(lista_jogos)
    
    # Filtro Dinâmico de Campeonatos Mundiais Reais
    todos_campeonatos = sorted(df_jogos['campeonato'].unique())
    campeonatos_selecionados = st.sidebar.multiselect("2. Selecione os Campeonatos", todos_campeonatos)
    
    if campeonatos_selecionados:
        df_jogos = df_jogos[df_jogos['campeonato'].isin(campeonatos_selecionados)]

    # --- ÁREA PRINCIPAL ---
    st.subheader(f"⚽ Partidas Reais Encontradas ({len(df_jogos)})")
    
    df_exibicao = df_jogos.copy()
    df_exibicao.rename(columns={'status': 'Status / Horário'}, inplace=True)
    st.dataframe(
        df_exibicao[['campeonato', 'time_casa', 'time_fora', 'Status / Horário']], 
        use_container_width=True, hide_index=True
    )
    
    st.divider()
    
    # Escolha do Jogo para Analisar
    df_jogos['partida'] = df_jogos['time_casa'] + " x " + df_jogos['time_fora']
    jogo_selecionado = st.selectbox("🎯 Selecione a partida que deseja dissecar:", df_jogos['partida'].unique())
    
    if jogo_selecionado:
        linha_jogo = df_jogos[df_jogos['partida'] == jogo_selecionado].iloc[0]
        
        id_jogo = str(linha_jogo['id'])
        t_casa = str(linha_jogo['time_casa'])
        t_fora = str(linha_jogo['time_fora'])
        
        with st.spinner("Puxando retrospecto real e dados analíticos..."):
            res = calcular_analise_completa(id_jogo, t_casa, t_fora)
        
        st.subheader(f"🛠️ O que você deseja analisar em {jogo_selecionado}?")
        
        analisar_tudo = st.checkbox("🔥 ANALISAR TUDO DE UMA SÓ VEZ", value=False)
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            quero_probabilidades = st.checkbox("📈 Probabilidades e Favoritismo", value=False if not analisar_tudo else True)
        with col_m2:
            quero_gols = st.checkbox("⚽ Histórico e Gols", value=False if not analisar_tudo else True)
        with col_m3:
            quero_cartoes = st.checkbox("🟨 Arbitragem e Elenco", value=False if not analisar_tudo else True)
        with col_m4:
            quero_escanteios = st.checkbox("📐 Escanteios", value=False if not analisar_tudo else True)
            
        st.divider()
        
        if analisar_tudo or quero_probabilidades:
            st.markdown("### 📈 Probabilidades e Previsões do Confronto")
            st.info(f"**Indicadores de Performance:** {res['probabilidade_vitoria']}")
            st.metric("⭐ Tendência Estatística", res['time_favorito'])
            st.write("---")

        if analisar_tudo or quero_gols:
            st.markdown("### ⚽ Retrospecto de Jogos e Gols Marcados")
            st.markdown(res['tendencia_gols'])
            st.write("---")
            
        if analisar_tudo or quero_cartoes:
            st.markdown("### 🟨 Arbitragem e Relatório de Campo")
            st.metric("👨‍⚖️ Árbitro Escalado", res['juiz_nome'])
            st.markdown(res['tendencia_cartoes'])
            st.write("---")
            
        if analisar_tudo or quero_escanteios:
            st.markdown("### 📐 Estatísticas de Escanteios")
            st.markdown(res['tendencia_escanteios'])
            st.write("---")
else:
    st.info("Selecione outra data no menu lateral caso não existam rodadas agendadas para o dia escolhido.")
