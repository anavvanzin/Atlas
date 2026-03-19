"""
codificacao.py — Sistema de Codificação dos 10 Indicadores
===========================================================
Implementa o protocolo de codificação quantitativa do corpus
iconográfico, operacionalizando 10 indicadores derivados do
referencial teórico da tese.

FUNDAMENTAÇÃO TEÓRICA:
    Os indicadores foram construídos para capturar as dimensões
    centrais do "contrato sexual visual" (conceito da tese):

    1. CORPORALIDADE (FEI, MVI): Como o corpo feminino é representado.
       Fundamenta-se em Pateman (1988) — o contrato sexual como
       exclusão fundante — e na análise de Warner (1985) sobre a
       instrumentalização do corpo feminino em alegorias nacionais.

    2. ESTILO CLÁSSICO (CII, RI, WI): A idealização greco-romana como
       código racial. Conecta Mills (1997) — o contrato racial — com
       a tradição neoclássica. H2 testa se CII e WI covariam.

    3. SIMBOLOGIA (SMI, SMS, PRI): Atributos materiais e postura da
       alegoria. Baseado em Panofsky (nível iconográfico) e na
       tipologia de regimes da tese.

    4. MILITARIZAÇÃO (AMCP): Perfil de armamento em contextos de crise.
       Conecta com Benjamin (reativação arcaica) e o Painel III.

    5. LIMITE ALEGORIA/PESSOA (AI): Erosão contemporânea da fronteira
       entre figura alegórica e pessoa real. H5 testa se AI aumenta
       ao longo do tempo.

ESCALAS:
    - Ordinais (0–3): FEI, CII, SMI, AMCP, MVI, WI, AI
    - Categóricos: PRI (serena/militante/sacrificial),
                    SMS (serena/militante/sacrificial)
    - Booleano (0/1): RI

PROTOCOLO DE CODIFICAÇÃO (cf. tese, Fase 7):
    1. Codificador 1 codifica todas as imagens (codificação primária)
    2. Codificador 2 codifica 20% + amostra piloto de 50
    3. Cohen's Kappa calculado por indicador (meta: κ ≥ 0.80)
    4. Reunião de consenso para discordâncias
    5. Recálculo de Kappa a cada 100 imagens (monitoramento de drift)

REFERÊNCIAS:
    - Pateman, C. (1988). The Sexual Contract.
    - Mills, C. (1997). The Racial Contract.
    - Warner, M. (1985). Monuments and Maidens.
    - Panofsky, E. (1939). Studies in Iconology.
"""

import csv
import json
from dataclasses import dataclass, asdict, fields
from datetime import datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Definições Operacionais dos 10 Indicadores
# ---------------------------------------------------------------------------
# Cada indicador contém:
#   - nome/nome_pt: nomenclatura bilíngue (inglês para publicações
#     internacionais, português para a tese)
#   - tipo: ordinal (0–3), categórico ou booleano
#   - escala: valores possíveis
#   - niveis: definição operacional de cada nível (manual de codificação)
#   - paineis: painéis do Atlas onde o indicador é central
#
# As definições operacionais foram calibradas durante a codificação
# piloto (50 imagens, Fase 7.2) e refinadas após teste de
# confiabilidade inter-codificadores.

