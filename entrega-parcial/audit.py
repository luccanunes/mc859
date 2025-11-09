import json
import os

# --- CONFIGURAÇÃO DA AUDITORIA ---
# Defina os AppIDs dos dois jogos que você quer verificar.
# Use um site como SteamDB para encontrar os AppIDs facilmente.

# Teste 1: Conexão Forte Esperada (Stardew Valley vs. Terraria)
APPID_1 = 413150  # Stardew Valley
NAME_1 = "Stardew Valley"
APPID_2 = 105600  # Terraria
NAME_2 = "Terraria"

# Teste 2: Conexão com Hub (CS2 vs. um jogo popular)
APPID_1 = 730     # Counter-Strike 2
NAME_1 = "Counter-Strike 2"
APPID_2 = 1172470 # Apex Legends
NAME_2 = "Apex Legends"

# Teste 3: Conexão Fraca/Inexistente (Euro Truck Simulator 2 vs. Hollow Knight)
APPID_1 = 227300  # Euro Truck Simulator 2
NAME_1 = "Euro Truck Simulator 2"
APPID_2 = 367520  # Hollow Knight
NAME_2 = "Hollow Knight"

CACHE_DIR = "steam_data_cache"

# -------------------------------------

def load_reviews_from_cache(appid: int) -> dict:
    """Carrega os dados de review para um único jogo a partir do cache."""
    cache_path = os.path.join(CACHE_DIR, f"{appid}_reviews.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"AVISO: Arquivo de cache para o AppID {appid} não encontrado.")
        return {}

# 1. Carregar os dados de review
print(f"Carregando reviews para '{NAME_1}' ({APPID_1}) e '{NAME_2}' ({APPID_2})...")
reviews1 = load_reviews_from_cache(APPID_1)
reviews2 = load_reviews_from_cache(APPID_2)

if not reviews1 or not reviews2:
    print("Não foi possível carregar os dados para um ou ambos os jogos. Abortando.")
    exit()

# 2. Encontrar os avaliadores em comum
reviewers1 = set(reviews1.keys())
reviewers2 = set(reviews2.keys())
common_reviewers = reviewers1.intersection(reviewers2)
num_common = len(common_reviewers)

print("\n--- ANÁLISE DA INTERSEÇÃO ---")
print(f"Avaliadores de '{NAME_1}': {len(reviewers1)}")
print(f"Avaliadores de '{NAME_2}': {len(reviewers2)}")
print(f"Avaliadores em Comum: {num_common}")

if num_common == 0:
    print("\nNão há avaliadores em comum. Nenhuma aresta deve existir entre esses jogos.")
    exit()

# 3. Calcular as métricas das arestas

# Métrica 1: Índice de Jaccard
union_reviewers = reviewers1.union(reviewers2)
jaccard_index = num_common / len(union_reviewers)

# Métrica 2: Média do Weighted Score
total_score = sum(reviews1[u]['weighted_vote_score'] + reviews2[u]['weighted_vote_score'] for u in common_reviewers)
avg_score = total_score / (2 * num_common)

# Métrica 3: Score de Sentimento
sentiment_score = sum(1 if reviews1[u]['voted_up'] == reviews2[u]['voted_up'] else -1 for u in common_reviewers)

print("\n--- MÉTRICAS DA ARESTA CALCULADAS ---")
print(f"Peso do Grafo Jaccard: {jaccard_index:.6f}")
print(f"Peso do Grafo Weighted Score: {avg_score:.6f}")
print(f"Peso do Grafo de Sentimento: {sentiment_score}")