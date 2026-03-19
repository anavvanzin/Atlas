#!/usr/bin/env python3
"""
Atlas Iconocrático — CLI Principal
====================================
Ponto de entrada para todas as operações do toolkit de pesquisa.

Uso:
    python main.py <comando> [opções]

Comandos disponíveis:
    corpus          Gestão do corpus visual
    codificacao     Sistema de codificação (10 indicadores)
    estatistica     Análise estatística e testes de hipóteses
    kappa           Confiabilidade inter-codificadores
    iconclass       Integração com Iconclass
    matriz          Matriz de evidências
    relatorio       Gerar relatório completo
    info            Informações sobre o toolkit
"""

import argparse
import json
import sys
from pathlib import Path

from atlas_iconocratico import __version__, __author__


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _banner():
    print(r"""
    ╔══════════════════════════════════════════════════════════╗
    ║        ATLAS ICONOCRÁTICO — Toolkit de Pesquisa         ║
    ║  Contrato Sexual Visual & Regime Iconocrático           ║
    ║  Alegorias Femininas na Cultura Jurídica (1789–2024)    ║
    ║  PPGD / UFSC                                            ║
    ╚══════════════════════════════════════════════════════════╝
    """)


def _resolver_dir(base: str) -> str:
    """Resolve o diretório base e garante que existe."""
    p = Path(base).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


# ──────────────────────────────────────────────
# Comando: info
# ──────────────────────────────────────────────

def cmd_info(args):
    """Mostra informações sobre o toolkit."""
    _banner()
    print(f"  Versão:  {__version__}")
    print(f"  Autor:   {__author__}")
    print()
    print("  Módulos instalados:")
    modules = {
        "corpus":      "Gestão do corpus visual (catálogo, metadados, organização)",
        "codificacao": "Sistema de codificação dos 10 indicadores",
        "estatistica": "Análise estatística descritiva e inferencial (H1–H5)",
        "kappa":       "Confiabilidade inter-codificadores (Cohen's Kappa)",
        "iconclass":   "Integração com a biblioteca Iconclass",
        "matriz":      "Matriz de evidências e exportação de dados",
    }
    for mod, desc in modules.items():
        status = "✓"
        try:
            __import__(f"atlas_iconocratico.{mod if mod != 'iconclass' else 'iconclass_'}")
        except ImportError:
            status = "✗"
        print(f"    [{status}] {mod:14s}  {desc}")
    print()


# ──────────────────────────────────────────────
# Comando: corpus
# ──────────────────────────────────────────────

def cmd_corpus(args):
    """Gestão do corpus visual."""
    from atlas_iconocratico.corpus import GerenciadorCorpus, ImagemCorpus

    gc = GerenciadorCorpus(diretorio_base=args.dir)

    if args.acao == "relatorio":
        gc.imprimir_relatorio()

    elif args.acao == "adicionar":
        if not all([args.titulo, args.pais, args.ano]):
            print("Erro: --titulo, --pais e --ano são obrigatórios para adicionar.")
            sys.exit(1)

        imagem = ImagemCorpus(
            Country=args.pais,
            Figure=args.titulo,
            Year=str(args.ano),
            Artist=args.autor or "Desconhecido",
            Support=args.tipo or "gravura",
            Collection=args.fonte or "",
            Description=args.notas or "",
        )
        image_id = gc.adicionar_imagem(
            imagem=imagem,
            arquivo_origem=args.arquivo or None,
        )
        print(f"Imagem adicionada com ID: {image_id}")

    elif args.acao == "listar":
        filtros = {}
        if args.pais:
            filtros["Country"] = args.pais
        imgs = gc.listar_imagens(filtros=filtros if filtros else None)
        if not imgs:
            print("Nenhuma imagem encontrada.")
        else:
            print(f"\n{'ID':<10} {'Figura':<40} {'País':<6} {'Ano':<6}")
            print("─" * 65)
            for img in imgs:
                print(f"{img.get('Image_ID',''):<10} {str(img.get('Figure',''))[:38]:<40} "
                      f"{img.get('Country',''):<6} {img.get('Year',''):<6}")
            print(f"\nTotal: {len(imgs)} imagens")

    elif args.acao == "contar":
        n = gc.contar_imagens()
        print(f"Total de imagens no corpus: {n}")

    elif args.acao == "fontes":
        gc.exportar_bibliografia_fontes()
        print("Relatório de fontes exportado.")

    else:
        print("Ação não reconhecida. Use: relatorio | adicionar | listar | contar | fontes")


