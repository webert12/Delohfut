import streamlit as st
import pandas as pd
from datetime import datetime
from scraper import buscar_jogos_do_dia
from analises import calcular_analise_completa

st.set_page_config(page_title="Dashboard Pro Analytics", layout="wide")

st.title("📊 Painel de Análise Estatística Pré-Jogo")
st.markdown("Filtro Ativo: **Apenas confrontos futuros** | Dados 100% Reais e Oficiais")

# --- FILTROS DE SELEÇÃO LATERAL ---
st.sidebar.header("🔍 Configurações do Filtro")

# 1. Alterar a Data recarrega exatamente os jogos reais daquele dia específico
data_selecionada = st.sidebar.date_input("1. Escolha a Data da Rodada", datetime.today())
data_formatada = data_selecionada.strftime('%Y-%m-%d')

lista_jogos = []
try:
    with st.spinner("Varrendo agenda de jogos futuros..."):
        lista_jogos = buscar_jogos_do_dia(data_formatada)
except Exception as e:
    st.sidebar.error(f"⚠️ {str(e)}")

if lista_jogos:
    df_jogos = pd.DataFrame(lista_jogos)
    
    # 2. Escolha do Campeonato (Atualiza dinamicamente com as ligas reais do dia)
    todos_campeonatos = sorted(df_jogos['campeonato'].unique())
    campeonato_selecionado = st.sidebar.selectbox("2. Escolha o Campeonato", ["Todos os Campeonatos"] + todos_campeonatos)
    
    if campeonato_selecionado != "Todos os Campeonatos":
        df_jogos = df_jogos[df_jogos['campeonato'] == campeonato_selecionado]

    # --- ÁREA PRINCIPAL ---
    st.subheader(f"📅 Agenda Pré-Jogo Disponível - {data_selecionada.strftime('%d/%m/%Y')}")
    
    df_exibicao = df_jogos.copy()
    df_exibicao.rename(columns={'campeonato': 'Campeonato', 'time_casa': 'Time da Casa', 'time_fora': 'Visitante', 'status': 'Horário de Início (BR)'}, inplace=True)
    
    st.dataframe(
        df_exibicao[['Campeonato', 'Time da Casa', 'Visitante', 'Horário de Início (BR)']], 
        use_container_width=True, hide_index=True
    )
    
    st.divider()
    
    # 3. Escolha da Partida Filtrada para Análise Dissecada
    df_jogos['partida'] = df_jogos['time_casa'] + " x " + df_jogos['time_fora']
    jogo_selecionado = st.selectbox("🎯 Escolha o confronto que deseja analisar:", df_jogos['partida'].unique())
    
    if jogo_selecionado:
        linha_jogo = df_jogos[df_jogos['partida'] == jogo_selecionado].iloc[0]
        
        id_jogo = str(linha_jogo['id'])
        t_casa = str(linha_jogo['time_casa'])
        t_fora = str(linha_jogo['time_fora'])
        
        with st.spinner(f"Coletando histórico real para {jogo_selecionado}..."):
            res = calcular_analise_completa(id_jogo, t_casa, t_fora)
        
        st.subheader(f"🛠️ Métricas de Estudo: {jogo_selecionado}")
        
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
    st.warning(f"Nenhum jogo futuro/pré-confronto agendado para {data_selecionada.strftime('%d/%m/%Y')}. Caso houvessem partidas hoje que já terminaram ou estão em andamento, elas foram ocultadas pelo filtro.")
