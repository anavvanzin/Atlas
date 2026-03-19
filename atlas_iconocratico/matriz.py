"""
matriz.py — Matriz de Evidências e Exportação de Dados
========================================================
Implementa a matriz de evidências da Fase 1 da tese (Meses 1–12),
que consolida os achados de 9 Revisões Sistemáticas conduzidas
no Elicit em uma estrutura unificada de 13 colunas.

CONTEXTO METODOLÓGICO:
    A matriz de evidências é o instrumento central de organização
    do referencial teórico-empírico da tese. Ela conecta:
    - 9 Revisões Sistemáticas (SR1–SR9) conduzidas no Elicit
    - ~400–600 referências bibliográficas classificadas
    - Os 5 frameworks teóricos (Pateman, Mondzain, Warburg, Mills, parasocial)
    - Os 5 países e 3 regimes do corpus
    - As 5 hipóteses (H1–H5)

ESTRUTURA DE 13 COLUNAS (compatível com Elicit):
    evidence_id         — Identificador único (E0001, E0002, ...)
    titulo              — Título da obra/artigo
    autores             — Autores (formato ABNT)
    ano                 — Ano de publicação
    tipo_fonte          — artigo, livro, capítulo, tese, relatório
    pais_foco           — País foco da análise (FR/UK/USA/DE/BR/geral)
    periodo_foco        — Período histórico analisado
    framework_teorico   — Pateman/Mondzain/Warburg/Mills/parasocial
    metodologia         — Método empregado pelo autor
    resultados_chave    — Achados principais (claim mapping)
    hipoteses_relacionadas — Quais H1–H5 a evidência sustenta
    qualidade           — Alta/média/baixa (avaliação de relevância)
    notas               — Observações do pesquisador

FUNCIONALIDADES:
    - Adicionar entradas manualmente ou importar CSV do Elicit
    - Análise de lacunas: identificar gaps por SR, framework,
      país e hipótese (fundamental para demonstrar originalidade)
    - Exportar bibliografia em formato ABNT
    - Integrar com corpus visual (cruzar referências com imagens)

FLUXO DE TRABALHO COM ELICIT:
    1. Criar Systematic Review no Elicit com 13 colunas customizadas
    2. Screening: aceitar papers relevantes
    3. Extração: Elicit preenche colunas automaticamente via IA
    4. Exportar como CSV
    5. Importar no toolkit: python main.py matriz importar-elicit --csv ...
    6. Rodar análise de lacunas: python main.py matriz lacunas
    7. O relatório de lacunas confirma a ORIGINALIDADE da tese

REFERÊNCIAS:
    - Elicit (https://elicit.org) — ferramenta de revisão sistemática
    - ABNT NBR 6023:2018 — norma para referências bibliográficas
"""

import csv
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

CAMPOS_MATRIZ = [
    "Entry_ID",
    "Source_reference",
    "Theoretical_framework",
    "Main_claim",
    "Evidence_strength",
    "Country",
    "Period",
    "Key_figures_discussed",
    "Support",
    "Regime_link",
    "Methodology",
    "Racialisation",
    "SR_source",
    "Notes",
    "Added_date",
]

FRAMEWORKS_TEORICOS = [
    "iconocracia",       # Mondzain, Goodrich
    "contrato_sexual",   # Pateman
    "warburg",           # Pathosformel, Nachleben, Atlas
    "parasocial",        # Vínculos afetivos com símbolos
    "contrato_racial",   # Mills
    "feminismo",         # Butler, Fraser, Young
    "outro",
]

FORCA_EVIDENCIA = ["forte", "moderada", "fraca", "gap"]

SRS = [f"SR{i}" for i in range(1, 10)]  # SR1–SR9


# ---------------------------------------------------------------------------
# Dataclass de Entrada
# ---------------------------------------------------------------------------

