
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def puxar_detalhes_do_jogo(id_jogo):
    """
    Busca os detalhes específicos do jogo (Árbitro, Estádio, etc)
     Usando o ID que pegamos no app.py
    """
    url = f"https://api.sofascore.com/api/v1/event/{id_jogo}"
    try:
        resposta = requests.get(url, headers=HEADERS)
        if resposta.status_code == 200:
            dados = resposta.json().get('event', {})
            
            # Extraindo informações do Árbitro
            arbitro_info = dados.get('referee', {})
            arbitro = {
                "nome": arbitro_info.get('name', 'Não informado'),
                "id": arbitro_info.get('id', None),
                "nacionalidade": arbitro_info.get('country', {}).get('name', 'N/A')
            }
            return {"arbitro": arbitro}
        return None
    except Exception:
        return None


def calcular_probabilidade_cartoes(id_arbitro):
    """
    Se o árbitro tiver um ID válido, buscamos o histórico dele na temporada
    para calcular a média e probabilidade de cartões.
    """
    if not id_arbitro:
        return {"media_amarelos": 0.0, "total_vermelhos": 0, "status": "Sem dados"}
        
    url = f"https://api.sofascore.com/api/v1/referee/{id_arbitro}/statistics"
    try:
        resposta = requests.get(url, headers=HEADERS)
        if resposta.status_code == 200:
            stats = resposta.json().get('statistics', {})
            
            # Dependendo da liga, o SofaScore quebra por temporada. Vamos pegar as médias gerais:
            cartoes_amarelos = float(stats.get('yellowCardsPerGame', 0))
            cartoes_vermelhos = int(stats.get('redCards', 0))
            jogos_apitados = int(stats.get('appearances', 0))
            
            # Definindo um índice de severidade do juiz
            if cartoes_amarelos > 4.5:
                tendencia = "🔥 Muito Rigoroso (Over Cartões)"
            elif cartoes_amarelos < 3.0:
                tendencia = "🍃 Maleável (Under Cartões)"
            else:
                tendencia = "⚖️ Padrão / Moderado"
                
            return {
                "media_amarelos": cartoes_amarelos,
                "total_vermelhos": cartoes_vermelhos,
                "jogos": jogos_apitados,
                "tendencia": tendencia
            }
        return {"media_amarelos": 0.0, "total_vermelhos": 0, "status": "Erro ao carregar estatísticas"}
    except Exception:
        return {"media_amarelos": 0.0, "total_vermelhos": 0, "status": "Erro de conexão"}


def analisar_gols_e_escanteios(id_jogo):
    """
    Busca o histórico recente dos dois times (Últimos jogos) 
    para calcular médias de Gols HT/FT e Escanteios.
    """
    # Nota: Para um sistema real, aqui nós puxamos o histórico de confrontos (H2H)
    url = f"https://api.sofascore.com/api/v1/event/{id_jogo}/h2h"
    try:
        resposta = requests.get(url, headers=HEADERS)
        if resposta.status_code == 200:
            dados = resposta.json()
            
            # Simulação de cálculo baseado no histórico H2H do SofaScore
            # Em sistemas avançados, varremos a lista de jogos anteriores calculando a média.
            # Vamos estruturar o retorno que alimentará nossos cards no Streamlit:
            analise = {
                "media_gols_marcados_casa": 1.75,  # Exemplo estatístico simulado provisoriamente
                "media_gols_sofridos_fora": 1.20,
                "probabilidade_gol_ht": "68%",
                "media_escanteios_jogo": 9.4
            }
            return analise
        return None
    except Exception:
        return None
