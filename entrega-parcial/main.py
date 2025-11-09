"""
Script completo para coleta de dados da Steam e construção de grafos de jogos.
(Versão refatorada para usar um dataset local em CSV como ponto de partida)

FLUXO DE TRABALHO:
1.  Lê um arquivo CSV da Steam (obtido do Kaggle) para obter uma lista base de jogos.
2.  Coleta reviews para cada jogo na lista, usando um sistema de cache em disco.
3.  Constrói três tipos de grafos com base nas avaliações em comum:
    - Grafo de Similaridade Jaccard
    - Grafo de Qualidade Média
    - Grafo de Sentimento
4.  Salva os grafos em formato .gexf, prontos para o Gephi.
"""

import requests
import time
import json
import os
import pandas as pd
from itertools import combinations
import networkx as nx
from typing import List, Tuple, Dict, Any, Set

# --- PARTE 0: CONFIGURAÇÕES GLOBAIS E CACHE ---

CACHE_DIR = "steam_data_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# --- PARTE 1: FUNÇÕES DE INTERAÇÃO COM A API (COM ROBUSTEZ) ---

def make_request_with_backoff(url: str, max_retries: int = 5, initial_backoff: float = 1.0) -> requests.Response | None:
    """
    Realiza uma requisição HTTP com uma estratégia de backoff exponencial para lidar com erros 429.
    """
    backoff_time = initial_backoff
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                print(f"\n  -> AVISO: Recebido erro 429 (Too Many Requests). Esperando {backoff_time:.2f} segundos...")
                time.sleep(backoff_time)
                backoff_time *= 2
            else:
                print(f"\n  -> ERRO: Recebido status {response.status_code} para {url}. Não tentarei novamente.")
                return None
        except requests.RequestException as e:
            print(f"\n  -> ERRO de Conexão: {e}. Esperando {backoff_time:.2f} segundos...")
            time.sleep(backoff_time)
            backoff_time *= 2
    
    print(f"\n  -> ERRO FATAL: Falha ao buscar URL após {max_retries} tentativas: {url}")
    return None

def collect_reviews_for_games(game_list: List[Tuple[int, str]], max_review_pages: int) -> Dict[int, Dict]:
    """Coleta reviews para uma lista de jogos, utilizando cache."""
    print("\n--- Iniciando Coleta de Reviews ---")
    reviews_by_game = {}
    for i, (appid, name) in enumerate(game_list):
        cache_path = os.path.join(CACHE_DIR, f"{appid}_reviews.json")
        print(f"({i+1}/{len(game_list)}) Verificando reviews para '{name}' ({appid})...")
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                reviews_by_game[appid] = json.load(f)
            print("  -> Encontrado no cache.")
        else:
            print("  -> Não está no cache. Baixando da API...")
            reviews_data = {}
            cursor = '*'
            for page_num in range(max_review_pages):
                print(f"\r    -> Baixando página {page_num + 1}/{max_review_pages}...", end="")
                url = (f"https://store.steampowered.com/appreviews/{appid}"
                       f"?json=1&num_per_page=100&cursor={cursor}&purchase_type=all&language=all")
                
                response = make_request_with_backoff(url)
                if not response: break

                data = response.json()
                if not data or not data.get('success') or not data.get('reviews'): break
                for rev in data['reviews']:
                    author_id = rev.get('author', {}).get('steamid')
                    if author_id:
                        reviews_data[author_id] = {'voted_up': rev.get('voted_up', False), 'weighted_vote_score': float(rev.get('weighted_vote_score', 0.0))}
                
                if data.get("query_summary") and data["query_summary"].get("total_reviews") and int(data["query_summary"]["total_reviews"]) < 100:
                    break
                cursor = data.get('cursor', '')
                if not cursor: break
                time.sleep(0.5)
            
            print(f"\r    -> Download concluído. Total de {len(reviews_data)} reviews coletadas.")
            if reviews_data:
                reviews_by_game[appid] = reviews_data
                with open(cache_path, 'w', encoding='utf-8') as f: json.dump(reviews_data, f)
    return reviews_by_game

# --- PARTE 2: FUNÇÕES DE CONSTRUÇÃO DOS GRAFOS ---

def build_graph_with_progress(graph_name: str, game_list: List[Tuple[int, str]], reviews: Dict, edge_logic_func):
    """Função genérica para construir um grafo mostrando o progresso."""
    print(f"\nConstruindo {graph_name}...")
    G = nx.Graph()
    valid_games = []
    for appid, name in game_list:
        if appid in reviews and reviews[appid]:
            G.add_node(appid, name=name)
            valid_games.append((appid, name))

    game_pairs = list(combinations(valid_games, 2))
    total_pairs = len(game_pairs)
    
    if total_pairs == 0:
        print("  -> Nenhum par de jogos com reviews para processar.")
        return G
        
    for i, ((id1, _), (id2, _)) in enumerate(game_pairs):
        if i % 1000 == 0 or i == total_pairs - 1:
            print(f"\r  -> Processando par {i+1}/{total_pairs} ({((i+1)/total_pairs)*100:.1f}%)", end="")
        edge_logic_func(G, id1, id2, reviews)

    print("\r" + " " * 70 + "\r", end="")
    print(f"  -> {graph_name} construído.")
    return G

