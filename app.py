import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import buscar_jogos_do_dia
from analises import calcular_analise_completa

st.set_page_config(page_title="Dashboard Pro Analytics", layout="wide")

st.title("📊 Dashboard de Análise Esportiva Avançada")
st.markdown("Fontes de Coleta Integrada: *SofaScore Real-Time*")

# --- FILTROS DE SELEÇÃO LATERAL ---
st.sidebar.header("🔍 Filtros de Busca")

data_selecionada = st.sidebar.date_input("1. Escolha a Data", datetime.today())
data_formatada = data_selecionada.strftime('%Y-%m-%d')

lista_jogos = []
try:
    with st.spinner("Buscando partidas reais no servidor..."):
        lista_jogos = buscar_jogos_do_dia(data_formatada)
except Exception as e:
    st.error(str(e))

if lista_jogos:
    df_jogos = pd.DataFrame(lista_jogos)
    
    # Filtro Dinâmico de Campeonatos Mundiais Reais
    todos_campeonatos = sorted(df_jogos['campeonato'].unique())
    campeonatos_selecionados = st.sidebar.multiselect("2. Selecione os Campeonatos", todos_campeonatos)
    
    if campeonatos_selecionados:
        df_jogos = df_jogos[df_jogos['campeonato'].isin(campeonatos_selecionados)]

    # --- ÁREA PRINCIPAL ---
    st.subheader(f"⚽ Partidas Encontradas ({len(df_jogos)})")
    
    df_exibicao = df_jogos.copy()
    df_exibicao.rename(columns={'status': 'Hora (Brasília)'}, inplace=True)
    st.dataframe(
        df_exibicao[['pais', 'campeonato', 'time_casa', 'time_fora', 'Hora (Brasília)']], 
        use_container_width=True, hide_index=True
    )
    
    st.divider()
    
    # Escolha do Jogo para Analisar
    df_jogos['partida'] = df_jogos['time_casa'] + " x " + df_jogos['time_fora']
    jogo_selecionado = st.selectbox("🎯 Selecione a partida que deseja dissecar:", df_jogos['partida'].unique())
    
    if jogo_selecionado:
        linha_jogo = df_jogos[df_jogos['partida'] == jogo_selecionado].iloc[0]
        
        id_jogo = int(linha_jogo['id'])
        t_casa = str(linha_jogo['time_casa'])
        t_fora = str(linha_jogo['time_fora'])
        
        # Puxar dados estritamente reais extraídos do SofaScore
        res = calcular_analise_completa(id_jogo, t_casa, t_fora)
        
        st.subheader(f"🛠️ O que você deseja analisar em {jogo_selecionado}?")
        
        # --- SELEÇÕES MÚLTIPLAS DE MERCADOS ---
        analisar_tudo = st.checkbox("🔥 ANALISAR TUDO DE UMA SÓ VEZ", value=False)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            quero_cartoes = st.checkbox("🟨 Cartões e Arbitragem", value=False if not analisar_tudo else True)
        with col_m2:
            quero_gols = st.checkbox("⚽ Tendências de Gols", value=False if not analisar_tudo else True)
        with col_m3:
            quero_probabilidades = st.checkbox("📈 Probabilidades Reais", value=False if not analisar_tudo else True)
            
        st.divider()
        
        # --- EXIBIÇÃO CONFORME ESCOLHA DOS BOTÕES ---
        
        if analisar_tudo or quero_probabilidades:
            st.markdown("### 📈 Probabilidades e Previsões do Confronto")
            st.info(f"**Votação Global do Público:** {res['probabilidade_vitoria']}")
            st.metric("⭐ Tendência de Favoritismo", res['time_favorito'])
            st.write("---")

        if analisar_tudo or quero_gols:
            st.markdown("### ⚽ Análise Real de Gols (Últimos Confrontos)")
            st.markdown(res['tendencia_gols'])
            st.write("---")
            
        if analisar_tudo or quero_cartoes:
            st.markdown("### 🟨 Relatório Disciplinar de Cartões")
            st.metric("👨‍⚖️ Árbitro Escalado", res['juiz_nome'])
            st.write("**Histórico de Padrões Recentes:**")
            st.markdown(res['tendencia_cartoes'])
            st.write("---")
            
        if not (analisar_tudo or quero_cartoes or quero_gols or quero_probabilidades):
            st.warning("Marque uma ou mais caixas acima para exibir as estatísticas correspondentes.")
else:
    if not lista_jogos:
        st.warning("Nenhum jogo oficial encontrado ou o servidor do SofaScore recusou a conexão automatizada.")
