"""
Atlas Iconocrático — Toolkit de Pesquisa
=========================================
Pacote Python para análise iconográfica quantitativa de alegorias
femininas na cultura jurídica ocidental (1789–2024).

Este toolkit foi desenvolvido como parte da tese de doutorado:
"Contrato Sexual Visual & Regime Iconocrático: Alegorias Femininas
na Cultura Jurídica (1789–2024)" — PPGD/UFSC.

O pacote implementa um método misto iconológico-forense que combina:
    1. A tradição warburguiana (Pathosformel, Nachleben, Denkraum)
       com análise de Didi-Huberman (iconologia do intervalo)
    2. Codificação quantitativa via 10 indicadores operacionalizados
    3. Testes estatísticos inferenciais para 5 hipóteses derivadas
       do referencial teórico (Pateman, Mondzain, Mills)

Módulos disponíveis:
    corpus      — Gestão do corpus visual de 300–500 imagens
                   organizadas por país (FR/UK/USA/DE/BR),
                   regime (fundacional/normativo/militar) e suporte
    codificacao — Sistema de codificação com 10 indicadores:
                   FEI, CII, PRI, SMI, SMS, AMCP, MVI, WI, RI, AI
    estatistica — Análise estatística descritiva e inferencial,
                   incluindo testes para as hipóteses H1–H5
    kappa       — Confiabilidade inter-codificadores via Cohen's
                   Kappa (weighted para ordinais, unweighted para
                   categóricos), com monitoramento de drift
    iconclass_  — Integração com o sistema internacional Iconclass,
                   mapeamento de códigos relevantes para alegorias
                   femininas e sugestão automática
    matriz      — Matriz de evidências com estrutura de 13 colunas
                   compatível com Elicit, análise de lacunas e
                   exportação de bibliografia ABNT

Referências teóricas fundamentais:
    - Pateman, C. (1988). The Sexual Contract.
    - Mondzain, M.-J. (1996/2005). Image, Icon, Economy.
    - Warburg, A. (1929). Bilderatlas Mnemosyne.
    - Didi-Huberman, G. (2002). L'image survivante.
    - Mills, C. (1997). The Racial Contract.

Uso básico:
    from atlas_iconocratico.corpus import criar_corpus
    from atlas_iconocratico.codificacao import CodificacaoImagem
    from atlas_iconocratico.estatistica import executar_todos_testes
"""

__version__ = "0.1.0"
__author__ = "Atlas Iconocrático — PPGD/UFSC"
