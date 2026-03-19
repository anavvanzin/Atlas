"""
iconclass_.py — Integração com o Sistema Internacional Iconclass
=================================================================
Conecta o sistema de codificação proprietário da tese (10 indicadores)
com o padrão internacional Iconclass para classificação iconográfica.

CONTEXTO:
    Iconclass é o sistema de classificação iconográfica mais utilizado
    em humanidades digitais, museus e acervos de arte. Desenvolvido
    por Henri van de Waal (Leiden), organiza temas visuais em hierarquia
    alfanumérica (ex.: 44A3 = Justiça; 31A2 = Figura feminina).

    A integração com Iconclass serve a dois propósitos na tese:
    1. COMPARABILIDADE INTERNACIONAL: permite que outros pesquisadores
       localizem imagens do corpus em bases de dados como RKD, British
       Museum, Rijksmuseum usando o mesmo vocabulário controlado.
    2. ENRIQUECIMENTO SEMÂNTICO: os códigos Iconclass adicionam uma
       camada de classificação temática que complementa os 10 indicadores
       quantitativos da tese.

MAPEAMENTO TESE → ICONCLASS:
    O módulo pré-mapeia ~40 códigos Iconclass organizados em 6 categorias
    temáticas relevantes para a tese:
    - alegoria_feminina: personificações (Justitia, Libertas, Pax, etc.)
    - justica: atributos específicos da Justiça (balança, espada, venda)
    - mulher: corpo feminino, nudez, seio
    - soberania: Estado, nação, lei, administração da justiça
    - atributos: coroa, balança, espada, escudo, gorro frígio
    - suportes: numismática, selos, escultura, arquitetura

MOTOR DE SUGESTÃO:
    A função sugerir_iconclass_para_indicadores() recebe os valores dos
    10 indicadores de uma imagem e sugere automaticamente códigos Iconclass
    relevantes. Por exemplo:
    - FEI ≥ 3 → sugere 31AA2311 (mulher nua)
    - CII ≥ 2 → sugere 48C181 (gorro frígio), 31E23 (coroa de louros)
    - AMCP ≥ 2 → sugere 45C1 (espada)
    - Figure = "Justiça" → sugere 44A3 (Justitia)

Dependências:
    pip install iconclass  (opcional — funciona sem a biblioteca,
    usando o mapeamento pré-definido como fallback)
    (Primeira execução com biblioteca baixa SQLite ~50 MB)
"""

import json
from pathlib import Path
from typing import Optional

try:
    import iconclass
    HAS_ICONCLASS = True
except ImportError:
    HAS_ICONCLASS = False


# ---------------------------------------------------------------------------
# Mapeamento de Códigos Relevantes para a Tese
# ---------------------------------------------------------------------------

CODIGOS_TESE = {
    # Alegorias femininas e personificações
    "alegoria_feminina": {
        "11L": "Fé, 'Fides'; Religião, 'Religio' — personificação feminina",
        "44A3": "Justiça, 'Justitia' — personificação",
        "44B1": "Paz, 'Pax' — personificação feminina",
        "44B2": "Liberdade, 'Libertas' — personificação feminina",
        "44B3": "Pátria — personificação feminina da nação",
        "44B6": "Fama, 'Gloria' — personificação feminina",
    },
    # Justiça e iconografia jurídica
    "justica": {
        "44A3": "Justiça, 'Justitia'",
        "44A31": "Atributos da Justiça: balança",
        "44A32": "Atributos da Justiça: espada",
        "44A33": "Atributos da Justiça: venda nos olhos",
        "44A34": "Atributos da Justiça: livro da lei",
        "48C5141": "Justiça como tema iconográfico",
    },
    # Mulher e corpo feminino
    "mulher": {
        "31A2": "Figura humana feminina",
        "31AA231": "Mulher (adulta)",
        "31AA2311": "Mulher nua",
        "31D14": "Seio feminino",
        "31D1": "Corpo feminino",
    },
    # Soberania e poder
    "soberania": {
        "44A": "Estado, governo",
        "44B": "Nação, povo",
        "44C": "Lei, legislação",
        "44D": "Administração da justiça",
    },
    # Atributos simbólicos
    "atributos": {
        "31E2": "Coroa",
        "31E23": "Coroa de louros",
        "41D2": "Balança",
        "45C1": "Espada",
        "45C12": "Escudo",
        "48C181": "Gorro frígio",
    },
    # Suportes materiais
    "suportes": {
        "48A98": "Numismática (moedas)",
        "48A981": "Moeda — anverso/reverso",
        "48A99": "Selo, carimbo",
        "48C7": "Escultura, monumento",
        "48C8": "Arquitetura",
    },
}


# ---------------------------------------------------------------------------
# Funções de Busca
# ---------------------------------------------------------------------------

