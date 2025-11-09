import networkx as nx
import argparse  # Importa a biblioteca de argumentos
import os

def convert_gexf_to_txt(gexf_file, txt_file):
    """
    Lê um arquivo GEXF e o converte para o formato TXT especificado.
    Formato:
    n m
    u1 v1 w1
    ...
    """
    try:
        # 4. O script lê o GEXF
        G = nx.read_gexf(gexf_file)

        # 5. Obtém o número de nós (n) e arestas (m)
        n = G.number_of_nodes()
        m = G.number_of_edges()

        # 6. Abre o arquivo TXT de saída para escrita
        with open(txt_file, 'w') as f:
            # Escreve a primeira linha "n m"
            f.write(f"{n} {m}\n")

            # Itera sobre todas as arestas
            for u, v, weight in G.edges(data='weight'):
                # Garante um valor de peso (0.0 se for Nulo)
                weight_val = weight if weight is not None else 0.0
                # Escreve a aresta no formato "a b c"
                f.write(f"{u} {v} {weight_val}\n") 

        print(f"✅ Sucesso! O arquivo '{gexf_file}' foi convertido para '{txt_file}'.")
        print(f"   Total de nós (n): {n}")
        print(f"   Total de arestas (m): {m}")

    except FileNotFoundError:
        print(f"❌ Erro: O arquivo de entrada não foi encontrado: {gexf_file}")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")

# O 'if __name__ == "__main__":' protege o script para que ele
# só execute este bloco quando chamado diretamente (e não se for importado)
if __name__ == "__main__":
    
    # 1. Configura o "parser" de argumentos
    parser = argparse.ArgumentParser(
        description="Converte um grafo GEXF ponderado para um arquivo TXT simples."
    )
    
    # 2. Define os argumentos que o script aceita
    parser.add_argument(
        "input_file",  # Nome do argumento
        help="O caminho para o arquivo GEXF de entrada (ex: grafo.gexf)"
    )
    parser.add_argument(
        "-o", "--output", # Nomes da flag (curto e longo)
        help="Nome do arquivo TXT de saída (opcional). Se não fornecido, usa o nome do arquivo de entrada com a extensão .txt."
    )
    
    # 3. Lê os argumentos fornecidos na linha de comando
    args = parser.parse_args()
    
    # Define o nome do arquivo de entrada
    gexf_path = args.input_file
    
    # Define o nome do arquivo de saída
    if args.output:
        # Se o usuário usou -o, usa o nome fornecido
        txt_path = args.output
    else:
        # Se não, cria o nome trocando a extensão
        base_name = os.path.splitext(gexf_path)[0]
        txt_path = base_name + ".txt"

    # Chama a função principal de conversão
    convert_gexf_to_txt(gexf_path, txt_path)