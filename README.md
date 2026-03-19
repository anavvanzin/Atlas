# Atlas Iconocrático — Toolkit de Pesquisa

**Contrato Sexual Visual & Regime Iconocrático: Alegorias Femininas na Cultura Jurídica (1789–2024)**

Toolkit completo em Python para a tese de doutorado no PPGD/UFSC. Inclui gestão de corpus visual, sistema de codificação com 10 indicadores, análise estatística, confiabilidade inter-codificadores, integração Iconclass e matriz de evidências.

---

## Instalação

```bash
# 1. Clonar / copiar o diretório
cd atlas-iconocratico-toolkit

# 2. Criar ambiente virtual (recomendado)
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. (Opcional) Instalar Iconclass
pip install iconclass
```

**Requisitos mínimos:** Python 3.10+

---

## Estrutura do Projeto

```
atlas-iconocratico-toolkit/
├── main.py                          # CLI principal
├── requirements.txt                 # Dependências
├── README.md                        # Este arquivo
├── atlas_iconocratico/              # Pacote Python
│   ├── __init__.py                  # v0.1.0
│   ├── corpus.py                    # Gestão do corpus visual
│   ├── codificacao.py               # Sistema de codificação (10 indicadores)
│   ├── estatistica.py               # Análise estatística (H1–H5)
│   ├── kappa.py                     # Confiabilidade inter-codificadores
│   ├── iconclass_.py                # Integração Iconclass
│   └── matriz.py                    # Matriz de evidências
├── data/                            # Dados de pesquisa
├── corpus/                          # Imagens organizadas por país
│   ├── FR/
│   ├── UK/
│   ├── USA/
│   ├── DE/
│   └── BR/
└── output/                          # Resultados gerados
    ├── graficos/
    ├── tabelas/
    └── relatorios/
```

---

## Uso Rápido

### Informações do toolkit

```bash
python main.py info
```

### 1. Corpus Visual

```bash
# Ver relatório de distribuição
python main.py corpus relatorio

# Adicionar imagem ao catálogo
python main.py corpus adicionar \
  --titulo "La Liberté guidant le peuple" \
  --pais FR \
  --ano 1830 \
  --autor "Eugène Delacroix" \
  --tipo pintura \
  --fonte "Musée du Louvre"

# Listar imagens (com filtro opcional)
python main.py corpus listar --pais FR

# Contar imagens
python main.py corpus contar

# Exportar bibliografia de fontes
python main.py corpus fontes
```

### 2. Codificação (10 Indicadores)

Os **10 indicadores** do sistema de codificação:

| Código | Indicador | Escala |
|--------|-----------|--------|
| FEI | Female Embodiment Index | 0–3 |
| CII | Constitutional Iconography Index | 0–1 |
| PRI | Patriarchal Representation Index | 0–3 |
| SMI | Sexual Metaphor Index | 0–1 |
| SMS | Sexual Morality Signifier | 0–1 |
| AMCP | Allegory of Masculine/Colonial Power | 0–1 |
| MVI | Male Visual Index | 0–3 |
| WI | Weaponry Index | 0–1 |
| RI | Racialization Index | 0–1 |
| AI | Anachronism Index | 0–1 |

```bash
# Ver todos os indicadores com definições operacionais
python main.py codificacao indicadores

# Detalhar um indicador
python main.py codificacao indicador --codigo FEI

# Árvore de decisão para codificação
python main.py codificacao arvore --codigo PRI

# Gerar manual de codificação (JSON)
python main.py codificacao manual

# Codificar imagem interativamente
python main.py codificacao codificar --image-id IMG001

# Codificar com segundo codificador
python main.py codificacao codificar --image-id IMG001 --coder COD2

# Ver progresso da codificação
python main.py codificacao progresso --coder COD1

# Consolidar dataset final
python main.py codificacao consolidar
```

### 3. Análise Estatística

```bash
# Estatísticas descritivas
python main.py estatistica descritivas

# Tabelas cruzadas (país × indicador, período × indicador)
python main.py estatistica cruzadas

# Testar TODAS as hipóteses (H1–H5)
python main.py estatistica hipoteses

# Testar uma hipótese específica
python main.py estatistica hipotese --hipotese H1

# Gerar todos os gráficos
python main.py estatistica graficos

# Relatório estatístico completo
python main.py estatistica relatorio
```

**Hipóteses testadas:**

