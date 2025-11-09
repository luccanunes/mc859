import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
from matplotlib.ticker import ScalarFormatter


# --- CONFIGURAÇÃO ---
GRAPH_FILE = "grafo_jaccard_27075_nodes.gexf" # Mude para o arquivo que deseja analisar

print(f"Carregando o grafo de '{GRAPH_FILE}'...")
G = nx.read_gexf(GRAPH_FILE)
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

# 3. Distribuição de Graus (Visualização Aprimorada)
degree_counts = Counter(graus)
grau, contagem = zip(*degree_counts.items())

plt.figure(figsize=(12, 8))
plt.scatter(grau, contagem, marker='.', s=20, alpha=0.7, label="Frequência do Grau")
plt.title('Distribuição de Graus do Grafo (Frequência vs. Grau)', fontsize=20)
plt.xlabel('Grau (k)', fontsize=15)
plt.ylabel('Frequência F(k) - Número de Vértices com Grau k', fontsize=15)
plt.xscale('log')
plt.yscale('log')
plt.grid(True, which="both", ls="--", linewidth=0.5)
plt.legend()
plt.savefig('distribuicao-graus-aprimorada.png', dpi=300, bbox_inches='tight')
print("\nGráfico aprimorado 'distribuicao-graus-aprimorada.png' foi salvo.")

# 4. Número de Componentes
componentes_conectadas = list(nx.connected_components(G))
num_componentes = len(componentes_conectadas)

print("\n--- Análise de Componentes ---")
print(f"Número de Componentes Conectadas: {num_componentes}")

# 5. Distribuição dos Tamanhos das Componentes (Visualização Aprimorada)
if num_componentes > 1:
    tamanhos_componentes = [len(c) for c in componentes_conectadas]
    tamanho_gigante = max(tamanhos_componentes)
    componentes_pequenas = [s for s in tamanhos_componentes if s < tamanho_gigante]
    
    print(f"Tamanho da maior componente (Componente Gigante): {tamanho_gigante} vértices")
    print(f"Número de componentes menores: {len(componentes_pequenas)}")
    
    if componentes_pequenas:
        distribuicao_tamanhos = Counter(componentes_pequenas)
        tamanho, contagem = zip(*sorted(distribuicao_tamanhos.items()))

        plt.figure(figsize=(12, 8))
        plt.bar(tamanho, contagem, width=1.0, edgecolor='black', alpha=0.8, label="Nº de Componentes")
        plt.title('Distribuição dos Tamanhos das Componentes (Excluindo a Gigante)', fontsize=20)
        plt.xlabel('Tamanho da Componente (k vértices)', fontsize=15)
        plt.ylabel('Frequência (Nº de componentes com tamanho k)', fontsize=15)
        plt.yscale('log')
        plt.xscale('log')
        
        # Melhora as marcações do eixo X para leitura em escala log
        ticks = [t for t in [1, 2, 3, 5, 10, 20, 50, 100, 200, 500] if t in tamanho]
        if not ticks or max(tamanho) > ticks[-1]:
             ticks.append(max(tamanho))
        plt.xticks(ticks)
        plt.gca().xaxis.set_major_formatter(ScalarFormatter())
        
        plt.grid(True, which="both", ls="--", linewidth=0.5)
        plt.legend()
        plt.savefig('distribuicao-componentes-aprimorada.png', dpi=300, bbox_inches='tight')
        print("Gráfico aprimorado 'distribuicao-componentes-aprimorada.png' foi salvo.")
    else:
        print("Não há componentes menores para plotar (o grafo é conexo ou só tem uma componente).")