def _check_iconclass():
    """Verifica se iconclass está instalado."""
    if not HAS_ICONCLASS:
        raise ImportError(
            "Biblioteca iconclass não encontrada. Instale com:\n"
            "  pip install iconclass\n"
            "Na primeira execução, será baixado um banco SQLite (~50 MB)."
        )


def buscar_codigo(notacao: str, idioma: str = "en") -> Optional[dict]:
    """
    Busca um código Iconclass e retorna suas informações.

    Args:
        notacao: Código Iconclass (ex.: "44A3", "31AA231").
        idioma: Código de idioma ("en", "de", "fr", "it", "nl", "pt").

    Returns:
        Dicionário com informações do código ou None.
    """
    _check_iconclass()

    try:
        resultado = iconclass.get(notacao)
        if resultado:
            return {
                "notacao": resultado.get("n", notacao),
                "texto": resultado.get("txt", {}).get(idioma, ""),
                "texto_pt": resultado.get("txt", {}).get("pt", ""),
                "texto_en": resultado.get("txt", {}).get("en", ""),
                "filhos": resultado.get("c", []),
                "pais": resultado.get("p", []),
            }
    except Exception as e:
        print(f"Erro ao buscar '{notacao}': {e}")

    return None


def buscar_hierarquia(notacao: str, profundidade: int = 2, idioma: str = "en") -> list[dict]:
    """
    Busca hierarquia (filhos) de um código Iconclass.

    Args:
        notacao: Código raiz.
        profundidade: Níveis de profundidade a explorar.
        idioma: Código de idioma.

    Returns:
        Lista de dicionários com códigos filhos.
    """
    _check_iconclass()

    resultados = []

    def _explorar(cod, nivel=0):
        if nivel >= profundidade:
            return
        info = buscar_codigo(cod, idioma)
        if info:
            info["nivel"] = nivel
            resultados.append(info)
            for filho in info.get("filhos", []):
                _explorar(filho, nivel + 1)

    _explorar(notacao)
    return resultados


def listar_codigos_tese() -> dict:
    """
    Retorna todos os códigos Iconclass mapeados para a tese,
    organizados por categoria temática.
    """
    return CODIGOS_TESE


def buscar_por_texto(termo: str, idioma: str = "en") -> list[dict]:
    """
    Busca códigos Iconclass por texto (quando a biblioteca suporta busca textual).
    Fallback: busca nos códigos pré-mapeados.
    """
    resultados = []

    termo_lower = termo.lower()
    for categoria, codigos in CODIGOS_TESE.items():
        for notacao, descricao in codigos.items():
            if termo_lower in descricao.lower():
                resultados.append({
                    "notacao": notacao,
                    "descricao": descricao,
                    "categoria": categoria,
                })

    return resultados


# ---------------------------------------------------------------------------
# Anotação de Imagens
# ---------------------------------------------------------------------------