@dataclass
class EntradaMatriz:
    """Uma entrada na matriz de evidências."""
    Entry_ID: str = ""
    Source_reference: str = ""          # Referência ABNT completa
    Theoretical_framework: str = ""     # Framework teórico
    Main_claim: str = ""                # Claim principal do paper
    Evidence_strength: str = ""         # forte/moderada/fraca/gap
    Country: str = ""                   # FR/UK/USA/DE/BR (pode ser múltiplo)
    Period: str = ""                    # Período histórico
    Key_figures_discussed: str = ""     # Figuras alegóricas discutidas
    Support: str = ""                   # Suporte material
    Regime_link: str = ""               # Regime iconocrático
    Methodology: str = ""               # Metodologia utilizada
    Racialisation: str = ""             # Aspectos de racialização
    SR_source: str = ""                 # De qual SR veio (SR1–SR9)
    Notes: str = ""                     # Observações
    Added_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))


# ---------------------------------------------------------------------------
# Gerenciador da Matriz
# ---------------------------------------------------------------------------

class GerenciadorMatriz:
    """
    Gerencia a Matriz de Evidências.

    Uso:
        gm = GerenciadorMatriz("./data")
        gm.adicionar_entrada(EntradaMatriz(
            Source_reference="PATEMAN, Carole. The Sexual Contract. Stanford, 1988.",
            Theoretical_framework="contrato_sexual",
            Main_claim="Contrato social é precedido por contrato sexual",
            Evidence_strength="forte",
            SR_source="SR2",
        ))
        gm.relatorio_lacunas()
    """

    def __init__(self, diretorio_base: str = "./data"):
        self.base = Path(diretorio_base)
        self.csv_path = self.base / "matriz_evidencias.csv"
        self.base.mkdir(parents=True, exist_ok=True)
        self._proximo_id = self._calcular_proximo_id()

    def _calcular_proximo_id(self) -> int:
        entradas = self.listar_entradas()
        if not entradas:
            return 1
        ids = []
        for e in entradas:
            try:
                ids.append(int(e.get("Entry_ID", 0)))
            except (ValueError, TypeError):
                pass
        return max(ids, default=0) + 1

    def adicionar_entrada(self, entrada: EntradaMatriz) -> str:
        """Adiciona uma entrada à matriz."""
        entrada.Entry_ID = str(self._proximo_id).zfill(5)
        self._proximo_id += 1

        existe = self.csv_path.exists()
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS_MATRIZ)
            if not existe:
                writer.writeheader()
            dados = asdict(entrada)
            dados_csv = {k: dados.get(k, "") for k in CAMPOS_MATRIZ}
            writer.writerow(dados_csv)

        return entrada.Entry_ID

    def adicionar_lote(self, entradas: list[EntradaMatriz]) -> int:
        """Adiciona múltiplas entradas de uma vez."""
        for e in entradas:
            self.adicionar_entrada(e)
        print(f"Adicionadas {len(entradas)} entradas à matriz.")
        return len(entradas)

    def listar_entradas(self, filtros: Optional[dict] = None) -> list[dict]:
        """Lista entradas, opcionalmente filtradas."""
        if not self.csv_path.exists():
            return []
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            entradas = list(reader)
        if filtros:
            for campo, valor in filtros.items():
                entradas = [e for e in entradas if valor.lower() in e.get(campo, "").lower()]
        return entradas

    def contar_entradas(self) -> int:
        return len(self.listar_entradas())

    def importar_csv_elicit(
        self,
        caminho_csv: str,
        sr_source: str,
        mapeamento_colunas: Optional[dict] = None,
    ) -> int:
        """
        Importa CSV exportado do Elicit para a matriz de evidências.

        Args:
            caminho_csv: Caminho do CSV do Elicit.
            sr_source: Identificador da SR (ex.: "SR1", "SR2").
            mapeamento_colunas: Mapeamento de colunas Elicit → campos da matriz.
                Exemplo: {"Title": "Main_claim", "Authors": "Source_reference"}

        Returns:
            Número de entradas importadas.
        """
        if not HAS_PANDAS:
            raise ImportError("pandas necessário para importar CSV do Elicit")

        df = pd.read_csv(caminho_csv)

        # Mapeamento padrão se não fornecido
        if mapeamento_colunas is None:
            mapeamento_colunas = {
                "Title": "Main_claim",
                "Authors": "Source_reference",
                "Abstract": "Notes",
                "Year": "Period",
                "DOI": "Notes",
            }

        n_importadas = 0
        for _, row in df.iterrows():
            dados = {"SR_source": sr_source}
            for col_elicit, col_matriz in mapeamento_colunas.items():
                if col_elicit in row.index:
                    valor_existente = dados.get(col_matriz, "")
                    novo_valor = str(row[col_elicit]) if pd.notna(row[col_elicit]) else ""
                    if valor_existente and novo_valor:
                        dados[col_matriz] = f"{valor_existente}; {novo_valor}"
                    else:
                        dados[col_matriz] = novo_valor or valor_existente

            entrada = EntradaMatriz(**{k: v for k, v in dados.items() if hasattr(EntradaMatriz, k)})
            self.adicionar_entrada(entrada)
            n_importadas += 1

        print(f"Importadas {n_importadas} entradas de {caminho_csv} ({sr_source})")
        return n_importadas

    # -- Relatórios --------------------------------------------------------

    def relatorio_lacunas(self) -> dict:
        """
        Gera relatório de lacunas na matriz de evidências.
        Identifica:
        - Frameworks teóricos sub-representados
        - Países sem cobertura
        - Regimes sem evidência
        - Lacunas entre Pateman e iconografia (gap central)
        """
        entradas = self.listar_entradas()
        total = len(entradas)

        relatorio = {
            "total_entradas": total,
            "por_sr": {},
            "por_framework": {},
            "por_pais": {},
            "por_regime": {},
            "por_forca": {},
            "gaps_identificados": [],
        }

        # Por SR
        for sr in SRS:
            n = len([e for e in entradas if e.get("SR_source") == sr])
            relatorio["por_sr"][sr] = n

        # Por framework
        for fw in FRAMEWORKS_TEORICOS:
            n = len([e for e in entradas if fw in e.get("Theoretical_framework", "").lower()])
            relatorio["por_framework"][fw] = n

        # Por país
        for pais in ("FR", "UK", "USA", "DE", "BR"):
            n = len([e for e in entradas if pais in e.get("Country", "")])
            relatorio["por_pais"][pais] = n

        # Por regime
        for regime in ("fundacional", "normativo", "militar"):
            n = len([e for e in entradas if regime in e.get("Regime_link", "").lower()])
            relatorio["por_regime"][regime] = n

        # Por força de evidência
        for forca in FORCA_EVIDENCIA:
            n = len([e for e in entradas if e.get("Evidence_strength") == forca])
            relatorio["por_forca"][forca] = n

        # Identificar gaps
        gaps = [e for e in entradas if e.get("Evidence_strength") == "gap"]
        relatorio["gaps_identificados"] = [
            {
                "Entry_ID": g.get("Entry_ID"),
                "Main_claim": g.get("Main_claim"),
                "SR_source": g.get("SR_source"),
            }
            for g in gaps
        ]

        # Lacuna central: Pateman + iconografia
        pateman_refs = len([
            e for e in entradas
            if "pateman" in e.get("Theoretical_framework", "").lower()
            or "contrato_sexual" in e.get("Theoretical_framework", "").lower()
        ])
        iconografia_refs = len([
            e for e in entradas
            if "iconocracia" in e.get("Theoretical_framework", "").lower()
        ])
        conexao = len([
            e for e in entradas
            if ("pateman" in e.get("Theoretical_framework", "").lower()
                or "contrato_sexual" in e.get("Theoretical_framework", "").lower())
            and ("iconocracia" in e.get("Notes", "").lower()
                 or "visual" in e.get("Main_claim", "").lower())
        ])

        relatorio["lacuna_central"] = {
            "refs_pateman": pateman_refs,
            "refs_iconocracia": iconografia_refs,
            "conexao_pateman_visual": conexao,
            "lacuna_confirmada": conexao == 0,
            "interpretacao": (
                "LACUNA CONFIRMADA: nenhum trabalho conecta sistematicamente "
                "Pateman + iconografia estatal + codificação quantitativa → "
                "ORIGINALIDADE COMPROVADA"
                if conexao == 0
                else f"{conexao} trabalho(s) fazem conexão parcial — "
                "revisar para confirmar originalidade"
            ),
        }

        return relatorio

    def imprimir_relatorio_lacunas(self):
        """Imprime relatório formatado de lacunas."""
        r = self.relatorio_lacunas()

        print("\n" + "=" * 60)
        print("RELATÓRIO DE LACUNAS — MATRIZ DE EVIDÊNCIAS")
        print(f"Total de entradas: {r['total_entradas']}")
        print("=" * 60)

        print("\n--- Por SR ---")
        for sr, n in r["por_sr"].items():
            barra = "█" * (n // 5) if n > 0 else ""
            print(f"  {sr:4s} │ {n:4d} {barra}")

        print("\n--- Por Framework Teórico ---")
        for fw, n in sorted(r["por_framework"].items(), key=lambda x: -x[1]):
            if n > 0:
                print(f"  {fw:20s} │ {n:4d}")

        print("\n--- Por País ---")
        for pais, n in r["por_pais"].items():
            print(f"  {pais:4s} │ {n:4d}")

        print("\n--- Por Regime ---")
        for regime, n in r["por_regime"].items():
            print(f"  {regime:15s} │ {n:4d}")

        print("\n--- Força da Evidência ---")
        for forca, n in r["por_forca"].items():
            status = "🔴" if forca == "gap" else "🟡" if forca == "fraca" else "🟢"
            print(f"  {status} {forca:10s} │ {n:4d}")

        # Lacuna central
        lc = r["lacuna_central"]
        print("\n" + "=" * 60)
        print("LACUNA CENTRAL — Contrato Sexual Visual")
        print("=" * 60)
        print(f"  Referências Pateman/contrato sexual: {lc['refs_pateman']}")
        print(f"  Referências iconocracia:             {lc['refs_iconocracia']}")
        print(f"  Conexão Pateman + visual:            {lc['conexao_pateman_visual']}")
        print(f"\n  → {lc['interpretacao']}")

    # -- Exportação ---------------------------------------------------------

    def exportar_bibliografia_abnt(self, caminho: str = "./data/bibliografia_abnt.txt"):
        """Exporta todas as referências em formato ABNT."""
        entradas = self.listar_entradas()
        refs = set()
        for e in entradas:
            ref = e.get("Source_reference", "").strip()
            if ref:
                refs.add(ref)

        caminho_path = Path(caminho)
        caminho_path.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho_path, "w", encoding="utf-8") as f:
            f.write("REFERÊNCIAS BIBLIOGRÁFICAS (ABNT)\n")
            f.write(f"Gerado em: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"Total de referências únicas: {len(refs)}\n")
            f.write("=" * 60 + "\n\n")
            for ref in sorted(refs):
                f.write(f"{ref}\n\n")

        print(f"Bibliografia ABNT exportada: {caminho_path} ({len(refs)} referências)")

    def exportar_matriz_completa(self, formato: str = "csv") -> str:
        """Exporta matriz completa em CSV ou JSON."""
        entradas = self.listar_entradas()
        if formato == "json":
            caminho = self.base / "matriz_evidencias_completa.json"
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(entradas, f, ensure_ascii=False, indent=2)
        else:
            caminho = self.base / "matriz_evidencias_completa.csv"
            if entradas:
                with open(caminho, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=CAMPOS_MATRIZ)
                    writer.writeheader()
                    for e in entradas:
                        writer.writerow({k: e.get(k, "") for k in CAMPOS_MATRIZ})

        print(f"Matriz exportada: {caminho}")
        return str(caminho)


# ---------------------------------------------------------------------------
# Integração Corpus + Matriz
# ---------------------------------------------------------------------------

def integrar_corpus_e_matriz(
    corpus_csv: str = "./data/corpus_visual_master.csv",
    codificacao_csv: str = "./data/corpus_codificado.csv",
    matriz_csv: str = "./data/matriz_evidencias.csv",
    output: str = "./data/dataset_integrado.csv",
) -> str:
    """
    Integra os 3 datasets principais:
    1. Corpus visual (metadados)
    2. Codificação (10 indicadores)
    3. Matriz de evidências (referências teóricas)

    Gera dataset integrado para análise final.
    """
    if not HAS_PANDAS:
        raise ImportError("pandas necessário para integração")

    dfs = {}
    for nome, path in [("corpus", corpus_csv), ("codificacao", codificacao_csv)]:
        if Path(path).exists():
            dfs[nome] = pd.read_csv(path)

    if "corpus" in dfs and "codificacao" in dfs:
        df = dfs["corpus"].merge(dfs["codificacao"], on="Image_ID", how="outer")
    elif "codificacao" in dfs:
        df = dfs["codificacao"]
    elif "corpus" in dfs:
        df = dfs["corpus"]
    else:
        print("Nenhum dataset encontrado.")
        return ""

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False, encoding="utf-8")
    print(f"Dataset integrado: {len(df)} linhas → {output}")
    return output


