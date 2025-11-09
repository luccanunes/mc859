import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter

# --- CONFIGURAÇÃO ---
# Escolha qual dos seus grafos .gexf você quer analisar
GRAPH_FILE = "grafo_jaccard_27075_nodes.gexf" # Mude para o arquivo que deseja analisar

print(f"Carregando o grafo de '{GRAPH_FILE}'...")
# Carrega o grafo do arquivo
G = nx.read_gexf(GRAPH_FILE)
# Os nós são strings no GEXF, convertemos para int para consistência se necessário
# G = nx.relabel_nodes(G, {node: int(node) for node in G.nodes()})
print("Grafo carregado com sucesso.")

# --- Análise e Geração de Dados ---

# 2. Tamanho do Grafo
num_vertices = G.number_of_nodes()
num_arestas = G.number_of_edges()
graus = [d for n, d in G.degree()]
grau_medio = np.mean(graus)

print("\n--- Métricas Básicas ---")
print(f"Número de Vértices: {num_vertices}")
print(f"Número de Arestas: {num_arestas}")
print(f"Grau Médio dos Vértices: {grau_medio:.2f}")

# 3. Distribuição de Graus
plt.figure(figsize=(12, 7))
sns.histplot(graus, bins=50, kde=False)
plt.title('Distribuição de Graus do Grafo', fontsize=20)
plt.xlabel('Grau (Número de Conexões)', fontsize=15)
plt.ylabel('Número de Vértices', fontsize=15)
plt.xscale('log') # Escala logarítmica é essencial para ver a cauda longa
plt.yscale('log')
plt.grid(True, which="both", ls="--", linewidth=0.5)
plt.savefig('distribuicao_graus.png')
print("\nGráfico 'distribuicao_graus.png' foi salvo.")

# 4. Número de Componentes
componentes_conectadas = list(nx.connected_components(G))
num_componentes = len(componentes_conectadas)

print("\n--- Análise de Componentes ---")
print(f"Número de Componentes Conectadas: {num_componentes}")

# 5. Distribuição dos Tamanhos das Componentes
if num_componentes > 1:
    tamanhos_componentes = [len(c) for c in componentes_conectadas]
    tamanhos_componentes.sort(reverse=True)
    
    print(f"Tamanho da maior componente (Componente Gigante): {tamanhos_componentes[0]} vértices")
    if len(tamanhos_componentes) > 1:
        print(f"Tamanho da segunda maior componente: {tamanhos_componentes[1]} vértices")

    # Conta a frequência de cada tamanho de componente
    distribuicao_tamanhos = Counter(tamanhos_componentes)
    
    plt.figure(figsize=(12, 7))
    plt.bar(distribuicao_tamanhos.keys(), distribuicao_tamanhos.values(), width=1.0)
    plt.title('Distribuição dos Tamanhos das Componentes', fontsize=20)
    plt.xlabel('Tamanho da Componente (k vértices)', fontsize=15)
    plt.ylabel('Frequência (Quantas componentes com tamanho k)', fontsize=15)
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, which="both", ls="--", linewidth=0.5)
    plt.savefig('distribuicao_componentes.png')
    print("Gráfico 'distribuicao_componentes.png' foi salvo.")