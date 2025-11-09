#!/usr/bin/env python3

"""
Script para encontrar os "Jogos-Chave" (Hubs e Pontes) na rede de
similaridade Jaccard, usando o mapa de comunidades.

VERSÃO 2.0: Usa GRAU PONDERADO (soma dos pesos Jaccard) para
encontrar "hubs" e evitar o ruído de jogos-spam.
"""

import networkx as nx
import pandas as pd
import time
import sys
from collections import defaultdict

# --- CONFIGURAÇÕES ---
# 1. Arquivos de entrada
GRAPH_FILE = "grafo_jaccard.txt"
COMUNIDADES_FILE = "comunidades.csv"
METADATA_FILE = "../entrega-parcial/steam.csv" # Usado para nomes

# 2. IDs das 5 maiores comunidades (do seu output)
COMUNIDADES_PARA_HUBS = [5, 0, 15, 8, 2]

# 3. IDs das duas maiores comunidades para encontrar pontes
COMM_A_ID = 5
COMM_B_ID = 0

# 4. Quantos jogos mostrar
TOP_N_HUBS = 3
TOP_N_BRIDGES = 5
# --- FIM DAS CONFIGURAÇÕES ---


def load_data_and_graph(graph_path, comunidades_path, metadata_path):
    """Carrega todos os dados necessários."""
    
    print("Carregando dados...")
    
    # --- 1. Carregar Grafo Jaccard (TXT) ---
    start_time = time.time()
    G = nx.Graph()
    try:
        with open(graph_path, 'r', encoding='utf-8') as f:
            next(f) # Pular cabeçalho
            for line in f:
                try:
                    u, v, w = line.strip().split()
                    G.add_edge(u, v, weight=float(w))
                except (ValueError, EOFError):
                    continue
    except FileNotFoundError:
        print(f"ERRO: Arquivo de grafo '{graph_path}' não encontrado.")
        sys.exit(1)
    
    print(f"Grafo Jaccard carregado em {time.time() - start_time:.2f}s ({G.number_of_nodes()} nós, {G.number_of_edges()} arestas)")

    # --- 2. Carregar Comunidades (CSV) ---
    try:
        df_comunidades = pd.read_csv(comunidades_path, dtype={'appid': str, 'community_id': int})
        community_map = df_comunidades.set_index('appid')['community_id'].to_dict()
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{comunidades_path}' não encontrado.")
        sys.exit(1)
        
    # --- 3. Carregar Metadados (CSV) ---
    try:
        df_metadata = pd.read_csv(metadata_path, dtype={'appid': str})
        df_metadata['appid_str'] = df_metadata['appid'].astype(str)
        id_to_name = df_metadata.set_index('appid_str')['name'].to_dict()
        id_to_name = defaultdict(lambda: "Nome Desconhecido", id_to_name)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{metadata_path}' não encontrado.")
        sys.exit(1)
        
    print("Todos os dados carregados.")
    return G, community_map, id_to_name

def find_hubs(G, community_map, id_to_name, community_ids, top_n):
    """Encontra os jogos mais centrais (hubs) DENTRO de cada comunidade."""
    
    print("\n--- 1. ENCONTRANDO 'HUBS' (USANDO GRAU PONDERADO) ---")
    
    for cid in community_ids:
        print(f"\nAnalisando Comunidade {cid}...")
        
        nodes_in_comm = [node for node, comm_id in community_map.items() if comm_id == cid and node in G]
        
        if not nodes_in_comm:
            print(f"  Nenhum jogo encontrado para a Comunidade {cid} no grafo.")
            continue
            
        G_comm = G.subgraph(nodes_in_comm)
        
        # %%%%%%%%%%%%%%%%%% MUDANÇA PRINCIPAL AQUI %%%%%%%%%%%%%%%%%%
        # Em vez de G_comm.degree() (contagem de arestas),
        # usamos a soma dos pesos (Jaccard) das arestas.
        internal_degrees = G_comm.degree(weight='weight')
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        top_hubs = sorted(internal_degrees, key=lambda x: x[1], reverse=True)[:top_n]
        
        print(f"Top {top_n} 'Hubs' (maior soma de pesos Jaccard) da Comunidade {cid}:")
        for node, degree in top_hubs:
            print(f"  - {id_to_name[node]} (ID: {node}) - Grau Ponderado: {degree:.4f}")

def find_bridges(G, community_map, id_to_name, comm_a_id, comm_b_id, top_n):
    """Encontra os 'jogos-ponte' entre duas comunidades."""

    print(f"\n--- 2. ENCONTRANDO 'JOGOS-PONTE' (BROKERS) ENTRE AS COMUNIDADES {comm_a_id} E {comm_b_id} ---")
    
    bridge_scores = []

    # Esta lógica de "ponte" ainda está OK, pois o score (A*B)
    # continuará a penalizar os jogos-spam que têm poucas conexões
    # com o cluster de jogos reais (C0).
    # (A saída anterior já mostrava isso: Viki Spotter tinha 3682 con. com C5 mas só 80 com C0)

    for u in G.nodes():
        u_comm = community_map.get(u)
        
        if u_comm not in [comm_a_id, comm_b_id]:
            continue
            
        connections_a = 0
        connections_b = 0
        
        for v in G.neighbors(u):
            v_comm = community_map.get(v)
            if v_comm == comm_a_id:
                connections_a += 1
            elif v_comm == comm_b_id:
                connections_b += 1
                
        if connections_a > 0 and connections_b > 0:
            score = connections_a * connections_b
            bridge_scores.append((u, score, u_comm, connections_a, connections_b))

    top_bridges = sorted(bridge_scores, key=lambda x: x[1], reverse=True)[:top_n]

    print(f"Top {top_n} 'Pontes' (jogos que conectam C{comm_a_id} e C{comm_b_id}):")
    for node, score, comm, con_a, con_b in top_bridges:
        print(f"\n  - {id_to_name[node]} (ID: {node})")
        print(f"    (Pertence à Comunidade {comm})")
        print(f"    Score (A*B): {score}")
        print(f"    Conexões com C{comm_a_id}: {con_a} | Conexões com C{comm_b_id}: {con_b}")

if __name__ == "__main__":
    G, c_map, id_map = load_data_and_graph(GRAPH_FILE, COMUNIDADES_FILE, METADATA_FILE)
    
    find_hubs(G, c_map, id_map, COMUNIDADES_PARA_HUBS, TOP_N_HUBS)
    
    find_bridges(G, c_map, id_map, COMM_A_ID, COMM_B_ID, TOP_N_BRIDGES)