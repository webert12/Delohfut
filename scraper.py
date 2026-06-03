import requests
from datetime import datetime, timedelta

def mapear_campeonato(nome_original):
    if not nome_original:
        return "⚽ Outros Confrontos"
        
    n = nome_original.lower().strip()
    
    # 🏆 Filtro Global da Copa do Mundo FIFA 2026 e Eliminatórias
    if "world cup" in n or "copa do mundo" in n or "fifa" in n:
        return "🏆 Copa do Mundo FIFA"
        
    # Continentais e Copas
    if "libertadores" in n:
        return "🏆 Copa Libertadores"
    if "sudamericana" in n or "sul-americana" in n:
        return "🌍 Copa Sul-Americana"
    if "copa do brasil" in n:
        return "🇧🇷 Copa do Brasil"
        
    # Brasil Série A e B
    if "brazil" in n or "brasileir" in n:
        if "série b" in n or "serie b" in n or "challenger" in n:
            return "🇧🇷 Brasileirão Série B"
        return "🇧🇷 Brasileirão Série A"
        
    # Ligas Internacionais Solicitadas
    if "saudi" in n or "arabia" in n or "saudita" in n:
        return "🇸🇦 Liga Saudita (Arábia Saudita)"
    if "spanish" in n or "laliga" in n or "españ" in n or "espanh" in n or "primera división" in n:
        return "🇪🇸 Campeonato Espanhol (LaLiga)"
    if "italian" in n or "serie a" in n:
        return "🇮🇹 Campeonato Italiano (Serie A)"
    if "bundesliga" in n or "german" in n or "alemã" in n:
        return "🇩🇪 Campeonato Alemão (Bundesliga)"
    if "french" in n or "ligue 1" in n or "franc" in n:
        return "🇫🇷 Campeonato Francês (Ligue 1)"
    if "portug" in n or "primeira liga" in n:
        return "🇵🇹 Campeonato Português (Liga Portugal)"
    if "argentin" in n:
        return "🇦🇷 Campeonato Argentino"
    if "norweg" in n or "eliteserien" in n or "norueg" in n:
        return "🇳🇴 Campeonato Norueguês (Eliteserien)"
        
    return "⚽ Outros Confrontos"

def buscar_jogos_do_dia(data_str=None):
    if data_str:
        data_espn = data_str.replace("-", "")
    else:
        data_espn = datetime.now().strftime("%Y%m%d")
        
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard?dates={data_espn}"
    jogos_formatados = []
    
    try:
        resposta = requests.get(url, timeout=10)
        if resposta.status_code != 200:
            return []
            
        dados = resposta.json()
        events = dados.get('events', [])
        
        for evento in events:
            # Try/Except interno: se um jogo falhar, o loop CONTINUA processando os outros jogos normalmente!
            try:
                competitions = evento.get('competitions', [])
                if not competitions:
                    continue
                competicao = competitions[0]
                
                # FILTRO PRÉ-JOGO: Apenas partidas futuras
                status_obj = competicao.get('status', {})
                estado_jogo = status_obj.get('type', {}).get('state', 'pre') 
                if estado_jogo != 'pre':
                    continue
                    
                leagues = evento.get('leagues', [])
                liga_obj = leagues[0] if leagues else {}
                campeonato_original = liga_obj.get('name', '')
                
                # Mapeamento inteligente por palavra-chave flexível
                campeonato_nome = mapear_campeonato(campeonato_original)
                
                competitors = competicao.get('competitors', [])
                time_casa = "Não definido"
                time_fora = "Não definido"
                
                for team_data in competitors:
                    if team_data.get('homeAway') == 'home':
                        time_casa = team_data.get('team', {}).get('name')
                    elif team_data.get('homeAway') == 'away':
                        time_fora = team_data.get('team', {}).get('name')
                
                # Conversão segura do Fuso Horário UTC -> Brasília
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
                    "campeonato": campeonato_nome,
                    "time_casa": time_casa,
                    "time_fora": time_fora,
                    "status": horario_brasilia
                })
            except Exception:
                continue # Pula o registro quebrado silenciosamente e mantém o resto do dia intacto
                
        return jogos_formatados
        
    except Exception:
        return []