def anotar_imagem(
    image_id: str,
    codigos_iconclass: list[str],
    notas: str = "",
    caminho_csv: str = "./data/anotacoes_iconclass.csv",
):
    """
    Salva anotação Iconclass para uma imagem do corpus.

    Args:
        image_id: ID da imagem no corpus.
        codigos_iconclass: Lista de códigos Iconclass aplicáveis.
        notas: Observações sobre a classificação.
        caminho_csv: Caminho do CSV de anotações.
    """
    import csv
    from datetime import datetime

    campos = ["Image_ID", "Iconclass_codes", "Iconclass_texts", "Notes", "Date"]

    # Buscar textos dos códigos
    textos = []
    for cod in codigos_iconclass:
        info = buscar_codigo(cod) if HAS_ICONCLASS else None
        if info and info.get("texto_en"):
            textos.append(f"{cod}: {info['texto_en']}")
        else:
            # Fallback para códigos pré-mapeados
            for _cat, _cods in CODIGOS_TESE.items():
                if cod in _cods:
                    textos.append(f"{cod}: {_cods[cod]}")
                    break
            else:
                textos.append(cod)

    caminho = Path(caminho_csv)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    existe = caminho.exists()

    with open(caminho, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        if not existe:
            writer.writeheader()
        writer.writerow({
            "Image_ID": image_id,
            "Iconclass_codes": "; ".join(codigos_iconclass),
            "Iconclass_texts": "; ".join(textos),
            "Notes": notas,
            "Date": datetime.now().strftime("%Y-%m-%d"),
        })


# ---------------------------------------------------------------------------
# Mapeamento Indicadores → Iconclass
# ---------------------------------------------------------------------------

INDICADOR_ICONCLASS_MAP = {
    "FEI": {
        "descricao": "Corporalidade feminina",
        "codigos_relevantes": ["31A2", "31D1", "31D14", "31AA231", "31AA2311"],
        "notas": "FEI alto (2–3) → buscar 31D14 (seio), 31AA2311 (nudez)",
    },
    "CII": {
        "descricao": "Ideal clássico",
        "codigos_relevantes": ["48C181", "31E23", "48C7"],
        "notas": "CII alto → elementos greco-romanos: peplos, coroa de louros, coluna",
    },
    "SMI": {
        "descricao": "Atributos simbólicos",
        "codigos_relevantes": ["41D2", "45C1", "44A31", "44A32", "44A33", "44A34"],
        "notas": "SMI mapeia quantidade de atributos (balança, espada, venda, livro)",
    },
    "AMCP": {
        "descricao": "Armamento e crise",
        "codigos_relevantes": ["45C1", "45C12", "45C"],
        "notas": "AMCP alto → armas ofensivas/defensivas (espada, escudo, arsenal)",
    },
    "MVI": {
        "descricao": "Maternidade e vulnerabilidade",
        "codigos_relevantes": ["31D14", "31A2"],
        "notas": "MVI alto → seio exposto (amamentação), corpo ferido",
    },
    "AI": {
        "descricao": "Limite alegoria/biografia",
        "codigos_relevantes": ["44B3", "44A3"],
        "notas": "AI alto → erosão da alegoria pura para pessoa real",
    },
}


def sugerir_iconclass_para_indicadores(codificacao: dict) -> list[str]:
    """
    Sugere códigos Iconclass com base nos valores dos indicadores.

    Args:
        codificacao: Dicionário com valores dos indicadores.

    Returns:
        Lista de códigos Iconclass sugeridos.
    """
    sugestoes = set()

    # FEI alto → corpo feminino
    if codificacao.get("FEI", 0) >= 2:
        sugestoes.update(["31A2", "31D1"])
    if codificacao.get("FEI", 0) >= 3:
        sugestoes.add("31AA2311")

    # CII alto → ideal clássico
    if codificacao.get("CII", 0) >= 2:
        sugestoes.update(["48C181", "31E23"])

    # SMI → atributos
    if codificacao.get("SMI", 0) >= 1:
        sugestoes.add("44A31")  # balança
    if codificacao.get("SMI", 0) >= 2:
        sugestoes.update(["44A32", "44A33"])  # espada, venda

    # AMCP alto → armas
    if codificacao.get("AMCP", 0) >= 2:
        sugestoes.add("45C1")
    if codificacao.get("AMCP", 0) >= 1:
        sugestoes.add("45C12")

    # MVI alto → maternidade
    if codificacao.get("MVI", 0) >= 2:
        sugestoes.add("31D14")

    # Figura específica
    figura = codificacao.get("Figure", "")
    if "Justiça" in figura or "Justitia" in figura:
        sugestoes.update(["44A3", "48C5141"])
    if "Marianne" in figura:
        sugestoes.update(["44B2", "44B3"])
    if "Britannia" in figura:
        sugestoes.update(["44B3"])
    if "Liberty" in figura or "Columbia" in figura:
        sugestoes.update(["44B2", "44B3"])
    if "República" in figura:
        sugestoes.update(["44B3"])

    return sorted(sugestoes)


# ---------------------------------------------------------------------------
# Exportação
# ---------------------------------------------------------------------------

def exportar_mapeamento_tese(caminho: str = "./data/iconclass_mapeamento_tese.json"):
    """Exporta todo o mapeamento Iconclass da tese como JSON."""
    dados = {
        "codigos_tese": CODIGOS_TESE,
        "indicador_iconclass": INDICADOR_ICONCLASS_MAP,
    }
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"Mapeamento Iconclass exportado: {caminho}")


if __name__ == "__main__":
    # Demonstração sem dependência da biblioteca iconclass
    print("=" * 60)
    print("MAPEAMENTO ICONCLASS PARA A TESE")
    print("=" * 60)

    for categoria, codigos in CODIGOS_TESE.items():
        print(f"\n--- {categoria.upper()} ---")
        for notacao, desc in codigos.items():
            print(f"  {notacao:>12s}  {desc}")

    # Sugestão para uma imagem codificada
    print("\n\n" + "=" * 60)
    print("SUGESTÃO DE ICONCLASS PARA IMAGEM EXEMPLO")
    print("=" * 60)

    exemplo = {
        "Figure": "Marianne",
        "FEI": 3, "CII": 1, "SMI": 2,
        "AMCP": 2, "MVI": 2, "AI": 1,
    }
    print(f"Imagem: {exemplo}")
    sugestoes = sugerir_iconclass_para_indicadores(exemplo)
    print(f"Códigos sugeridos: {sugestoes}")

    # Busca por texto
    print("\n--- Busca por 'justiça' ---")
    for r in buscar_por_texto("Justiça"):
        print(f"  {r['notacao']:>12s}  {r['descricao']}  [{r['categoria']}]")

    exportar_mapeamento_tese()
