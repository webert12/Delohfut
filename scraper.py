import requests
from datetime import datetime, timedelta

# Dicionário mapeador estruturado para linkar a API com a sua lista fixa da tela
MAPA_CAMPEONATOS = {
    "fifa world cup": "🏆 Copa do Mundo FIFA",
    "world cup": "🏆 Copa do Mundo FIFA",
    "fifa world cup qualifying": "🏆 Copa do Mundo FIFA",
    "copa libertadores": "🏆 Copa Libertadores",
    "copa sudamericana": "🌍 Copa Sul-Americana",
    "brazilian série a": "🇧🇷 Brasileirão Série A",
    "brazilian serie a": "🇧🇷 Brasileirão Série A",
    "brazilian série b": "🇧🇷 Brasileirão Série B",
    "brazilian serie b": "🇧🇷 Brasileirão Série B",
    "brazilian challenger sn": "🇧🇷 Brasileirão Série B",
    "brazilian copa do brasil": "🇧🇷 Copa do Brasil",
    "saudi professional league": "🇸🇦 Liga Saudita (Arábia Saudita)",
    "spanish laliga": "🇪🇸 Campeonato Espanhol (LaLiga)",
    "spanish primera división": "🇪🇸 Campeonato Espanhol (LaLiga)",
    "italian serie a": "🇮🇹 Campeonato Italiano (Serie A)",
    "german bundesliga": "🇩🇪 Campeonato Alemão (Bundesliga)",
    "french ligue 1": "🇫🇷 Campeonato Francês (Ligue 1)",
    "portuguese primeira liga": "🇵🇹 Campeonato Português (Liga Portugal)",
    "argentine liga profesional de fútbol": "🇦🇷 Campeonato Argentino",
    "argentine primera división": "🇦🇷 Campeonato Argentino",
    "norwegian eliteserien": "🇳🇴 Campeonato Norueguês (Eliteserien)"
}

def buscar_jogos_do_dia(data_str=None):
    if data_str:
        data_espn = data_str.replace("-", "")
    else:
        data_espn = datetime.now().strftime("%Y%m%d")
        
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard?dates={data_espn}"
    
    try:
        resposta = requests.get(url, timeout=10)
        if resposta.status_code != 200:
            return []
            
        dados = resposta.json()
        events = dados.get('events', [])
        
        jogos_formatados = []
        for evento in events:
            competicao = evento.get('competitions', [{}])[0]
            
            # FILTRO PRÉ-JOGO: Descarta o que já começou ou terminou
            status_obj = competicao.get('status', {})
            estado_jogo = status_obj.get('type', {}).get('state', 'pre') 
            if estado_jogo != 'pre':
                continue
                
            campeonato_original = evento.get('leagues', [{}])[0].get('name', '').strip()
            
            # Se a liga não estiver no mapa solicitado, ela cai em "Outros Confrontos"
            campeonato_nome = MAPA_CAMPEONATOS.get(campeonato_original.lower(), "⚽ Outros Confrontos")
            
            competitors = competicao.get('competitors', [])
            time_casa = "Não definido"
            time_fora = "Não definido"
            
            for team_data in competitors:
                if team_data.get('homeAway') == 'home':
                    time_casa = team_data.get('team', {}).get('name')
                elif team_data.get('homeAway') == 'away':
                    time_fora = team_data.get('team', {}).get('name')
            
            # Ajuste de Fuso Horário (UTC para Brasília)
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
            
        return jogos_formatados
        
    except Exception:
        return []
