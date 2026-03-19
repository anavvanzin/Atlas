"""
estatistica.py — Análise Estatística Descritiva e Inferencial
==============================================================
Implementa as análises estatísticas da Fase 2 da tese (Meses 13–18):
análise descritiva dos 10 indicadores, testes inferenciais para
as 5 hipóteses derivadas do referencial teórico, e suite de
visualizações para inclusão nos capítulos e painéis do atlas.

ESTRUTURA DAS ANÁLISES:
    1. DESCRITIVAS (Meses 13–15):
       - Frequências e distribuições por país/regime/suporte
       - Médias, desvios-padrão, medianas (indicadores ordinais)
       - Tabelas cruzadas estratégicas: Regime × FEI, País × WI,
         Suporte × AI, País × Regime

    2. INFERENCIAIS (Meses 16–18) — 5 Hipóteses:
       H1: Regimes militar-imperiais → AMCP e MVI mais altos
           Teste: Kruskal-Wallis + Mann-Whitney U (não-paramétrico,
           apropriado para dados ordinais com distribuição desconhecida)
       H2: Correlação CII ↔ WI ("clássico como código racial")
           Teste: Spearman (rho) — correlação de postos para ordinais
       H3: Suportes íntimos (moeda/selo) → FEI mais baixo
           Teste: Mann-Whitney U (rotina fraternal exige feminilidade
           suavizada — cf. Painel V: Ubiquidade Íntima)
       H4: BR e USA → RI=1 em ≥80% pós-1889
           Teste: Binomial (proporção observada vs. esperada)
       H5: AI aumenta ao longo do tempo (1789→2024)
           Teste: Regressão linear simples (ano como preditor)

    3. VISUALIZAÇÕES:
       - Gráficos de barras (distribuição por indicador)
       - Heatmap de correlações de Spearman (inter-indicadores)
       - Boxplots por regime e por país
       - Scatterplot CII × WI com regressão (H2)
       - Gráfico temporal AI (H5)

JUSTIFICATIVA DOS TESTES NÃO-PARAMÉTRICOS:
    Dados ordinais (0–3) não atendem aos pressupostos de normalidade
    exigidos por testes paramétricos (ANOVA, t-test). Por isso,
    utilizamos Kruskal-Wallis (equivalente não-paramétrico da ANOVA),
    Mann-Whitney U (equivalente do t-test) e Spearman (equivalente
    de Pearson para postos). Cf. Siegel & Castellan (1988).

NÍVEL DE SIGNIFICÂNCIA:
    α = 0.05 (padrão em ciências sociais)

Dependências:
    pip install pandas numpy scipy matplotlib seaborn
"""

import csv
from pathlib import Path
from typing import Optional

try:
    import pandas as pd
    import numpy as np
    from scipy import stats
    import matplotlib
    matplotlib.use("Agg")  # Backend sem GUI
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

from .codificacao import (
    INDICADORES_ORDINAIS,
    INDICADORES_CATEGORICOS,
    TODOS_INDICADORES,
)


# ---------------------------------------------------------------------------
# Verificação de dependências
# ---------------------------------------------------------------------------

def _check_deps():
    if not HAS_DEPS:
        raise ImportError(
            "Dependências não encontradas. Instale com:\n"
            "  pip install pandas numpy scipy matplotlib seaborn"
        )


# ---------------------------------------------------------------------------
# Carregamento de Dados
# ---------------------------------------------------------------------------