INDICADORES = {
    "FEI": {
        "nome": "Feminine Embodiment Index",
        "nome_pt": "Índice de Corporalidade Feminina",
        "tipo": "ordinal",
        "escala": (0, 1, 2, 3),
        "niveis": {
            0: "Abstrata/geométrica — sem corpo feminino reconhecível",
            1: "Corpo sugerido — drapeado, silhueta coberta",
            2: "Corpo visível — seios/cintura perceptíveis sob vestes",
            3: "Corpo enfatizado — nudez parcial/total, sensualidade explícita",
        },
        "paineis": ["I — Mães Fundacionais", "V — Ubiquidade Íntima"],
    },
    "CII": {
        "nome": "Classical Ideal Index",
        "nome_pt": "Índice de Ideal Clássico",
        "tipo": "ordinal",
        "escala": (0, 1, 2, 3),
        "niveis": {
            0: "Medieval/barroco/moderno — sem referência clássica",
            1: "Elementos clássicos mistos — traço isolado (coluna, drapeado)",
            2: "Predominância clássica — peplos, coroa mural, perfil greco-romano",
            3: "Clássico puro — iconografia greco-romana canônica completa",
        },
        "paineis": ["II — Justiça como Templo", "IV — República Branca"],
    },
    "PRI": {
        "nome": "Posture & Realm Index",
        "nome_pt": "Índice de Postura e Domínio",
        "tipo": "categórico",
        "escala": ("serena", "militante", "sacrificial"),
        "niveis": {
            "serena": "Sentada/de pé estática — contemplação, governo pacífico",
            "militante": "Marcha/gesto de ataque — ação bélica, resistência",
            "sacrificial": "Ferida/morta/lamento — fundação pelo sofrimento",
        },
        "paineis": ["I — Mães Fundacionais", "III — Corpos em Armas"],
    },
    "SMI": {
        "nome": "Symbolic Material Index",
        "nome_pt": "Índice de Material Simbólico",
        "tipo": "ordinal",
        "escala": (0, 1, 2, 3),
        "niveis": {
            0: "Nenhum atributo simbólico identificável",
            1: "1 atributo (ex.: balança OU espada OU venda)",
            2: "2–3 atributos (ex.: balança + espada)",
            3: "4+ atributos (balança + espada + venda + livro + coluna)",
        },
        "paineis": ["II — Justiça como Templo"],
    },
    "SMS": {
        "nome": "Symbolic Meaning Score",
        "nome_pt": "Pontuação de Significado Simbólico",
        "tipo": "categórico",
        "escala": ("serena", "militante", "sacrificial"),
        "niveis": {
            "serena": "Lei/ordem — estabilidade jurídica, normatividade",
            "militante": "Guerra/crise — mobilização, defesa, emergência",
            "sacrificial": "Fundação/trauma — sangue fundacional, violência originária",
        },
        "paineis": ["III — Corpos em Armas", "VII — Justiça Contestada"],
    },
    "AMCP": {
        "nome": "Armament & Crisis Profile",
        "nome_pt": "Perfil de Armamento e Crise",
        "tipo": "ordinal",
        "escala": (0, 1, 2, 3),
        "niveis": {
            0: "Nenhuma arma ou instrumento bélico",
            1: "Arma defensiva (escudo, muralha)",
            2: "Arma ofensiva (espada, lança, tridente)",
            3: "Arsenal completo (canhão, rifle, capacete, múltiplas armas)",
        },
        "paineis": ["III — Corpos em Armas"],
    },
    "MVI": {
        "nome": "Maternal-Vulnerability Index",
        "nome_pt": "Índice de Maternidade-Vulnerabilidade",
        "tipo": "ordinal",
        "escala": (0, 1, 2, 3),
        "niveis": {
            0: "Sem marcas maternais ou de vulnerabilidade",
            1: "Maternidade sugerida — criança ao lado, gesto protetor",
            2: "Seio exposto — amamentação simbólica da nação",
            3: "Corpo ferido/sangrante/morto — sacrifício maternal",
        },
        "paineis": ["I — Mães Fundacionais"],
    },
    "WI": {
        "nome": "Whiteness Index",
        "nome_pt": "Índice de Branquitude",
        "tipo": "ordinal",
        "escala": (0, 1, 2, 3),
        "niveis": {
            0: "Racialmente ambíguo/diverso — sem idealização racial visível",
            1: "Traços clássicos — cabelo ondulado, nariz reto, pele clara sugerida",
            2: "Branquitude explícita — pele clara, idealização neoclássica evidente",
            3: "Branquitude + hierarquia — contraste com figuras racializadas subordinadas",
        },
        "paineis": ["IV — República Branca"],
    },
    "RI": {
        "nome": "Racial Idealisation",
        "nome_pt": "Idealização Racial",
        "tipo": "booleano",
        "escala": (0, 1),
        "niveis": {
            0: "Não clássico OU diversidade visível",
            1: "Ideal clássico branco — convergência greco-romana, branqueamento",
        },
        "paineis": ["IV — República Branca"],
    },
    "AI": {
        "nome": "Allegory-Biography Index",
        "nome_pt": "Índice Alegoria-Biografia",
        "tipo": "ordinal",
        "escala": (0, 1, 2, 3),
        "niveis": {
            0: "Alegoria pura — sem traços individuais identificáveis",
            1: "Alegoria com nome — figura nomeada genérica (ex.: Marianne)",
            2: "Alegoria inspirada em pessoa real (ex.: Bardot como Marianne)",
            3: "Pessoa real iconizada como alegoria (ex.: Thatcher-Britannia)",
        },
        "paineis": ["VI — Damas de Ferro"],
    },
}