# ──────────────────────────────────────────────
# Comando: codificacao
# ──────────────────────────────────────────────

def cmd_codificacao(args):
    """Sistema de codificação dos 10 indicadores."""
    from atlas_iconocratico.codificacao import (
        GerenciadorCodificacao,
        CodificacaoImagem,
        descrever_indicador,
        descrever_todos_indicadores,
        gerar_manual_codificacao,
        arvore_decisao,
    )

    if args.acao == "indicadores":
        descrever_todos_indicadores()

    elif args.acao == "indicador":
        if not args.codigo:
            print("Erro: --codigo é obrigatório (ex: FEI, CII, PRI).")
            sys.exit(1)
        print(descrever_indicador(args.codigo.upper()))

    elif args.acao == "arvore":
        if not args.codigo:
            print("Erro: --codigo é obrigatório.")
            sys.exit(1)
        print(arvore_decisao(args.codigo.upper(), args.descricao or ""))

    elif args.acao == "manual":
        caminho = args.saida or "./data/manual_codificacao.json"
        gerar_manual_codificacao(caminho)
        print(f"Manual de codificação exportado para: {caminho}")

    elif args.acao == "progresso":
        gm = GerenciadorCodificacao(diretorio_base=args.dir)
        coder = args.coder or "COD1"
        total = int(args.total) if args.total else 500
        gm.imprimir_progresso(coder, total)

    elif args.acao == "consolidar":
        gm = GerenciadorCodificacao(diretorio_base=args.dir)
        coder = args.coder or "COD1"
        path = gm.consolidar_dataset(coder)
        print(f"Dataset consolidado salvo em: {path}")

    elif args.acao == "codificar":
        if not args.image_id:
            print("Erro: --image-id é obrigatório.")
            sys.exit(1)
        gm = GerenciadorCodificacao(diretorio_base=args.dir)
        coder = args.coder or "COD1"

        print(f"\n── Codificação da imagem {args.image_id} (codificador: {coder}) ──\n")
        indicadores_cod = [
            "FEI", "CII", "PRI", "SMI", "SMS",
            "AMCP", "MVI", "WI", "RI", "AI",
        ]
        valores = {}
        for ind in indicadores_cod:
            desc = descrever_indicador(ind).split("\n")[0]
            while True:
                val = input(f"  {ind} ({desc}): valor [0/1] ou [0-3]: ").strip()
                if val in ("0", "1", "2", "3"):
                    valores[ind] = int(val)
                    break
                print("    → Valor inválido. Use 0, 1, 2 ou 3.")

        cod = CodificacaoImagem(
            image_id=args.image_id,
            coder_id=coder,
            **valores,
        )
        erros = cod.validar()
        if erros:
            print(f"\n⚠ Erros de validação: {erros}")
        else:
            gm.salvar_codificacao(cod)
            print(f"\n✓ Codificação salva para {args.image_id} ({coder}).")
            print(cod.perfil_resumido())

    else:
        print("Ação não reconhecida. Use: indicadores | indicador | arvore | manual | "
              "progresso | consolidar | codificar")


# ──────────────────────────────────────────────
# Comando: estatistica
# ──────────────────────────────────────────────

