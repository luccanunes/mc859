#!/usr/bin/env python3

"""
Script para detectar comunidades em um grafo de similaridade de jogos
usando o algoritmo Louvain.

Versão para grafos em formato TXT (edgelist).

Este script:
1. Carrega o Grafo de Similaridade Jaccard (de um arquivo .txt 'u v peso').
2. Executa o algoritmo Louvain (best_partition) para encontrar
   comunidades. Este algoritmo usa os pesos das arestas (o índice Jaccard)
   por padrão, o que é ideal.
3. Imprime um resumo (ex: número de comunidades encontradas).
4. Salva os resultados em um arquivo 'comunidades.csv' no formato:
   appid,community_id
"""

import networkx as nx
import community.community_louvain as community_louvain # Importa o submódulo correto
import pandas as pd
import time
import sys

# --- CONFIGURAÇÕES ---
# 1. Coloque o nome do seu arquivo .txt do Grafo Jaccard
GRAPH_FILE = "grafo_jaccard.txt" # ASSUMINDO ser este o nome

# 2. Nome do arquivo de saída
OUTPUT_FILE = "comunidades.csv"
# --- FIM DAS CONFIGURAÇÕES ---


def detect_communities(graph_path, output_path):
    """
    Função principal para carregar o grafo, rodar Louvain e salvar
    a partição de comunidades.
    """
    
    # --- 1. Carregar Grafo Jaccard (a partir de TXT Edgelist) ---
    print(f"Carregando grafo de '{graph_path}' (formato edgelist txt)...")
    start_time = time.time()
    G_jaccard = nx.Graph()
    lines_read = 0
    try:
        with open(graph_path, 'r', encoding='utf-8') as f:
            # Tentar pular a primeira linha (cabeçalho 'n m')
            try:
                next(f)
                lines_read = 1
            except StopIteration:
                print("Arquivo vazio.")
                sys.exit(1)
            except Exception:
                print("Cabeçalho 'n m' não encontrado. Lendo como edgelist pura.")
                f.seek(0) # Volta ao início
                lines_read = 0
            
            # Ler o restante das linhas (as arestas)
            for line in f:
                lines_read += 1
                try:
                    parts = line.strip().split()
                    if len(parts) == 3:
                        u, v, w = parts
                        # Adiciona a aresta com o peso (Jaccard)
                        G_jaccard.add_edge(u, v, weight=float(w))
                    elif len(parts) > 0:
                        print(f"Ignorando linha {lines_read} (formato inesperado): '{line.strip()}'")
                except (ValueError, EOFError):
                    print(f"Ignorando linha {lines_read} (erro de dados): '{line.strip()}'")

    except FileNotFoundError:
        print(f"ERRO: Arquivo '{graph_path}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao ler o arquivo: {e}")
        sys.exit(1)

    end_time = time.time()
    print(f"Grafo carregado em {end_time - start_time:.2f} segundos.")
    print(f"O grafo possui {G_jaccard.number_of_nodes()} nós (jogos) e {G_jaccard.number_of_edges()} arestas.")

    if G_jaccard.number_of_edges() == 0:
        print("ERRO: O grafo não tem arestas. Não é possível detectar comunidades.")
        sys.exit(1)

    # --- 2. Executar Algoritmo Louvain ---
    print("\nIniciando detecção de comunidades (algoritmo Louvain)...")
    print("Isso também pode demorar, aguarde...")
    start_time = time.time()
    
    # best_partition() usa os pesos ('weight') das arestas por padrão.
    # No seu caso, ele usará o Índice de Jaccard, o que é perfeito.
    partition = community_louvain.best_partition(G_jaccard)
    
    end_time = time.time()
    print(f"Detecção de comunidades concluída em {end_time - start_time:.2f} segundos.")

    # --- 3. Analisar e Salvar Resultados ---
    if not partition:
        print("ERRO: O algoritmo Louvain não retornou nenhuma partição.")
        sys.exit(1)

    # 'partition' é um dicionário: {'appid_1': 0, 'appid_2': 1, 'appid_100': 0}
    
    # Converter o dicionário para um DataFrame do Pandas
    df_comunidades = pd.DataFrame(partition.items(), columns=['appid', 'community_id'])
    
    # Contar o número de comunidades encontradas
    community_count = df_comunidades['community_id'].nunique()
    print(f"\n--- Resultado ---")
    print(f"O algoritmo encontrou {community_count} comunidades.")
    
    # Mostrar as 5 maiores comunidades
    print("\nTop 5 maiores comunidades (por número de jogos):")
    print(df_comunidades['community_id'].value_counts().head(5))

    # Salvar em CSV
    try:
        df_comunidades.to_csv(output_path, index=False)
        print(f"\nResultados salvos com sucesso em '{output_path}'!")
    except Exception as e:
        print(f"\nERRO ao salvar o arquivo CSV: {e}")

if __name__ == "__main__":
    detect_communities(GRAPH_FILE, OUTPUT_FILE)