def jaccard_edge_logic(G, id1, id2, reviews):
    """Lógica para adicionar aresta com peso Jaccard."""
    r1, r2 = set(reviews[id1].keys()), set(reviews[id2].keys())
    intersection, union = len(r1.intersection(r2)), len(r1.union(r2))
    if intersection > 0:
        G.add_edge(id1, id2, weight=intersection / union)

def weighted_score_edge_logic(G, id1, id2, reviews):
    """Lógica para adicionar aresta com peso de score médio."""
    common = set(reviews[id1].keys()).intersection(set(reviews[id2].keys()))
    if len(common) > 0:
        total_score = sum(reviews[id1][u]['weighted_vote_score'] + reviews[id2][u]['weighted_vote_score'] for u in common)
        avg_score = total_score / (2 * len(common))
        G.add_edge(id1, id2, weight=avg_score, common_users=len(common))

def sentiment_edge_logic(G, id1, id2, reviews):
    """Lógica para adicionar aresta com peso de sentimento."""
    common = set(reviews[id1].keys()).intersection(set(reviews[id2].keys()))
    if len(common) > 0:
        score = sum(1 if reviews[id1][u]['voted_up'] == reviews[id2][u]['voted_up'] else -1 for u in common)
        if score != 0:
            G.add_edge(id1, id2, weight=score, common_users=len(common))

# --- PARTE 3: EXECUÇÃO PRINCIPAL ---

if __name__ == "__main__":
    # --- PARÂMETROS DE CONFIGURAÇÃO ---
    # Caminho para o dataset CSV do Kaggle
    DATASET_PATH = 'steam.csv'
    
    # Limite o número de jogos do CSV para testes rápidos.
    # Defina como None para usar o dataset completo.
    LIMIT_GAMES = 30000  # Exemplo: processa apenas os primeiros 1000 jogos do CSV

    # Defina quantas páginas de reviews coletar para cada jogo (1 página = 100 reviews).
    MAX_REVIEW_PAGES_PER_GAME = 10
    # -------------------------------------

    # Etapa 1: Carregar a lista de jogos do arquivo CSV
    print(f"--- Etapa 1: Carregando jogos do dataset '{DATASET_PATH}' ---")
    try:
        df = pd.read_csv(DATASET_PATH)
        df.dropna(subset=['appid'], inplace=True)
        df['appid'] = df['appid'].astype(int)
        
        # Cria a lista de tuplas (appid, name) que o resto do script espera
        full_game_list = list(zip(df['appid'], df['name']))
        print(f"Dataset carregado com sucesso. Total de {len(full_game_list)} jogos encontrados.")

    except FileNotFoundError:
        print(f"ERRO: Dataset '{DATASET_PATH}' não encontrado. Verifique o caminho e o nome do arquivo.")
        exit()

    # Aplica o limite para testes, se definido
    if LIMIT_GAMES is not None:
        final_game_list = full_game_list[:LIMIT_GAMES]
        print(f"Aplicando limite de teste: Apenas os primeiros {len(final_game_list)} jogos serão processados.")
    else:
        final_game_list = full_game_list
    
    # Etapa 2: Coletar reviews para a lista final de jogos
    reviews_data = collect_reviews_for_games(final_game_list, MAX_REVIEW_PAGES_PER_GAME)
    
    # Etapa 3: Construir os três grafos
    print("\n--- Etapa 3: Construindo os grafos ---")
    graph_jaccard = build_graph_with_progress("Grafo Jaccard", final_game_list, reviews_data, jaccard_edge_logic)
    graph_score = build_graph_with_progress("Grafo Weighted Score", final_game_list, reviews_data, weighted_score_edge_logic)
    graph_sentiment = build_graph_with_progress("Grafo de Sentimento", final_game_list, reviews_data, sentiment_edge_logic)
    
    num_nodes_processed = len(final_game_list)
    print(f"\n--- Resumo dos Grafos Gerados ({num_nodes_processed} jogos processados) ---")
    print(f"Grafo Jaccard: {graph_jaccard.number_of_nodes()} nós, {graph_jaccard.number_of_edges()} arestas.")
    print(f"Grafo Weighted Score: {graph_score.number_of_nodes()} nós, {graph_score.number_of_edges()} arestas.")
    print(f"Grafo de Sentimento: {graph_sentiment.number_of_nodes()} nós, {graph_sentiment.number_of_edges()} arestas.")
    
    # Etapa 4: Salvar os grafos
    nx.write_gexf(graph_jaccard, f"grafo_jaccard_{num_nodes_processed}_nodes.gexf")
    nx.write_gexf(graph_score, f"grafo_score_{num_nodes_processed}_nodes.gexf")
    nx.write_gexf(graph_sentiment, f"grafo_sentimento_{num_nodes_processed}_nodes.gexf")
    
    print(f"\nSucesso! Grafos para {num_nodes_processed} jogos foram salvos em arquivos .gexf.")
    print("Você pode abri-los no Gephi para visualização e análise.")