def cmd_estatistica(args):
    """Análise estatística e testes de hipóteses."""
    from atlas_iconocratico import estatistica as est

    if args.acao == "descritivas":
        df = est.carregar_dataset(args.csv or "./data/corpus_codificado.csv")
        est.descritivas_indicadores(df, output_dir=args.saida or "./output/tabelas")
        print("Tabelas descritivas exportadas.")

    elif args.acao == "cruzadas":
        df = est.carregar_dataset(args.csv or "./data/corpus_codificado.csv")
        est.tabelas_cruzadas(df, output_dir=args.saida or "./output/tabelas")
        print("Tabelas cruzadas exportadas.")

    elif args.acao == "hipoteses":
        df = est.carregar_dataset(args.csv or "./data/corpus_codificado.csv")
        resultados = est.executar_todos_testes(df)
        est.imprimir_resultados_testes(resultados)

    elif args.acao == "hipotese":
        if not args.hipotese:
            print("Erro: --hipotese é obrigatório (ex: H1, H2, H3, H4, H5).")
            sys.exit(1)
        df = est.carregar_dataset(args.csv or "./data/corpus_codificado.csv")
        func_map = {
            "H1": est.teste_h1,
            "H2": est.teste_h2,
            "H3": est.teste_h3,
            "H4": est.teste_h4,
            "H5": est.teste_h5,
        }
        h = args.hipotese.upper()
        if h not in func_map:
            print(f"Hipótese desconhecida: {h}. Use H1–H5.")
            sys.exit(1)
        resultado = func_map[h](df)
        print(json.dumps(resultado, indent=2, ensure_ascii=False, default=str))

    elif args.acao == "graficos":
        df = est.carregar_dataset(args.csv or "./data/corpus_codificado.csv")
        est.gerar_todas_visualizacoes(df, output_dir=args.saida or "./output/graficos")
        print("Gráficos gerados.")

    elif args.acao == "relatorio":
        df = est.carregar_dataset(args.csv or "./data/corpus_codificado.csv")
        est.gerar_relatorio_estatistico(
            df,
            output_dir=args.saida or "./output/relatorios",
        )
        print("Relatório estatístico completo gerado.")

    else:
        print("Ação não reconhecida. Use: descritivas | cruzadas | hipoteses | "
              "hipotese | graficos | relatorio")


# ──────────────────────────────────────────────
# Comando: kappa
# ──────────────────────────────────────────────

def cmd_kappa(args):
    """Confiabilidade inter-codificadores (Cohen's Kappa)."""
    from atlas_iconocratico import kappa as kp

    if args.acao == "calcular":
        csv1 = args.csv1 or "./data/codificacoes_COD1.csv"
        csv2 = args.csv2 or "./data/codificacoes_COD2.csv"
        resultados = kp.calcular_kappa_todos(csv1, csv2)
        kp.imprimir_relatorio_kappa(resultados)

        if args.salvar:
            kp.salvar_relatorio_kappa(
                resultados,
                caminho=args.saida or "./output/relatorios/kappa_report.txt",
            )
            print(f"\nRelatório salvo em: {args.saida or './output/relatorios/kappa_report.txt'}")

    elif args.acao == "discordancias":
        csv1 = args.csv1 or "./data/codificacoes_COD1.csv"
        csv2 = args.csv2 or "./data/codificacoes_COD2.csv"
        disc = kp.identificar_discordancias(csv1, csv2)
        if not disc:
            print("Nenhuma discordância encontrada.")
        else:
            print(f"\n{'image_id':<12} {'indicador':<10} {'COD1':<6} {'COD2':<6}")
            print("─" * 36)
            for d in disc[:50]:
                print(f"{d['image_id']:<12} {d['indicador']:<10} "
                      f"{d['valor_cod1']:<6} {d['valor_cod2']:<6}")
            if len(disc) > 50:
                print(f"\n... e mais {len(disc) - 50} discordâncias.")
            print(f"\nTotal: {len(disc)} discordâncias")

    elif args.acao == "drift":
        csv1 = args.csv1 or "./data/codificacoes_COD1.csv"
        csv2 = args.csv2 or "./data/codificacoes_COD2.csv"
        drift = kp.verificar_drift(csv1, csv2)
        if not drift:
            print("Nenhum drift detectado.")
        else:
            print(json.dumps(drift, indent=2, ensure_ascii=False, default=str))

    else:
        print("Ação não reconhecida. Use: calcular | discordancias | drift")


