"""
MC859 - Script Principal de Análise dos Grafos de Jogos da Steam
Autores: Yvens Ian Prado Porto e Lucca Miranda Nunes

Script integrado que executa todas as análises nos três grafos:
1. Grafo de Similaridade (Jaccard)
2. Grafo de Qualidade da Discussão (Weighted Score)
3. Grafo de Alinhamento de Sentimento

Inclui:
- Análise de comunidades e centralidade
- Análise de equilíbrio fraco (grafo de sentimento)
- Modelo de difusão
- Visualizações comparativas
"""

import os
import json
import time
from datetime import datetime

# Importa os módulos de análise
from analise_comunidades import AnalisadorComunidades
from analise_equilibrio_fraco import AnalisadorEquilibrioFraco
from modelo_difusao import ModeloDifusao


def criar_pasta_resultados():
    """Cria pasta para armazenar resultados."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pasta = f"resultados_{timestamp}"
    os.makedirs(pasta, exist_ok=True)
    print(f"Pasta de resultados criada: {pasta}\n")
    return pasta


def analisar_grafo_completo(grafo_path, nome_grafo, pasta_resultados):
    """
    Executa análise completa de um grafo.
    
    Args:
        grafo_path: Caminho para o arquivo GEXF
        nome_grafo: Nome descritivo do grafo
        pasta_resultados: Pasta onde salvar resultados
    
    Returns:
        dict com todos os resultados
    """
    print("\n" + "="*70)
    print(f"INICIANDO ANÁLISE: {nome_grafo.upper()}")
    print("="*70 + "\n")
    
    inicio = time.time()
    resultados = {'nome_grafo': nome_grafo}
    
    # 1. Análise de Comunidades e Centralidade
    print("\n--- ANÁLISE DE COMUNIDADES E CENTRALIDADE ---\n")
    try:
        analisador = AnalisadorComunidades(grafo_path, nome_grafo)
        output_file = os.path.join(pasta_resultados, f"{nome_grafo.lower().replace(' ', '_')}_comunidades.json")
        relatorio_comunidades = analisador.gerar_relatorio(output_file)
        resultados['comunidades'] = relatorio_comunidades
        print(f"✓ Análise de comunidades concluída")
    except Exception as e:
        print(f"✗ Erro na análise de comunidades: {e}")
        resultados['comunidades'] = {'erro': str(e)}
    
    # 2. Modelo de Difusão
    print("\n--- MODELO DE DIFUSÃO ---\n")
    try:
        modelo = ModeloDifusao(grafo_path)
        output_file = os.path.join(pasta_resultados, f"{nome_grafo.lower().replace(' ', '_')}_difusao.json")
        relatorio_difusao = modelo.gerar_relatorio(output_file)
        
        # Move visualização para pasta de resultados
        if os.path.exists('difusao_exemplo.png'):
            os.rename('difusao_exemplo.png', 
                     os.path.join(pasta_resultados, f"{nome_grafo.lower().replace(' ', '_')}_difusao.png"))
        
        resultados['difusao'] = relatorio_difusao
        print(f"✓ Modelo de difusão concluído")
    except Exception as e:
        print(f"✗ Erro no modelo de difusão: {e}")
        resultados['difusao'] = {'erro': str(e)}
    
    tempo_total = time.time() - inicio
    print(f"\n✓ Análise de {nome_grafo} concluída em {tempo_total:.2f} segundos")
    
    return resultados


def analisar_grafo_sentimento(grafo_path, nome_grafo, pasta_resultados):
    """
    Análise específica para o grafo de sentimento (inclui equilíbrio fraco).
    
    Args:
        grafo_path: Caminho para o arquivo GEXF
        nome_grafo: Nome descritivo do grafo
        pasta_resultados: Pasta onde salvar resultados
    
    Returns:
        dict com todos os resultados
    """
    print("\n" + "="*70)
    print(f"INICIANDO ANÁLISE: {nome_grafo.upper()}")
    print("="*70 + "\n")
    
    inicio = time.time()
    resultados = {'nome_grafo': nome_grafo}
    
    # 1. Análise de Comunidades e Centralidade
    print("\n--- ANÁLISE DE COMUNIDADES E CENTRALIDADE ---\n")
    try:
        analisador = AnalisadorComunidades(grafo_path, nome_grafo)
        output_file = os.path.join(pasta_resultados, f"{nome_grafo.lower().replace(' ', '_')}_comunidades.json")
        relatorio_comunidades = analisador.gerar_relatorio(output_file)
        resultados['comunidades'] = relatorio_comunidades
        print(f"✓ Análise de comunidades concluída")
    except Exception as e:
        print(f"✗ Erro na análise de comunidades: {e}")
        resultados['comunidades'] = {'erro': str(e)}
    
    # 2. Análise de Equilíbrio Fraco (específico para grafo de sentimento)
    print("\n--- ANÁLISE DE EQUILÍBRIO FRACO ---\n")
    try:
        analisador_eq = AnalisadorEquilibrioFraco(grafo_path)
        output_file = os.path.join(pasta_resultados, f"{nome_grafo.lower().replace(' ', '_')}_equilibrio_fraco.json")
        relatorio_equilibrio = analisador_eq.gerar_relatorio(output_file)
        resultados['equilibrio_fraco'] = relatorio_equilibrio
        print(f"✓ Análise de equilíbrio fraco concluída")
    except Exception as e:
        print(f"✗ Erro na análise de equilíbrio fraco: {e}")
        resultados['equilibrio_fraco'] = {'erro': str(e)}
    
    # 3. Modelo de Difusão
    print("\n--- MODELO DE DIFUSÃO ---\n")
    try:
        modelo = ModeloDifusao(grafo_path)
        output_file = os.path.join(pasta_resultados, f"{nome_grafo.lower().replace(' ', '_')}_difusao.json")
        relatorio_difusao = modelo.gerar_relatorio(output_file)
        
        # Move visualização
        if os.path.exists('difusao_exemplo.png'):
            os.rename('difusao_exemplo.png', 
                     os.path.join(pasta_resultados, f"{nome_grafo.lower().replace(' ', '_')}_difusao.png"))
        
        resultados['difusao'] = relatorio_difusao
        print(f"✓ Modelo de difusão concluído")
    except Exception as e:
        print(f"✗ Erro no modelo de difusão: {e}")
        resultados['difusao'] = {'erro': str(e)}
    
    tempo_total = time.time() - inicio
    print(f"\n✓ Análise de {nome_grafo} concluída em {tempo_total:.2f} segundos")
    
    return resultados


def gerar_relatorio_comparativo(resultados_todos, pasta_resultados):
    """
    Gera relatório comparativo entre os três grafos.
    
    Args:
        resultados_todos: Lista com resultados de todos os grafos
        pasta_resultados: Pasta onde salvar o relatório
    """
    print("\n" + "="*70)
    print("GERANDO RELATÓRIO COMPARATIVO")
    print("="*70 + "\n")
    
    comparacao = {
        'timestamp': datetime.now().isoformat(),
        'grafos_analisados': [],
        'comparacao_metricas': {}
    }
    
    # Coleta métricas básicas
    for resultado in resultados_todos:
        nome = resultado['nome_grafo']
        comparacao['grafos_analisados'].append(nome)
        
        # Informações básicas
        if 'comunidades' in resultado and 'info_basica' in resultado['comunidades']:
            info = resultado['comunidades']['info_basica']
            comparacao['comparacao_metricas'][nome] = {
                'num_nos': info.get('num_nos', 0),
                'num_arestas': info.get('num_arestas', 0),
                'densidade': info.get('densidade', 0),
                'grau_medio': info.get('grau_medio', 0)
            }
            
            # Comunidades
            if 'comunidades' in resultado['comunidades']:
                comparacao['comparacao_metricas'][nome]['num_comunidades'] = \
                    resultado['comunidades']['comunidades'].get('num_comunidades', 0)
                comparacao['comparacao_metricas'][nome]['modularity'] = \
                    resultado['comunidades']['comunidades'].get('modularity', 0)
            
            # Difusão
            if 'difusao' in resultado and 'melhor_estrategia' in resultado['difusao']:
                melhor = resultado['difusao']['melhor_estrategia']
                comparacao['comparacao_metricas'][nome]['alcance_difusao'] = \
                    melhor['desempenho']['alcance_medio']
    
    # Salva relatório comparativo
    output_file = os.path.join(pasta_resultados, 'relatorio_comparativo.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparacao, f, indent=2, ensure_ascii=False)
    
    # Imprime resumo
    print("RESUMO COMPARATIVO")
    print("-" * 70)
    print(f"{'Grafo':<30} {'Nós':<10} {'Arestas':<10} {'Comunidades':<12} {'Modularidade':<12}")
    print("-" * 70)
    
    for nome in comparacao['grafos_analisados']:
        if nome in comparacao['comparacao_metricas']:
            m = comparacao['comparacao_metricas'][nome]
            print(f"{nome:<30} {m.get('num_nos', 0):<10} {m.get('num_arestas', 0):<10} "
                  f"{m.get('num_comunidades', 0):<12} {m.get('modularity', 0):<12.4f}")
    
    print("\n✓ Relatório comparativo salvo em:", output_file)
    
    return comparacao


def main():
    """Função principal que coordena todas as análises."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Análise Completa dos Grafos de Jogos da Steam',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Análise completa dos três grafos
  python analise_principal.py --jaccard grafo_jaccard.gexf --score grafo_score.gexf --sentimento grafo_sentimento.gexf
  
  # Análise apenas do grafo Jaccard
  python analise_principal.py --jaccard grafo_jaccard.gexf
  
  # Análise com grafos padrão (assume nomes padrão)
  python analise_principal.py --completo
        """
    )
    
    parser.add_argument('--jaccard', type=str, help='Caminho para grafo Jaccard (GEXF)')
    parser.add_argument('--score', type=str, help='Caminho para grafo Score (GEXF)')
    parser.add_argument('--sentimento', type=str, help='Caminho para grafo Sentimento (GEXF)')
    parser.add_argument('--completo', action='store_true', 
                       help='Executa análise completa com nomes de arquivo padrão')
    
    args = parser.parse_args()
    
    # Define caminhos dos grafos
    if args.completo:
        grafos = {
            'Grafo Jaccard': 'grafo_jaccard_27075_nodes.gexf',
            'Grafo Score': 'grafo_score_27075_nodes.gexf',
            'Grafo Sentimento': 'grafo_sentimento_27075_nodes.gexf'
        }
    else:
        grafos = {}
        if args.jaccard:
            grafos['Grafo Jaccard'] = args.jaccard
        if args.score:
            grafos['Grafo Score'] = args.score
        if args.sentimento:
            grafos['Grafo Sentimento'] = args.sentimento
    
    if not grafos:
        print("ERRO: Nenhum grafo especificado!")
        print("Use --completo ou especifique ao menos um grafo (--jaccard, --score, --sentimento)")
        print("Execute 'python analise_principal.py --help' para mais informações")
        return
    
    # Cria pasta de resultados
    pasta_resultados = criar_pasta_resultados()
    
    # Banner inicial
    print("="*70)
    print(" "*15 + "ANÁLISE DE REDES DE JOGOS DA STEAM")
    print(" "*10 + "MC859 - Yvens Ian Prado Porto e Lucca Miranda Nunes")
    print("="*70)
    print(f"\nGrafos a analisar: {len(grafos)}")
    for nome in grafos.keys():
        print(f"  - {nome}")
    print()
    
    inicio_total = time.time()
    
    # Executa análises
    resultados_todos = []
    
    for nome_grafo, caminho_grafo in grafos.items():
        # Verifica se arquivo existe
        if not os.path.exists(caminho_grafo):
            print(f"AVISO: Arquivo não encontrado: {caminho_grafo}")
            print(f"Pulando análise de {nome_grafo}\n")
            continue
        
        # Análise específica para grafo de sentimento
        if 'sentimento' in nome_grafo.lower():
            resultado = analisar_grafo_sentimento(caminho_grafo, nome_grafo, pasta_resultados)
        else:
            resultado = analisar_grafo_completo(caminho_grafo, nome_grafo, pasta_resultados)
        
        resultados_todos.append(resultado)
    
    # Gera relatório comparativo se mais de um grafo foi analisado
    if len(resultados_todos) > 1:
        gerar_relatorio_comparativo(resultados_todos, pasta_resultados)
    
    # Resumo final
    tempo_total = time.time() - inicio_total
    print("\n" + "="*70)
    print("ANÁLISE COMPLETA CONCLUÍDA")
    print("="*70)
    print(f"Tempo total: {tempo_total:.2f} segundos ({tempo_total/60:.2f} minutos)")
    print(f"Resultados salvos em: {pasta_resultados}/")
    print("\nArquivos gerados:")
    for arquivo in sorted(os.listdir(pasta_resultados)):
        print(f"  - {arquivo}")
    print("\n" + "="*70)


if __name__ == '__main__':
    main()

