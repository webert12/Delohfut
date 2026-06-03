import requests
from datetime import datetime, timedelta

def buscar_jogos_do_dia(data_str, liga_slug="all"):
    if data_str:
        data_espn = str(data_str).replace("-", "")
    else:
        data_espn = datetime.now().strftime("%Y%m%d")
        
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{liga_slug}/scoreboard?dates={data_espn}"
    jogos_formatados = []
    
    try:
        resposta = requests.get(url, timeout=10)
        if resposta.status_code != 200:
            return []
            
        dados = resposta.json()
        events = dados.get('events', [])
        
        for evento in events:
            try:
                competitions = evento.get('competitions', [])
                if not competitions:
                    continue
                competicao = competitions[0]
                
                # Filtra apenas partidas que não começaram (pré-jogo)
                status_obj = competicao.get('status', {})
                estado_jogo = status_obj.get('type', {}).get('state', 'pre') 
                if estado_jogo != 'pre':
                    continue
                
                competitors = competicao.get('competitors', [])
                time_casa = "Não definido"
                time_fora = "Não definido"
                
                for team_data in competitors:
                    if team_data.get('homeAway') == 'home':
                        time_casa = team_data.get('team', {}).get('name')
                    elif team_data.get('homeAway') == 'away':
                        time_fora = team_data.get('team', {}).get('name')
                
                # Fuso Horário UTC -> Brasília
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
                    "id": str(evento.get('id')),
                    "time_casa": time_casa,
                    "time_fora": time_fora,
                    "status": horario_brasilia
                })
            except Exception:
                continue
                
        return jogos_formatados
        
    except Exception:
        return []
