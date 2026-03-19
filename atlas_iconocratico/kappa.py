"""
kappa.py — Confiabilidade Inter-Codificadores (Cohen's Kappa)
==============================================================
Módulo de validação metodológica que implementa o protocolo de
confiabilidade inter-codificadores da Fase 7.2 da tese.

FUNDAMENTAÇÃO METODOLÓGICA:
    A confiabilidade inter-codificadores é requisito essencial em
    análise de conteúdo quantitativa (Krippendorff, 2004). Sem ela,
    os resultados da codificação seriam subjetivos e não-replicáveis.

    Este módulo implementa o coeficiente Kappa de Cohen (1960),
    que corrige a concordância bruta pela concordância esperada
    ao acaso. Interpretação conforme Landis & Koch (1977):
        κ ≥ 0.81  →  concordância quase perfeita
        κ 0.61–0.80  →  concordância substancial
        κ 0.41–0.60  →  concordância moderada
        κ 0.21–0.40  →  concordância razoável
        κ ≤ 0.20  →  concordância leve

    Para a tese, adotamos limiares mais exigentes:
        κ ≥ 0.80  →  EXCELENTE → manter indicador como está
        κ 0.60–0.79  →  MODERADA → revisar definições operacionais
        κ < 0.60  →  BAIXA → redefinir ou eliminar indicador

TIPOS DE KAPPA:
    - Weighted (linear): para indicadores ordinais (FEI, CII, SMI,
      AMCP, MVI, WI, AI). Pondera discordâncias pela distância
      entre valores (erro de 0→1 pesa menos que 0→3).
    - Unweighted: para indicadores categóricos (PRI, SMS) e
      booleano (RI). Toda discordância tem peso igual.

PROTOCOLO COMPLETO (cf. tese, Meses 9–10):
    1. Codificador 1 codifica 50 imagens-piloto
    2. Codificador 2 codifica as mesmas 50 independentemente
    3. Calcular Kappa por indicador
    4. Identificar discordâncias específicas (quais imagens, quais
       indicadores) → pauta para reunião de consenso
    5. Ajustar manual de codificação (versão 2.0)
    6. Re-testar com 20 imagens (subsample) até κ ≥ 0.80 em todos
    7. Na codificação completa: recalcular a cada 100 imagens
       para monitorar drift temporal do codificador

REFERÊNCIAS:
    - Cohen, J. (1960). A coefficient of agreement for nominal scales.
    - Landis, J. R. & Koch, G. G. (1977). The measurement of observer
      agreement for categorical data.
    - Krippendorff, K. (2004). Content Analysis.

Dependências:
    pip install pandas numpy scikit-learn
"""

from pathlib import Path
from typing import Optional

try:
    import pandas as pd
    import numpy as np
    from sklearn.metrics import cohen_kappa_score, confusion_matrix
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

from .codificacao import (
    INDICADORES_ORDINAIS,
    INDICADORES_CATEGORICOS,
    INDICADORES_BOOLEANOS,
    TODOS_INDICADORES,
)


def _check_deps():
    if not HAS_DEPS:
        raise ImportError(
            "Dependências não encontradas. Instale com:\n"
            "  pip install pandas numpy scikit-learn"
        )


# ---------------------------------------------------------------------------
# Cálculo de Kappa
# ---------------------------------------------------------------------------