# ---------------------------------------------------------------------------
# Dataclass de Codificação
# ---------------------------------------------------------------------------

@dataclass
class CodificacaoImagem:
    """Codificação completa de uma imagem do corpus."""
    Image_ID: str = ""
    Coder_ID: str = ""              # Identificador do codificador
    Coding_date: str = ""
    FEI: int = -1                   # 0–3
    CII: int = -1                   # 0–3
    PRI: str = ""                   # serena / militante / sacrificial
    SMI: int = -1                   # 0–3
    SMS: str = ""                   # serena / militante / sacrificial
    AMCP: int = -1                  # 0–3
    MVI: int = -1                   # 0–3
    WI: int = -1                    # 0–3
    RI: int = -1                    # 0 / 1
    AI: int = -1                    # 0–3
    Notes: str = ""                 # Observações qualitativas

    def __post_init__(self):
        if not self.Coding_date:
            self.Coding_date = datetime.now().strftime("%Y-%m-%d")

    def validar(self) -> list[str]:
        """Valida que todos os indicadores foram preenchidos corretamente."""
        erros = []
        if not self.Image_ID:
            erros.append("Image_ID é obrigatório")
        if not self.Coder_ID:
            erros.append("Coder_ID é obrigatório")

        # Indicadores ordinais (0–3)
        for ind in ("FEI", "CII", "SMI", "AMCP", "MVI", "WI", "AI"):
            val = getattr(self, ind)
            if val not in (0, 1, 2, 3):
                erros.append(f"{ind} deve ser 0, 1, 2 ou 3 (recebido: {val})")

        # Indicador booleano
        if self.RI not in (0, 1):
            erros.append(f"RI deve ser 0 ou 1 (recebido: {self.RI})")

        # Indicadores categóricos
        cats_validos = ("serena", "militante", "sacrificial")
        for ind in ("PRI", "SMS"):
            val = getattr(self, ind)
            if val not in cats_validos:
                erros.append(f"{ind} deve ser {cats_validos} (recebido: '{val}')")

        return erros

    def como_dict(self) -> dict:
        """Retorna como dicionário para exportação CSV."""
        return asdict(self)

    def perfil_resumido(self) -> str:
        """Retorna perfil resumido dos indicadores."""
        return (
            f"FEI={self.FEI} CII={self.CII} PRI={self.PRI} "
            f"SMI={self.SMI} SMS={self.SMS} AMCP={self.AMCP} "
            f"MVI={self.MVI} WI={self.WI} RI={self.RI} AI={self.AI}"
        )


# ---------------------------------------------------------------------------
# Campos do CSV de codificação
# ---------------------------------------------------------------------------

CAMPOS_CODIFICACAO = [
    "Image_ID", "Coder_ID", "Coding_date",
    "FEI", "CII", "PRI", "SMI", "SMS",
    "AMCP", "MVI", "WI", "RI", "AI", "Notes",
]

INDICADORES_ORDINAIS = ["FEI", "CII", "SMI", "AMCP", "MVI", "WI", "AI"]
INDICADORES_CATEGORICOS = ["PRI", "SMS"]
INDICADORES_BOOLEANOS = ["RI"]
TODOS_INDICADORES = INDICADORES_ORDINAIS + INDICADORES_CATEGORICOS + INDICADORES_BOOLEANOS


# ---------------------------------------------------------------------------
# Gerenciador de Codificação
# ---------------------------------------------------------------------------

