"""
corpus.py — Gestão do Corpus Visual
=====================================
Módulo responsável pela gestão do corpus iconográfico de 300–500 imagens
de alegorias femininas em suportes oficiais do Estado.

CONTEXTO METODOLÓGICO:
    A coleta de corpus segue a Fase 1 da tese (Meses 4–6), conforme
    descrito em Agulhon (1979) para fontes francesas, Warner (1985)
    para fontes transatlânticas, e Carvalho para iconografia brasileira.

    O corpus é organizado em 3 dimensões cruzadas:
    - 5 PAÍSES: França (Marianne), Reino Unido (Britannia), EUA
      (Columbia/Liberty), Alemanha (Germania/Justitia), Brasil (República)
    - 3 REGIMES ICONOCRÁTICOS: fundacional-sacrificial, normativo-jurídico,
      militar-imperial (tipologia derivada de Mondzain e Goodrich)
    - MÚLTIPLOS SUPORTES: moedas, selos, monumentos, arquitetura forense,
      emblemas, pinturas, gravuras (cada suporte implica circulação
      diferente — cf. Painel V: Ubiquidade Íntima)

FUNCIONALIDADES:
    - Criar e manter corpus_visual_master.csv (catálogo mestre)
    - Adicionar imagens com metadados completos (13 campos)
    - Organizar arquivos em pastas por país (/corpus/FR/, etc.)
    - Validar completude: checkpoints de 300 e 500 imagens,
      mínimo 50 por país, cobertura dos 3 regimes
    - Gerar relatório de distribuição e fontes

FORMATO DO CATÁLOGO (CSV com 13 campos):
    Image_ID            — Identificador único incremental (0001, 0002, ...)
    Country             — Código do país (FR, UK, USA, DE, BR)
    Figure              — Alegoria representada (Marianne, Britannia, etc.)
    Support             — Suporte material (moeda, selo, monumento, etc.)
    Year                — Ano de criação/emissão
    Source_URL           — Link permanente da fonte digital
    Rights              — Status de direitos (domínio_público, fair_use)
    File_path           — Caminho local no repositório
    Regime_preliminary  — Classificação preliminar do regime iconocrático
    Description         — Descrição iconográfica breve
    Artist              — Artista/gravador (se conhecido)
    Collection          — Acervo de origem
    Added_date          — Data de inclusão no corpus

CONVENÇÃO DE NOMES DE ARQUIVO:
    {País}_{Figura}_{Ano}_{Suporte}_{ID}.{ext}
    Exemplo: FR_Marianne_1792_moeda_0001.jpg

REFERÊNCIAS:
    - Agulhon, M. (1979). Marianne au combat.
    - Warner, M. (1985). Monuments and Maidens.
    - Carvalho, J. M. de (1990). A formação das almas.
"""

import csv
import os
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constantes — Vocabulário Controlado
# ---------------------------------------------------------------------------
# Todas as constantes abaixo formam o vocabulário controlado do corpus.
# Cada valor foi definido a partir do referencial teórico da tese e
# não deve ser alterado sem revisão do protocolo de codificação.

# Os 5 países cobrem o arco transatlântico das alegorias femininas
# estudadas na tese (cf. Painel VIII: Transatlântico em Montagem)
PAISES = ("FR", "UK", "USA", "DE", "BR")

# Figuras alegóricas: cada uma corresponde a uma personificação
# nacional específica, com tradição iconográfica própria
# "Outra" permite inclusão de alegorias regionais ou secundárias
FIGURAS = (
    "Marianne", "Britannia", "Liberty", "Columbia",
    "Germania", "República", "Justiça", "Outra",
)

# Suportes materiais: cada tipo implica um circuito de circulação
# diferente. Moedas e selos = circulação íntima/cotidiana (Painel V);
# monumentos e arquitetura = circulação pública/monumental;
# pinturas e gravuras = circulação institucional/museal
SUPORTES = (
    "moeda", "selo", "monumento", "arquitetura_forense",
    "emblema", "pintura", "gravura", "fotografia", "outro",
)

# Os 3 regimes iconocráticos derivam da tipologia proposta na tese:
# - fundacional: momentos de fundação/revolução (1789, 1848, 1889)
#   → Pathosformel sacrificial, sangue fundacional (Painel I)
# - normativo: período de estabilidade jurídica
#   → Justiça serena, lei como templo (Painel II)
# - militar: crises de guerra e emergência
#   → Mobilização bélica, corpo armado (Painel III)
REGIMES = ("fundacional", "normativo", "militar")