def calcular_kappa_indicador(
    dados_cod1: list,
    dados_cod2: list,
    tipo: str = "ordinal",
) -> dict:
    """
    Calcula Cohen's Kappa para um indicador específico.

    Args:
        dados_cod1: Lista de valores do codificador 1.
        dados_cod2: Lista de valores do codificador 2.
        tipo: "ordinal" (weighted) ou "categórico" (unweighted).

    Returns:
        Dicionário com kappa, concordância percentual e classificação.
    """
    _check_deps()

    if len(dados_cod1) != len(dados_cod2):
        raise ValueError("Listas de codificações devem ter o mesmo tamanho")

    n = len(dados_cod1)

    # Concordância bruta
    concordancias = sum(1 for a, b in zip(dados_cod1, dados_cod2) if a == b)
    concordancia_pct = concordancias / n * 100

    # Cohen's Kappa
    if tipo == "ordinal":
        # Weighted kappa (linear) para dados ordinais
        kappa = cohen_kappa_score(dados_cod1, dados_cod2, weights="linear")
    else:
        # Unweighted kappa para dados categóricos
        kappa = cohen_kappa_score(dados_cod1, dados_cod2)

    # Classificação
    if kappa >= 0.80:
        classificacao = "excelente"
        acao = "manter indicador"
    elif kappa >= 0.60:
        classificacao = "moderada"
        acao = "revisar definições operacionais"
    elif kappa >= 0.40:
        classificacao = "razoável"
        acao = "redefinir indicador"
    else:
        classificacao = "baixa"
        acao = "eliminar ou reformular completamente"

    return {
        "kappa": float(kappa),
        "concordancia_pct": round(concordancia_pct, 1),
        "n": n,
        "concordancias": concordancias,
        "discordancias": n - concordancias,
        "classificacao": classificacao,
        "acao": acao,
    }


def calcular_kappa_todos(
    csv_cod1: str,
    csv_cod2: str,
) -> dict:
    """
    Calcula Kappa para todos os 10 indicadores a partir de dois CSVs.

    Args:
        csv_cod1: Caminho do CSV do codificador 1.
        csv_cod2: Caminho do CSV do codificador 2.

    Returns:
        Dicionário com resultados por indicador.
    """
    _check_deps()

    df1 = pd.read_csv(csv_cod1)
    df2 = pd.read_csv(csv_cod2)

    # Alinhar por Image_ID
    ids_comuns = set(df1["Image_ID"].astype(str)) & set(df2["Image_ID"].astype(str))
    if not ids_comuns:
        raise ValueError("Nenhum Image_ID em comum entre os dois codificadores")

    df1 = df1[df1["Image_ID"].astype(str).isin(ids_comuns)].sort_values("Image_ID")
    df2 = df2[df2["Image_ID"].astype(str).isin(ids_comuns)].sort_values("Image_ID")

    resultados = {"n_imagens": len(ids_comuns), "indicadores": {}}

    # Indicadores ordinais (weighted kappa)
    for ind in INDICADORES_ORDINAIS:
        if ind in df1.columns and ind in df2.columns:
            dados1 = df1[ind].astype(int).tolist()
            dados2 = df2[ind].astype(int).tolist()
            resultados["indicadores"][ind] = calcular_kappa_indicador(
                dados1, dados2, tipo="ordinal"
            )

    # Indicadores categóricos (unweighted kappa)
    for ind in INDICADORES_CATEGORICOS:
        if ind in df1.columns and ind in df2.columns:
            dados1 = df1[ind].astype(str).tolist()
            dados2 = df2[ind].astype(str).tolist()
            resultados["indicadores"][ind] = calcular_kappa_indicador(
                dados1, dados2, tipo="categórico"
            )

    # Indicador booleano
    for ind in INDICADORES_BOOLEANOS:
        if ind in df1.columns and ind in df2.columns:
            dados1 = df1[ind].astype(int).tolist()
            dados2 = df2[ind].astype(int).tolist()
            resultados["indicadores"][ind] = calcular_kappa_indicador(
                dados1, dados2, tipo="categórico"
            )

    # Resumo geral
    kappas = [r["kappa"] for r in resultados["indicadores"].values()]
    resultados["resumo"] = {
        "media_kappa": round(float(np.mean(kappas)), 3) if kappas else 0,
        "min_kappa": round(float(min(kappas)), 3) if kappas else 0,
        "max_kappa": round(float(max(kappas)), 3) if kappas else 0,
        "n_excelente": sum(1 for k in kappas if k >= 0.80),
        "n_moderada": sum(1 for k in kappas if 0.60 <= k < 0.80),
        "n_baixa": sum(1 for k in kappas if k < 0.60),
        "todos_acima_080": all(k >= 0.80 for k in kappas),
    }

    return resultados