def carregar_dataset(caminho: str = "./data/corpus_codificado.csv") -> "pd.DataFrame":
    """
    Carrega o dataset codificado como DataFrame pandas.

    Espera colunas: Image_ID, Coder_ID, Coding_date,
    FEI, CII, PRI, SMI, SMS, AMCP, MVI, WI, RI, AI, Notes
    """
    _check_deps()
    df = pd.read_csv(caminho)

    # Converter tipos
    for col in INDICADORES_ORDINAIS + ["RI"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def carregar_com_metadados(
    codificacao: str = "./data/corpus_codificado.csv",
    corpus: str = "./data/corpus_visual_master.csv",
) -> "pd.DataFrame":
    """
    Carrega dataset codificado com metadados do corpus (país, suporte, etc.).
    Faz merge por Image_ID.
    """
    _check_deps()
    df_cod = pd.read_csv(codificacao)
    df_corpus = pd.read_csv(corpus)

    df = df_cod.merge(df_corpus, on="Image_ID", how="left")

    for col in INDICADORES_ORDINAIS + ["RI"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# Estatísticas Descritivas
# ---------------------------------------------------------------------------

def descritivas_indicadores(df: "pd.DataFrame", output_dir: str = "./output/tabelas"):
    """
    Gera estatísticas descritivas para todos os indicadores.
    Salva tabelas em CSV.
    """
    _check_deps()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Indicadores ordinais: média, desvio-padrão, mediana, min, max
    cols_ord = [c for c in INDICADORES_ORDINAIS + ["RI"] if c in df.columns]
    if cols_ord:
        desc = df[cols_ord].describe().T
        desc["mediana"] = df[cols_ord].median()
        desc.to_csv(out / "descritivas_ordinais.csv")
        print(f"Descritivas ordinais salvas: {out / 'descritivas_ordinais.csv'}")
        print(desc.to_string())

    # Indicadores categóricos: frequências
    for col in INDICADORES_CATEGORICOS:
        if col in df.columns:
            freq = df[col].value_counts()
            freq_pct = df[col].value_counts(normalize=True) * 100
            tabela = pd.DataFrame({"n": freq, "%": freq_pct.round(1)})
            tabela.to_csv(out / f"frequencias_{col}.csv")
            print(f"\nFrequências {col}:")
            print(tabela.to_string())

    return desc if cols_ord else None


def tabelas_cruzadas(df: "pd.DataFrame", output_dir: str = "./output/tabelas"):
    """
    Gera tabelas cruzadas estratégicas:
    - Regime × FEI
    - País × WI
    - Suporte × AI
    - País × Regime
    """
    _check_deps()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    cruzamentos = [
        ("Regime_preliminary", "FEI", "regime_x_fei"),
        ("Country", "WI", "pais_x_wi"),
        ("Support", "AI", "suporte_x_ai"),
        ("Country", "Regime_preliminary", "pais_x_regime"),
    ]

    for col1, col2, nome in cruzamentos:
        if col1 in df.columns and col2 in df.columns:
            tab = pd.crosstab(df[col1], df[col2], margins=True)
            tab.to_csv(out / f"cruzada_{nome}.csv")
            print(f"\nTabela cruzada {col1} × {col2}:")
            print(tab.to_string())


# ---------------------------------------------------------------------------
# Testes de Hipóteses H1–H5
# ---------------------------------------------------------------------------

def teste_h1(df: "pd.DataFrame") -> dict:
    """
    H1: Regimes militar-imperiais apresentam AMCP e MVI significativamente
    mais altos que regimes normativos.

    Teste: ANOVA (ou Kruskal-Wallis se não-normal) entre os 3 regimes.
    """
    # ─── HIPÓTESE 1 ───────────────────────────────────────────────
    # Fundamentação: Mondzain (iconocracia como poder) + análise de
    # momentos de crise (Benjamin, reativação arcaica). Em regimes
    # militar-imperiais, a alegoria feminina é mobilizada como arma
    # visual — daí AMCP e MVI (sacrifício maternal) devem ser maiores.
    #
    # Escolha do teste: Kruskal-Wallis (3 grupos: fundacional,
    # normativo, militar) seguido de Mann-Whitney U para comparação
    # par-a-par (militar vs. normativo, a comparação teoricamente
    # mais relevante). Usamos alternative="greater" pois a hipótese
    # é direcional (militar > normativo).
    # ─────────────────────────────────────────────────────────────────
    _check_deps()
    resultados = {"hipotese": "H1", "descricao": "AMCP e MVI por regime"}

    if "Regime_preliminary" not in df.columns:
        resultados["erro"] = "Coluna 'Regime_preliminary' não encontrada"
        return resultados

    for indicador in ("AMCP", "MVI"):
        if indicador not in df.columns:
            continue

        grupos = {}
        for regime in ("fundacional", "normativo", "militar"):
            dados = df[df["Regime_preliminary"] == regime][indicador].dropna()
            grupos[regime] = dados

        if len(grupos) < 2 or any(len(v) < 2 for v in grupos.values()):
            resultados[indicador] = {"erro": "Dados insuficientes"}
            continue

        # Kruskal-Wallis (não-paramétrico, mais seguro para ordinais)
        h_stat, p_value = stats.kruskal(*grupos.values())

        # Médias por grupo
        medias = {k: float(v.mean()) for k, v in grupos.items()}
        ns = {k: len(v) for k, v in grupos.items()}

        # Mann-Whitney pairwise (militar vs normativo)
        if "militar" in grupos and "normativo" in grupos:
            u_stat, p_pair = stats.mannwhitneyu(
                grupos["militar"], grupos["normativo"],
                alternative="greater"
            )
            pair_result = {
                "U": float(u_stat),
                "p": float(p_pair),
                "significativo": p_pair < 0.05,
            }
        else:
            pair_result = None

        resultados[indicador] = {
            "kruskal_wallis": {"H": float(h_stat), "p": float(p_value)},
            "significativo_global": p_value < 0.05,
            "medias": medias,
            "n": ns,
            "militar_vs_normativo": pair_result,
        }

    return resultados


def teste_h2(df: "pd.DataFrame") -> dict:
    """
    H2: Há correlação positiva entre CII (ideal clássico) e WI (branquitude).
    Valida "clássico como código racial".

    Teste: Correlação de Spearman (dados ordinais).
    """
    # ─── HIPÓTESE 2 ───────────────────────────────────────────────
    # Fundamentação: Mills (1997) — o contrato racial opera através
    # da idealização do corpo branco como universal. Na iconografia,
    # o "clássico" (CII) funciona como código para "branco" (WI).
    # Se CII e WI covariam, confirma-se que a estética greco-romana
    # nas alegorias femininas é um veículo de branqueamento.
    #
    # Escolha do teste: Spearman (rho) — correlação de postos,
    # adequada para dados ordinais. Também calcula por país para
    # verificar se o padrão é transatlântico ou localizado.
    # ─────────────────────────────────────────────────────────────────
    _check_deps()
    resultados = {"hipotese": "H2", "descricao": "Correlação CII × WI"}

    if "CII" not in df.columns or "WI" not in df.columns:
        resultados["erro"] = "Colunas CII e/ou WI não encontradas"
        return resultados

    dados = df[["CII", "WI"]].dropna()
    if len(dados) < 5:
        resultados["erro"] = "Dados insuficientes (n < 5)"
        return resultados

    rho, p_value = stats.spearmanr(dados["CII"], dados["WI"])

    resultados["spearman"] = {
        "rho": float(rho),
        "p": float(p_value),
        "n": len(dados),
        "significativo": p_value < 0.05,
        "interpretacao": (
            "Correlação forte" if abs(rho) > 0.7
            else "Correlação moderada" if abs(rho) > 0.4
            else "Correlação fraca" if abs(rho) > 0.2
            else "Correlação negligível"
        ),
    }

    # Por país
    if "Country" in df.columns:
        por_pais = {}
        for pais in df["Country"].unique():
            sub = df[df["Country"] == pais][["CII", "WI"]].dropna()
            if len(sub) >= 5:
                r, p = stats.spearmanr(sub["CII"], sub["WI"])
                por_pais[pais] = {"rho": float(r), "p": float(p), "n": len(sub)}
        resultados["por_pais"] = por_pais

    return resultados


def teste_h3(df: "pd.DataFrame") -> dict:
    """
    H3: Suportes de circulação íntima (moedas/selos) apresentam FEI
    mais baixo que monumentos.
    Hipótese: rotina fraternal exige feminilidade suavizada.

    Teste: Mann-Whitney U.
    """
    # ─── HIPÓTESE 3 ───────────────────────────────────────────────
    # Fundamentação: A "rotina fraternal" (Pateman) opera através
    # de suportes de circulação íntima (moedas, selos) que entram
    # no cotidiano. Nestes suportes, a feminilidade deve ser
    # "suavizada" (FEI baixo) para ser aceitável na esfera doméstica,
    # enquanto monumentos permitem corporalidade mais explícita.
    # Cf. Painel V: Ubiquidade Íntima.
    #
    # Escolha do teste: Mann-Whitney U (2 grupos: íntimo vs.
    # monumental). alternative="less" pois a hipótese é direcional
    # (íntimo < monumental).
    # ─────────────────────────────────────────────────────────────────
    _check_deps()
    resultados = {"hipotese": "H3", "descricao": "FEI em moedas/selos vs monumentos"}

    if "FEI" not in df.columns or "Support" not in df.columns:
        resultados["erro"] = "Colunas FEI e/ou Support não encontradas"
        return resultados

    intimo = df[df["Support"].isin(["moeda", "selo"])]["FEI"].dropna()
    monumental = df[df["Support"].isin(["monumento", "pintura", "gravura"])]["FEI"].dropna()

    if len(intimo) < 2 or len(monumental) < 2:
        resultados["erro"] = "Dados insuficientes"
        return resultados

    u_stat, p_value = stats.mannwhitneyu(intimo, monumental, alternative="less")

    resultados["mann_whitney"] = {
        "U": float(u_stat),
        "p": float(p_value),
        "significativo": p_value < 0.05,
        "media_intimo": float(intimo.mean()),
        "media_monumental": float(monumental.mean()),
        "n_intimo": len(intimo),
        "n_monumental": len(monumental),
    }

    return resultados


def teste_h4(df: "pd.DataFrame") -> dict:
    """
    H4: Brasil e EUA apresentam RI=1 (branqueamento) em ≥80%
    das imagens pós-1889.

    Teste: Proporção binomial.
    """
    # ─── HIPÓTESE 4 ───────────────────────────────────────────────
    # Fundamentação: Brasil (pós-1889) e EUA compartilham um projeto
    # republicano que instrumentaliza a alegoria feminina branca como
    # símbolo de modernidade. O "branqueamento alegórico" (RI=1) deve
    # estar presente em ≥80% das imagens, confirmando a convergência
    # neoclássica transatlântica como código racial.
    # Cf. Painel IV: República Branca.
    #
    # Escolha do teste: Teste binomial (H0: p = 0.80). Verifica se
    # a proporção observada de RI=1 é estatisticamente compatível
    # com a hipótese de ≥80%.
    # ─────────────────────────────────────────────────────────────────
    _check_deps()
    resultados = {"hipotese": "H4", "descricao": "RI=1 em BR e USA pós-1889"}

    if "RI" not in df.columns or "Country" not in df.columns:
        resultados["erro"] = "Colunas RI e/ou Country não encontradas"
        return resultados

    for pais in ("BR", "USA"):
        filtro = df[(df["Country"] == pais)]
        if "Year" in df.columns:
            filtro = filtro[pd.to_numeric(filtro["Year"], errors="coerce") >= 1889]

        ri_dados = filtro["RI"].dropna()
        if len(ri_dados) < 2:
            resultados[pais] = {"erro": "Dados insuficientes"}
            continue

        n_total = len(ri_dados)
        n_ri1 = int((ri_dados == 1).sum())
        proporcao = n_ri1 / n_total

        # Teste binomial: H0: p = 0.80
        p_value = float(stats.binomtest(n_ri1, n_total, p=0.80, alternative="two-sided").pvalue)

        resultados[pais] = {
            "n_total": n_total,
            "n_RI_1": n_ri1,
            "proporcao": round(proporcao, 3),
            "hipotese_80pct": proporcao >= 0.80,
            "p_binomial": p_value,
        }

    return resultados


def teste_h5(df: "pd.DataFrame") -> dict:
    """
    H5: AI aumenta ao longo do tempo (1789 → 2024).

    Teste: Regressão linear simples (ano como preditor de AI).
    """
    # ─── HIPÓTESE 5 ───────────────────────────────────────────────
    # Fundamentação: A erosão contemporânea da fronteira entre alegoria
    # e pessoa real (AI crescente) reflete a crise da representação
    # simbólica na modernidade tardia. Bardot/Deneuve como Marianne,
    # Thatcher como Britannia, juízas como Justiça: o anacronismo
    # visual persiste mas se transforma.
    # Cf. Painel VI: Damas de Ferro.
    #
    # Escolha do teste: Regressão linear simples (ano como preditor
    # contínuo, AI como variável dependente). O coeficiente angular
    # (slope) indica a taxa de mudança por ano.
    # ─────────────────────────────────────────────────────────────────
    _check_deps()
    resultados = {"hipotese": "H5", "descricao": "AI aumenta ao longo do tempo"}

    if "AI" not in df.columns or "Year" not in df.columns:
        resultados["erro"] = "Colunas AI e/ou Year não encontradas"
        return resultados

    dados = df[["Year", "AI"]].copy()
    dados["Year"] = pd.to_numeric(dados["Year"], errors="coerce")
    dados = dados.dropna()

    if len(dados) < 5:
        resultados["erro"] = "Dados insuficientes (n < 5)"
        return resultados

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        dados["Year"], dados["AI"]
    )

    resultados["regressao"] = {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_value ** 2),
        "p": float(p_value),
        "std_err": float(std_err),
        "n": len(dados),
        "significativo": p_value < 0.05,
        "direcao": "crescente" if slope > 0 else "decrescente",
        "interpretacao": (
            f"Para cada ano adicional, AI aumenta em média {slope:.4f} pontos."
            if slope > 0
            else f"Para cada ano adicional, AI diminui em média {abs(slope):.4f} pontos."
        ),
    }

    return resultados


