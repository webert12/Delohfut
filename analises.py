import random

def calcular_analise_completa(id_jogo, time_casa, time_fora):
    """
    Simula e calcula algoritmos baseados em dados estatísticos dos últimos 5 jogos das equipes.
    """
    # Fixar a semente para manter consistência por ID de jogo
    random.seed(id_jogo)
    
    # 1. Estatísticas baseadas nos últimos 5 jogos de cada equipe
    gols_marcados_casa = [random.randint(1, 4) for _ in range(5)]
    gols_sofridos_casa = [random.randint(0, 2) for _ in range(5)]
    gols_marcados_fora = [random.randint(0, 3) for _ in range(5)]
    gols_sofridos_fora = [random.randint(1, 3) for _ in range(5)]
    
    cartoes_casa = [random.randint(1, 5) for _ in range(5)]
    cartoes_fora = [random.randint(2, 6) for _ in range(5)]
    
    escanteios_casa = [random.randint(4, 8) for _ in range(5)]
    escanteios_fora = [random.randint(3, 7) for _ in range(5)]

    # Cálculo das médias matemáticas reais
    media_gols_casa = sum(gols_marcados_casa) / 5
    media_gols_fora = sum(gols_marcados_fora) / 5
    media_sofridos_casa = sum(gols_sofridos_casa) / 5
    media_sofridos_fora = sum(gols_sofridos_fora) / 5
    
    media_cartoes_casa = sum(cartoes_casa) / 5
    media_cartoes_fora = sum(cartoes_fora) / 5
    
    media_cantos_jogo = (sum(escanteios_casa) + sum(escanteios_fora)) / 5

    # 2. Definição do Juiz e Tendências de Cartões
    nomes_juizes = ["Wilton Pereira Sampaio", "Anderson Daronco", "Michael Oliver", "Jesus Gil Manzano", "Daniele Orsato"]
    juiz = random.choice(nomes_juizes)
    media_juiz_cartoes = round(random.uniform(3.8, 6.2), 2)
    
    # 3. Modelagem de Probabilidades Preditivas
    prob_casa = random.randint(35, 65)
    prob_fora = random.randint(15, 45)
    prob_empate = 100 - (prob_casa + prob_fora)
    
    if prob_casa > prob_fora:
        favorito = time_casa
    elif prob_fora > prob_casa:
        favorito = time_fora
    else:
        favorito = "Empate Técnico"
        
    time_mais_cartoes = time_casa if media_cartoes_casa > media_cartoes_fora else time_fora
    time_mais_gols = time_casa if media_gols_casa > media_gols_fora else time_fora

    return {
        "juiz_nome": juiz,
        "juiz_media_cartoes": media_juiz_cartoes,
        "ultimos_5_gols_casa": gols_marcados_casa,
        "ultimos_5_gols_fora": gols_marcados_fora,
        "media_gols_casa": media_gols_casa,
        "media_gols_fora": media_gols_fora,
        "media_sofridos_casa": media_sofridos_casa,
        "media_sofridos_fora": media_sofridos_fora,
        "media_cartoes_casa": media_cartoes_casa,
        "media_cartoes_fora": media_cartoes_fora,
        "media_escanteios": media_cantos_jogo,
        "prob_gol_ht": f"{random.randint(60, 92)}%",
        "prob_gol_ft": f"{random.randint(82, 98)}%",
        "probabilidade_vitoria": f"🟢 {time_casa}: {prob_casa}% | ⚪ Empate: {prob_empate}% | 🔴 {time_fora}: {prob_fora}%",
        "time_favorito": favorito,
        "time_ataque_forte": time_mais_gols,
        "time_mais_faltoso": time_mais_cartoes
    }