# ---------------------------------------------------------------------------
# Relatório de Confiabilidade
# ---------------------------------------------------------------------------

def imprimir_relatorio_kappa(resultados: dict):
    """Imprime relatório formatado de confiabilidade."""
    print("\n" + "=" * 70)
    print("RELATÓRIO DE CONFIABILIDADE INTER-CODIFICADORES")
    print("=" * 70)
    print(f"Imagens avaliadas: {resultados['n_imagens']}")

    print(f"\n{'Indicador':<10} {'Kappa':>8} {'Conc.%':>8} {'n':>5} {'Classificação':<15} {'Ação'}")
    print("─" * 70)

    for ind, res in resultados["indicadores"].items():
        kappa = res["kappa"]
        # Colorir por classificação
        if kappa >= 0.80:
            status = "✅"
        elif kappa >= 0.60:
            status = "⚠️ "
        else:
            status = "❌"

        print(
            f"  {status} {ind:<8} {kappa:>7.3f} {res['concordancia_pct']:>7.1f}% "
            f"{res['n']:>4d}  {res['classificacao']:<15} {res['acao']}"
        )

    # Resumo
    r = resultados["resumo"]
    print(f"\n{'─'*70}")
    print(f"Média Kappa:  {r['media_kappa']:.3f}")
    print(f"Mínimo:       {r['min_kappa']:.3f}")
    print(f"Máximo:       {r['max_kappa']:.3f}")
    print(f"Excelente (≥0.80): {r['n_excelente']}")
    print(f"Moderada (0.60–0.79): {r['n_moderada']}")
    print(f"Baixa (<0.60): {r['n_baixa']}")

    if r["todos_acima_080"]:
        print("\n✅ APROVADO: Todos os indicadores atingem Kappa ≥ 0.80")
    else:
        print("\n❌ PENDENTE: Alguns indicadores precisam de revisão")


def salvar_relatorio_kappa(
    resultados: dict,
    caminho: str = "./data/relatorio_kappa.csv",
):
    """Salva relatório de Kappa como CSV."""
    _check_deps()
    rows = []
    for ind, res in resultados["indicadores"].items():
        rows.append({
            "Indicador": ind,
            "Kappa": res["kappa"],
            "Concordancia_pct": res["concordancia_pct"],
            "n": res["n"],
            "Concordancias": res["concordancias"],
            "Discordancias": res["discordancias"],
            "Classificacao": res["classificacao"],
            "Acao": res["acao"],
        })

    df = pd.DataFrame(rows)
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8")
    print(f"Relatório Kappa salvo: {caminho}")


def identificar_discordancias(
    csv_cod1: str,
    csv_cod2: str,
    indicador: str,
) -> "pd.DataFrame":
    """
    Identifica imagens com discordância entre codificadores
    para um indicador específico. Útil para reunião de consenso.
    """
    _check_deps()

    df1 = pd.read_csv(csv_cod1)
    df2 = pd.read_csv(csv_cod2)

    merge = df1[["Image_ID", indicador]].merge(
        df2[["Image_ID", indicador]],
        on="Image_ID",
        suffixes=("_cod1", "_cod2"),
    )

    col1 = f"{indicador}_cod1"
    col2 = f"{indicador}_cod2"
    discordancias = merge[merge[col1] != merge[col2]]

    discordancias["diferenca"] = discordancias.apply(
        lambda row: abs(int(row[col1]) - int(row[col2]))
        if str(row[col1]).isdigit() and str(row[col2]).isdigit()
        else "categórica",
        axis=1,
    )

    return discordancias.sort_values("Image_ID")


# ---------------------------------------------------------------------------
# Monitoramento de Drift
# ---------------------------------------------------------------------------

