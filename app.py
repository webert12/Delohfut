import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.sofascore.com/",
    "Origin": "https://www.sofascore.com"
}

def calcular_analise_completa(id_jogo, time_casa, time_fora):
    # 1. Buscar Árbitro Real
    url_evento = f"https://api.sofascore.com/api/v1/event/{id_jogo}"
    juiz_nome = "Não informado ou não escalado ainda"
    try:
        r_ev = requests.get(url_evento, headers=HEADERS, timeout=6)
        if r_ev.status_code == 200:
            ev_data = r_ev.json().get('event', {})
            juiz_nome = ev_data.get('referee', {}).get('name', "Não informado")
    except:
        pass

    # 2. Buscar Probabilidades baseadas nos votos reais da plataforma
    url_votos = f"https://api.sofascore.com/api/v1/event/{id_jogo}/votes"
    prob_texto = "Sem votação registrada para esta partida"
    favorito = "Dados insuficientes"
    try:
        r_vo = requests.get(url_votos, headers=HEADERS, timeout=6)
        if r_vo.status_code == 200:
            votos = r_vo.json().get('votes', {})
            v_casa = votos.get('home', 0)
            v_empate = votos.get('draw', 0)
            v_fora = votos.get('away', 0)
            total = v_casa + v_empate + v_fora
            if total > 0:
                p_casa = round((v_casa / total) * 100)
                p_emp = round((v_empate / total) * 100)
                p_fora = round((v_fora / total) * 100)
                prob_texto = f"🟢 {time_casa}: {p_casa}% | ⚪ Empate: {p_emp}% | 🔴 {time_fora}: {p_fora}%"
                
                if p_casa > p_fora and p_casa > p_emp:
                    favorito = f"{time_casa} (Baseado no voto do público)"
                elif p_fora > p_casa and p_fora > p_emp:
                    favorito = f"{time_fora} (Baseado no voto do público)"
                else:
                    favorito = "Equilíbrio / Empate Técnico"
    except:
        pass

    # 3. Buscar Tendências Reais (Team Streaks) dos últimos jogos
    url_streaks = f"https://api.sofascore.com/api/v1/event/{id_jogo}/team-streaks"
    tendencias_gols = []
    tendencias_cartoes = []
    try:
        r_st = requests.get(url_streaks, headers=HEADERS, timeout=6)
        if r_st.status_code == 200:
            streaks = r_st.json()
            for streak in streaks.get('general', []):
                name = streak.get('name', '')
                team = time_casa if streak.get('team') == 'home' else time_fora
                
                # Filtrar padrões reais de gols
                if any(x in name.lower() for x in ['goals', 'gols', 'score', 'fewer']):
                    tendencias_gols.append(f"⚽ **{team}**: {name}")
                # Filtrar padrões reais de cartões
                if any(x in name.lower() for x in ['cards', 'cartões', 'yellow']):
                    tendencias_cartoes.append(f"🟨 **{team}**: {name}")
    except:
        pass

    txt_gols = "\n".join(tendencias_gols) if tendencias_gols else "Sem sequências de gols marcantes registradas nos últimos 5 jogos."
    txt_cartoes = "\n".join(tendencias_cartoes) if tendencias_cartoes else "Sem alertas de cartões específicos catalogados para hoje."

    return {
        "juiz_nome": juiz_nome,
        "probabilidade_vitoria": prob_texto,
        "time_favorito": favorito,
        "tendencia_gols": txt_gols,
        "tendencia_cartoes": txt_cartoes
    }