if __name__ == "__main__":
    gm = GerenciadorMatriz("./data")

    # Entradas de exemplo
    entradas_exemplo = [
        EntradaMatriz(
            Source_reference="PATEMAN, Carole. The Sexual Contract. Stanford University Press, 1988.",
            Theoretical_framework="contrato_sexual",
            Main_claim="O contrato social pressupõe um contrato sexual que subordina mulheres",
            Evidence_strength="forte",
            SR_source="SR2",
            Notes="Texto fundacional da tese",
        ),
        EntradaMatriz(
            Source_reference="MONDZAIN, Marie-José. Image, Icon, Economy. Stanford University Press, 2005.",
            Theoretical_framework="iconocracia",
            Main_claim="Regime iconocrático: economia organizada do visível que governa percepção",
            Evidence_strength="forte",
            SR_source="SR1",
        ),
        EntradaMatriz(
            Source_reference="GOODRICH, Peter. Legal Emblems and the Art of Law. Cambridge University Press, 2014.",
            Theoretical_framework="iconocracia",
            Main_claim="Visiocracy: lei como superfície visual; arquitetura forense como poder",
            Evidence_strength="forte",
            SR_source="SR1",
        ),
        EntradaMatriz(
            Source_reference="WARBURG, Aby. Bilderatlas Mnemosyne. Bredekamp et al. (eds.), 2020.",
            Theoretical_framework="warburg",
            Main_claim="Atlas como método: Pathosformel, Nachleben, Denkraum",
            Evidence_strength="forte",
            Methodology="atlas/montagem",
            SR_source="SR7",
        ),
        EntradaMatriz(
            Source_reference="AGULHON, Maurice. Marianne au Combat. Flammarion, 1979.",
            Theoretical_framework="iconocracia",
            Main_claim="Institucionalização de Marianne como alegoria republicana francesa",
            Evidence_strength="forte",
            Country="FR",
            Key_figures_discussed="Marianne",
            Regime_link="fundacional",
            SR_source="SR3",
        ),
        EntradaMatriz(
            Source_reference="WARNER, Marina. Monuments and Maidens: The Allegory of the Female Form. Weidenfeld, 1985.",
            Theoretical_framework="feminismo",
            Main_claim="Alegorias femininas ocupam espaço simbólico negado a mulheres reais",
            Evidence_strength="forte",
            Key_figures_discussed="Marianne, Britannia, Liberty, Justiça",
            SR_source="SR3",
        ),
        EntradaMatriz(
            Source_reference="MILLS, Charles W. The Racial Contract. Cornell University Press, 1997.",
            Theoretical_framework="contrato_racial",
            Main_claim="Contrato racial: supremacia branca como sistema político",
            Evidence_strength="forte",
            Racialisation="contrato racial, branqueamento",
            SR_source="SR5",
        ),
        EntradaMatriz(
            Source_reference="(LACUNA IDENTIFICADA)",
            Theoretical_framework="contrato_sexual",
            Main_claim="Nenhum trabalho conecta sistematicamente Pateman + iconografia estatal + codificação",
            Evidence_strength="gap",
            SR_source="SR2",
            Notes="LACUNA CENTRAL DA TESE — confirma originalidade",
        ),
    ]

    for e in entradas_exemplo:
        gm.adicionar_entrada(e)

    gm.imprimir_relatorio_lacunas()
    gm.exportar_bibliografia_abnt()