class GerenciadorCodificacao:
    """
    Gerencia o processo de codificação do corpus visual.

    Uso:
        gc = GerenciadorCodificacao("./data")
        cod = CodificacaoImagem(
            Image_ID="0001", Coder_ID="COD1",
            FEI=3, CII=1, PRI="militante", SMI=2, SMS="militante",
            AMCP=2, MVI=2, WI=1, RI=0, AI=1,
            Notes="Seio exposto, gorro frígio, barricada",
        )
        gc.salvar_codificacao(cod)
    """

    def __init__(self, diretorio_base: str = "./data"):
        self.base = Path(diretorio_base)
        self.base.mkdir(parents=True, exist_ok=True)

    def _csv_path(self, coder_id: str) -> Path:
        """Retorna caminho do CSV para um codificador específico."""
        return self.base / f"codificacao_{coder_id}.csv"

    def _csv_completo_path(self) -> Path:
        """Retorna caminho do dataset completo consolidado."""
        return self.base / "corpus_codificado.csv"

    def salvar_codificacao(self, cod: CodificacaoImagem):
        """Salva uma codificação no CSV do codificador."""
        erros = cod.validar()
        if erros:
            raise ValueError(
                f"Codificação inválida:\n" + "\n".join(f"  - {e}" for e in erros)
            )

        csv_path = self._csv_path(cod.Coder_ID)
        existe = csv_path.exists()

        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS_CODIFICACAO)
            if not existe:
                writer.writeheader()
            writer.writerow(cod.como_dict())

    def salvar_lote(self, codificacoes: list[CodificacaoImagem]):
        """Salva múltiplas codificações de uma vez."""
        for cod in codificacoes:
            self.salvar_codificacao(cod)
        print(f"Salvas {len(codificacoes)} codificações.")

    def carregar_codificacoes(self, coder_id: str) -> list[dict]:
        """Carrega todas as codificações de um codificador."""
        csv_path = self._csv_path(coder_id)
        if not csv_path.exists():
            return []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            dados = list(reader)
        # Converter tipos
        for row in dados:
            for ind in INDICADORES_ORDINAIS:
                if row.get(ind):
                    row[ind] = int(row[ind])
            if row.get("RI"):
                row["RI"] = int(row["RI"])
        return dados

    def consolidar_dataset(self, coder_id_principal: str = "COD1") -> Path:
        """
        Consolida as codificações do codificador principal
        no dataset final corpus_codificado.csv.

        Returns:
            Caminho do arquivo consolidado.
        """
        codificacoes = self.carregar_codificacoes(coder_id_principal)
        csv_path = self._csv_completo_path()

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS_CODIFICACAO)
            writer.writeheader()
            for cod in codificacoes:
                writer.writerow(cod)

        print(f"Dataset consolidado: {len(codificacoes)} imagens → {csv_path}")
        return csv_path

    def imprimir_progresso(self, coder_id: str, total_corpus: int = 500):
        """Imprime progresso da codificação."""
        cods = self.carregar_codificacoes(coder_id)
        n = len(cods)
        pct = (n / total_corpus * 100) if total_corpus > 0 else 0

        print(f"\nProgresso de Codificação — Codificador: {coder_id}")
        print("=" * 50)
        print(f"  Imagens codificadas: {n}/{total_corpus} ({pct:.1f}%)")

        barra = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
        print(f"  [{barra}]")

        if cods:
            # Distribuição por país
            paises = {}
            for c in cods:
                # Precisa do corpus para saber o país — simplificado aqui
                pass
            # Última codificação
            ultima = cods[-1]
            print(f"  Última: Image_ID={ultima['Image_ID']} em {ultima.get('Coding_date', '?')}")


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def descrever_indicador(codigo: str) -> str:
    """Imprime descrição completa de um indicador."""
    ind = INDICADORES.get(codigo)
    if not ind:
        return f"Indicador '{codigo}' não encontrado."

    linhas = [
        f"\n{'='*60}",
        f"{codigo} — {ind['nome']}",
        f"({ind['nome_pt']})",
        f"{'='*60}",
        f"Tipo: {ind['tipo']}",
        f"Escala: {ind['escala']}",
        f"\nNíveis:",
    ]
    for nivel, desc in ind["niveis"].items():
        linhas.append(f"  {nivel}: {desc}")
    linhas.append(f"\nPainéis relacionados:")
    for painel in ind["paineis"]:
        linhas.append(f"  → {painel}")

    texto = "\n".join(linhas)
    print(texto)
    return texto


def descrever_todos_indicadores():
    """Imprime descrição de todos os 10 indicadores."""
    for codigo in INDICADORES:
        descrever_indicador(codigo)
        print()


def gerar_manual_codificacao(caminho: str = "./data/manual_codificacao.json"):
    """Exporta o manual de codificação como JSON."""
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(INDICADORES, f, ensure_ascii=False, indent=2)
    print(f"Manual de codificação exportado: {caminho}")


