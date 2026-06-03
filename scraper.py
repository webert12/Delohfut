import requests
from datetime import datetime, timedelta

# Dicionário de mapeamento oficial expandido com a Copa do Mundo
MAPA_CAMPEONATOS = {
    "fifa world cup": "🏆 Copa do Mundo FIFA",
    "world cup": "🏆 Copa Mundo FIFA",
    "fifa world cup qualifying": "🏆 Eliminatórias da Copa do Mundo",
    "copa libertadores": "🏆 Copa Libertadores",
    "copa sudamericana": "🌍 Copa Sul-Americana",
    "brazilian série a": "🇧🇷 Brasileirão Série A",
    "brazilian serie a": "🇧🇷 Brasileirão Série A",
    "brazilian série b": "🇧🇷 Brasileirão Série B",
    "brazilian serie b": "🇧🇷 Brasileirão Série B",
    "brazilian challenger sn": "🇧🇷 Brasileirão Série B",
    "brazilian copa do brasil": "🇧🇷 Copa do Brasil",
    "saudi professional league": "🇸🇦 Liga Saudita (Arabia Saudita)",
    "spanish laliga": "🇪🇸 Campeonato Espanhol (LaLiga)",
    "spanish primera división": "🇪🇸 Campeonato Espanhol (LaLiga)",
    "italian serie a": "🇮🇹 Campeonato Italiano (Serie A)",
    "german bundesliga": "🇩🇪 Campeonato Alemão (Bundesliga)",
    "german 2. bundesliga": "🇩🇪 Alemanha - 2. Bundesliga",
    "french ligue 1": "🇫🇷 Campeonato Francês (Ligue 1)",
    "portuguese primeira liga": "🇵🇹 Campeonato Português (Liga Portugal)",
    "argentine liga profesional de fútbol": "🇦🇷 Campeonato Argentino",
    "argentine primera división": "🇦🇷 Campeonato Argentino",
    "norwegian eliteserien": "🇳🇴 Campeonato Norueguês (Eliteserien)",
    "norwegian 1. divisjon": "🇳🇴 Campeonato Norueguês (1. Divisão)",
    "english premier league": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)",
    "uefa champions league": "🇪🇺 UEFA Champions League",
    "uefa europa league": "🇪🇺 UEFA Europa League"
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
            raise Exception(f"Erro na comunicação: Status {resposta.status_code}")
            
        dados = resposta.json()
        events = dados.get('events', [])
        
        jogos_formatados = []
        for evento in events:
            id_jogo = evento.get('id')
            competicao = evento.get('competitions', [{}])[0]
            
            # FILTRO PRÉ-JOGO: Apenas partidas futuras
            status_obj = competicao.get('status', {})
            estado_jogo = status_obj.get('type', {}).get('state', 'pre') 
            if estado_jogo != 'pre':
                continue
                
            campeonato_original = evento.get('leagues', [{}])[0].get('name', 'Outros Confrontos')
            campeonato_nome = MAPA_CAMPEONATOS.get(campeonato_original.lower(), campeonato_original)
            
            competitors = competicao.get('competitors', [])
            time_casa = "Não definido"
            time_fora = "Não definido"
            
            for team_data in competitors:
                if team_data.get('homeAway') == 'home':
                    time_casa = team_data.get('team', {}).get('name')
                elif team_data.get('homeAway') == 'away':
                    time_fora = team_data.get('team', {}).get('name')
            
            # Fuso Horário UTC para Brasília
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
        raise Exception(f"Erro ao conectar com a base de dados: {str(e)}")
