#!/usr/bin/env python3

"""
Script para calcular o Adjusted Rand Index (ARI) comparando
as comunidades do Louvain (Partição A) com os gêneros da loja (Partição B).

Este script:
1. Carrega 'comunidades.csv' (Partição A).
2. Carrega 'seu_arquivo.csv' (Metadados).
3. Cria a Partição B pegando a primeira tag de 'steamspy_tags'
   como o "gênero principal".
4. Alinha as duas partições (encontra os jogos em comum).
5. Calcula e imprime a pontuação ARI.
"""

import pandas as pd
from sklearn.metrics import adjusted_rand_score
import sys

# --- CONFIGURAÇÕES ---
# 1. O arquivo CSV gerado pelo script de comunidades
COMUNIDADES_FILE = "comunidades.csv"

# 2. O arquivo CSV com os metadados dos jogos
METADATA_FILE = "../entrega-parcial/steam.csv"

# 3. A coluna de tags que queremos usar como "gênero"
TAG_COLUMN = 'steamspy_tags'
# --- FIM DAS CONFIGURAÇÕES ---


def calculate_ari(comunidades_path, metadata_path, tag_col):
    """
    Função principal para carregar, preparar e
    calcular o Adjusted Rand Index.
    """
    
    # --- 1. Carregar Partição A (Louvain) ---
    print(f"Carregando Partição A (Comunidades) de '{comunidades_path}'...")
    try:
        df_louvain = pd.read_csv(comunidades_path)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{comunidades_path}' não encontrado.")
        sys.exit(1)

    # --- 2. Carregar e Preparar Partição B (Gêneros) ---
    print(f"Carregando Partição B (Metadados) de '{metadata_path}'...")
    try:
        df_metadata = pd.read_csv(metadata_path)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{metadata_path}' não encontrado.")
        sys.exit(1)

    # Verificar se as colunas necessárias existem
    if tag_col not in df_metadata.columns:
        print(f"ERRO: A coluna de tags '{tag_col}' não foi encontrada em '{metadata_path}'.")
        sys.exit(1)
    if 'appid' not in df_metadata.columns:
        print("ERRO: Coluna 'appid' não encontrada no arquivo de metadados.")
        sys.exit(1)

    # Criar a Partição B: "gênero principal" é a primeira tag
    df_metadata['main_genre'] = df_metadata[tag_col].astype(str).apply(
        lambda x: x.split(';')[0] if pd.notna(x) else 'Desconhecido'
    )
    
    # --- 3. Alinhar Partições ---
    print("Alinhando partições (encontrando jogos em comum)...")
    
    # Garantir que os 'appids' sejam strings para um 'merge' seguro
    df_louvain['appid'] = df_louvain['appid'].astype(str)
    df_metadata['appid_str'] = df_metadata['appid'].astype(str)

    # Juntar os dois DataFrames
    df_merged = pd.merge(
        df_louvain, # Colunas: ['appid', 'community_id']
        df_metadata[['appid_str', 'main_genre']], # Colunas: ['appid_str', 'main_genre']
        left_on='appid',
        right_on='appid_str',
        how='inner' # 'inner' = só jogos presentes em AMBOS os arquivos
    )

    if df_merged.empty:
        print("ERRO: A junção dos arquivos não produziu resultados.")
        print("Verifique se os 'appids' nos seus arquivos são compatíveis.")
        sys.exit(1)
        
    print(f"Comparando {len(df_merged)} jogos presentes em ambas as partições.")
    
    # --- 4. Extrair Rótulos e Calcular ARI ---
    
    # Lista de rótulos da Partição A (Comunidades)
    labels_comunidade = df_merged['community_id']
    
    # Lista de rótulos da Partição B (Gêneros)
    labels_genero = df_merged['main_genre']

    print("Calculando o Adjusted Rand Index...")
    
    # Calcular a pontuação
    ari_score = adjusted_rand_score(labels_genero, labels_comunidade)
    
    # --- 5. Imprimir Resultado ---
    print("\n==============================================")
    print(f" Pontuação ARI: {ari_score:.6f}")
    print("==============================================")

    if ari_score > 0.5:
        print("Interpretação: Alinhamento forte!")
        print("As comunidades de jogadores e os gêneros da loja são muito parecidos.")
    elif ari_score > 0.1:
        print("Interpretação: Alinhamento fraco.")
        print("Há uma pequena sobreposição, mas as comunidades são, em grande parte, diferentes dos gêneros.")
    else:
        print("Interpretação: Nenhum alinhamento (ou alinhamento muito baixo).")
        print("DESCOBERTA: As 'tribos de jogadores' (o que você encontrou) NÃO são")
        print("a mesma coisa que os 'gêneros da loja' (o que você provou ser inferior).")


if __name__ == "__main__":
    # Garantir que o scikit-learn está instalado
    try:
        from sklearn.metrics import adjusted_rand_score
    except ImportError:
        print("Erro: A biblioteca 'scikit-learn' não foi encontrada.")
        print("Por favor, instale-a com: pip install scikit-learn")
        sys.exit(1)
        
    calculate_ari(COMUNIDADES_FILE, METADATA_FILE, TAG_COLUMN)