import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import buscar_jogos_do_dia

# Configuração da página do Streamlit
st.set_page_config(page_title="Analytics Pro - Esportes", layout="wide")

st.title("📊 Dashboard de Análise Esportiva Profissional")
st.markdown("Fontes: *SofaScore & Flashscore*")

# --- BARRA LATERAL DE FILTROS ---
st.sidebar.header("Filtros de Seleção")

# 1. Filtro de Data
data_selecionada = st.sidebar.date_input("Escolha a Data", datetime.today())
data_formatada = data_selecionada.strftime('%Y-%m-%d')

# Buscar os dados usando o nosso scraper
with st.spinner("Buscando jogos no SofaScore..."):
    lista_jogos = buscar_jogos_do_dia(data_formatada)

if lista_jogos:
    # Converter a lista de jogos para um DataFrame do Pandas (Tabela)
    df_jogos = pd.DataFrame(lista_jogos)
    
    # 2. Filtro de Campeonato (Dinâmico baseado nos jogos do dia)
    lista_campeonatos = sorted(df_jogos['campeonato'].unique())
    campeonatos_selecionados = st.sidebar.multiselect("Filtrar por Campeonato", lista_campeonatos)
    
    # Aplicar filtro de campeonato se houver algum selecionado
    if campeonatos_selecionados:
        df_jogos = df_jogos[df_jogos['campeonato'].isin(campeonatos_selecionados)]
        
    # --- ÁREA PRINCIPAL ---
    st.subheader(f"⚽ Jogos Encontrados ({len(df_jogos)})")
    
    # Exibir a tabela formatada na tela
    st.dataframe(
        df_jogos[['pais', 'campeonato', 'time_casa', 'time_fora', 'status']], 
        use_container_width=True,
        hide_index=True
    )
    
    # Próximo passo do sistema (Seleção de um jogo específico para análise)
    st.divider()
    st.subheader("🔍 Análise Detalhada da Partida")
    
    # Criar uma lista de nomes de jogos para o usuário escolher qual analisar
    df_jogos['partida'] = df_jogos['time_casa'] + " x " + df_jogos['time_fora']
    jogo_para_analisar = st.selectbox("Selecione um jogo para abrir as estatísticas de Gols, Cartões e Árbitro:", df_jogos['partida'])

    # --- CONECTANDO O ARQUIVO DE ANÁLISES ---
    if jogo_para_analisar:
        # Descobrir o ID do jogo selecionado
        id_do_jogo = df_jogos[df_jogos['partida'] == jogo_para_analisar]['id'].values[0]
        
        st.subheader(f"📊 Relatório Avançado: {jogo_para_analisar}")
        
        # Importando as funções do analises.py dinamicamente
        from analises import puxar_detalhes_do_jogo, calcular_probabilidade_cartoes, analisar_gols_e_escanteios
        
        detalhes = puxar_detalhes_do_jogo(id_do_jogo)
        
        col1, col2, col3 = st.columns(3)
        
        if detalhes and detalhes.get('arbitro', {}).get('nome') != 'Não informado':
            arbitro = detalhes['arbitro']
            stats_arbitro = calcular_probabilidade_cartoes(arbitro['id'])
            
            with col1:
                st.metric(label="👨‍⚖️ Árbitro Escalado", value=arbitro['nome'])
                st.write(f"**Tendência:** {stats_arbitro.get('tendencia', 'N/A')}")
                st.write(f"📊 Média de Amarelos/Jogo: **{stats_arbitro.get('media_amarelos')}**")
        else:
            with col1:
                st.info("Árbitro ainda não escalado ou não encontrado para esta partida.")
                
        # Bloco de Gols e Escanteios
        stats_jogo = analisar_gols_e_escanteios(id_do_jogo)
        if stats_jogo:
            with col2:
                st.metric(label="⚽ Probabilidade Gol no 1º Tempo (HT)", value=stats_jogo['probabilidade_gol_ht'])
                st.caption("Baseado nos últimos 10 jogos de ambas as equipes.")
                
            with col3:
                st.metric(label="📐 Média Est. de Escanteios", value=f"{stats_jogo['media_escanteios_jogo']} Cantos")
                st.caption("Tendência da linha de Over/Under para o mercado.")

else:
    st.warning("Nenhum jogo encontrado para a data selecionada ou limite de requisições atingido.")
