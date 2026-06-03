import requests
from datetime import datetime, timedelta

def buscar_jogos_do_dia(data_str=None):
    # Converte o formato do calendário (YYYY-MM-DD) para o padrão da API (YYYYMMDD)
    if data_str:
        data_espn = data_str.replace("-", "")
    else:
        data_espn = datetime.now().strftime("%Y%m%d")
        
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard?dates={data_espn}"
    
    try:
        resposta = requests.get(url, timeout=10)
        if resposta.status_code != 200:
            raise Exception(f"Erro na comunicação: Status {resposta.status_code}")
            
        dados = resposta.json()
        events = dados.get('events', [])
        
        jogos_formatados = []
        for evento in events:
            id_jogo = evento.get('id')
            competicao = evento.get('competitions', [{}])[0]
            
            # 🚫 FILTRO DE SEGURANÇA: Descarta jogos ao vivo ('in') ou finalizados ('post')
            status_obj = competicao.get('status', {})
            estado_jogo = status_obj.get('type', {}).get('state', 'pre') 
            
            if estado_jogo != 'pre':
                continue # Ignora completamente e pula para o próximo
                
            campeonato_nome = evento.get('leagues', [{}])[0].get('name', 'Outros Confrontos')
            
            competitors = competicao.get('competitors', [])
            time_casa = "Não definido"
            time_fora = "Não definido"
            
            for team_data in competitors:
                if team_data.get('homeAway') == 'home':
                    time_casa = team_data.get('team', {}).get('name')
                elif team_data.get('homeAway') == 'away':
                    time_fora = team_data.get('team', {}).get('name')
            
            # Trata o fuso horário UTC da API para o Horário de Brasília (UTC-3)
            data_utc_str = competicao.get('date', '') 
            horario_brasilia = "--:--"
            if data_utc_str:
                try:
                    dt_utc = datetime.strptime(data_utc_str, "%Y-%m-%dT%H:%MZ")
                    dt_br = dt_utc - timedelta(hours=3)
                    horario_brasilia = dt_br.strftime('%H:%M')
                except:
                    horario_brasilia = status_obj.get('type', {}).get('shortDetail', '--:--')

            jogos_formatados.append({
                "id": str(id_jogo),
                "campeonato": campeonato_nome,
                "time_casa": time_casa,
                "time_fora": time_fora,
                "status": horario_brasilia
            })
            
        return jogos_formatados
        
    except Exception as e:
        raise Exception(f"Erro ao conectar com a base de dados esportiva: {str(e)}")