def arvore_decisao(indicador: str, imagem_desc: str = "") -> str:
    """
    Retorna árvore de decisão simplificada para um indicador.
    Útil para o manual de codificação.
    """
    arvores = {
        "FEI": """
ÁRVORE DE DECISÃO — FEI (Feminine Embodiment Index)
    A imagem contém um corpo feminino?
    ├─ NÃO → FEI = 0 (abstrata/geométrica)
    └─ SIM
        O corpo é coberto/sugerido apenas por drapeado?
        ├─ SIM → FEI = 1 (corpo sugerido)
        └─ NÃO
            O corpo mostra seios/cintura sob vestes transparentes?
            ├─ SIM → FEI = 2 (corpo visível)
            └─ NÃO → há nudez parcial/total ou sensualidade explícita?
                ├─ SIM → FEI = 3 (corpo enfatizado)
                └─ NÃO → revisar: provavelmente FEI = 2
""",
        "CII": """
ÁRVORE DE DECISÃO — CII (Classical Ideal Index)
    A imagem contém referências greco-romanas?
    ├─ NÃO → CII = 0 (sem referência clássica)
    └─ SIM
        Quantos elementos clássicos estão presentes?
        ├─ 1 elemento isolado (coluna, drapeado, etc.) → CII = 1
        ├─ Predominância clássica (peplos + coroa mural + perfil) → CII = 2
        └─ Iconografia greco-romana completa e canônica → CII = 3
""",
        "AMCP": """
ÁRVORE DE DECISÃO — AMCP (Armament & Crisis Profile)
    A figura porta armas ou instrumentos bélicos?
    ├─ NÃO → AMCP = 0
    └─ SIM
        A arma é defensiva (escudo, muralha)?
        ├─ SIM (apenas defensiva) → AMCP = 1
        └─ NÃO
            A arma é ofensiva (espada, lança)?
            ├─ SIM (uma arma ofensiva) → AMCP = 2
            └─ Arsenal completo (múltiplas armas, canhão, rifle) → AMCP = 3
""",
        "WI": """
ÁRVORE DE DECISÃO — WI (Whiteness Index)
    A figura apresenta racialização visível?
    ├─ Ambígua/diversa → WI = 0
    └─ Traços clássicos europeus identificáveis
        ├─ Apenas traços sutis (cabelo ondulado, nariz reto) → WI = 1
        ├─ Branquitude explícita (pele clara, idealização neoclássica) → WI = 2
        └─ Branquitude + hierarquia (contraste com figuras subordinadas) → WI = 3
""",
        "MVI": """
ÁRVORE DE DECISÃO — MVI (Maternal-Vulnerability Index)
    A figura apresenta marcas de maternidade ou vulnerabilidade?
    ├─ NÃO → MVI = 0
    └─ SIM
        ├─ Criança ao lado / gesto protetor → MVI = 1
        ├─ Seio exposto (amamentação simbólica) → MVI = 2
        └─ Corpo ferido / sangrante / morto → MVI = 3
""",
        "RI": """
ÁRVORE DE DECISÃO — RI (Racial Idealisation)
    A figura corresponde ao ideal clássico branco (convergência greco-romana)?
    ├─ NÃO (não clássico OU diversidade visível) → RI = 0
    └─ SIM (ideal clássico branco presente) → RI = 1
""",
        "AI": """
ÁRVORE DE DECISÃO — AI (Allegory-Biography Index)
    A figura é puramente alegórica (sem traços individuais)?
    ├─ SIM → AI = 0 (alegoria pura)
    └─ NÃO
        ├─ Alegoria nomeada genérica (ex.: "Marianne") → AI = 1
        ├─ Alegoria inspirada em pessoa real (ex.: Bardot) → AI = 2
        └─ Pessoa real iconizada como alegoria (ex.: Thatcher) → AI = 3
""",
    }

    if indicador in arvores:
        return arvores[indicador]
    return f"Árvore de decisão não disponível para '{indicador}'."


if __name__ == "__main__":
    # Demonstração
    descrever_todos_indicadores()

    # Exemplo de codificação
    gc = GerenciadorCodificacao("./data")

    cod = CodificacaoImagem(
        Image_ID="0001", Coder_ID="COD1",
        FEI=3, CII=1, PRI="militante", SMI=2, SMS="militante",
        AMCP=2, MVI=2, WI=1, RI=0, AI=1,
        Notes="Seio exposto, gorro frígio, barricada ao fundo — Delacroix 1830",
    )
    print(f"\nPerfil: {cod.perfil_resumido()}")
    gc.salvar_codificacao(cod)
    print("Codificação salva com sucesso.")

    # Árvores de decisão
    print(arvore_decisao("FEI"))
    print(arvore_decisao("WI"))
