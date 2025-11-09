#!/usr/bin/env python3

"""
Script para encontrar e interpretar triângulos frustrados (++-)
ligados a um jogo específico, usando os thresholds de "Alta Confiança".

Este script:
1. Carrega os metadados dos jogos (CSV) para mapear Nomes <-> IDs.
2. Carrega o grafo de sentimento ponderado (TXT).
3. Binariza o grafo usando os thresholds de "Alta Confiança" (1.5 e -1.5).
4. Pede ao usuário o nome de um jogo para investigar.
5. Encontra todos os triângulos (++-) conectados a esse jogo.
6. Imprime os triângulos encontrados, com os nomes dos jogos,
   para permitir uma interpretação real.
"""

import networkx as nx
import pandas as pd
import time
import sys
from collections import defaultdict, deque

# --- CONFIGURAÇÕES ---
# 1. Arquivo CSV com metadados dos jogos (appid, name, etc.)
CSV_METADATA = "../entrega-parcial/steam.csv"

# 2. Arquivo TXT do grafo de sentimento (u v peso)
GRAPH_FILE = "grafo_sentimento.txt"

# 3. Thresholds de "ALTA CONFIANÇA" (para explicar os 1.77% de frustração)
POS_THRESHOLD = 0.5
NEG_THRESHOLD = -0.5

# 4. Limite de triângulos para imprimir (para não lotar a tela)
PRINT_LIMIT = 20
# --- FIM DAS CONFIGURAÇÕES ---


def load_data(csv_path, graph_path, pos_thresh, neg_thresh):
    """Carrega o CSV e o grafo binarizado."""
    
    # --- 1. Carregar Metadados (CSV) ---
    print(f"Carregando metadados de '{csv_path}'...")
    try:
        df_games = pd.read_csv(CSV_METADATA)
        # Garantir que o appid seja string, para bater com os nós do grafo
        df_games['appid_str'] = df_games['appid'].astype(str)
        
        # Criar mapas para tradução
        # (usamos .lower() para facilitar a busca)
        name_to_id = pd.Series(df_games.appid_str.values, index=df_games.name.str.lower()).to_dict()
        
        # O id_to_name precisa ser um defaultdict
        id_to_name = pd.Series(df_games.name.values, index=df_games.appid_str).to_dict()
        id_to_name = defaultdict(lambda: "Nome Desconhecido", id_to_name)
        
        print(f"Metadados carregados. {len(id_to_name)} jogos no mapa.")
    except FileNotFoundError:
        print(f"ERRO: Arquivo CSV '{csv_path}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"ERRO ao carregar CSV: {e}")
        sys.exit(1)

    # --- 2. Carregar e Binarizar Grafo (TXT) ---
    print(f"Carregando e binarizando grafo de '{graph_path}'...")
    print(f"(Usando thresholds: Pos > {pos_thresh}, Neg < {neg_thresh})")
    start_time = time.time()
    G_bin = nx.Graph()
    try:
        with open(graph_path, 'r', encoding='utf-8') as f:
            next(f) # Pular cabeçalho
            for line in f:
                try:
                    u, v, w = line.strip().split()
                    weight = float(w)
                    
                    # Adiciona nós para garantir que o mapa de nomes funcione
                    G_bin.add_node(u)
                    G_bin.add_node(v)

                    if weight > pos_thresh:
                        G_bin.add_edge(u, v, sign=1)
                    elif weight < neg_thresh:
                        G_bin.add_edge(u, v, sign=-1)
                except (ValueError, EOFError):
                    continue # Ignora linhas mal formatadas
    except FileNotFoundError:
        print(f"ERRO: Arquivo de grafo '{graph_path}' não encontrado.")
        sys.exit(1)

    end_time = time.time()
    print(f"Grafo binarizado carregado em {end_time - start_time:.2f}s.")
    print(f"Nós: {G_bin.number_of_nodes()}, Arestas: {G_bin.number_of_edges()}")
    
    return G_bin, name_to_id, id_to_name


def find_frustrated_triangles(G_bin, id_to_name, root_node_id, limit):
    """Encontra e imprime triângulos ++- ligados ao 'root_node_id'."""
    
    if root_node_id not in G_bin:
        print(f"Erro: Jogo '{id_to_name[root_node_id]}' (ID: {root_node_id}) não encontrado no grafo binarizado.")
        print("Isso pode ser porque ele não tem nenhuma aresta de 'Alta Confiança'.")
        return

    root_name = id_to_name[root_node_id]
    print(f"\n--- 🔎 Investigando Triângulos Frustrados para: {root_name} ({root_node_id}) ---")
    
    frustrated_count = 0
    # Usamos deque para otimizar a iteração
    neighbors_u = deque(G_bin.neighbors(root_node_id))
    
    if len(neighbors_u) < 2:
        print("Este jogo não tem vizinhos suficientes (com Alta Confiança) para formar triângulos.")
        return

    # Iterar por todos os pares de vizinhos do nosso jogo-raiz (U)
    # U = root_node_id
    
    # Para evitar contar 2x (U-V-W e U-W-V), mantemos um set de pares já vistos
    seen_pairs = set()

    for v in neighbors_u:
        # V = Jogo Vizinho 1
        s_uv = G_bin[root_node_id][v]['sign'] # Sinal (U, V)
        
        # Agora procuramos vizinhos de V que também sejam vizinhos de U
        # Isso é mais rápido que combinations(neighbors_u, 2)
        for w in G_bin.neighbors(v):
            # W = Vizinho do Vizinho
            
            # 1. W não pode ser o nó raiz ou o próprio V
            if w == root_node_id or w == v:
                continue
                
            # 2. W precisa fechar o triângulo (ser vizinho de U)
            if G_bin.has_edge(root_node_id, w):
                
                # 3. Garantir que não contamos V-W e W-V
                pair = tuple(sorted((v, w)))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)

                # Temos um triângulo (U, V, W)! Vamos checar os sinais.
                s_uw = G_bin[root_node_id][w]['sign'] # Sinal (U, W)
                s_vw = G_bin[v][w]['sign']       # Sinal (V, W)
                
                # Checa a regra de frustração: ++-
                # Produto dos sinais é -1 E a soma é +1
                if (s_uv * s_uw * s_vw == -1) and (s_uv + s_uw + s_vw == 1):
                    # Encontramos um!
                    frustrated_count += 1
                    
                    # Imprimir (só os primeiros N, para não lotar a tela)
                    if frustrated_count <= limit:
                        name_v = id_to_name[v]
                        name_w = id_to_name[w]
                        
                        print(f"\nTriângulo #{frustrated_count} [TIPO: ++-]")
                        print(f"  Jogo U (Ponte): {root_name}")
                        print(f"  Jogo V:         {name_v}")
                        print(f"  Jogo W:         {name_w}")
                        print("  Lógica da Tensão:")
                        print(f"    ({root_name}, {name_v}) -> Sinal {s_uv}")
                        print(f"    ({root_name}, {name_w}) -> Sinal {s_uw}")
                        print(f"    ({name_v}, {name_w}) -> Sinal {s_vw}")

    if frustrated_count > limit:
        print(f"\n... e mais {frustrated_count - limit} outros triângulos frustrados.")
        
    print(f"\n--- ✅ Análise Concluída ---")
    print(f"Encontrados {frustrated_count} triângulos frustrados ('++-') envolvendo {root_name}.")


