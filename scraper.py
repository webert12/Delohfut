import requests
from datetime import datetime, timedelta

def buscar_jogos_do_dia(data_str=None):
    if not data_str:
        fuso_brasil = datetime.utcnow() - timedelta(hours=3)
        data_str = fuso_brasil.strftime('%Y-%m-%d')
        
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{data_str}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Referer": "https://www.sofascore.com/",
        "Origin": "https://www.sofascore.com"
    }
    
    resposta = requests.get(url, headers=headers, timeout=12)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        events = dados.get('events', [])
        
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
    elif resposta.status_code == 403:
        raise Exception("O SofaScore bloqueou temporariamente o IP do servidor (Erro 403 - Cloudflare). Tente novamente em instantes.")
    else:
        raise Exception(f"Erro na API do SofaScore: Status {resposta.status_code}")
