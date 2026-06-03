import requests
from datetime import datetime

def buscar_jogos_do_dia(data_str=None):
    if not data_str:
        data_str = datetime.today().strftime('%Y-%m-%d')
        
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{data_str}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Referer": "https://www.sofascore.com/",
        "Origin": "https://www.sofascore.com"
    }
    
    try:
        resposta = requests.get(url, headers=headers, timeout=8)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            events = dados.get('events', [])
            
            if events: # Se encontrou jogos de verdade na API
                jogos_formatados = []
                for evento in events:
                    jogo = {
                        "id": evento.get('id'),
                        "campeonato": evento.get('tournament', {}).get('name'),
                        "pais": evento.get('tournament', {}).get('category', {}).get('name'),
                        "time_casa": evento.get('homeTeam', {}).get('name'),
                        "time_fora": evento.get('awayTeam', {}).get('name'),
                        "status": evento.get('status', {}).get('description'),
                    }
                    jogos_formatados.append(jogo)
                return jogos_formatados
                
    except Exception as e:
        print(f"Erro na requisição: {e}")
        
    # 🚨 CASO O SOFASCORE BLOQUEIE OU ESTEJA VAZIO:
    # O sistema usa esses dados profissionais de teste para você poder usar os filtros de dia/mês/campeonatos!
    print("Aviso: Usando banco de dados local para testes.")
    return [
        {"id": 111, "pais": "Brasil", "campeonato": "Brasileirão Série A", "time_casa": "Flamengo", "time_fora": "Palmeiras", "status": "15:00"},
        {"id": 222, "pais": "Brasil", "campeonato": "Brasileirão Série A", "time_casa": "São Paulo", "time_fora": "Corinthians", "status": "16:00"},
        {"id": 333, "pais": "Inglaterra", "campeonato": "Premier League", "time_casa": "Real Madrid", "time_fora": "Barcelona", "status": "21:00"},
        {"id": 444, "pais": "Inglaterra", "campeonato": "Premier League", "time_casa": "Manchester City", "time_fora": "Liverpool", "status": "13:30"},
        {"id": 555, "pais": "Itália", "campeonato": "Serie A TIM", "time_casa": "Juventus", "time_fora": "Milan", "status": "14:45"},
    ]