DIREITOS = ("domínio_público", "fair_use_acadêmico", "licença_CC", "outro")

CAMPOS_CSV = [
    "Image_ID", "Country", "Figure", "Support", "Year",
    "Source_URL", "Rights", "File_path", "Regime_preliminary",
    "Description", "Artist", "Collection", "Added_date",
]


# ---------------------------------------------------------------------------
# Dataclass de Imagem
# ---------------------------------------------------------------------------

@dataclass
class ImagemCorpus:
    """Representa uma imagem no corpus visual."""
    Image_ID: str = ""
    Country: str = ""          # FR, UK, USA, DE, BR
    Figure: str = ""           # Marianne, Britannia, etc.
    Support: str = ""          # moeda, selo, monumento, etc.
    Year: str = ""             # Ano de criação/emissão
    Source_URL: str = ""       # Link permanente da fonte
    Rights: str = ""           # domínio_público, fair_use, etc.
    File_path: str = ""        # Caminho local no repositório
    Regime_preliminary: str = ""  # fundacional, normativo, militar
    Description: str = ""      # Descrição breve
    Artist: str = ""           # Artista/autor (se conhecido)
    Collection: str = ""       # Acervo de origem
    Added_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def validar(self) -> list[str]:
        """Retorna lista de campos obrigatórios faltantes."""
        erros = []
        if not self.Country or self.Country not in PAISES:
            erros.append(f"Country inválido: '{self.Country}' (use {PAISES})")
        if not self.Figure:
            erros.append("Figure é obrigatório")
        if not self.Support:
            erros.append("Support é obrigatório")
        if not self.Year:
            erros.append("Year é obrigatório")
        if self.Regime_preliminary and self.Regime_preliminary not in REGIMES:
            erros.append(f"Regime inválido: '{self.Regime_preliminary}' (use {REGIMES})")
        return erros

    def nome_arquivo(self, extensao: str = "jpg") -> str:
        """Gera nome padronizado: FR_Marianne_1792_moeda_001.jpg"""
        fig = self.Figure.replace(" ", "_")
        sup = self.Support.replace(" ", "_")
        return f"{self.Country}_{fig}_{self.Year}_{sup}_{self.Image_ID}.{extensao}"


# ---------------------------------------------------------------------------
# Gerenciador do Corpus
# ---------------------------------------------------------------------------