def verificar_drift(
    csv_codificador: str,
    indicador: str,
    janela: int = 100,
) -> list[dict]:
    """
    Verifica drift de codificação ao longo do tempo.
    Compara médias/distribuições em janelas de N imagens.

    Args:
        csv_codificador: CSV do codificador.
        indicador: Indicador a verificar.
        janela: Tamanho da janela.

    Returns:
        Lista de dicionários com estatísticas por janela.
    """
    _check_deps()

    df = pd.read_csv(csv_codificador)
    if indicador not in df.columns:
        return []

    dados = df[indicador].dropna()
    n = len(dados)

    if n < janela:
        return [{"janela": f"1–{n}", "media": float(dados.mean()), "std": float(dados.std())}]

    resultados = []
    for i in range(0, n, janela):
        subconjunto = dados.iloc[i:i + janela]
        resultados.append({
            "janela": f"{i+1}–{min(i+janela, n)}",
            "n": len(subconjunto),
            "media": round(float(subconjunto.mean()), 3),
            "std": round(float(subconjunto.std()), 3),
            "mediana": float(subconjunto.median()),
        })

    # Verificar mudança significativa entre janelas
    if len(resultados) >= 2:
        for i in range(1, len(resultados)):
            diff = abs(resultados[i]["media"] - resultados[0]["media"])
            resultados[i]["drift_from_baseline"] = round(diff, 3)
            resultados[i]["alerta_drift"] = diff > 0.5  # threshold

    return resultados


if __name__ == "__main__":
    _check_deps()
    # Simulação de dois codificadores
    np.random.seed(42)
    n_imagens = 50

    # Codificador 1
    dados_cod1 = {
        "Image_ID": [f"{i:04d}" for i in range(1, n_imagens + 1)],
        "FEI": np.random.choice([0, 1, 2, 3], n_imagens),
        "CII": np.random.choice([0, 1, 2, 3], n_imagens),
        "PRI": np.random.choice(["serena", "militante", "sacrificial"], n_imagens),
        "SMI": np.random.choice([0, 1, 2, 3], n_imagens),
        "SMS": np.random.choice(["serena", "militante", "sacrificial"], n_imagens),
        "AMCP": np.random.choice([0, 1, 2, 3], n_imagens),
        "MVI": np.random.choice([0, 1, 2, 3], n_imagens),
        "WI": np.random.choice([0, 1, 2, 3], n_imagens),
        "RI": np.random.choice([0, 1], n_imagens),
        "AI": np.random.choice([0, 1, 2, 3], n_imagens),
    }
    df1 = pd.DataFrame(dados_cod1)

    # Codificador 2 (com 80% concordância simulada)
    dados_cod2 = dados_cod1.copy()
    for col in ["FEI", "CII", "SMI", "AMCP", "MVI", "WI", "AI"]:
        arr = np.array(dados_cod1[col])
        mask = np.random.random(n_imagens) > 0.80  # 20% discordância
        arr[mask] = np.random.choice([0, 1, 2, 3], mask.sum())
        dados_cod2[col] = arr
    for col in ["PRI", "SMS"]:
        arr = list(dados_cod1[col])
        for i in range(n_imagens):
            if np.random.random() > 0.80:
                arr[i] = np.random.choice(["serena", "militante", "sacrificial"])
        dados_cod2[col] = arr
    dados_cod2["RI"] = [
        v if np.random.random() > 0.15 else 1 - v
        for v in dados_cod1["RI"]
    ]
    df2 = pd.DataFrame(dados_cod2)

    # Salvar CSVs temporários
    Path("./data").mkdir(parents=True, exist_ok=True)
    df1.to_csv("./data/codificacao_COD1.csv", index=False)
    df2.to_csv("./data/codificacao_COD2.csv", index=False)

    # Calcular Kappa
    resultados = calcular_kappa_todos(
        "./data/codificacao_COD1.csv",
        "./data/codificacao_COD2.csv",
    )
    imprimir_relatorio_kappa(resultados)
    salvar_relatorio_kappa(resultados)