def executar_todos_testes(df: "pd.DataFrame") -> dict:
    """Executa todos os 5 testes de hipóteses e retorna resultados."""
    return {
        "H1": teste_h1(df),
        "H2": teste_h2(df),
        "H3": teste_h3(df),
        "H4": teste_h4(df),
        "H5": teste_h5(df),
    }


def imprimir_resultados_testes(resultados: dict):
    """Imprime resultados dos testes de forma formatada."""
    for hip_id, res in resultados.items():
        print(f"\n{'='*60}")
        print(f"{hip_id}: {res.get('descricao', '')}")
        print(f"{'='*60}")

        if "erro" in res:
            print(f"  ⚠️  {res['erro']}")
            continue

        for chave, valor in res.items():
            if chave in ("hipotese", "descricao"):
                continue
            if isinstance(valor, dict):
                print(f"\n  {chave}:")
                for k, v in valor.items():
                    if isinstance(v, float):
                        print(f"    {k}: {v:.4f}")
                    else:
                        print(f"    {k}: {v}")
            else:
                print(f"  {chave}: {valor}")


# ---------------------------------------------------------------------------
# Visualizações
# ---------------------------------------------------------------------------

def grafico_distribuicao_indicadores(
    df: "pd.DataFrame",
    output_dir: str = "./output/graficos",
):
    """Gera gráficos de barras para distribuição de cada indicador ordinal."""
    _check_deps()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid", font_scale=1.1)

    for ind in INDICADORES_ORDINAIS + ["RI"]:
        if ind not in df.columns:
            continue

        fig, ax = plt.subplots(figsize=(8, 5))
        counts = df[ind].value_counts().sort_index()
        counts.plot(kind="bar", ax=ax, color="#c4a35a", edgecolor="#2a2826")
        ax.set_title(f"Distribuição — {ind}", fontsize=14, fontweight="bold")
        ax.set_xlabel(ind)
        ax.set_ylabel("Frequência")
        plt.tight_layout()
        fig.savefig(out / f"dist_{ind}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)

    print(f"Gráficos de distribuição salvos em: {out}")


def heatmap_correlacoes(
    df: "pd.DataFrame",
    output_dir: str = "./output/graficos",
):
    """Gera heatmap de correlações (Spearman) entre indicadores ordinais."""
    _check_deps()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    cols = [c for c in INDICADORES_ORDINAIS + ["RI"] if c in df.columns]
    if len(cols) < 2:
        print("Dados insuficientes para heatmap.")
        return

    corr_matrix = df[cols].corr(method="spearman")

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr_matrix,
        annot=True, fmt=".2f",
        cmap="YlOrBr",
        vmin=-1, vmax=1,
        square=True,
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title("Correlações de Spearman entre Indicadores", fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(out / "heatmap_correlacoes.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Heatmap salvo: {out / 'heatmap_correlacoes.png'}")


def boxplots_por_regime(
    df: "pd.DataFrame",
    output_dir: str = "./output/graficos",
):
    """Gera boxplots de indicadores por regime."""
    _check_deps()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if "Regime_preliminary" not in df.columns:
        print("Coluna 'Regime_preliminary' não encontrada.")
        return

    indicadores = [c for c in INDICADORES_ORDINAIS if c in df.columns]
    if not indicadores:
        return

    n_ind = len(indicadores)
    ncols = 3
    nrows = (n_ind + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows))
    axes = axes.flatten() if n_ind > 1 else [axes]

    palette = {"fundacional": "#7a2e3a", "normativo": "#c4a35a", "militar": "#4a4a4a"}

    for i, ind in enumerate(indicadores):
        sns.boxplot(
            data=df, x="Regime_preliminary", y=ind,
            ax=axes[i], palette=palette, order=["fundacional", "normativo", "militar"],
        )
        axes[i].set_title(ind, fontweight="bold")
        axes[i].set_xlabel("")

    # Esconder eixos vazios
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.suptitle("Indicadores por Regime Iconocrático", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(out / "boxplots_regime.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Boxplots salvos: {out / 'boxplots_regime.png'}")


def boxplots_por_pais(
    df: "pd.DataFrame",
    output_dir: str = "./output/graficos",
):
    """Gera boxplots de indicadores por país."""
    _check_deps()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if "Country" not in df.columns:
        print("Coluna 'Country' não encontrada.")
        return

    indicadores = [c for c in INDICADORES_ORDINAIS if c in df.columns]
    if not indicadores:
        return

    n_ind = len(indicadores)
    ncols = 3
    nrows = (n_ind + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows))
    axes = axes.flatten() if n_ind > 1 else [axes]

    for i, ind in enumerate(indicadores):
        sns.boxplot(
            data=df, x="Country", y=ind,
            ax=axes[i], palette="Set2", order=["FR", "UK", "USA", "DE", "BR"],
        )
        axes[i].set_title(ind, fontweight="bold")
        axes[i].set_xlabel("")

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.suptitle("Indicadores por País", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(out / "boxplots_pais.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Boxplots salvos: {out / 'boxplots_pais.png'}")


def scatterplot_cii_wi(
    df: "pd.DataFrame",
    output_dir: str = "./output/graficos",
):
    """Gera scatterplot CII × WI (H2) colorido por país."""
    _check_deps()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if "CII" not in df.columns or "WI" not in df.columns:
        return

    fig, ax = plt.subplots(figsize=(8, 6))

    if "Country" in df.columns:
        sns.scatterplot(
            data=df, x="CII", y="WI", hue="Country",
            style="Country", s=100, alpha=0.7, ax=ax,
        )
    else:
        sns.scatterplot(data=df, x="CII", y="WI", s=100, alpha=0.7, ax=ax)

    # Linha de regressão
    dados = df[["CII", "WI"]].dropna()
    if len(dados) >= 5:
        z = np.polyfit(dados["CII"], dados["WI"], 1)
        p = np.poly1d(z)
        x_line = np.linspace(dados["CII"].min(), dados["CII"].max(), 100)
        ax.plot(x_line, p(x_line), "--", color="gray", alpha=0.5, label="Tendência")

    ax.set_title("H2: CII × WI — Clássico como Código Racial", fontsize=14, fontweight="bold")
    ax.set_xlabel("CII (Classical Ideal Index)")
    ax.set_ylabel("WI (Whiteness Index)")
    ax.legend(title="País")
    plt.tight_layout()
    fig.savefig(out / "scatter_cii_wi.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Scatterplot salvo: {out / 'scatter_cii_wi.png'}")


def grafico_ai_temporal(
    df: "pd.DataFrame",
    output_dir: str = "./output/graficos",
):
    """Gera gráfico de dispersão AI × Year com regressão (H5)."""
    _check_deps()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if "AI" not in df.columns or "Year" not in df.columns:
        return

    dados = df[["Year", "AI"]].copy()
    dados["Year"] = pd.to_numeric(dados["Year"], errors="coerce")
    dados = dados.dropna()

    if len(dados) < 5:
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(dados["Year"], dados["AI"], alpha=0.5, color="#c4a35a", s=50)

    # Regressão
    z = np.polyfit(dados["Year"], dados["AI"], 1)
    p_fn = np.poly1d(z)
    x_line = np.linspace(dados["Year"].min(), dados["Year"].max(), 100)
    ax.plot(x_line, p_fn(x_line), "--", color="#7a2e3a", linewidth=2, label="Regressão linear")

    ax.set_title("H5: Evolução do AI ao Longo do Tempo", fontsize=14, fontweight="bold")
    ax.set_xlabel("Ano")
    ax.set_ylabel("AI (Allegory-Biography Index)")
    ax.legend()
    plt.tight_layout()
    fig.savefig(out / "ai_temporal.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Gráfico temporal salvo: {out / 'ai_temporal.png'}")


def gerar_todas_visualizacoes(df: "pd.DataFrame", output_dir: str = "./output/graficos"):
    """Gera todas as visualizações de uma vez."""
    _check_deps()
    print("Gerando visualizações...")
    grafico_distribuicao_indicadores(df, output_dir)
    heatmap_correlacoes(df, output_dir)
    boxplots_por_regime(df, output_dir)
    boxplots_por_pais(df, output_dir)
    scatterplot_cii_wi(df, output_dir)
    grafico_ai_temporal(df, output_dir)
    print("Todas as visualizações geradas.")


# ---------------------------------------------------------------------------
# Relatório Completo
# ---------------------------------------------------------------------------

def gerar_relatorio_estatistico(
    df: "pd.DataFrame",
    output_dir: str = "./output",
):
    """
    Gera relatório estatístico completo:
    - Tabelas descritivas (CSV)
    - Tabelas cruzadas (CSV)
    - Resultados dos testes H1–H5 (texto)
    - Gráficos (PNG)
    """
    _check_deps()
    out = Path(output_dir)

    print("\n" + "=" * 60)
    print("RELATÓRIO ESTATÍSTICO COMPLETO")
    print("=" * 60)

    # 1. Descritivas
    print("\n>>> Estatísticas Descritivas")
    descritivas_indicadores(df, str(out / "tabelas"))

    # 2. Tabelas cruzadas
    print("\n>>> Tabelas Cruzadas")
    tabelas_cruzadas(df, str(out / "tabelas"))

    # 3. Testes de hipóteses
    print("\n>>> Testes de Hipóteses")
    resultados = executar_todos_testes(df)
    imprimir_resultados_testes(resultados)

    # Salvar resultados em texto
    relatorio_path = out / "relatorios" / "resultados_hipoteses.txt"
    relatorio_path.parent.mkdir(parents=True, exist_ok=True)
    with open(relatorio_path, "w", encoding="utf-8") as f:
        import json
        f.write("RESULTADOS DOS TESTES DE HIPÓTESES\n")
        f.write(f"Data: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"N total: {len(df)}\n")
        f.write("=" * 60 + "\n\n")
        f.write(json.dumps(resultados, indent=2, ensure_ascii=False, default=str))
    print(f"\nResultados salvos: {relatorio_path}")

    # 4. Visualizações
    print("\n>>> Visualizações")
    gerar_todas_visualizacoes(df, str(out / "graficos"))

    print("\n" + "=" * 60)
    print("Relatório completo gerado.")
    print(f"Diretório: {out}")
    print("=" * 60)


if __name__ == "__main__":
    # Exemplo com dados simulados
    _check_deps()

    np.random.seed(42)
    n = 100

    df_exemplo = pd.DataFrame({
        "Image_ID": [f"{i:04d}" for i in range(1, n + 1)],
        "Country": np.random.choice(["FR", "UK", "USA", "DE", "BR"], n),
        "Support": np.random.choice(["moeda", "selo", "monumento", "pintura", "gravura"], n),
        "Regime_preliminary": np.random.choice(["fundacional", "normativo", "militar"], n, p=[0.3, 0.4, 0.3]),
        "Year": np.random.choice(range(1789, 2025), n),
        "FEI": np.random.choice([0, 1, 2, 3], n, p=[0.1, 0.3, 0.4, 0.2]),
        "CII": np.random.choice([0, 1, 2, 3], n, p=[0.15, 0.25, 0.35, 0.25]),
        "PRI": np.random.choice(["serena", "militante", "sacrificial"], n, p=[0.5, 0.3, 0.2]),
        "SMI": np.random.choice([0, 1, 2, 3], n, p=[0.1, 0.3, 0.4, 0.2]),
        "SMS": np.random.choice(["serena", "militante", "sacrificial"], n, p=[0.5, 0.3, 0.2]),
        "AMCP": np.random.choice([0, 1, 2, 3], n, p=[0.3, 0.25, 0.25, 0.2]),
        "MVI": np.random.choice([0, 1, 2, 3], n, p=[0.4, 0.3, 0.2, 0.1]),
        "WI": np.random.choice([0, 1, 2, 3], n, p=[0.1, 0.25, 0.4, 0.25]),
        "RI": np.random.choice([0, 1], n, p=[0.3, 0.7]),
        "AI": np.random.choice([0, 1, 2, 3], n, p=[0.4, 0.3, 0.2, 0.1]),
    })

    gerar_relatorio_estatistico(df_exemplo)