# ──────────────────────────────────────────────
# Comando: iconclass
# ──────────────────────────────────────────────

def cmd_iconclass(args):
    """Integração com Iconclass."""
    from atlas_iconocratico import iconclass_ as ic

    if args.acao == "buscar":
        if not args.notacao:
            print("Erro: --notacao é obrigatório (ex: 44B).")
            sys.exit(1)
        resultado = ic.buscar_codigo(args.notacao, idioma=args.idioma or "en")
        if resultado:
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        else:
            print(f"Código {args.notacao} não encontrado.")

    elif args.acao == "hierarquia":
        if not args.notacao:
            print("Erro: --notacao é obrigatório.")
            sys.exit(1)
        h = ic.buscar_hierarquia(
            args.notacao,
            profundidade=int(args.profundidade or 2),
            idioma=args.idioma or "en",
        )
        for item in h:
            indent = "  " * item.get("level", 0)
            print(f"{indent}{item.get('notation', '')} — {item.get('text', '')}")

    elif args.acao == "tese":
        codigos = ic.listar_codigos_tese()
        for grupo, lista in codigos.items():
            print(f"\n── {grupo} ──")
            for cod in lista:
                print(f"  {cod}")

    elif args.acao == "texto":
        if not args.termo:
            print("Erro: --termo é obrigatório.")
            sys.exit(1)
        resultados = ic.buscar_por_texto(args.termo, idioma=args.idioma or "en")
        if not resultados:
            print("Nenhum resultado encontrado.")
        else:
            for r in resultados[:20]:
                print(f"  {r.get('notation', ''):<12} {r.get('text', '')}")

    elif args.acao == "sugerir":
        if not args.json_codificacao:
            print("Erro: --json-codificacao é obrigatório (JSON com valores dos indicadores).")
            sys.exit(1)
        codificacao = json.loads(args.json_codificacao)
        sugestoes = ic.sugerir_iconclass_para_indicadores(codificacao)
        print("Sugestões Iconclass para esta codificação:")
        for s in sugestoes:
            print(f"  {s}")

    elif args.acao == "mapeamento":
        caminho = args.saida or "./data/iconclass_mapeamento_tese.json"
        ic.exportar_mapeamento_tese(caminho)
        print(f"Mapeamento exportado para: {caminho}")

    else:
        print("Ação não reconhecida. Use: buscar | hierarquia | tese | texto | "
              "sugerir | mapeamento")


# ──────────────────────────────────────────────
# Comando: matriz
# ──────────────────────────────────────────────

