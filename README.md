# MC859 - Análise de Redes de Jogos da Steam

**Autores:** Yvens Ian Prado Porto (RA 184031) e Lucca Miranda Nunes (RA 230554)  
**Disciplina:** MC859 - Projeto em Teoria da Computação 
**UNICAMP** - Instituto de Computação

---

## Uso Rápido

### **Analisar um grafo:**

```bash
bash analisar_grafo.sh nome.gexf "Grafo nome"
```
---

## 📦 Instalação

O script `analisar_grafo.sh` faz tudo automaticamente:
- ✅ Cria virtual environment
- ✅ Instala dependências
- ✅ Organiza pastas
- ✅ Executa análises
- ✅ Gera relatórios

**Requisitos:**
- Python 3.8+
- 4GB+ RAM
- Linux/WSL

---

## 📊 O que é analisado?

Para cada grafo:
- ✅ Número de nós e arestas
- ✅ Grau médio e densidade
- ✅ Componentes conectadas
- ✅ Centralidade de Grau (Top 10)
- ✅ PageRank (Top 10)
- ✅ Comunidades (Louvain)
- ✅ Modularidade

**Resultados gerados:**
- `analise.json` - Dados completos em JSON
- `relatorio.txt` - Relatório em texto
- Logs completos em `logs/`

---

## 📝 Grafos do Projeto

1. **Grafo Jaccard** (560MB)
   - Similaridade por sobreposição de público
   - Peso: Índice de Jaccard

2. **Grafo Score** (1.1GB)
   - Qualidade da discussão crítica
   - Peso: Média de `weighted_vote_score`

3. **Grafo Sentimento** (1GB)
   - Alinhamento de opinião
   - Peso: Soma de sentimentos (+1/-1)

---

## 📚 Documentação

- **Proposta:** `Proposta/main.tex`
- **Entrega Parcial:** `entrega-parcial/relatorio/main.tex`
- **Relatório Final:** `entrega-final/relatorio/main.tex`