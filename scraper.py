import requests
from datetime import datetime

def buscar_jogos_do_dia(data_str=None):
    if not data_str:
        data_str = datetime.today().strftime('%Y-%m-%d')
        
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{data_str}"
    
    # Headers profissionais muito mais completos para evitar o travamento/bloqueio
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        "Referer": "https://www.sofascore.com/",
        "Origin": "https://www.sofascore.com",
        "Cache-Control": "max-age=0"
    }
    
    try:
        # Colocamos um timeout de 10 segundos. Se o site travar, o código não fica rodando infinito
        resposta = requests.get(url, headers=headers, timeout=10)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            jogos_formatados = []
            
            for evento in dados.get('events', []):
                jogo = {
                    "id": evento.get('id'),
                    "campeonato": evento.get('tournament', {}).get('name'),
                    "pais": evento.get('tournament', {}).get('category', {}).get('name'),
                    "time_casa": evento.get('homeTeam', {}).get('name'),
                    "time_fora": evento.get('awayTeam', {}).get('name'),
                    "placar_casa": evento.get('homeScore', {}).get('current'),
                    "placar_fora": evento.get('awayScore', {}).get('current'),
                    "status": evento.get('status', {}).get('description'),
                    "slug": evento.get('slug')
                }
                jogos_formatados.append(jogo)
            return jogos_formatados
        else:
            print(f"Erro SofaScore: Status {resposta.status_code}")
            return []
    except Exception as e:
        print(f"Erro crítico de conexão: {e}")
        return []
