import requests
from datetime import datetime

def buscar_jogos_do_dia(data_str=None):
    # Converte o formato do Streamlit (YYYY-MM-DD) para o formato da ESPN (YYYYMMDD)
    if data_str:
        data_espn = data_str.replace("-", "")
    else:
        data_espn = datetime.now().strftime("%Y%m%d")
        
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard?dates={data_espn}"
    
    try:
        resposta = requests.get(url, timeout=10)
        if resposta.status_code != 200:
            raise Exception(f"Erro na comunicação com a ESPN: Status {resposta.status_code}")
            
        dados = resposta.json()
        events = dados.get('events', [])
        
        jogos_formatados = []
        for evento in events:
            id_jogo = evento.get('id')
            competicao = evento.get('competitions', [{}])[0]
            campeonato_nome = evento.get('leagues', [{}])[0].get('name', 'Outros Confrontos')
            
            # Identificar Time da Casa e Visitante
            competitors = competicao.get('competitors', [])
            time_casa = "Não definido"
            time_fora = "Não definido"
            
            for team_data in competitors:
                if team_data.get('homeAway') == 'home':
                    time_casa = team_data.get('team', {}).get('name')
                elif team_data.get('homeAway') == 'away':
                    time_fora = team_data.get('team', {}).get('name')
            
            # Extrair Horário ou Status em Tempo Real
            status_jogo = competicao.get('status', {}).get('type', {}).get('shortDetail', '--:--')
            
            jogos_formatados.append({
                "id": str(id_jogo),
                "campeonato": campeonato_nome,
                "pais": "Futebol Profissional",
                "time_casa": time_casa,
                "time_fora": time_fora,
                "status": status_jogo
            })
            
        return jogos_formatados
        
    except Exception as e:
        raise Exception(f"Erro ao conectar com a base de dados esportiva: {str(e)}")