def cmd_matriz(args):
    """Matriz de evidências e exportação de dados."""
    from atlas_iconocratico.matriz import (
        GerenciadorMatriz,
        EntradaMatriz,
        integrar_corpus_e_matriz,
    )

    gm = GerenciadorMatriz(diretorio_base=args.dir)

    if args.acao == "lacunas":
        gm.imprimir_relatorio_lacunas()

    elif args.acao == "adicionar":
        if not all([args.titulo, args.autores]):
            print("Erro: --titulo e --autores são obrigatórios.")
            sys.exit(1)
        entrada = EntradaMatriz(
            titulo=args.titulo,
            autores=args.autores,
            ano=int(args.ano) if args.ano else 0,
            tipo_fonte=args.tipo_fonte or "artigo",
            pais_foco=args.pais_foco or "",
            periodo_foco=args.periodo_foco or "",
            metodologia=args.metodologia or "",
            resultados_chave=args.resultados_chave or "",
            hipoteses_relacionadas=args.hipoteses_rel or "",
            qualidade=args.qualidade or "media",
            notas=args.notas or "",
        )
        eid = gm.adicionar_entrada(entrada)
        print(f"Entrada adicionada com ID: {eid}")

    elif args.acao == "importar-elicit":
        if not args.csv:
            print("Erro: --csv é obrigatório (caminho do CSV exportado pelo Elicit).")
            sys.exit(1)
        n = gm.importar_csv_elicit(args.csv)
        print(f"{n} entradas importadas do Elicit.")

    elif args.acao == "listar":
        entradas = gm.listar_entradas()
        if not entradas:
            print("Nenhuma entrada na matriz.")
        else:
            print(f"\n{'ID':<10} {'Ano':<6} {'Título':<50} {'País':<6}")
            print("─" * 75)
            for e in entradas:
                print(f"{e.get('evidence_id',''):<10} {e.get('ano',''):<6} "
                      f"{str(e.get('titulo',''))[:48]:<50} {e.get('pais_foco',''):<6}")
            print(f"\nTotal: {len(entradas)} entradas")

    elif args.acao == "contar":
        n = gm.contar_entradas()
        print(f"Total de entradas na matriz: {n}")

    elif args.acao == "exportar":
        fmt = args.formato or "csv"
        path = gm.exportar_matriz_completa(formato=fmt)
        print(f"Matriz exportada para: {path}")

    elif args.acao == "bibliografia":
        caminho = args.saida or "./data/bibliografia_abnt.txt"
        gm.exportar_bibliografia_abnt(caminho)
        print(f"Bibliografia ABNT exportada para: {caminho}")

    elif args.acao == "integrar":
        integrar_corpus_e_matriz(args.dir)
        print("Integração corpus ↔ matriz concluída.")

    else:
        print("Ação não reconhecida. Use: lacunas | adicionar | importar-elicit | "
              "listar | contar | exportar | bibliografia | integrar")


# ──────────────────────────────────────────────
# Comando: relatorio
# ──────────────────────────────────────────────

def cmd_relatorio(args):
    """Gera o relatório completo de pesquisa."""
    from atlas_iconocratico.corpus import GerenciadorCorpus
    from atlas_iconocratico.codificacao import GerenciadorCodificacao
    from atlas_iconocratico.matriz import GerenciadorMatriz

    print("\n╔══════════════════════════════════════╗")
    print("║   RELATÓRIO COMPLETO DE PESQUISA     ║")
    print("╚══════════════════════════════════════╝\n")

    base = args.dir

    # 1. Status do corpus
    print("═══ 1. CORPUS VISUAL ═══\n")
    gc = GerenciadorCorpus(diretorio_base=base)
    gc.imprimir_relatorio()

    # 2. Progresso da codificação
    print("\n═══ 2. CODIFICAÇÃO ═══\n")
    gcd = GerenciadorCodificacao(diretorio_base=base)
    for coder in ["COD1", "COD2"]:
        try:
            gcd.imprimir_progresso(coder, total_corpus=gc.contar_imagens() or 500)
        except Exception:
            print(f"  {coder}: sem dados de codificação ainda.")

    # 3. Matriz de evidências
    print("\n═══ 3. MATRIZ DE EVIDÊNCIAS ═══\n")
    gm = GerenciadorMatriz(diretorio_base=base)
    gm.imprimir_relatorio_lacunas()

    # 4. Testes estatísticos (se houver dados)
    print("\n═══ 4. ANÁLISE ESTATÍSTICA ═══\n")
    csv_path = Path(base) / "corpus_codificado.csv"
    if csv_path.exists():
        from atlas_iconocratico import estatistica as est
        df = est.carregar_dataset(str(csv_path))
        resultados = est.executar_todos_testes(df)
        est.imprimir_resultados_testes(resultados)
        est.gerar_relatorio_estatistico(df)
    else:
        print("  Dataset consolidado ainda não disponível.")
        print(f"  Execute: python main.py codificacao consolidar")
        print(f"  para gerar {csv_path}")

    # 5. Kappa (se houver dados de dois codificadores)
    print("\n═══ 5. CONFIABILIDADE INTER-CODIFICADORES ═══\n")
    csv1 = Path(base) / "codificacoes_COD1.csv"
    csv2 = Path(base) / "codificacoes_COD2.csv"
    if csv1.exists() and csv2.exists():
        from atlas_iconocratico import kappa as kp
        resultados_k = kp.calcular_kappa_todos(str(csv1), str(csv2))
        kp.imprimir_relatorio_kappa(resultados_k)
    else:
        print("  Dados de dois codificadores ainda não disponíveis.")
        print("  Necessário: codificacoes_COD1.csv e codificacoes_COD2.csv")

    print("\n═══════════════════════════════════════════")
    print("  Relatório concluído.")
    print("═══════════════════════════════════════════\n")


