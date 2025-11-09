#!/usr/bin/env python3

"""
Script para analisar e identificar o "perfil" (tags e jogos populares)
de cada comunidade de jogos encontrada pelo algoritmo Louvain.

Este script:
1. Carrega 'comunidades.csv' (o resultado do Louvain).
2. Carrega 'seu_arquivo.csv' (os metadados com nomes, tags e ratings).
3. Junta (merge) os dois arquivos pelo 'appid'.
4. Para cada comunidade, imprime as tags mais comuns e os jogos
   mais populares (com base em 'positive_ratings').
"""

import pandas as pd
from collections import Counter
import sys

# --- CONFIGURAÇÕES ---
# 1. O arquivo CSV com os metadados dos jogos
METADATA_FILE = "../entrega-parcial/steam.csv"

# 2. O arquivo CSV gerado pelo script de comunidades
COMUNIDADES_FILE = "comunidades.csv"

# 3. Os IDs das 5 maiores comunidades que você encontrou
COMUNIDADES_PARA_ANALISAR = [5, 0, 15, 8, 2] # Use os IDs do seu output

# 4. A coluna de tags que queremos analisar
TAG_COLUMN = 'steamspy_tags'

# 5. Quantas top tags e jogos mostrar por comunidade
TOP_N_TAGS = 10
TOP_N_GAMES = 5
# --- FIM DAS CONFIGURAÇÕES ---


def analyze_community_profiles(metadata_path, comunidades_path, community_ids, tag_col):
    """
    Função principal para carregar, juntar e analisar
    os perfis das comunidades.
    """
    
    # --- 1. Carregar Arquivos ---
    print("Carregando arquivos...")
    try:
        df_metadata = pd.read_csv(metadata_path)
    except FileNotFoundError:
        print(f"ERRO: Arquivo de metadados '{metadata_path}' não encontrado.")
        sys.exit(1)

    try:
        df_comunidades = pd.read_csv(comunidades_path)
    except FileNotFoundError:
        print(f"ERRO: Arquivo de comunidades '{comunidades_path}' não encontrado.")
        sys.exit(1)

    # --- 2. Preparar e Juntar (Merge) ---
    print("Juntando dados...")
    
    # Garante que os 'appids' possam ser juntados (ambos como string)
    if 'appid' not in df_metadata.columns:
        print("Coluna 'appid' não encontrada no CSV de metadados.")
        sys.exit(1)
        
    # Assegura que colunas essenciais existem
    for col in ['name', 'positive_ratings', tag_col]:
        if col not in df_metadata.columns:
            print(f"ERRO: Coluna obrigatória '{col}' não encontrada em '{metadata_path}'.")
            sys.exit(1)

    df_metadata['appid_str'] = df_metadata['appid'].astype(str)
    df_comunidades['appid'] = df_comunidades['appid'].astype(str)

    # Juntar os dois dataframes
    df_merged = pd.merge(
        df_comunidades,
        df_metadata,
        left_on='appid',
        right_on='appid_str',
        how='inner'
    )
    
    if df_merged.empty:
        print("ERRO: A junção dos arquivos não produziu resultados.")
        print("Verifique se os 'appids' nos seus arquivos são compatíveis.")
        sys.exit(1)

    print("Dados juntados com sucesso.")

    # --- 3. Analisar cada Comunidade ---
    print("\n--- INICIANDO ANÁLISE DE PERFIL DAS COMUNIDADES ---")
    
    for cid in community_ids:
        # Filtrar o dataframe para incluir apenas jogos desta comunidade
        df_cluster = df_merged[df_merged['community_id'] == cid].copy()
        
        print(f"\n==============================================")
        print(f"  PERFIL DA COMUNIDADE: {cid}")
        print(f"  Total de jogos: {len(df_cluster)}")
        print(f"==============================================")
        
        if df_cluster.empty:
            print("  (Sem jogos encontrados após a junção. Pulando.)")
            continue
        
        # --- ANÁLISE DE TAGS ---
        all_tags = []
        for tags_str in df_cluster[tag_col].dropna():
            tags = tags_str.split(';')
            all_tags.extend(tags)
            
        tag_counts = Counter(all_tags)
        
        if not tag_counts:
            print("  Nenhuma tag encontrada para esta comunidade.")
        else:
            print(f"Top {TOP_N_TAGS} tags mais comuns:")
            total_jogos_no_cluster = len(df_cluster)
            for tag, count in tag_counts.most_common(TOP_N_TAGS):
                percent = (count / total_jogos_no_cluster) * 100
                print(f"  - {tag:<20} : {count:>5} jogos ({percent:.1f}%)")

        # --- NOVA SEÇÃO: JOGOS MAIS POPULARES ---
        print(f"\nTop {TOP_N_GAMES} jogos mais populares (por avaliações positivas):")
        
        # Garante que 'positive_ratings' é numérico, tratando erros
        df_cluster['positive_ratings'] = pd.to_numeric(df_cluster['positive_ratings'], errors='coerce')
        
        # Ordena o cluster por 'positive_ratings'
        df_top_games = df_cluster.sort_values(by='positive_ratings', ascending=False)
        
        # Imprime o top N
        for index, row in df_top_games.head(TOP_N_GAMES).iterrows():
            print(f"  - {row['name']} (Ratings: {int(row['positive_ratings'])})")
            
    print("\n--- Análise concluída ---")


if __name__ == "__main__":
    analyze_community_profiles(
        METADATA_FILE,
        COMUNIDADES_FILE,
        COMUNIDADES_PARA_ANALISAR,
        TAG_COLUMN
    )