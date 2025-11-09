#!/usr/bin/env python3

"""
Script para analisar a distribuição de pesos de um grafo em formato edgelist.

Este script:
1. Lê um arquivo .txt (ex: 'u v peso') linha por linha.
2. Armazena apenas os pesos em um array.
3. Calcula estatísticas descritivas (média, mediana, min, max).
4. Calcula percentis (quantis) para ajudar a definir os thresholds.

Como usar:
1. Tenha a biblioteca numpy instalada: pip install numpy
2. Coloque o nome do seu arquivo .txt na variável 'GRAPH_FILE'.
3. Execute o script: python analise_pesos.py
"""

import numpy as np
import time
import sys

# --- CONFIGURAÇÃO ---
# 1. Coloque o nome do seu arquivo .txt aqui
GRAPH_FILE = "grafo_sentimento.txt"
# --- FIM DA CONFIGURAÇÃO ---


def analyze_weights(graph_path):
    """
    Função principal que carrega os pesos e calcula as estatísticas.
    """
    
    print(f"Iniciando análise de pesos de '{graph_path}'...")
    print("Isso pode demorar alguns minutos se o arquivo for muito grande.")
    
    weights = []
    lines_read = 0
    start_time = time.time()

    # --- 1. Ler os pesos do arquivo ---
    try:
        with open(graph_path, 'r', encoding='utf-8') as f:
            # Tentar pular a primeira linha (cabeçalho 'n m')
            try:
                next(f)
                lines_read = 1
            except StopIteration:
                print("Arquivo vazio.") # Arquivo está vazio
                return
            except Exception as e:
                print(f"Erro ao pular cabeçalho (pode não ser um problema): {e}")
                f.seek(0) # Resetar se a leitura falhar (ex: não era 'n m')
                lines_read = 0

            # Ler o restante das linhas (as arestas)
            for line in f:
                lines_read += 1
                try:
                    parts = line.strip().split()
                    if len(parts) == 3:
                        # Adiciona o peso (terceira coluna) à lista
                        weights.append(float(parts[2]))
                    
                    if lines_read % 1000000 == 0:
                        print(f"... {lines_read // 1000000} milhão de linhas lidas ...")
                        
                except (ValueError, IndexError):
                    print(f"Ignorando linha {lines_read} (formato inesperado): '{line.strip()}'")
                except Exception as e:
                    print(f"Erro inesperado na linha {lines_read}: {e}")

    except FileNotFoundError:
        print(f"ERRO: Arquivo '{graph_path}' não encontrado.")
        sys.exit(1) # Sair do script com erro
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao ler o arquivo: {e}")
        sys.exit(1)

    end_time = time.time()
    print(f"Leitura concluída em {end_time - start_time:.2f} segundos.")
    
    if not weights:
        print("Nenhum peso foi carregado. Verifique o formato do arquivo.")
        return

    # --- 2. Calcular Estatísticas com NumPy ---
    print("Calculando estatísticas com NumPy...")
    try:
        weights_array = np.array(weights)
        del weights # Liberar memória da lista original

        # Estatísticas básicas
        count = len(weights_array)
        mean_val = np.mean(weights_array)
        std_val = np.std(weights_array)
        median_val = np.median(weights_array)
        min_val = np.min(weights_array)
        max_val = np.max(weights_array)

        # Percentis (o mais importante!)
        percentiles_to_calc = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        percentile_values = np.percentile(weights_array, percentiles_to_calc)

        # --- 3. Imprimir Relatório ---
        print("\n--- Análise da Distribuição de Pesos ---")
        print(f"  Total de Arestas (Pesos): {count}")
        print(f"  Média:                    {mean_val:.4f}")
        print(f"  Desvio Padrão:            {std_val:.4f}")
        print(f"  Mínimo (Max Negativo):    {min_val:.4f}")
        print(f"  Mediana (Percentil 50):   {median_val:.4f}")
        print(f"  Máximo (Max Positivo):    {max_val:.4f}")

        print("\n--- Tabela de Percentis ---")
        print(" (Use estes valores para escolher seus thresholds)")
        print(" -------------------------------------------------")
        
        suggestion_neg = None
        suggestion_pos = None

        for p, val in zip(percentiles_to_calc, percentile_values):
            label = f"  {p:02d}º Percentil:"
            print(f"{label:<28} {val:.4f}")
            if p == 10:
                suggestion_neg = val
            if p == 90:
                suggestion_pos = val
        
        print(" -------------------------------------------------")
        
        print("\n--- 💡 SUGESTÃO DE THRESHOLDS 💡 ---")
        if suggestion_neg is not None and suggestion_pos is not None:
            print("Baseado nesta análise, um bom ponto de partida para seu script de triângulos seria:")
            print(f"   NEG_THRESHOLD = {suggestion_neg:.4f}  (Percentil 10)")
            print(f"   POS_THRESHOLD = {suggestion_pos:.4f}  (Percentil 90)")
        else:
            print("Não foi possível gerar sugestões (erro nos percentis).")

    except Exception as e:
        print(f"Erro durante o cálculo com NumPy: {e}")
        print("Verifique se a biblioteca NumPy está instalada: pip install numpy")


if __name__ == "__main__":
    analyze_weights(GRAPH_FILE)