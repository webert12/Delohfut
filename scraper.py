import requests
from datetime import datetime, timedelta
import json

def formatar_eventos_sofa(events):
    jogos_formatados = []
    for evento in events:
        timestamp_jogo = evento.get('startTimestamp')
        horario_brasilia = "--:--"
        if timestamp_jogo:
            dt_utc = datetime.utcfromtimestamp(timestamp_jogo)
            dt_brasilia = dt_utc - timedelta(hours=3)
            horario_brasilia = dt_brasilia.strftime('%H:%M')
        
        jogos_formatados.append({
            "id": int(evento.get('id')),
            "campeonato": evento.get('tournament', {}).get('name', 'Outros'),
            "pais": evento.get('tournament', {}).get('category', {}).get('name', 'Internacional'),
            "time_casa": evento.get('homeTeam', {}).get('name'),
            "time_fora": evento.get('awayTeam', {}).get('name'),
            "status": horario_brasilia
        })
    return jogos_formatados

def buscar_jogos_do_dia(data_str=None):
    if not data_str:
        fuso_brasil = datetime.utcnow() - timedelta(hours=3)
        data_str = fuso_brasil.strftime('%Y-%m-%d')
        
    url_sofa = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{data_str}"
    
    # ROTA 1: Emulação Direta de App Mobile Nativo
    headers_mobile = {
        "User-Agent": "SofaScore/Android/24.11.2 (Xiaomi; Android 14)",
        "X-So-Client": "android",
        "Accept": "*/*"
    }
    try:
        resposta = requests.get(url_sofa, headers=headers_mobile, timeout=5)
        if resposta.status_code == 200:
            events = resposta.json().get('events', [])
            if events:
                return formatar_eventos_sofa(events)
    except Exception:
        pass

    # ROTA 2: Túnel de Contingência de Alta Velocidade (corsproxy.io)
    try:
        url_proxy_io = f"https://corsproxy.io/?{requests.utils.quote(url_sofa)}"
        resposta = requests.get(url_proxy_io, timeout=6)
        if resposta.status_code == 200:
            events = resposta.json().get('events', [])
            if events:
                return formatar_eventos_sofa(events)
    except Exception:
        pass

    # ROTA 3: Túnel de Contingência Secundário (allorigins)
    try:
        url_allorigins = f"https://api.allorigins.win/get?url={requests.utils.quote(url_sofa)}"
        resposta = requests.get(url_allorigins, timeout=7)
        if resposta.status_code == 200:
            dados_proxy = resposta.json()
            conteudo_json = json.loads(dados_proxy.get('contents', '{}'))
            events = conteudo_json.get('events', [])
            if events:
                return formatar_eventos_sofa(events)
    except Exception:
        pass
        
    raise Exception("Todos os túneis de dados estão congestionados no momento. Mude a data do filtro ou recarregue a página para forçar uma nova rota de comunicação.")