| ID | Hipótese | Teste |
|----|----------|-------|
| H1 | Alegorias femininas reforçam o contrato sexual visual | Binomial + Proporção |
| H2 | Regime iconocrático varia entre países | Kruskal-Wallis |
| H3 | Revolução Francesa intensifica a instrumentalização | Mann-Whitney U |
| H4 | Correlação entre simbologia constitucional e armamento | Phi / Fisher |
| H5 | Anacronismo visual persiste na era contemporânea | Tendência temporal |

### 4. Confiabilidade Inter-Codificadores

```bash
# Calcular Cohen's Kappa para todos os indicadores
python main.py kappa calcular

# Salvar relatório
python main.py kappa calcular --salvar

# Identificar discordâncias específicas
python main.py kappa discordancias

# Verificar drift temporal
python main.py kappa drift
```

### 5. Iconclass

```bash
# Ver códigos pré-mapeados para a tese
python main.py iconclass tese

# Buscar código Iconclass
python main.py iconclass buscar --notacao 44B

# Explorar hierarquia
python main.py iconclass hierarquia --notacao 44B --profundidade 3

# Buscar por texto
python main.py iconclass texto --termo "justice"

# Sugerir códigos baseado na codificação
python main.py iconclass sugerir \
  --json-codificacao '{"FEI": 3, "CII": 1, "WI": 1}'

# Exportar mapeamento completo
python main.py iconclass mapeamento
```

### 6. Matriz de Evidências

```bash
# Ver relatório de lacunas
python main.py matriz lacunas

# Adicionar entrada manualmente
python main.py matriz adicionar \
  --titulo "The Sexual Contract" \
  --autores "Carole Pateman" \
  --ano 1988 \
  --tipo-fonte livro

# Importar do Elicit (CSV)
python main.py matriz importar-elicit --csv elicit_export.csv

# Listar entradas
python main.py matriz listar

# Exportar bibliografia ABNT
python main.py matriz bibliografia

# Exportar matriz completa
python main.py matriz exportar --formato csv

# Integrar corpus ↔ matriz
python main.py matriz integrar
```

### 7. Relatório Completo

```bash
# Gera relatório unificado de todos os módulos
python main.py relatorio
```

---

## Fluxo de Trabalho Típico

```
1. Montar corpus       →  python main.py corpus adicionar ...
2. Codificar (COD1)    →  python main.py codificacao codificar --image-id IMG001
3. Codificar (COD2)    →  python main.py codificacao codificar --image-id IMG001 --coder COD2
4. Verificar Kappa     →  python main.py kappa calcular
5. Consolidar dados    →  python main.py codificacao consolidar
6. Anotar Iconclass    →  python main.py iconclass sugerir ...
7. Testar hipóteses    →  python main.py estatistica hipoteses
8. Montar matriz       →  python main.py matriz importar-elicit --csv ...
9. Relatório final     →  python main.py relatorio
```

---

## Uso como Biblioteca Python

Todos os módulos podem ser importados diretamente:

```python
from atlas_iconocratico.corpus import GerenciadorCorpus, criar_corpus
from atlas_iconocratico.codificacao import (
    CodificacaoImagem, GerenciadorCodificacao,
    descrever_indicador, arvore_decisao,
)
from atlas_iconocratico.estatistica import (
    carregar_dataset, executar_todos_testes,
    gerar_todas_visualizacoes, gerar_relatorio_estatistico,
)
from atlas_iconocratico.kappa import (
    calcular_kappa_todos, identificar_discordancias, verificar_drift,
)
from atlas_iconocratico.iconclass_ import (
    buscar_codigo, buscar_por_texto, sugerir_iconclass_para_indicadores,
)
from atlas_iconocratico.matriz import (
    GerenciadorMatriz, EntradaMatriz, integrar_corpus_e_matriz,
)

# Exemplo: criar corpus e adicionar imagem
gc = criar_corpus("./data")
gc.adicionar_imagem(
    titulo="La Liberté guidant le peuple",
    pais="FR", ano=1830, autor="Eugène Delacroix",
    tipo="pintura", fonte="Musée du Louvre",
)

# Exemplo: codificar imagem
from atlas_iconocratico.codificacao import CodificacaoImagem, GerenciadorCodificacao
cod = CodificacaoImagem(
    image_id="IMG001", coder_id="COD1",
    FEI=3, CII=1, PRI=2, SMI=1, SMS=0,
    AMCP=0, MVI=1, WI=1, RI=0, AI=0,
)
gcd = GerenciadorCodificacao("./data")
gcd.salvar_codificacao(cod)

# Exemplo: testar hipóteses
df = carregar_dataset("./data/corpus_codificado.csv")
resultados = executar_todos_testes(df)
```

---

## Licença

Uso acadêmico — PPGD/UFSC. Todos os direitos reservados.
