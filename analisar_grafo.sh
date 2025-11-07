################################################################################
# MC859 - Script Master de Análise de Grafos
# Autores: Yvens Ian Prado Porto e Lucca Miranda Nunes
#
# Uso: bash analisar_grafo.sh <arquivo.gexf> [nome_descritivo]
#
# Exemplo:
#   bash analisar_grafo.sh grafo_jaccard_27075_nodes.gexf "Grafo Jaccard"
################################################################################

set -e  # Para na primeiro erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para print colorido
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

# Banner
echo "======================================================================"
echo "           MC859 - ANÁLISE DE GRAFOS DA STEAM"
echo "       Yvens Ian Prado Porto & Lucca Miranda Nunes"
echo "======================================================================"
echo ""

# Verificar argumentos
if [ $# -lt 1 ]; then
    print_error "Uso: $0 <arquivo.gexf> [nome_descritivo]"
    echo ""
    echo "Exemplos:"
    echo "  $0 grafo_jaccard_27075_nodes.gexf"
    echo "  $0 grafo_jaccard_27075_nodes.gexf \"Grafo Jaccard\""
    echo ""
    exit 1
fi

ARQUIVO_GRAFO="$1"
NOME_GRAFO="${2:-Grafo}"

# Verificar se arquivo existe
if [ ! -f "$ARQUIVO_GRAFO" ]; then
    print_error "Arquivo não encontrado: $ARQUIVO_GRAFO"
    exit 1
fi

print_info "Arquivo: $ARQUIVO_GRAFO"
print_info "Nome: $NOME_GRAFO"
print_info "Tamanho: $(du -h "$ARQUIVO_GRAFO" | cut -f1)"
echo ""

# Criar estrutura de pastas
print_info "Criando estrutura de pastas..."
mkdir -p src
mkdir -p resultados
mkdir -p logs

# Mover scripts Python para src/ se ainda não estiverem lá
if [ -f "analise_comunidades.py" ]; then
    mv -n analise_comunidades.py src/ 2>/dev/null || true
    mv -n analise_equilibrio_fraco.py src/ 2>/dev/null || true
    mv -n modelo_difusao.py src/ 2>/dev/null || true
    mv -n visualizacao_grafos.py src/ 2>/dev/null || true
fi

print_success "Estrutura criada"
echo ""

# Verificar/criar venv
if [ ! -d "venv" ]; then
    print_info "Criando virtual environment..."
    python3 -m venv venv
    print_success "Venv criado"
fi

# Ativar venv
print_info "Ativando virtual environment..."
source venv/bin/activate

# Instalar dependências
if [ ! -f "venv/.deps_installed" ]; then
    print_info "Instalando dependências..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
    touch venv/.deps_installed
    print_success "Dependências instaladas"
else
    print_success "Dependências já instaladas"
fi
echo ""

# Timestamp para arquivos
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PASTA_RESULTADO="resultados/${NOME_GRAFO// /_}_${TIMESTAMP}"
mkdir -p "$PASTA_RESULTADO"
LOG_FILE="logs/analise_${TIMESTAMP}.log"

print_info "Pasta de resultados: $PASTA_RESULTADO"
print_info "Log: $LOG_FILE"
echo ""

# Criar script Python temporário para análise
SCRIPT_TEMP="$PASTA_RESULTADO/analise_temp.py"
cat > "$SCRIPT_TEMP" << 'PYTHON_SCRIPT'
import sys
import os
import json
import gc
import networkx as nx

arquivo = sys.argv[1]
nome = sys.argv[2]
pasta_out = sys.argv[3]

print(f"\n{'='*70}")
print(f"ANALISANDO: {nome}")
print(f"{'='*70}\n")

try:
    # 1. Carregar grafo
    print(f"1. Carregando {arquivo}...")
    G = nx.read_gexf(arquivo)
    print(f"   ✓ Carregado: {G.number_of_nodes():,} nós, {G.number_of_edges():,} arestas\n")
    
    resultados = {
        'nome': nome,
        'arquivo': arquivo,
        'num_nos': G.number_of_nodes(),
        'num_arestas': G.number_of_edges()
    }
    
    # 2. Métricas básicas
    print("2. Calculando métricas básicas...")
    graus = dict(G.degree())
    resultados['grau_medio'] = sum(graus.values()) / len(graus)
    resultados['grau_max'] = max(graus.values())
    resultados['grau_min'] = min(graus.values())
    resultados['densidade'] = nx.density(G)
    print(f"   ✓ Grau médio: {resultados['grau_medio']:.2f}")
    print(f"   ✓ Densidade: {resultados['densidade']:.8f}\n")
    
    # 3. Componentes
    print("3. Analisando componentes...")
    if G.is_directed():
        G_und = G.to_undirected()
    else:
        G_und = G
    
    componentes = list(nx.connected_components(G_und))
    tamanhos = sorted([len(c) for c in componentes], reverse=True)
    
    resultados['num_componentes'] = len(componentes)
    resultados['tamanho_maior_componente'] = tamanhos[0] if tamanhos else 0
    resultados['tamanho_segunda_componente'] = tamanhos[1] if len(tamanhos) > 1 else 0
    print(f"   ✓ Componentes: {resultados['num_componentes']}")
    print(f"   ✓ Maior: {resultados['tamanho_maior_componente']:,} nós\n")
    
    # 4. Centralidade de Grau (Top 10)
    print("4. Calculando centralidade de grau...")
    degree_cent = nx.degree_centrality(G)
    top_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:10]
    resultados['top_10_grau'] = [(str(k), float(v)) for k, v in top_degree]
    print(f"   ✓ Top 1: Nó {top_degree[0][0]} ({top_degree[0][1]:.6f})\n")
    
    # 5. PageRank (Top 10)
    print("5. Calculando PageRank...")
    try:
        pagerank = nx.pagerank(G, max_iter=50, weight='weight')
        top_pr = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]
        resultados['top_10_pagerank'] = [(str(k), float(v)) for k, v in top_pr]
        print(f"   ✓ Top 1: Nó {top_pr[0][0]} ({top_pr[0][1]:.6f})\n")
    except:
        resultados['top_10_pagerank'] = []
        print("   ⚠ PageRank falhou\n")
    
    # 6. Comunidades (Louvain)
    print("6. Detectando comunidades...")
    try:
        import community as community_louvain
        
        maior_comp = max(componentes, key=len)
        G_comp = G_und.subgraph(maior_comp).copy()
        
        comunidades = community_louvain.best_partition(G_comp, weight='weight')
        modularity = community_louvain.modularity(comunidades, G_comp, weight='weight')
        num_comunidades = len(set(comunidades.values()))
        
        resultados['num_comunidades'] = num_comunidades
        resultados['modularity'] = modularity
        print(f"   ✓ Comunidades: {num_comunidades}")
        print(f"   ✓ Modularidade: {modularity:.4f}\n")
        
        del G_comp, comunidades
        gc.collect()
    except Exception as e:
        print(f"   ⚠ Detecção de comunidades falhou: {e}\n")
        resultados['num_comunidades'] = 0
        resultados['modularity'] = 0
    
    # 7. Salvar resultados
    output_json = os.path.join(pasta_out, 'analise.json')
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Resultados salvos: {output_json}\n")
    
    # 8. Gerar relatório texto
    output_txt = os.path.join(pasta_out, 'relatorio.txt')
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(f"RELATÓRIO DE ANÁLISE: {nome}\n")
        f.write("="*70 + "\n\n")
        f.write(f"Arquivo: {arquivo}\n")
        f.write(f"Número de nós: {resultados['num_nos']:,}\n")
        f.write(f"Número de arestas: {resultados['num_arestas']:,}\n")
        f.write(f"Grau médio: {resultados['grau_medio']:.2f}\n")
        f.write(f"Densidade: {resultados['densidade']:.8f}\n")
        f.write(f"Componentes: {resultados['num_componentes']}\n")
        f.write(f"Maior componente: {resultados['tamanho_maior_componente']:,} nós\n")
        f.write(f"Comunidades: {resultados['num_comunidades']}\n")
        f.write(f"Modularidade: {resultados['modularity']:.4f}\n")
        f.write("\nTop 10 - Centralidade de Grau:\n")
        for i, (no, val) in enumerate(resultados['top_10_grau'], 1):
            f.write(f"  {i}. Nó {no}: {val:.6f}\n")
        if resultados['top_10_pagerank']:
            f.write("\nTop 10 - PageRank:\n")
            for i, (no, val) in enumerate(resultados['top_10_pagerank'], 1):
                f.write(f"  {i}. Nó {no}: {val:.6f}\n")
    
    print(f"✓ Relatório texto: {output_txt}\n")
    
    print("="*70)
    print("ANÁLISE CONCLUÍDA COM SUCESSO!")
    print("="*70)
    
except MemoryError:
    print("\n✗ ERRO: Memória insuficiente!")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

# Executar análise
print_info "Iniciando análise (pode demorar)..."
echo ""

python "$SCRIPT_TEMP" "$ARQUIVO_GRAFO" "$NOME_GRAFO" "$PASTA_RESULTADO" 2>&1 | tee "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo ""
    print_success "Análise concluída com sucesso!"
    echo ""
    print_info "Resultados:"
    ls -lh "$PASTA_RESULTADO"
    echo ""
    print_info "Para ver o relatório:"
    echo "  cat $PASTA_RESULTADO/relatorio.txt"
    echo ""
else
    print_error "Análise falhou! Veja o log: $LOG_FILE"
    exit 1
fi

# Limpar script temporário
rm -f "$SCRIPT_TEMP"

echo "======================================================================"
print_success "CONCLUÍDO!"
echo "======================================================================"