# --- Execução Principal ---
if __name__ == "__main__":
    G, name_map, id_map = load_data(CSV_METADATA, GRAPH_FILE, POS_THRESHOLD, NEG_THRESHOLD)
    
    if not G:
        sys.exit(1)
        
    print("\nDigite 'SAIR' a qualquer momento para fechar.")
    while True:
        try:
            game_name_input = input("\nDigite o nome (ou parte do nome) do jogo que deseja investigar: ").lower()
            
            if game_name_input == 'sair':
                break
                
            # Encontrar jogos que batem com a busca
            matches = {name: appid for name, appid in name_map.items() if game_name_input in name}
            
            if not matches:
                print("Nenhum jogo encontrado com esse nome. Tente novamente.")
                continue
            
            if len(matches) == 1:
                selected_name_lower = list(matches.keys())[0]
                selected_id = matches[selected_name_lower]
                find_frustrated_triangles(G, id_map, selected_id, PRINT_LIMIT)
            else:
                print("Múltiplos jogos encontrados. Qual você quer?")
                # Converte os IDs de volta para nomes reais para exibição
                display_matches = {appid: id_map[appid] for appid in matches.values()}
                
                # Lista para manter a ordem
                match_list = list(display_matches.items())
                
                for i, (appid, name) in enumerate(match_list):
                    if i >= 10: break # Limita a 10 opções
                    print(f"  {i+1}: {name} (ID: {appid})")
                
                choice = input(f"Digite um número (1-{min(len(match_list), 10)}): ")
                selected_id = match_list[int(choice)-1][0]
                find_frustrated_triangles(G, id_map, selected_id, PRINT_LIMIT)

        except (KeyboardInterrupt, EOFError):
            print("\nSaindo...")
            break
        except Exception as e:
            print(f"Ocorreu um erro: {e}")