# ──────────────────────────────────────────────
# Parser principal
# ──────────────────────────────────────────────

def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atlas-iconocratico",
        description="Atlas Iconocrático — Toolkit de Pesquisa (CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py info
  python main.py corpus relatorio
  python main.py corpus adicionar --titulo "Marianne 1792" --pais FR --ano 1792
  python main.py codificacao indicadores
  python main.py codificacao codificar --image-id IMG001
  python main.py estatistica hipoteses --csv ./data/corpus_codificado.csv
  python main.py kappa calcular --salvar
  python main.py iconclass buscar --notacao 44B
  python main.py matriz lacunas
  python main.py matriz importar-elicit --csv elicit_export.csv
  python main.py relatorio
        """,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="comando", help="Comando a executar")

    # ─── info ───
    p_info = subparsers.add_parser("info", help="Informações sobre o toolkit")
    p_info.set_defaults(func=cmd_info)

    # ─── corpus ───
    p_corpus = subparsers.add_parser("corpus", help="Gestão do corpus visual")
    p_corpus.add_argument("acao", nargs="?", default="relatorio",
                          help="relatorio | adicionar | listar | contar | fontes")
    p_corpus.add_argument("--dir", default="./data", help="Diretório base dos dados")
    p_corpus.add_argument("--titulo", help="Título da imagem")
    p_corpus.add_argument("--pais", help="País (FR/UK/USA/DE/BR)")
    p_corpus.add_argument("--ano", help="Ano de produção")
    p_corpus.add_argument("--autor", help="Autor/artista")
    p_corpus.add_argument("--tipo", help="Tipo (gravura/pintura/escultura/cartaz/fotografia)")
    p_corpus.add_argument("--fonte", help="Fonte/acervo")
    p_corpus.add_argument("--arquivo", help="Caminho do arquivo original")
    p_corpus.add_argument("--notas", help="Notas adicionais")
    p_corpus.set_defaults(func=cmd_corpus)

    # ─── codificacao ───
    p_cod = subparsers.add_parser("codificacao", help="Sistema de codificação")
    p_cod.add_argument("acao", nargs="?", default="indicadores",
                       help="indicadores | indicador | arvore | manual | progresso | consolidar | codificar")
    p_cod.add_argument("--dir", default="./data", help="Diretório base")
    p_cod.add_argument("--codigo", help="Código do indicador (FEI, CII, etc.)")
    p_cod.add_argument("--descricao", help="Descrição da imagem (para árvore de decisão)")
    p_cod.add_argument("--saida", help="Caminho de saída")
    p_cod.add_argument("--coder", help="ID do codificador (COD1, COD2)")
    p_cod.add_argument("--total", help="Total do corpus (para progresso)")
    p_cod.add_argument("--image-id", dest="image_id", help="ID da imagem")
    p_cod.set_defaults(func=cmd_codificacao)

    # ─── estatistica ───
    p_est = subparsers.add_parser("estatistica", help="Análise estatística")
    p_est.add_argument("acao", nargs="?", default="descritivas",
                       help="descritivas | cruzadas | hipoteses | hipotese | graficos | relatorio")
    p_est.add_argument("--csv", help="Caminho do CSV de dados codificados")
    p_est.add_argument("--saida", help="Diretório de saída")
    p_est.add_argument("--hipotese", help="Hipótese específica (H1–H5)")
    p_est.set_defaults(func=cmd_estatistica)

    # ─── kappa ───
    p_kappa = subparsers.add_parser("kappa", help="Confiabilidade inter-codificadores")
    p_kappa.add_argument("acao", nargs="?", default="calcular",
                         help="calcular | discordancias | drift")
    p_kappa.add_argument("--csv1", help="CSV do codificador 1")
    p_kappa.add_argument("--csv2", help="CSV do codificador 2")
    p_kappa.add_argument("--saida", help="Caminho de saída do relatório")
    p_kappa.add_argument("--salvar", action="store_true", help="Salvar relatório em arquivo")
    p_kappa.set_defaults(func=cmd_kappa)

    # ─── iconclass ───
    p_ic = subparsers.add_parser("iconclass", help="Integração Iconclass")
    p_ic.add_argument("acao", nargs="?", default="tese",
                      help="buscar | hierarquia | tese | texto | sugerir | mapeamento")
    p_ic.add_argument("--notacao", help="Notação Iconclass (ex: 44B)")
    p_ic.add_argument("--idioma", help="Idioma (en/de/fr/it)")
    p_ic.add_argument("--profundidade", help="Profundidade da hierarquia")
    p_ic.add_argument("--termo", help="Termo de busca textual")
    p_ic.add_argument("--json-codificacao", dest="json_codificacao",
                      help="JSON com codificação (para sugestões)")
    p_ic.add_argument("--saida", help="Caminho de saída")
    p_ic.set_defaults(func=cmd_iconclass)

    # ─── matriz ───
    p_mat = subparsers.add_parser("matriz", help="Matriz de evidências")
    p_mat.add_argument("acao", nargs="?", default="lacunas",
                       help="lacunas | adicionar | importar-elicit | listar | contar | "
                            "exportar | bibliografia | integrar")
    p_mat.add_argument("--dir", default="./data", help="Diretório base")
    p_mat.add_argument("--titulo", help="Título da fonte")
    p_mat.add_argument("--autores", help="Autores")
    p_mat.add_argument("--ano", help="Ano de publicação")
    p_mat.add_argument("--tipo-fonte", dest="tipo_fonte", help="Tipo de fonte")
    p_mat.add_argument("--pais-foco", dest="pais_foco", help="País foco")
    p_mat.add_argument("--periodo-foco", dest="periodo_foco", help="Período foco")
    p_mat.add_argument("--metodologia", help="Metodologia")
    p_mat.add_argument("--resultados-chave", dest="resultados_chave", help="Resultados-chave")
    p_mat.add_argument("--hipoteses-rel", help="Hipóteses relacionadas (H1–H5)")
    p_mat.add_argument("--qualidade", help="Qualidade (alta/media/baixa)")
    p_mat.add_argument("--notas", help="Notas")
    p_mat.add_argument("--csv", help="Caminho do CSV (para importação)")
    p_mat.add_argument("--formato", help="Formato de exportação (csv/json)")
    p_mat.add_argument("--saida", help="Caminho de saída")
    p_mat.set_defaults(func=cmd_matriz)

    # ─── relatorio ───
    p_rel = subparsers.add_parser("relatorio", help="Relatório completo de pesquisa")
    p_rel.add_argument("--dir", default="./data", help="Diretório base")
    p_rel.set_defaults(func=cmd_relatorio)

    return parser


# ──────────────────────────────────────────────
# Entrypoint
# ──────────────────────────────────────────────

def main():
    parser = criar_parser()
    args = parser.parse_args()

    if not args.comando:
        _banner()
        parser.print_help()
        sys.exit(0)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
