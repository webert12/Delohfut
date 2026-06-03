import requests
from datetime import datetime

def buscar_jogos_do_dia(data_str=None):
    """
    Busca os jogos do dia direto da API interna do SofaScore.
    Formato da data esperado: 'YYYY-MM-DD'
    """
    if not data_str:
        data_str = datetime.today().strftime('%Y-%m-%d')
        
    # URL da API interna do SofaScore para os jogos do dia
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{data_str}"
    
    # Headers necessários para simular um navegador real e evitar bloqueios
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resposta = requests.get(url, headers=headers)
        if resposta.status_code == 200:
            dados = resposta.json()
            jogos_formatados = []
            
            # Filtrando e organizando o que nos interessa
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
            print(f"Erro ao acessar SofaScore: Status {resposta.status_code}")
            return []
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return []
