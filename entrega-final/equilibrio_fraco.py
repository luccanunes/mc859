#!/usr/bin/env python3

"""
Script para Análise de Equilíbrio Estrutural Fraco (Contagem de Triângulos)
em uma rede de sentimento de jogos da Steam.

Este script:
1. Carrega um grafo a partir de um arquivo .txt no formato edgelist:
   Linha 1: n m (número de nós, número de arestas)
   Linhas seguintes: u v peso (onde 'peso' é a soma dos sentimentos, ex: +50, -20)
2. "Binariza" o grafo, convertendo pesos em arestas +1 (aliança) e -1 (polarização)
   com base em limiares (thresholds).
3. Itera por todos os triângulos no grafo binarizado.
4. Conta a proporção de triângulos "frustrados" do tipo (++-).
5. Reporta a "proporção de frustração", que indica se a rede é "clusterizável".
"""

import networkx as nx
from itertools import combinations
import time

# --- CONFIGURAÇÕES ---
# 1. Coloque o nome do seu arquivo .txt aqui
GRAPH_FILE = "grafo_sentimento.txt"

# 2. Defina seus limiares (thresholds)
#    VOCÊ PRECISA MUDAR ESTES VALORES COM BASE NA ANÁLISE ESTATÍSTICA
#    DOS SEUS DADOS (ex: usando percentis 90% e 10%).
#    Os valores abaixo são apenas exemplos.
POS_THRESHOLD = 1.5  # Peso acima do qual a aresta vira +1 (forte alinhamento)
NEG_THRESHOLD = -1.5  # Peso abaixo do qual a aresta vira -1 (forte polarização)
# --- FIM DAS CONFIGURAÇÕES ---


def analyze_weak_balance(graph_path, pos_thresh, neg_thresh):
    """
    Função principal que carrega o grafo, binariza e conta os triângulos.
    """
    
    # --- 1. Carregar Grafo (a partir de TXT Edgelist Ponderado) ---
    print(f"Carregando grafo de '{graph_path}' (formato edgelist txt)...")
    G_sentiment = nx.Graph()
    lines_read = 0
    try:
        with open(graph_path, 'r', encoding='utf-8') as f:
            # Tentar ler a primeira linha (n m)
            try:
                first_line = next(f).strip()
                n, m = map(int, first_line.split())
                print(f"Informação do cabeçalho: {n} nós, {m} arestas esperadas.")
                lines_read += 1
            except (ValueError, StopIteration):
                print("Cabeçalho 'n m' não encontrado. Lendo como edgelist pura.")
                f.seek(0) # Volta ao início do arquivo
            
            # Ler o restante das linhas (as arestas)
            for line in f:
                lines_read += 1
                try:
                    parts = line.strip().split()
                    if len(parts) == 3:
                        u, v, w = parts
                        # Adiciona a aresta com o peso original
                        G_sentiment.add_edge(u, v, weight=float(w))
                    elif len(parts) > 0:
                        print(f"Ignorando linha {lines_read} (formato inesperado): '{line.strip()}'")
                except (ValueError, EOFError):
                    print(f"Ignorando linha {lines_read} (erro de dados): '{line.strip()}'")

    except FileNotFoundError:
        print(f"ERRO: Arquivo '{graph_path}' não encontrado.")
        return
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao ler o arquivo: {e}")
        return
    
    print(f"Grafo ponderado carregado com {G_sentiment.number_of_nodes()} nós e {G_sentiment.number_of_edges()} arestas.")

    # --- 2. Binarizar Grafo ---
    print(f"\nBinarizando grafo com thresholds: Positivo > {pos_thresh}, Negativo < {neg_thresh}")
    G_bin = nx.Graph() # Criar um novo grafo binarizado (só com +1 e -1)

    for u, v, data in G_sentiment.edges(data=True):
        weight = data.get('weight', 0)
        
        G_bin.add_node(u) # Garante que nós isolados sejam mantidos
        G_bin.add_node(v)
        
        if weight > pos_thresh:
            G_bin.add_edge(u, v, sign=1)  # Aresta positiva
        elif weight < neg_thresh:
            G_bin.add_edge(u, v, sign=-1) # Aresta negativa
        # Arestas entre [NEG_THRESHOLD, POS_THRESHOLD] são ignoradas (ruído).

    print(f"Grafo binarizado (sinais) criado com {G_bin.number_of_nodes()} nós e {G_bin.number_of_edges()} arestas.")
    if G_bin.number_of_edges() == 0:
        print("AVISO: Grafo binarizado não tem arestas. Seus thresholds estão muito altos!")
        return

    # --- 3. Contagem de Triângulos ---
    print("\nIniciando contagem de triângulos...")
    print("!!! ATENÇÃO: Esta etapa pode demorar MUITO (horas ou dias) !!!")
    start_time = time.time()

    counts = {
        '+++': 0, '++-': 0, '+--': 0, '---': 0
    }

    nodes_processed = 0
    total_nodes = G_bin.number_of_nodes()
    
    for u in G_bin.nodes():
        neighbors_u = list(G_bin.neighbors(u))
        if len(neighbors_u) < 2:
            continue
            
        for v, w in combinations(neighbors_u, 2):
            if G_bin.has_edge(v, w):
                
                # Garante que cada triângulo seja contado apenas UMA vez
                if str(u) > str(v) or str(v) > str(w):
                     continue

                s_uv = G_bin[u][v]['sign']
                s_uw = G_bin[u][w]['sign']
                s_vw = G_bin[v][w]['sign']
                
                product = s_uv * s_uw * s_vw
                
                if product == 1: # Sinais: +++ ou +--
                    if s_uv + s_uw + s_vw > 0: counts['+++'] += 1
                    else: counts['+--'] += 1
                else: # Sinais: ++- ou ---
                    if s_uv + s_uw + s_vw > 0: counts['++-'] += 1
                    else: counts['---'] += 1

        nodes_processed += 1
        if nodes_processed % 1000 == 0:
            print(f"... processados {nodes_processed} / {total_nodes} nós ...")


    end_time = time.time()
    print(f"\nContagem de triângulos concluída em {end_time - start_time:.2f} segundos.")

    # --- 4. Resultados ---
    total_triangulos = sum(counts.values())

    if total_triangulos == 0:
        print("\nNenhum triângulo encontrado no grafo binarizado.")
        print("Tente ajustar os THRESHOLDS para incluir mais arestas.")
    else:
        # A frustração do equilíbrio fraco é a proporção de triângulos "++-"
        frustration_ratio_weak = counts['++-'] / total_triangulos

        print("\n--- Resultado (Equilíbrio Fraco) ---")
        print(f"Thresholds usados: Pos > {pos_thresh}, Neg < {neg_thresh}")
        print(f"Total de Triângulos encontrados: {total_triangulos}")
        print(f"   Balanceados (+++): {counts['+++']}")
        print(f"   Balanceados (+--): {counts['+--']}")
        print(f"   Balanceados (---): {counts['---']} (só frustrado no sentido 'forte')")
        print(f"   FRUSTRADOS (++-): {counts['++-']}")
        
        print("\n========================================================")
        print(f" Proporção de Frustração (Fraca) [++- / Total]: {frustration_ratio_weak:.6f}")
        print("========================================================")

        if frustration_ratio_weak < 0.05:
            print("Interpretação: Rede altamente equilibrada!")
        elif frustration_ratio_weak < 0.2:
            print("Interpretação: Rede 'quase' equilibrada.")
        else:
            print("Interpretação: Rede caótica!")


if __name__ == "__main__":
    analyze_weak_balance(GRAPH_FILE, POS_THRESHOLD, NEG_THRESHOLD)