class GerenciadorCorpus:
    """
    Gerencia o corpus visual: catálogo CSV, organização de arquivos,
    validação e relatórios.

    Uso:
        gc = GerenciadorCorpus("./data")
        gc.adicionar_imagem(ImagemCorpus(
            Country="FR", Figure="Marianne", Support="moeda",
            Year="1792", Source_URL="https://...",
            Rights="domínio_público", Regime_preliminary="fundacional",
        ))
        gc.relatorio_distribuicao()
    """

    def __init__(self, diretorio_base: str = "./data"):
        self.base = Path(diretorio_base)
        self.csv_path = self.base / "corpus_visual_master.csv"
        self.corpus_dir = self.base / "corpus"
        self._garantir_estrutura()
        self._proximo_id = self._calcular_proximo_id()

    # -- Estrutura de diretórios -------------------------------------------

    def _garantir_estrutura(self):
        """Cria diretórios necessários se não existirem."""
        self.base.mkdir(parents=True, exist_ok=True)
        for pais in PAISES:
            (self.corpus_dir / pais).mkdir(parents=True, exist_ok=True)
        if not self.csv_path.exists():
            self._criar_csv_vazio()

    def _criar_csv_vazio(self):
        """Cria CSV com cabeçalho."""
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
            writer.writeheader()

    def _calcular_proximo_id(self) -> int:
        """Calcula o próximo ID incremental."""
        imagens = self.listar_imagens()
        if not imagens:
            return 1
        ids_numericos = []
        for img in imagens:
            try:
                ids_numericos.append(int(img["Image_ID"]))
            except (ValueError, KeyError):
                pass
        return max(ids_numericos, default=0) + 1

    # -- CRUD de Imagens ---------------------------------------------------

    def adicionar_imagem(
        self,
        imagem: ImagemCorpus,
        arquivo_origem: Optional[str] = None,
    ) -> str:
        """
        Adiciona uma imagem ao corpus.

        Args:
            imagem: Dados da imagem.
            arquivo_origem: Caminho do arquivo de imagem para copiar
                            ao diretório do corpus (opcional).

        Returns:
            Image_ID atribuído.
        """
        # Atribuir ID
        imagem.Image_ID = str(self._proximo_id).zfill(4)
        self._proximo_id += 1

        # Validar
        erros = imagem.validar()
        if erros:
            raise ValueError(f"Dados inválidos:\n" + "\n".join(f"  - {e}" for e in erros))

        # Copiar arquivo se fornecido
        if arquivo_origem and os.path.exists(arquivo_origem):
            ext = Path(arquivo_origem).suffix.lstrip(".")
            nome = imagem.nome_arquivo(ext)
            destino = self.corpus_dir / imagem.Country / nome
            shutil.copy2(arquivo_origem, destino)
            imagem.File_path = str(destino.relative_to(self.base))

        # Salvar no CSV
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
            dados = asdict(imagem)
            # Filtrar apenas campos do CSV
            dados_csv = {k: dados.get(k, "") for k in CAMPOS_CSV}
            writer.writerow(dados_csv)

        return imagem.Image_ID

    def listar_imagens(self, filtros: Optional[dict] = None) -> list[dict]:
        """
        Lista imagens do corpus, opcionalmente filtradas.

        Args:
            filtros: Dicionário {campo: valor} para filtrar.
                     Exemplo: {"Country": "FR", "Support": "moeda"}

        Returns:
            Lista de dicionários com dados das imagens.
        """
        if not self.csv_path.exists():
            return []
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            imagens = list(reader)

        if filtros:
            for campo, valor in filtros.items():
                imagens = [img for img in imagens if img.get(campo) == valor]

        return imagens

    def contar_imagens(self) -> int:
        """Retorna total de imagens no corpus."""
        return len(self.listar_imagens())

    def buscar_por_id(self, image_id: str) -> Optional[dict]:
        """Busca imagem por ID."""
        for img in self.listar_imagens():
            if img["Image_ID"] == image_id:
                return img
        return None

    # -- Relatórios --------------------------------------------------------

    def relatorio_distribuicao(self) -> dict:
        """
        Gera relatório de distribuição do corpus.

        Returns:
            Dicionário com contagens por país, regime, suporte e figura.
        """
        imagens = self.listar_imagens()
        total = len(imagens)

        relatorio = {
            "total": total,
            "por_pais": {},
            "por_regime": {},
            "por_suporte": {},
            "por_figura": {},
            "por_pais_regime": {},
        }

        for pais in PAISES:
            imgs_pais = [i for i in imagens if i["Country"] == pais]
            relatorio["por_pais"][pais] = len(imgs_pais)
            relatorio["por_pais_regime"][pais] = {}
            for regime in REGIMES:
                n = len([i for i in imgs_pais if i["Regime_preliminary"] == regime])
                relatorio["por_pais_regime"][pais][regime] = n

        for regime in REGIMES:
            relatorio["por_regime"][regime] = len(
                [i for i in imagens if i["Regime_preliminary"] == regime]
            )

        for suporte in SUPORTES:
            n = len([i for i in imagens if i["Support"] == suporte])
            if n > 0:
                relatorio["por_suporte"][suporte] = n

        for figura in FIGURAS:
            n = len([i for i in imagens if i["Figure"] == figura])
            if n > 0:
                relatorio["por_figura"][figura] = n

        return relatorio

    def imprimir_relatorio(self):
        """Imprime relatório formatado da distribuição do corpus."""
        r = self.relatorio_distribuicao()

        print("=" * 60)
        print("RELATÓRIO DO CORPUS VISUAL")
        print(f"Total de imagens: {r['total']}")
        print("=" * 60)

        print("\n--- Por País ---")
        for pais, n in r["por_pais"].items():
            pct = (n / r["total"] * 100) if r["total"] > 0 else 0
            barra = "█" * int(pct / 2)
            print(f"  {pais:4s} │ {n:4d} ({pct:5.1f}%) {barra}")

        print("\n--- Por Regime ---")
        for regime, n in r["por_regime"].items():
            pct = (n / r["total"] * 100) if r["total"] > 0 else 0
            print(f"  {regime:15s} │ {n:4d} ({pct:5.1f}%)")

        print("\n--- Por Suporte ---")
        for suporte, n in sorted(r["por_suporte"].items(), key=lambda x: -x[1]):
            print(f"  {suporte:20s} │ {n:4d}")

        print("\n--- Por Figura ---")
        for figura, n in sorted(r["por_figura"].items(), key=lambda x: -x[1]):
            print(f"  {figura:15s} │ {n:4d}")

        print("\n--- País × Regime ---")
        header = f"{'':6s}"
        for regime in REGIMES:
            header += f" │ {regime:>12s}"
        print(header)
        print("  " + "─" * (6 + 15 * len(REGIMES)))
        for pais in PAISES:
            row = f"  {pais:4s}"
            for regime in REGIMES:
                n = r["por_pais_regime"][pais][regime]
                row += f" │ {n:>12d}"
            print(row)

        # Validação de checkpoints
        print("\n" + "=" * 60)
        print("VALIDAÇÃO DE CHECKPOINTS")
        print("=" * 60)
        total = r["total"]
        min_por_pais = min(r["por_pais"].values()) if r["por_pais"] else 0

        checks = [
            (total >= 300, f"Corpus ≥ 300 imagens: {total}/300"),
            (total >= 500, f"Corpus ≥ 500 imagens (ideal): {total}/500"),
            (min_por_pais >= 50, f"Mínimo 50 por país: mín={min_por_pais}/50"),
            (
                all(r["por_regime"].get(reg, 0) > 0 for reg in REGIMES),
                "Todos os 3 regimes representados",
            ),
        ]
        for ok, msg in checks:
            status = "✅" if ok else "❌"
            print(f"  {status} {msg}")

    def exportar_bibliografia_fontes(self, caminho: str = "relatorio_fontes.txt"):
        """Exporta lista de fontes únicas do corpus."""
        imagens = self.listar_imagens()
        fontes = set()
        for img in imagens:
            if img.get("Collection"):
                fontes.add(img["Collection"])
            if img.get("Source_URL"):
                fontes.add(img["Source_URL"])

        caminho_completo = self.base / caminho
        with open(caminho_completo, "w", encoding="utf-8") as f:
            f.write("FONTES DO CORPUS VISUAL\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"Total de imagens: {len(imagens)}\n")
            f.write("=" * 60 + "\n\n")
            for fonte in sorted(fontes):
                f.write(f"  - {fonte}\n")

        print(f"Relatório de fontes salvo em: {caminho_completo}")


# ---------------------------------------------------------------------------
# Funções de conveniência
# ---------------------------------------------------------------------------

def criar_corpus(diretorio: str = "./data") -> GerenciadorCorpus:
    """Cria ou abre um gerenciador de corpus."""
    return GerenciadorCorpus(diretorio)


if __name__ == "__main__":
    # Exemplo de uso
    gc = criar_corpus("./data")

    # Adicionar imagens de exemplo
    exemplos = [
        ImagemCorpus(
            Country="FR", Figure="Marianne", Support="pintura",
            Year="1830", Source_URL="https://commons.wikimedia.org/wiki/File:Liberty_Leading_the_People.jpg",
            Rights="domínio_público", Regime_preliminary="fundacional",
            Description="La Liberté guidant le peuple — Delacroix",
            Artist="Eugène Delacroix", Collection="Musée du Louvre",
        ),
        ImagemCorpus(
            Country="UK", Figure="Britannia", Support="gravura",
            Year="1886", Source_URL="https://victorianweb.org/victorian/photos/misc/britannia.jpg",
            Rights="domínio_público", Regime_preliminary="normativo",
            Description="Britannia personificação vitoriana",
            Collection="Victorian Web Archive",
        ),
        ImagemCorpus(
            Country="DE", Figure="Justiça", Support="monumento",
            Year="1611", Source_URL="https://commons.wikimedia.org/wiki/File:Justitia_Frankfurt.jpg",
            Rights="domínio_público", Regime_preliminary="normativo",
            Description="Justitia — Fonte da Justiça de Frankfurt",
            Collection="Gerechtigkeitsbrunnen, Frankfurt am Main",
        ),
        ImagemCorpus(
            Country="USA", Figure="Columbia", Support="gravura",
            Year="1900", Source_URL="https://commons.wikimedia.org/wiki/File:ColumbiaStahrArtwork.jpg",
            Rights="domínio_público", Regime_preliminary="militar",
            Description="Columbia — personificação dos EUA",
            Artist="Paul Stahr", Collection="Wikimedia Commons",
        ),
        ImagemCorpus(
            Country="BR", Figure="República", Support="pintura",
            Year="1889", Source_URL="https://commons.wikimedia.org/wiki/File:Rodrigues-republica-mab.jpg",
            Rights="domínio_público", Regime_preliminary="fundacional",
            Description="Efígie da República — alegoria brasileira",
            Collection="Museu de Arte da Bahia",
        ),
    ]

    for img in exemplos:
        img_id = gc.adicionar_imagem(img)
        print(f"Adicionada: {img.Country}/{img.Figure} ({img.Year}) → ID {img_id}")

    print()
    gc.imprimir_relatorio()
