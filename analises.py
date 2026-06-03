import requests
import json

HEADERS_MOBILE = {
    "User-Agent": "SofaScore/Android/24.11.2 (Xiaomi; Android 14)",
    "X-So-Client": "android"
}

def fazer_requisicao_segura(url):
    try:
        res = requests.get(url, headers=HEADERS_MOBILE, timeout=6)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    try:
        url_proxy = f"https://api.allorigins.win/get?url={requests.utils.quote(url)}"
        res_proxy = requests.get(url_proxy, timeout=8)
        if res_proxy.status_code == 200:
            return json.loads(res_proxy.json().get('contents', '{}'))
    except Exception:
        pass
    return {}

def calcular_analise_completa(id_jogo, time_casa, time_fora):
    # 1. Informações básicas da partida (Árbitro Escaldado)
    url_evento = f"https://api.sofascore.com/api/v1/event/{id_jogo}"
    dados_evento = fazer_requisicao_segura(url_evento)
    evento = dados_evento.get('event', {})
    juiz_nome = evento.get('referee', {}).get('name', "Árbitro ainda não escalado para esta partida")
    
    juiz_id = evento.get('referee', {}).get('id')
    media_juiz = "Sem histórico recente registrado"
    if juiz_id:
        url_ref = f"https://api.sofascore.com/api/v1/referee/{juiz_id}"
        dados_ref = fazer_requisicao_segura(url_ref)
        ref_stats = dados_ref.get('referee', {})
        if ref_stats.get('yellowCardsPerGame'):
            media_juiz = f"{ref_stats.get('yellowCardsPerGame')} Amarelos por jogo"

    # 2. Votação e Probabilidades Reais da Comunidade Global
    url_votos = f"https://api.sofascore.com/api/v1/event/{id_jogo}/votes"
    dados_votos = fazer_requisicao_segura(url_votos)
    votos = dados_votos.get('votes', {})
    v_casa = votos.get('home', 0)
    v_empate = votos.get('draw', 0)
    v_fora = votos.get('away', 0)
    total_votos = v_casa + v_empate + v_fora
    
    if total_votos > 0:
        p_casa = round((v_casa / total_votos) * 100)
        p_empate = round((v_empate / total_votos) * 100)
        p_fora = round((v_fora / total_votos) * 100)
        probabilidade_vitoria = f"🟢 {time_casa}: {p_casa}% | ⚪ Empate: {p_empate}% | 🔴 {time_fora}: {p_fora}%"
        time_favorito = time_casa if p_casa > p_fora else (time_fora if p_fora > p_casa else "Empate Técnico")
    else:
        probabilidade_vitoria = "Votação de favoritismo ainda indisponível para este confronto."
        time_favorito = "Análise pendente por falta de interações"

    # 3. Tendências Reais Avançadas (Team Streaks) dos últimos confrontos
    url_streaks = f"https://api.sofascore.com/api/v1/event/{id_jogo}/team-streaks"
    dados_streaks = fazer_requisicao_segura(url_streaks)
    
    alertas_gols = []
    alertas_cartoes = []
    alertas_escanteios = []
    
    for streak in dados_streaks.get('general', []):
        nome_streak = streak.get('name', '')
        time_alvo = time_casa if streak.get('team') == 'home' else time_fora
        texto_formatado = f"• **{time_alvo}**: {nome_streak} (Nos últimos {streak.get('value')} jogos)"
        
        nome_lower = nome_streak.lower()
        if any(x in nome_lower for x in ['gols', 'goals', 'marcou', 'btts', 'ambas', 'gols']):
            alertas_gols.append(texto_formatado)
        elif any(x in nome_lower for x in ['cartões', 'cards', 'yellow', 'faltas']):
            alertas_cartoes.append(texto_formatado)
        elif any(x in nome_lower for x in ['escanteios', 'corners', 'cantos']):
            alertas_escanteios.append(texto_formatado)

    txt_gols = "\n".join(alertas_gols) if alertas_gols else "Sem alertas de gols específicos catalogados para os últimos jogos."
    txt_cartoes = "\n".join(alertas_cartoes) if alertas_cartoes else "Sem tendências disciplinares acentuadas para os elencos atuais."
    txt_escanteios = "\n".join(alertas_escanteios) if alertas_escanteios else "Sem médias críticas de escanteios registradas recentemente."

    time_mais_gols = "Ver detalhes nas tendências"
    time_mais_cartoes = "Ver detalhes nas tendências"
    
    for streak in dados_streaks.get('general', []):
        n = streak.get('name', '').lower()
        t = time_casa if streak.get('team') == 'home' else time_fora
        if 'mais de 2.5' in n or 'more than 2.5' in n:
            time_mais_gols = t
        if 'mais de 4.5 cart' in n or 'more than 4.5 cards' in n:
            time_mais_cartoes = t

    return {
        "juiz_nome": juiz_nome,
        "media_juiz": media_juiz,
        "probabilidade_vitoria": probabilidade_vitoria,
        "time_favorito": time_favorito,
        "tendencia_gols": txt_gols,
        "tendencia_cartoes": txt_cartoes,
        "tendencia_escanteios": txt_escanteios,
        "time_ataque_forte": time_mais_gols,
        "time_mais_faltoso": time_mais_cartoes
    }
