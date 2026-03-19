const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, TableOfContents,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak, TabStopPosition, TabStopType
} = require("docx");

// ── Helpers ──────────────────────────────────────────────────────────────────

const FONT = "Calibri";
const PAGE_WIDTH = 11906; // A4
const PAGE_HEIGHT = 16838;
const MARGIN = 1440;
const CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN; // 9026

const border = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0 };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };

function p(text, opts = {}) {
  const runs = [];
  if (typeof text === "string") {
    runs.push(new TextRun({ text, font: FONT, size: opts.size || 22, bold: !!opts.bold, italics: !!opts.italics, color: opts.color }));
  } else if (Array.isArray(text)) {
    text.forEach(t => {
      if (typeof t === "string") {
        runs.push(new TextRun({ text: t, font: FONT, size: opts.size || 22 }));
      } else {
        runs.push(new TextRun({ text: t.text, font: FONT, size: t.size || opts.size || 22, bold: t.bold, italics: t.italics, color: t.color }));
      }
    });
  }
  return new Paragraph({
    alignment: opts.alignment || AlignmentType.JUSTIFIED,
    spacing: { after: opts.after !== undefined ? opts.after : 200, before: opts.before || 0, line: opts.line || 276 },
    indent: opts.indent,
    children: runs,
    ...(opts.heading ? { heading: opts.heading } : {}),
    ...(opts.numbering ? { numbering: opts.numbering } : {}),
  });
}

function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 240 },
    children: [new TextRun({ text, font: FONT, size: 28, bold: true, color: "1a1a2e" })],
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 300, after: 200 },
    children: [new TextRun({ text, font: FONT, size: 24, bold: true, color: "16213e" })],
  });
}

function heading3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 240, after: 160 },
    children: [new TextRun({ text, font: FONT, size: 22, bold: true, italics: true, color: "1a1a2e" })],
  });
}

function emptyPara(h = 100) {
  return new Paragraph({ spacing: { after: h }, children: [] });
}

function makeCell(text, width, opts = {}) {
  const runs = [];
  if (typeof text === "string") {
    runs.push(new TextRun({ text, font: FONT, size: opts.size || 18, bold: !!opts.bold, italics: !!opts.italics, color: opts.color }));
  } else if (Array.isArray(text)) {
    text.forEach(t => {
      if (typeof t === "string") {
        runs.push(new TextRun({ text: t, font: FONT, size: opts.size || 18 }));
      } else {
        runs.push(new TextRun({ text: t.text, font: FONT, size: t.size || opts.size || 18, bold: t.bold, italics: t.italics, color: t.color }));
      }
    });
  }
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    shading: opts.shading ? { fill: opts.shading, type: ShadingType.CLEAR } : undefined,
    children: [new Paragraph({
      alignment: opts.alignment || AlignmentType.LEFT,
      spacing: { after: 40 },
      children: runs,
    })],
  });
}

function makeCellMultiPara(paragraphs, width, opts = {}) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    shading: opts.shading ? { fill: opts.shading, type: ShadingType.CLEAR } : undefined,
    children: paragraphs,
  });
}

// ── Content ──────────────────────────────────────────────────────────────────

const children = [];

// Title page
children.push(emptyPara(2000));
children.push(p("UNIVERSIDADE FEDERAL DE SANTA CATARINA", { alignment: AlignmentType.CENTER, size: 22, bold: true }));
children.push(p("PROGRAMA DE P\u00D3S-GRADUA\u00C7\u00C3O EM DIREITO (PPGD/UFSC)", { alignment: AlignmentType.CENTER, size: 20 }));
children.push(emptyPara(800));
children.push(p("AP\u00CANDICE METODOL\u00D3GICO", { alignment: AlignmentType.CENTER, size: 36, bold: true }));
children.push(emptyPara(200));
children.push(p("TOOLKIT COMPUTACIONAL PARA AN\u00C1LISE ICONOGR\u00C1FICA QUANTITATIVA", { alignment: AlignmentType.CENTER, size: 26, bold: true }));
children.push(emptyPara(400));
children.push(p([
  { text: "Tese: ", bold: true, size: 22 },
  { text: "\u201CContrato Sexual Visual & Regime Iconocr\u00E1tico: Alegorias Femininas na Cultura Jur\u00EDdica (1789\u20132024)\u201D", italics: true, size: 22 }
], { alignment: AlignmentType.CENTER }));
children.push(emptyPara(2000));
children.push(p("Florian\u00F3polis, 2026", { alignment: AlignmentType.CENTER, size: 22 }));

// Page break + TOC
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(p("SUM\u00C1RIO", { alignment: AlignmentType.CENTER, size: 28, bold: true, after: 400 }));
children.push(new TableOfContents("Sum\u00E1rio", { hyperlink: true, headingStyleRange: "1-3" }));

// ── Section 1: Introdu\u00E7\u00E3o e Justificativa ──
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading1("1. Introdu\u00E7\u00E3o e Justificativa"));

children.push(p("A presente tese de doutorado, intitulada \u201CContrato Sexual Visual & Regime Iconocr\u00E1tico: Alegorias Femininas na Cultura Jur\u00EDdica (1789\u20132024)\u201D, desenvolvida no \u00E2mbito do Programa de P\u00F3s-Gradua\u00E7\u00E3o em Direito da Universidade Federal de Santa Catarina (PPGD/UFSC), investiga como as alegorias femininas do poder estatal \u2014 Marianne, Justitia, Columbia, a Rep\u00FAblica e Britannia \u2014 operam como dispositivos visuais que simultaneamente legitimam e invisibilizam o contrato sexual subjacente \u00E0 ordem jur\u00EDdica moderna. Para conduzir esta investiga\u00E7\u00E3o com rigor metodol\u00F3gico, tornou-se necess\u00E1rio desenvolver um conjunto de ferramentas computacionais capazes de operacionalizar categorias anal\u00EDticas oriundas da iconologia warburguiana, da cr\u00EDtica feminista do direito e da teoria cr\u00EDtica racial."));

children.push(p("A lacuna metodol\u00F3gica que este toolkit busca preencher \u00E9 significativa. Na intersec\u00E7\u00E3o entre estudos visuais, teoria jur\u00EDdica e humanidades digitais, n\u00E3o existe ferramenta que combine a an\u00E1lise iconol\u00F3gica de tradi\u00E7\u00E3o warburguiana (Warburg, 1929; Didi-Huberman, 2002) com a codifica\u00E7\u00E3o quantitativa de alegorias de g\u00EAnero no Estado. As ferramentas existentes no campo das humanidades digitais \u2014 como o Iconclass Browser ou plataformas de an\u00E1lise de imagens \u2014 n\u00E3o oferecem indicadores espec\u00EDficos para capturar dimens\u00F5es como a corporalidade feminina (FEI), a idealiza\u00E7\u00E3o racial (WI/RI) ou a vulnerabilidade maternal (MVI) presentes nas alegorias jur\u00EDdicas."));

children.push(p("O m\u00E9todo adotado pela tese \u00E9 designado como \u201Ciconol\u00F3gico-forense\u201D, combinando a leitura profunda (close reading) das imagens \u2014 em di\u00E1logo com Aby Warburg, Erwin Panofsky e Georges Didi-Huberman \u2014 com a codifica\u00E7\u00E3o sistem\u00E1tica de dez indicadores quantitativos que permitem compara\u00E7\u00F5es transversais entre pa\u00EDses, regimes pol\u00EDticos e suportes materiais. Este enfoque misto (mixed-method) responde \u00E0 exig\u00EAncia de se analisar um corpus de 300 a 500 imagens distribu\u00EDdas por cinco pa\u00EDses (Fran\u00E7a, Brasil, Estados Unidos, Reino Unido e Alemanha), tr\u00EAs tipos de regime (normativo, militar/autorit\u00E1rio e transit\u00F3rio) e m\u00FAltiplos suportes (moedas, selos, monumentos, pinturas oficiais, cartazes e m\u00EDdia digital)."));

children.push(p("O toolkit foi integralmente desenvolvido em Python 3.10+, utilizando exclusivamente bibliotecas de c\u00F3digo aberto. Esta escolha responde a tr\u00EAs imperativos acad\u00EAmicos: (a) reprodutibilidade, permitindo que outros pesquisadores repliquem e verifiquem os resultados; (b) transpar\u00EAncia, com todo o c\u00F3digo-fonte dispon\u00EDvel para inspe\u00E7\u00E3o da banca e da comunidade cient\u00EDfica; e (c) acessibilidade, n\u00E3o exigindo licen\u00E7as comerciais de software. O presente ap\u00EAndice documenta cada m\u00F3dulo, suas justificativas te\u00F3ricas, regras operacionais e decis\u00F5es de design, visando oferecer \u00E0 banca examinadora uma vis\u00E3o completa e cr\u00EDtica do aparato metodol\u00F3gico empregado."));

children.push(p("Cabe ressaltar que o desenvolvimento do toolkit n\u00E3o constitui um fim em si mesmo, mas um meio para garantir a validade interna e externa da pesquisa. Cada m\u00F3dulo corresponde a uma etapa espec\u00EDfica do cronograma da tese, desde a constitui\u00E7\u00E3o do corpus (Meses 4\u20136) at\u00E9 a an\u00E1lise estat\u00EDstica final (Meses 13\u201318), passando pela codifica\u00E7\u00E3o inter-codificadores (Meses 9\u201310) e pela integra\u00E7\u00E3o com o padr\u00E3o internacional Iconclass. A documenta\u00E7\u00E3o que se segue reflete este percurso, apresentando n\u00E3o apenas o \u201Ccomo\u201D, mas sobretudo o \u201Cpor qu\u00EA\u201D de cada decis\u00E3o arquitetural e anal\u00EDtica."));


// ── Section 2: Arquitetura do Sistema ──
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading1("2. Arquitetura do Sistema"));

children.push(p("O toolkit \u00E9 composto por seis m\u00F3dulos interdependentes, cada um respons\u00E1vel por uma etapa espec\u00EDfica do fluxo de pesquisa: (1) corpus.py, para gest\u00E3o e valida\u00E7\u00E3o do acervo de imagens; (2) codificacao.py, que implementa o sistema de dez indicadores de codifica\u00E7\u00E3o; (3) estatistica.py, respons\u00E1vel pelas an\u00E1lises descritivas e inferenciais; (4) kappa.py, dedicado ao c\u00E1lculo de confiabilidade inter-codificadores; (5) iconclass_.py, que realiza a ponte entre o sistema de codifica\u00E7\u00E3o pr\u00F3prio e o padr\u00E3o internacional Iconclass; e (6) matriz.py, que gerencia a matriz de evid\u00EAncias proveniente das revis\u00F5es sistem\u00E1ticas. Todos os m\u00F3dulos s\u00E3o orquestrados por um ponto de entrada unificado (main.py) que oferece uma interface de linha de comando (CLI)."));

children.push(p("O fluxo de dados segue um pipeline sequencial com retroalimenta\u00E7\u00F5es. O pesquisador inicia pela constitui\u00E7\u00E3o do corpus, adicionando imagens com seus metadados (pa\u00EDs, figura aleg\u00F3rica, suporte, ano, fonte). Uma vez que o corpus atinge o checkpoint m\u00EDnimo de valida\u00E7\u00E3o (\u2265300 imagens, \u226550 por pa\u00EDs, todos os tr\u00EAs regimes representados), procede-se \u00E0 etapa de codifica\u00E7\u00E3o, na qual cada imagem recebe valores nos dez indicadores. Os dados codificados alimentam simultaneamente o m\u00F3dulo de estat\u00EDstica (para testes de hip\u00F3teses), o m\u00F3dulo de kappa (para verifica\u00E7\u00E3o de confiabilidade entre codificadores) e o m\u00F3dulo Iconclass (para mapeamento ao padr\u00E3o internacional). A matriz de evid\u00EAncias opera em paralelo, integrando achados bibliogr\u00E1ficos das nove revis\u00F5es sistem\u00E1ticas previstas na tese."));

children.push(p("As escolhas tecnol\u00F3gicas foram guiadas por crit\u00E9rios de reprodutibilidade, maturidade e adequa\u00E7\u00E3o ao campo das humanidades digitais. Python 3.10+ foi escolhido como linguagem principal por ser a mais utilizada em projetos de humanidades digitais, al\u00E9m de oferecer um ecossistema robusto de bibliotecas cient\u00EDficas. As depend\u00EAncias centrais incluem: pandas (vers\u00E3o \u22651.5) para manipula\u00E7\u00E3o de dados tabulares; scipy (vers\u00E3o \u22651.7) para testes estat\u00EDsticos n\u00E3o-param\u00E9tricos; scikit-learn para m\u00E9tricas de concord\u00E2ncia como o Cohen\u2019s Kappa; matplotlib e seaborn para visualiza\u00E7\u00F5es estat\u00EDsticas; e a biblioteca padr\u00E3o do Python para opera\u00E7\u00F5es de sistema de arquivos e serializa\u00E7\u00E3o JSON."));

children.push(p("A op\u00E7\u00E3o por ferramentas de c\u00F3digo aberto n\u00E3o \u00E9 meramente pragm\u00E1tica, mas epistemol\u00F3gica. Em uma tese que investiga regimes de visibilidade e poder, a transpar\u00EAncia do aparato anal\u00EDtico constitui em si mesma um posicionamento metodol\u00F3gico. Diferentemente de softwares propriet\u00E1rios como SPSS ou NVivo, cujos algoritmos internos s\u00E3o opacos, o toolkit aqui documentado permite inspe\u00E7\u00E3o integral de cada c\u00E1lculo, cada regra de valida\u00E7\u00E3o e cada \u00E1rvore de decis\u00E3o empregada na codifica\u00E7\u00E3o. As bibliotecas selecionadas (pandas, scipy, scikit-learn, matplotlib, seaborn) s\u00E3o amplamente validadas pela comunidade cient\u00EDfica internacional e possuem documenta\u00E7\u00E3o extensa, garantindo que futuras replica\u00E7\u00F5es possam ser conduzidas sem depend\u00EAncia do presente pesquisador."));


// ── Section 3: M\u00F3dulo de Gest\u00E3o do Corpus ──
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading1("3. M\u00F3dulo de Gest\u00E3o do Corpus (corpus.py)"));

children.push(p("O m\u00F3dulo corpus.py constitui o alicerce do toolkit, sendo respons\u00E1vel pela gest\u00E3o sistem\u00E1tica de um acervo de 300 a 500 imagens que comp\u00F5em o corpus iconogr\u00E1fico da tese. Estas imagens s\u00E3o distribu\u00EDdas por cinco pa\u00EDses (Fran\u00E7a, Brasil, Estados Unidos, Reino Unido e Alemanha), tr\u00EAs tipos de regime pol\u00EDtico (normativo, militar/autorit\u00E1rio e transit\u00F3rio) e m\u00FAltiplos suportes materiais (moedas, selos, monumentos, pinturas oficiais, cartazes e m\u00EDdia digital). A complexidade combinat\u00F3ria destas dimens\u00F5es exige uma estrutura de dados rigorosa que previna erros de classifica\u00E7\u00E3o e garanta a completude do corpus."));

children.push(p("O modelo de dados central \u00E9 implementado como uma dataclass Python denominada ImagemCorpus, contendo 13 campos estruturados: Image_ID (identificador \u00FAnico alfanum\u00E9rico), Country (c\u00F3digo ISO do pa\u00EDs: FR, BR, US, GB, DE), Figure (figura aleg\u00F3rica: Marianne, Justitia, Columbia, Rep\u00FAblica, Britannia), Support (suporte material: moeda, selo, monumento, pintura, cartaz, digital), Year (ano de produ\u00E7\u00E3o ou estimativa), Source_URL (URL da fonte digital), Rights (regime de direitos autorais), File_path (caminho relativo do arquivo de imagem), Regime_preliminary (classifica\u00E7\u00E3o preliminar do regime pol\u00EDtico), Description (descri\u00E7\u00E3o iconogr\u00E1fica breve), Artist (artista ou autor, quando identificado), Collection (cole\u00E7\u00E3o ou acervo de origem) e Added_date (data de inser\u00E7\u00E3o no corpus)."));

children.push(p("As regras de valida\u00E7\u00E3o implementadas servem como salvaguardas contra inconsist\u00EAncias que comprometeriam a an\u00E1lise comparativa. O campo Country aceita exclusivamente os c\u00F3digos dos cinco pa\u00EDses estudados; o campo Figure \u00E9 restrito \u00E0s cinco alegorias mapeadas; o campo Year deve situar-se no intervalo 1789\u20132024; e o campo Support deve corresponder a uma das seis categorias predefinidas. Estas restri\u00E7\u00F5es n\u00E3o s\u00E3o arbitr\u00E1rias, mas decorrem diretamente do recorte temporal e geogr\u00E1fico da tese, garantindo que toda imagem inserida no corpus seja compar\u00E1vel com as demais dentro dos eixos anal\u00EDticos propostos."));

children.push(p("A organiza\u00E7\u00E3o f\u00EDsica dos arquivos segue o padr\u00E3o hier\u00E1rquico /corpus/{country}/, de modo que as imagens francesas residem em /corpus/FR/, as brasileiras em /corpus/BR/, e assim por diante. A conven\u00E7\u00E3o de nomenclatura dos arquivos obedece ao formato: {PA\u00CDS}_{FIGURA}_{ANO}_{SUPORTE}_{SEQUENCIAL}.jpg, como por exemplo FR_Marianne_1792_moeda_001.jpg. Esta conven\u00E7\u00E3o torna o arquivo autoexplicativo, permitindo identifica\u00E7\u00E3o visual r\u00E1pida mesmo fora do ambiente do toolkit, e facilita opera\u00E7\u00F5es de backup e migra\u00E7\u00E3o."));

children.push(p("O sistema de checkpoint de valida\u00E7\u00E3o opera em tr\u00EAs n\u00EDveis: (a) o corpus deve conter no m\u00EDnimo 300 imagens para que as an\u00E1lises estat\u00EDsticas tenham poder suficiente; (b) cada pa\u00EDs deve ter no m\u00EDnimo 50 imagens para permitir compara\u00E7\u00F5es intra-pa\u00EDs significativas; e (c) os tr\u00EAs tipos de regime devem estar representados em cada pa\u00EDs para viabilizar a an\u00E1lise comparativa por regime. Estes checkpoints est\u00E3o alinhados com o cronograma da tese, devendo ser atingidos entre os Meses 4 e 6 da pesquisa. O toolkit emite relat\u00F3rios detalhados de progresso indicando lacunas espec\u00EDficas a serem preenchidas."));


// ── Section 4: Sistema de Codifica\u00E7\u00E3o ──
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading1("4. Sistema de Codifica\u00E7\u00E3o: Os 10 Indicadores (codificacao.py)"));

children.push(p("O m\u00F3dulo codificacao.py implementa o cora\u00E7\u00E3o anal\u00EDtico do toolkit: um sistema de dez indicadores que operacionalizam as categorias te\u00F3ricas centrais da tese em vari\u00E1veis mensur\u00E1veis. Cada indicador foi desenhado para capturar uma dimens\u00E3o espec\u00EDfica das alegorias femininas no direito, articulando tradi\u00E7\u00F5es te\u00F3ricas distintas \u2014 a cr\u00EDtica do contrato sexual (Pateman, 1988), a economia ic\u00F4nica (Mondzain, 1996), a iconologia warburguiana (Warburg, 1929; Didi-Huberman, 2002), o contrato racial (Mills, 1997) e a hist\u00F3ria das alegorias republicanas (Agulhon, 1979; Warner, 1985). O sistema de codifica\u00E7\u00E3o foi concebido para ser utilizado tanto pelo pesquisador principal quanto por codificadores independentes, viabilizando o c\u00E1lculo de confiabilidade inter-codificadores (Se\u00E7\u00E3o 6)."));

children.push(p("A l\u00F3gica de design dos indicadores segue dois princ\u00EDpios fundamentais. Primeiro, cada indicador deve ser operacionaliz\u00E1vel: sua defini\u00E7\u00E3o deve ser suficientemente precisa para que dois codificadores independentes, diante da mesma imagem, cheguem ao mesmo valor na grande maioria dos casos (Kappa \u2265 0,80). Segundo, cada indicador deve ser teoricamente ancorado: n\u00E3o se trata de medir propriedades visuais arbitr\u00E1rias, mas de quantificar dimens\u00F5es que a literatura identifica como constitutivas do regime iconocr\u00E1tico. A tabela a seguir apresenta os dez indicadores com suas defini\u00E7\u00F5es operacionais completas."));

// ── Table: 10 Indicators ──
// We'll split this into two tables for readability: one overview and one with full definitions

children.push(heading2("4.1 Tabela dos Indicadores"));

// Overview table with 7 columns
const indColWidths = [700, 1000, 1300, 800, 700, 3226, 1300];
const indHeaderShading = "1a1a2e";
const indHeaderColor = "FFFFFF";
const indAltShading = "F2F4F8";

function indHeaderCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    shading: { fill: indHeaderShading, type: ShadingType.CLEAR },
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 20 },
      children: [new TextRun({ text, font: FONT, size: 16, bold: true, color: indHeaderColor })],
    })],
  });
}

function indRow(cells, alt) {
  const sh = alt ? indAltShading : undefined;
  return new TableRow({
    children: cells.map((text, i) => {
      const w = indColWidths[i];
      const isLast2 = i >= 5;
      return makeCellMultiPara(
        [new Paragraph({
          alignment: i < 5 ? AlignmentType.CENTER : AlignmentType.LEFT,
          spacing: { after: 20 },
          children: [new TextRun({ text, font: FONT, size: 15, italics: i === 1 })],
        })],
        w,
        { shading: sh }
      );
    }),
  });
}

const indicatorTable = new Table({
  width: { size: CONTENT_WIDTH, type: WidthType.DXA },
  columnWidths: indColWidths,
  rows: [
    new TableRow({
      children: [
        indHeaderCell("C\u00F3digo", indColWidths[0]),
        indHeaderCell("Nome (EN)", indColWidths[1]),
        indHeaderCell("Nome (PT)", indColWidths[2]),
        indHeaderCell("Tipo", indColWidths[3]),
        indHeaderCell("Escala", indColWidths[4]),
        indHeaderCell("Defini\u00E7\u00E3o Operacional", indColWidths[5]),
        indHeaderCell("Pain\u00E9is", indColWidths[6]),
      ],
    }),
    indRow(["FEI", "Feminine Embodiment Index", "\u00CDndice de Corporalidade Feminina", "Ordinal", "0\u20133", "0 = abstrato/geom\u00E9trico (s\u00EDmbolo sem corpo); 1 = corpo sugerido por drapejamento; 2 = corpo vis\u00EDvel (seios/cintura); 3 = corpo enfatizado (nudez/sensualidade)", "I, II, III"], true),
    indRow(["CII", "Classical Ideal Index", "\u00CDndice de Ideal Cl\u00E1ssico", "Ordinal", "0\u20133", "0 = medieval/barroco/moderno (sem tra\u00E7os cl\u00E1ssicos); 1 = elementos cl\u00E1ssicos mistos; 2 = predomin\u00E2ncia cl\u00E1ssica; 3 = cl\u00E1ssico puro (toga, perfil greco-romano)", "I, IV"], false),
    indRow(["PRI", "Posture & Realm Index", "\u00CDndice de Postura e Dom\u00EDnio", "Categ\u00F3rico", "3 cat.", "serena (passividade digna, est\u00E1tica); militante (a\u00E7\u00E3o combativa, din\u00E2mica); sacrificial (sofrimento, entrega, vulnerabilidade)", "II, V"], true),
    indRow(["SMI", "Symbolic Material Index", "\u00CDndice de Material Simb\u00F3lico", "Ordinal", "0\u20133", "Contagem de atributos simb\u00F3licos presentes: balan\u00E7a, espada, venda, livro, fasces, tocha, coroa, barrete fr\u00EDgio, etc. 0 = nenhum; 1 = um; 2 = dois; 3 = tr\u00EAs ou mais", "III, IV"], false),
    indRow(["SMS", "Symbolic Meaning Score", "Escore de Significado Simb\u00F3lico", "Categ\u00F3rico", "3 cat.", "Cruzamento de PRI com contexto material: serena (atributos de paz/justi\u00E7a); militante (atributos de combate/liberdade); sacrificial (atributos de sofrimento/martir\u00EDzio)", "III, V"], true),
    indRow(["AMCP", "Armament & Crisis Profile", "Perfil de Armamento e Crise", "Ordinal", "0\u20133", "0 = sem armas; 1 = armamento defensivo (escudo, \u00E9gide); 2 = armamento ofensivo (espada empunhada, lan\u00E7a); 3 = arsenal completo (m\u00FAltiplas armas + postura combativa)", "II, V, VI"], false),
    indRow(["MVI", "Maternal-Vulnerability Index", "\u00CDndice de Vulnerabilidade Maternal", "Ordinal", "0\u20133", "0 = nenhuma vulnerabilidade; 1 = vulnerabilidade sugerida (express\u00E3o facial, gest\u00E3o protetiva); 2 = seio exposto (amamentamento aleg\u00F3rico); 3 = ferida/morta (sacrif\u00EDcio corporal expl\u00EDcito)", "II, V, VII"], true),
    indRow(["WI", "Whiteness Index", "\u00CDndice de Branquitude", "Ordinal", "0\u20133", "0 = amb\u00EDguo/diverso (tra\u00E7os n\u00E3o-europeus ou indeterminados); 1 = tra\u00E7os cl\u00E1ssicos (pele clara, nariz reto); 2 = branquitude expl\u00EDcita (fei\u00E7\u00F5es europeias marcadas); 3 = branquitude + hierarquia (contraste com figuras racializadas)", "IV, VIII"], false),
    indRow(["RI", "Racial Idealisation", "Idealiza\u00E7\u00E3o Racial", "Bin\u00E1rio", "0/1", "0 = n\u00E3o se conforma ao ideal cl\u00E1ssico branco / apresenta diversidade; 1 = reproduz o ideal cl\u00E1ssico branco (pele alabastro, tra\u00E7os greco-romanos, cabelo liso)", "IV, VIII"], true),
    indRow(["AI", "Allegory-Biography Index", "\u00CDndice Alegoria-Biografia", "Ordinal", "0\u20133", "0 = alegoria pura (sem refer\u00EAncia a pessoa real); 1 = alegoria nomeada (ex.: \u201CMariannes\u201D gen\u00E9ricas); 2 = inspirada em pessoa real (modelo identificado); 3 = pessoa real como alegoria (ex.: Brigitte Bardot como Marianne)", "IX"], false),
  ],
});

children.push(indicatorTable);
children.push(emptyPara(200));

// ── Detailed explanations of key indicators ──
children.push(heading2("4.2 \u00C1rvores de Decis\u00E3o e Fundamenta\u00E7\u00E3o Te\u00F3rica"));

children.push(heading3("4.2.1 FEI \u2014 \u00CDndice de Corporalidade Feminina"));
children.push(p("O FEI (Feminine Embodiment Index) operacionaliza a tese central de Carole Pateman (1988) sobre o contrato sexual: a ordem jur\u00EDdica moderna funda-se na subordina\u00E7\u00E3o do corpo feminino, que \u00E9 simultaneamente mobilizado como s\u00EDmbolo do Estado e apagado como sujeito pol\u00EDtico. A \u00E1rvore de decis\u00E3o do FEI procede em quatro n\u00EDveis: primeiro, verifica-se se a representao \u00E9 abstrata ou geom\u00E9trica (FEI=0), como no caso de s\u00EDmbolos her\u00E1ldicos sem figura humana; segundo, se o corpo \u00E9 apenas sugerido por drapejamentos que ocultam a forma (FEI=1), como nas Mariannes de moedas convencionais; terceiro, se o corpo \u00E9 vis\u00EDvel com marca\u00E7\u00E3o de seios ou cintura (FEI=2), como na Libert\u00E9 de Delacroix; e quarto, se h\u00E1 \u00EAnfase na nudez ou sensualidade (FEI=3), como em certas alegorias acad\u00EAmicas do s\u00E9culo XIX."));

children.push(p("A gradua\u00E7\u00E3o do FEI permite mensurar aquilo que Marina Warner (1985) denomina a \u201Cparadoxal desnudez da virtude\u201D: quanto mais a alegoria feminina se despoja de roupas, mais ela supostamente se aproxima da verdade e da pureza, mas simultaneamente mais se oferece ao olhar masculino como objeto de contempla\u00E7\u00E3o. O cruzamento do FEI com o suporte material (Se\u00E7\u00E3o 5, Hip\u00F3tese H3) permite testar se os suportes de circula\u00E7\u00E3o \u00EDntima (moedas, selos) demandam uma feminilidade mais contida do que os monumentos p\u00FAblicos \u2014 o que Pateman chamaria de modula\u00E7\u00E3o do contrato sexual conforme o espa\u00E7o de visibilidade."));

children.push(heading3("4.2.2 AMCP \u2014 Perfil de Armamento e Crise"));
children.push(p("O AMCP (Armament & Crisis Profile) quantifica a rela\u00E7\u00E3o entre regimes pol\u00EDticos de exce\u00E7\u00E3o e a militariza\u00E7\u00E3o da imagem feminina aleg\u00F3rica. A hip\u00F3tese subjacente, informada pela iconologia warburguiana (Warburg, 1929), \u00E9 que as Pathosformeln (f\u00F3rmulas de pat\u00E9tico) migram entre \u00E9pocas e contextos, de modo que regimes militares tendem a recrutar a energia visual da guerreira cl\u00E1ssica (Atena/Minerva) para suas alegorias nacionais. A \u00E1rvore de decis\u00E3o opera da seguinte forma: se a figura n\u00E3o porta nenhuma arma (AMCP=0); se porta armamento defensivo como escudo ou \u00E9gide (AMCP=1); se porta armamento ofensivo como espada empunhada ou lan\u00E7a (AMCP=2); e se apresenta arsenal completo com m\u00FAltiplas armas combinadas a uma postura combativa (AMCP=3)."));

children.push(p("A rela\u00E7\u00E3o entre AMCP e tipo de regime constitui a Hip\u00F3tese H1 da tese: espera-se que regimes militares/autorit\u00E1rios apresentem valores de AMCP significativamente superiores aos regimes normativos. Esta hip\u00F3tese \u00E9 inspirada pela observa\u00E7\u00E3o de Agulhon (1979) sobre as transforma\u00E7\u00F5es de Marianne entre per\u00EDodos de paz e guerra na Fran\u00E7a, e pela an\u00E1lise de Goodrich (2014) sobre os emblemas jur\u00EDdicos como dispositivos de poder soberano."));

children.push(heading3("4.2.3 WI \u2014 \u00CDndice de Branquitude"));
children.push(p("O WI (Whiteness Index) operacionaliza a contribui\u00E7\u00E3o de Charles Mills (1997) sobre o contrato racial: a ordem pol\u00EDtica moderna n\u00E3o apenas subordina o feminino, mas o faz atrav\u00E9s de uma idealiza\u00E7\u00E3o racial espec\u00EDfica. A \u00E1rvore de decis\u00E3o do WI distingue quatro n\u00EDveis: (WI=0) quando os tra\u00E7os s\u00E3o amb\u00EDguos ou n\u00E3o-europeus, como em alegorias ind\u00EDgenas ou afrodescendentes; (WI=1) quando h\u00E1 tra\u00E7os cl\u00E1ssicos (pele clara, nariz reto) sem hierarquiza\u00E7\u00E3o racial expl\u00EDcita; (WI=2) quando a branquitude \u00E9 expl\u00EDcita com fei\u00E7\u00F5es marcadamente europeias; e (WI=3) quando a branquitude \u00E9 acompanhada de hierarquiza\u00E7\u00E3o racial, tipicamente pela presen\u00E7a de figuras racializadas em posi\u00E7\u00E3o subalterna ao redor da alegoria branca."));

children.push(p("O cruzamento entre WI e CII (Hip\u00F3tese H2) testa a tese de que o \u201Ccl\u00E1ssico\u201D funciona como c\u00F3digo racial: quanto mais uma alegoria se aproxima do ideal greco-romano (CII alto), mais ela tende a reproduzir a branquitude (WI alto). Esta correla\u00E7\u00E3o, se confirmada estatisticamente, refor\u00E7aria a leitura de Mills de que o universalismo jur\u00EDdico ocidental opera atrav\u00E9s de uma est\u00E9tica racial espec\u00EDfica, naturalizando a branquitude como padr\u00E3o de beleza e verdade."));

children.push(heading3("4.2.4 AI \u2014 \u00CDndice Alegoria-Biografia"));
children.push(p("O AI (Allegory-Biography Index) captura uma dimens\u00E3o original desta tese: o processo hist\u00F3rico pelo qual alegorias femininas do Estado deixam de ser figuras puramente simb\u00F3licas para se tornarem personas biogr\u00E1ficas, frequentemente encarnadas por celebridades ou modelos reais. A \u00E1rvore de decis\u00E3o distingue: (AI=0) alegoria pura, sem qualquer refer\u00EAncia a uma pessoa real, como a Justitia convencional; (AI=1) alegoria nomeada, que recebe um nome pr\u00F3prio mas sem correspond\u00EAncia biogr\u00E1fica, como as \u201CMariannes\u201D gen\u00E9ricas; (AI=2) alegoria inspirada em pessoa real, cujo modelo pode ser identificado nos registros hist\u00F3ricos; e (AI=3) pessoa real como alegoria, como nos casos em que Brigitte Bardot, Catherine Deneuve ou Laetitia Casta serviram de modelo para bustos oficiais de Marianne."));

children.push(p("A Hip\u00F3tese H5 da tese postula que o AI aumenta ao longo do tempo (1789\u21922024), refletindo uma tend\u00EAncia moderna de \u201Cbiografizar\u201D a alegoria \u2014 o que constitui, argumenta-se, uma nova forma de contrato sexual visual em que mulheres reais s\u00E3o chamadas a encarnar o Estado, mas nos termos definidos pelo olhar masculino institucional. A an\u00E1lise de tend\u00EAncia temporal ser\u00E1 realizada por regress\u00E3o linear (Se\u00E7\u00E3o 5)."));

children.push(heading2("4.3 Manual de Codifica\u00E7\u00E3o e Conectores Te\u00F3ricos"));
children.push(p("O m\u00F3dulo codificacao.py inclui uma funcionalidade de gera\u00E7\u00E3o autom\u00E1tica de manual de codifica\u00E7\u00E3o, produzindo um documento formatado que pode ser entregue a codificadores independentes. O manual cont\u00E9m, para cada indicador: a defini\u00E7\u00E3o operacional completa, a \u00E1rvore de decis\u00E3o com exemplos ilustrativos, as regras de desempate para casos amb\u00EDguos e os conectores te\u00F3ricos que justificam a exist\u00EAncia do indicador. Esta funcionalidade \u00E9 essencial para o protocolo de confiabilidade inter-codificadores (Se\u00E7\u00E3o 6), pois garante que todos os codificadores operam com as mesmas defini\u00E7\u00F5es."));

children.push(p("Os conectores te\u00F3ricos vinculam cada indicador ao quadro conceitual da tese. O FEI e o MVI ancoram-se na teoria do contrato sexual de Pateman (1988) e na an\u00E1lise de Warner (1985) sobre a desnudez aleg\u00F3rica; o CII dialoga com a iconologia de Warburg (1929) e a economia ic\u00F4nica de Mondzain (1996/2005); o AMCP conecta-se \u00E0 an\u00E1lise warburguiana das Pathosformeln e \u00E0 hist\u00F3ria das alegorias republicanas de Agulhon (1979); o WI e o RI operacionalizam o contrato racial de Mills (1997); e o AI articula-se com a cr\u00EDtica feminista da cultura visual e com a teoria dos emblemas jur\u00EDdicos de Goodrich (2014). O PRI, o SMI e o SMS funcionam como indicadores de media\u00E7\u00E3o, capturando a materialidade simb\u00F3lica e a postura corporal que articulam as demais dimens\u00F5es."));

children.push(p("A rela\u00E7\u00E3o entre os indicadores e os pain\u00E9is da tese (coluna \u201CPain\u00E9is Relacionados\u201D na tabela) garante que cada indicador contribui para pelo menos uma das hip\u00F3teses em teste. O Painel I (O Corpo da Na\u00E7\u00E3o) mobiliza primariamente FEI e CII; o Painel II (A Guerreira e a M\u00E3e) cruza PRI, AMCP e MVI; o Painel IV (O Cl\u00E1ssico como C\u00F3digo Racial) depende de CII, WI e RI; e o Painel IX (Da Alegoria \u00E0 Celebridade) centra-se no AI. Esta estrutura garante que n\u00E3o h\u00E1 indicadores orf\u00E3os nem hip\u00F3teses sem suporte emp\u00EDrico."));


// ── Section 5: An\u00E1lise Estat\u00EDstica ──
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading1("5. An\u00E1lise Estat\u00EDstica (estatistica.py)"));

children.push(p("O m\u00F3dulo estatistica.py \u00E9 respons\u00E1vel por toda a an\u00E1lise quantitativa dos dados codificados, compreendendo duas etapas complementares: a estat\u00EDstica descritiva, que caracteriza o corpus em termos de frequ\u00EAncias, m\u00E9dias e distribui\u00E7\u00F5es; e a estat\u00EDstica inferencial, que testa as cinco hip\u00F3teses centrais da tese. A escolha dos testes estat\u00EDsticos foi guiada pela natureza dos dados: como a maioria dos indicadores \u00E9 ordinal (escalas 0\u20133), os testes n\u00E3o-param\u00E9tricos s\u00E3o prefer\u00EDveis aos param\u00E9tricos, que pressup\u00F5em normalidade e intervalos iguais entre os n\u00EDveis da escala."));

children.push(p("Na etapa descritiva, o m\u00F3dulo calcula: distribui\u00E7\u00F5es de frequ\u00EAncia para cada indicador, segmentadas por pa\u00EDs, regime e suporte; m\u00E9dias e desvios-padr\u00E3o (com a ressalva de que m\u00E9dias de vari\u00E1veis ordinais s\u00E3o interpretadas com cautela); tabula\u00E7\u00F5es cruzadas (cross-tabulations) entre pares de indicadores relevantes; e medianas, que para dados ordinais constituem a medida de tend\u00EAncia central mais apropriada. Estes resultados descritivos fornecem a base emp\u00EDrica sobre a qual as hip\u00F3teses inferenciais ser\u00E3o testadas."));

children.push(heading2("5.1 Tabela das Hip\u00F3teses e Testes Estat\u00EDsticos"));

// Hypotheses table
const hypColWidths = [600, 2600, 2400, 3426];
const hypTable = new Table({
  width: { size: CONTENT_WIDTH, type: WidthType.DXA },
  columnWidths: hypColWidths,
  rows: [
    new TableRow({
      children: [
        makeCell("Hip.", hypColWidths[0], { shading: "1a1a2e", bold: true, color: "FFFFFF", alignment: AlignmentType.CENTER }),
        makeCell("Descri\u00E7\u00E3o", hypColWidths[1], { shading: "1a1a2e", bold: true, color: "FFFFFF" }),
        makeCell("Teste Estat\u00EDstico", hypColWidths[2], { shading: "1a1a2e", bold: true, color: "FFFFFF" }),
        makeCell("Justificativa do Teste", hypColWidths[3], { shading: "1a1a2e", bold: true, color: "FFFFFF" }),
      ],
    }),
    new TableRow({
      children: [
        makeCell("H1", hypColWidths[0], { shading: indAltShading, alignment: AlignmentType.CENTER, bold: true }),
        makeCell("Regimes militares apresentam AMCP e MVI mais altos que regimes normativos", hypColWidths[1], { shading: indAltShading }),
        makeCell("Kruskal-Wallis (3 grupos) + Mann-Whitney U (compara\u00E7\u00F5es par a par)", hypColWidths[2], { shading: indAltShading }),
        makeCell("Testes n\u00E3o-param\u00E9tricos adequados para dados ordinais (escala 0\u20133) sem pressuposto de normalidade. Kruskal-Wallis compara 3 regimes simultaneamente; Mann-Whitney U realiza compara\u00E7\u00F5es post-hoc.", hypColWidths[3], { shading: indAltShading }),
      ],
    }),
    new TableRow({
      children: [
        makeCell("H2", hypColWidths[0], { alignment: AlignmentType.CENTER, bold: true }),
        makeCell("Correla\u00E7\u00E3o positiva entre CII e WI (\u201Ccl\u00E1ssico como c\u00F3digo racial\u201D)", hypColWidths[1]),
        makeCell("Correla\u00E7\u00E3o de Spearman (\u03C1)", hypColWidths[2]),
        makeCell("Spearman \u00E9 a correla\u00E7\u00E3o de ordem adequada para vari\u00E1veis ordinais, n\u00E3o exigindo linearidade nem normalidade bivariada. Testa monotonicidade entre idealiza\u00E7\u00E3o cl\u00E1ssica e branquitude.", hypColWidths[3]),
      ],
    }),
    new TableRow({
      children: [
        makeCell("H3", hypColWidths[0], { shading: indAltShading, alignment: AlignmentType.CENTER, bold: true }),
        makeCell("Suportes de circula\u00E7\u00E3o \u00EDntima (moedas/selos) t\u00EAm FEI menor que monumentos", hypColWidths[1], { shading: indAltShading }),
        makeCell("Mann-Whitney U", hypColWidths[2], { shading: indAltShading }),
        makeCell("Compara\u00E7\u00E3o entre dois grupos independentes (suporte \u00EDntimo vs. monumental) em vari\u00E1vel ordinal. Testa se a rotina fraterna exige feminilidade atenuada nos objetos cotidianos.", hypColWidths[3], { shading: indAltShading }),
      ],
    }),
    new TableRow({
      children: [
        makeCell("H4", hypColWidths[0], { alignment: AlignmentType.CENTER, bold: true }),
        makeCell("Brasil e EUA t\u00EAm RI=1 em \u226580% das imagens p\u00F3s-1889", hypColWidths[1]),
        makeCell("Teste binomial", hypColWidths[2]),
        makeCell("Teste exato para propor\u00E7\u00F5es em uma amostra. Verifica se a propor\u00E7\u00E3o observada de RI=1 \u00E9 significativamente \u2265 80%, testando a hip\u00F3tese de que na\u00E7\u00F5es de coloniza\u00E7\u00E3o recente naturalizam a branquitude aleg\u00F3rica.", hypColWidths[3]),
      ],
    }),
    new TableRow({
      children: [
        makeCell("H5", hypColWidths[0], { shading: indAltShading, alignment: AlignmentType.CENTER, bold: true }),
        makeCell("AI aumenta ao longo do tempo (1789\u21922024)", hypColWidths[1], { shading: indAltShading }),
        makeCell("Regress\u00E3o linear simples (AI ~ Ano)", hypColWidths[2], { shading: indAltShading }),
        makeCell("Regress\u00E3o avalia tend\u00EAncia temporal do \u00EDndice alegoria-biografia. Apesar de AI ser ordinal, a regress\u00E3o sobre o tempo captura a dire\u00E7\u00E3o e a for\u00E7a da tend\u00EAncia secular de biografiza\u00E7\u00E3o das alegorias.", hypColWidths[3], { shading: indAltShading }),
      ],
    }),
  ],
});

children.push(hypTable);
children.push(emptyPara(200));

children.push(p("A l\u00F3gica de cada teste merece detalhamento. Para a Hip\u00F3tese H1, o Kruskal-Wallis \u00E9 empregado como an\u00E1logo n\u00E3o-param\u00E9trico da ANOVA de um fator, comparando as distribui\u00E7\u00F5es de AMCP e MVI entre os tr\u00EAs tipos de regime (normativo, militar/autorit\u00E1rio, transit\u00F3rio). Em caso de resultado significativo (p < 0,05), compara\u00E7\u00F5es post-hoc par a par s\u00E3o realizadas com Mann-Whitney U, aplicando corre\u00E7\u00E3o de Bonferroni para controlar a taxa de erro tipo I. A dire\u00E7\u00E3o esperada \u00E9 que regimes militares apresentem medianas superiores em ambos os indicadores, refletindo a militariza\u00E7\u00E3o e a vulnerabiliza\u00E7\u00E3o do corpo feminino aleg\u00F3rico em per\u00EDodos de exce\u00E7\u00E3o."));

children.push(p("Para a Hip\u00F3tese H2, a correla\u00E7\u00E3o de Spearman (\u03C1) entre CII e WI testa se a ades\u00E3o ao ideal cl\u00E1ssico greco-romano est\u00E1 monotonicamente associada \u00E0 branquitude da figura aleg\u00F3rica. Uma correla\u00E7\u00E3o positiva forte (\u03C1 > 0,5) e significativa confirmaria a tese de que o \u201Ccl\u00E1ssico\u201D funciona como c\u00F3digo racial na iconografia jur\u00EDdica. A Hip\u00F3tese H3 emprega Mann-Whitney U para comparar os valores de FEI entre suportes de circula\u00E7\u00E3o \u00EDntima (moedas e selos, manuseados cotidianamente) e monumentos (expostos no espa\u00E7o p\u00FAblico). A hip\u00F3tese patemniana \u00E9 que a \u201Crotina fraterna\u201D do contrato sexual exige uma feminilidade mais contida nos objetos de uso cotidiano."));

children.push(heading2("5.2 Suite de Visualiza\u00E7\u00E3o"));
children.push(p("O m\u00F3dulo estatistica.py gera automaticamente seis tipos de gr\u00E1ficos, cada um escolhido por sua adequa\u00E7\u00E3o ao tipo de dado e \u00E0 pergunta de pesquisa: (1) gr\u00E1ficos de barras mostrando distribui\u00E7\u00F5es de frequ\u00EAncia por indicador, segmentados por pa\u00EDs ou regime; (2) heatmap de correla\u00E7\u00F5es (Spearman) entre todos os indicadores ordinais, revelando padr\u00F5es de co-ocorr\u00EAncia; (3) boxplots de indicadores-chave por tipo de regime, visualizando as diferen\u00E7as testadas em H1; (4) boxplots por pa\u00EDs, permitindo compara\u00E7\u00F5es geogr\u00E1ficas; (5) scatterplot de CII \u00D7 WI com linha de tend\u00EAncia, correspondendo \u00E0 H2; e (6) gr\u00E1fico de tend\u00EAncia temporal do AI (1789\u20132024) com linha de regress\u00E3o, correspondendo \u00E0 H5. Todos os gr\u00E1ficos s\u00E3o produzidos em alta resolu\u00E7\u00E3o (300 DPI) nos formatos PNG e PDF, utilizando seaborn para est\u00E9tica e matplotlib para customiza\u00E7\u00E3o fina."));

children.push(p("A funcionalidade de gera\u00E7\u00E3o de relat\u00F3rio completo consolida todas as an\u00E1lises \u2014 descritivas e inferenciais \u2014 em um \u00FAnico documento estruturado, incluindo tabelas de resultados, valores-p, tamanhos de efeito e interpreta\u00E7\u00F5es preliminares. Este relat\u00F3rio serve como base para a reda\u00E7\u00E3o do cap\u00EDtulo de resultados da tese e pode ser compartilhado com o orientador para discuss\u00E3o interina dos achados."));


// ── Section 6: Confiabilidade Inter-Codificadores ──
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading1("6. Confiabilidade Inter-Codificadores (kappa.py)"));

children.push(p("O m\u00F3dulo kappa.py implementa o protocolo de confiabilidade inter-codificadores, elemento essencial para a valida\u00E7\u00E3o do sistema de codifica\u00E7\u00E3o. Em qualquer estudo que empregue codifica\u00E7\u00E3o manual de dados visuais, a confiabilidade entre codificadores \u00E9 a pedra angular da credibilidade cient\u00EDfica: se dois codificadores independentes, utilizando o mesmo manual, n\u00E3o chegam a resultados consistentes, o sistema de codifica\u00E7\u00E3o carece de validade. O padr\u00E3o adotado nesta tese \u00E9 o coeficiente Kappa de Cohen (1960), com interpreta\u00E7\u00E3o conforme os benchmarks de Landis e Koch (1977)."));

children.push(p("A implementa\u00E7\u00E3o distingue entre dois tipos de Kappa conforme a natureza do indicador. Para indicadores ordinais (FEI, CII, SMI, AMCP, MVI, WI e AI, todos em escala 0\u20133), utiliza-se o Kappa ponderado com pesos lineares. A pondera\u00E7\u00E3o linear \u00E9 adequada porque, nestas escalas, a discord\u00E2ncia entre valores adjacentes (ex.: 1 vs. 2) \u00E9 menos grave que a discord\u00E2ncia entre valores distantes (ex.: 0 vs. 3). Para indicadores categ\u00F3ricos (PRI e SMS, cada um com tr\u00EAs categorias nominais) e bin\u00E1rios (RI, com valores 0/1), utiliza-se o Kappa n\u00E3o-ponderado, pois n\u00E3o h\u00E1 ordena\u00E7\u00E3o inerente entre as categorias."));

children.push(p("Os limiares de classifica\u00E7\u00E3o adotados seguem a escala de Landis e Koch (1977), com ajuste para a exig\u00EAncia desta pesquisa: Kappa \u2265 0,80 \u00E9 classificado como \u201Cexcelente\u201D e constitui o objetivo m\u00EDnimo para cada indicador; Kappa entre 0,60 e 0,79 \u00E9 \u201Cmoderado\u201D e sinaliza necessidade de revis\u00E3o do manual de codifica\u00E7\u00E3o para o indicador em quest\u00E3o; Kappa inferior a 0,60 \u00E9 \u201Cbaixo\u201D e exige reformula\u00E7\u00E3o da defini\u00E7\u00E3o operacional ou exclus\u00E3o do indicador. O limiar de 0,80 \u00E9 mais rigoroso que o habitualmente aceito em ci\u00EAncias sociais (onde 0,60\u20130,70 \u00E9 frequentemente considerado suficiente), refletindo a aspira\u00E7\u00E3o desta tese \u00E0 precis\u00E3o quantitativa."));

children.push(p("O m\u00F3dulo inclui funcionalidades avan\u00E7adas de identifica\u00E7\u00E3o de discord\u00E2ncias e monitoramento de deriva. A identifica\u00E7\u00E3o de discord\u00E2ncias lista todas as imagens onde os codificadores divergiram acima de um limiar configur\u00E1vel (por padr\u00E3o, discord\u00E2ncia \u2265 2 pontos na escala ordinal), gerando insumos para reuni\u00F5es de consenso entre os codificadores. O monitoramento de deriva opera por janela deslizante de 100 imagens, calculando o Kappa m\u00F3vel para detectar degradamento progressivo da concord\u00E2ncia ao longo do tempo \u2014 fen\u00F4meno comum em projetos de codifica\u00E7\u00E3o prolongados, onde a fadiga do codificador pode comprometer a consist\u00EAncia."));

children.push(p("No cronograma da tese, o protocolo de confiabilidade inter-codificadores est\u00E1 previsto para os Meses 9\u201310. O procedimento compreende: (a) treinamento dos codificadores independentes com o manual gerado pelo m\u00F3dulo codificacao.py; (b) codifica\u00E7\u00E3o piloto de 50 imagens com c\u00E1lculo de Kappa prelimimnar; (c) reuni\u00E3o de consenso e ajuste do manual se necess\u00E1rio; (d) codifica\u00E7\u00E3o completa do corpus com monitoramento cont\u00EDnuo de deriva; e (e) relat\u00F3rio final de confiabilidade com Kappa por indicador e identifica\u00E7\u00E3o de padr\u00F5es de discord\u00E2ncia."));


// ── Section 7: Integra\u00E7\u00E3o Iconclass ──
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading1("7. Integra\u00E7\u00E3o Iconclass (iconclass_.py)"));

children.push(p("O m\u00F3dulo iconclass_.py realiza a ponte entre o sistema de codifica\u00E7\u00E3o pr\u00F3prio desta tese e o Iconclass, o sistema internacional de classifica\u00E7\u00E3o iconogr\u00E1fica desenvolvido pelo Henri van de Waal e mantido pelo Rijksbureau voor Kunsthistorische Documentatie (RKD). O Iconclass \u00E9 o padr\u00E3o de facto para cataloga\u00E7\u00E3o de conte\u00FAdo visual em museus, bibliotecas e projetos de humanidades digitais em todo o mundo, organizado em uma hierarquia alfanum\u00E9rica que vai de categorias amplas (ex.: 11 = Religi\u00E3o Crist\u00E3) a descri\u00E7\u00F5es altamente espec\u00EDficas (ex.: 44B62(SWORD) = Espada como s\u00EDmbolo de Justi\u00E7a)."));

children.push(p("A integra\u00E7\u00E3o com o Iconclass serve a dois prop\u00F3sitos estrat\u00E9gicos para a tese. Primeiro, garante a comparabilidade internacional dos resultados: outros pesquisadores que utilizem o Iconclass poder\u00E3o localizar o corpus desta tese dentro da taxonomia global, facilitando estudos comparativos e meta-an\u00E1lises. Segundo, insere a tese no ecossistema das humanidades digitais, demonstrando que a pesquisa jur\u00EDdica pode dialogar com os padr\u00F5es e infraestruturas da hist\u00F3ria da arte computacional, \u00E1rea em r\u00E1pido crescimento."));

children.push(p("O m\u00F3dulo cont\u00E9m um conjunto pr\u00E9-mapeado de c\u00F3digos Iconclass organizado por seis temas centrais da tese: (1) alegorias femininas (31A \u2014 mulher, 31AA \u2014 mulher ideal, 44A3 \u2014 Justi\u00E7a como mulher); (2) justi\u00E7a e direito (44B6 \u2014 Justi\u00E7a, 44B62 \u2014 atributos da Justi\u00E7a); (3) mulher e corpo (31D \u2014 corpo humano feminino); (4) soberania e Estado (44A \u2014 governo, 44C \u2014 legisla\u00E7\u00E3o); (5) atributos simb\u00F3licos (49L \u2014 atributos de figuras personificadas); e (6) suportes materiais (48A98 \u2014 numism\u00E1tica, 49M \u2014 her\u00E1ldica)."));

children.push(p("O motor de sugest\u00E3o autom\u00E1tica opera a partir dos valores dos indicadores atribu\u00EDdos a cada imagem. Por exemplo, uma imagem codificada com FEI=3 (corpo enfatizado) e AMCP=2 (armamento ofensivo) receber\u00E1 sugest\u00F5es de c\u00F3digos Iconclass relacionados a alegorias femininas armadas com \u00EAnfase corporal (31AA + 45C). Uma imagem com WI=3 (branquitude + hierarquia) receber\u00E1 c\u00F3digos relacionados a hierarquias sociais representadas visualmente. O pesquisador pode aceitar, rejeitar ou modificar cada sugest\u00E3o, mantendo o controle intelectual sobre a classifica\u00E7\u00E3o final."));

children.push(p("A implementa\u00E7\u00E3o do mapeamento indicador-Iconclass segue uma l\u00F3gica de correspond\u00EAncia m\u00FAltipla: cada valor de cada indicador pode mapear para um ou mais c\u00F3digos Iconclass, e cada c\u00F3digo Iconclass pode ser sugerido por m\u00FAltiplos indicadores. Esta rela\u00E7\u00E3o many-to-many reflete a complexidade inerente \u00E0 classifica\u00E7\u00E3o iconogr\u00E1fica, onde uma mesma imagem pode legitimamente receber m\u00FAltiplas categorias. O m\u00F3dulo registra todas as decis\u00F5es de aceita\u00E7\u00E3o/rejei\u00E7\u00E3o de sugest\u00F5es, criando um log de auditoria que pode ser inspecionado pela banca ou por futuros pesquisadores."));


// ── Section 8: Matriz de Evid\u00EAncias ──
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading1("8. Matriz de Evid\u00EAncias (matriz.py)"));

children.push(p("O m\u00F3dulo matriz.py gerencia a matriz de evid\u00EAncias proveniente das nove revis\u00F5es sistem\u00E1ticas previstas na Fase 1 da tese (Meses 1\u201312). A revis\u00E3o sistem\u00E1tica \u00E9 o m\u00E9todo escolhido para mapear a literatura existente sobre cada um dos temas centrais da tese \u2014 contrato sexual, iconografia jur\u00EDdica, alegorias de g\u00EAnero, teoria cr\u00EDtica racial, Iconclass, entre outros \u2014 de forma exaustiva, reprodut\u00EDvel e transparente. A matriz de evid\u00EAncias consolida os achados de todas as revis\u00F5es em uma estrutura tabular \u00FAnica, facilitando a identifica\u00E7\u00E3o de padr\u00F5es transversais e lacunas na literatura."));

children.push(p("A estrutura da matriz compreende 13 colunas, alinhadas com o fluxo de trabalho da plataforma Elicit (ferramenta de revis\u00E3o sistem\u00E1tica assistida por intelig\u00EAncia artificial): ID (identificador sequencial da evid\u00EAncia), Review_number (n\u00FAmero da revis\u00E3o sistem\u00E1tica de origem, 1\u20139), Authors (autores do estudo), Year (ano de publica\u00E7\u00E3o), Title (t\u00EDtulo do trabalho), Journal (peri\u00F3dico ou editora), DOI (identificador digital), Country_focus (pa\u00EDs ou regi\u00E3o de foco do estudo), Key_finding (achado principal), Relevance_score (escore de relev\u00E2ncia de 1 a 5), Theoretical_framework (quadro te\u00F3rico empregado), Methodology (metodologia do estudo) e Notes (observa\u00E7\u00F5es do pesquisador)."));

children.push(p("A funcionalidade de an\u00E1lise de lacunas (gap analysis) constitui uma contribui\u00E7\u00E3o original do toolkit. A partir da matriz preenchida, o m\u00F3dulo identifica automaticamente: (a) pa\u00EDses subrepresentados na literatura (por exemplo, se h\u00E1 poucos estudos sobre alegorias jur\u00EDdicas no Brasil comparado \u00E0 Fran\u00E7a); (b) per\u00EDodos hist\u00F3ricos com lacunas (por exemplo, a aus\u00EAncia de estudos sobre alegorias em regimes transit\u00F3rios); (c) quadros te\u00F3ricos pouco explorados (por exemplo, a escassez de aplica\u00E7\u00F5es do contrato racial de Mills \u00E0 iconografia jur\u00EDdica); e (d) cruzamentos tem\u00E1ticos inexplorados (por exemplo, a intersec\u00E7\u00E3o entre g\u00EAnero e ra\u00E7a nas alegorias de justi\u00E7a). Estas lacunas constituem, em si mesmas, justificativas para a presente tese."));

children.push(p("O m\u00F3dulo oferece exporta\u00E7\u00E3o em formato ABNT (Associa\u00E7\u00E3o Brasileira de Normas T\u00E9cnicas), gerando refer\u00EAncias bibliogr\u00E1ficas formatadas conforme a NBR 6023:2018 a partir dos metadados da matriz. Esta funcionalidade elimina a necessidade de reformata\u00E7\u00E3o manual das refer\u00EAncias ao transcrever os achados das revis\u00F5es para o texto da tese, reduzindo erros e economizando tempo. A integra\u00E7\u00E3o entre a matriz de evid\u00EAncias e o corpus iconogr\u00E1fico permite, ainda, vincular evid\u00EAncias bibliogr\u00E1ficas a imagens espec\u00EDficas, criando um tecido anal\u00EDtico que conecta teoria e emp\u00EDrico de forma rastreavel."));

children.push(p("A integra\u00E7\u00E3o entre corpus e matriz de evid\u00EAncias opera bidirecionalmente. De um lado, os achados bibliogr\u00E1ficos orientam a sele\u00E7\u00E3o e a codifica\u00E7\u00E3o das imagens: por exemplo, se a revis\u00E3o sistem\u00E1tica sobre o contrato racial identifica que Mills (1997) analisa a \u201Cbrancura\u201D como pressuposto do contrato social, isso informa a operacionaliza\u00E7\u00E3o do WI. De outro lado, os resultados da codifica\u00E7\u00E3o podem revelar padr\u00F5es n\u00E3o antecipados pela literatura, gerando novos termos de busca para revis\u00F5es complementares. Esta circularidade hermeneutica \u00E9 caracter\u00EDstica do m\u00E9todo iconol\u00F3gico-forense proposto pela tese."));


// ── Section 9: Interface de Linha de Comando ──
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading1("9. Interface de Linha de Comando (main.py)"));

children.push(p("O m\u00F3dulo main.py constitui o ponto de entrada unificado do toolkit, oferecendo uma interface de linha de comando (CLI) que orquestra todos os m\u00F3dulos descritos nas se\u00E7\u00F5es anteriores. A CLI foi projetada segundo o princ\u00EDpio de \u201Cconven\u00E7\u00E3o sobre configura\u00E7\u00E3o\u201D: o pesquisador pode executar opera\u00E7\u00F5es complexas com comandos simples, enquanto op\u00E7\u00F5es avan\u00E7adas permanecem acess\u00EDveis para personaliza\u00E7\u00E3o. A arquitetura de comandos e subcomandos segue a estrutura hier\u00E1rquica dos m\u00F3dulos do toolkit."));

children.push(p("O toolkit disponibiliza oito comandos principais: (1) corpus, para opera\u00E7\u00F5es de gest\u00E3o do acervo (adicionar imagens, validar metadados, verificar checkpoints, gerar relat\u00F3rios de progresso); (2) codificar, para codifica\u00E7\u00E3o interativa ou em lote das imagens (atribuir valores aos 10 indicadores, gerar manual de codifica\u00E7\u00E3o); (3) estatistica, para an\u00E1lises descritivas e inferenciais (calcular frequ\u00EAncias, executar testes de hip\u00F3teses, gerar visualiza\u00E7\u00F5es); (4) kappa, para c\u00E1lculo de confiabilidade (computar Kappa por indicador, identificar discord\u00E2ncias, monitorar deriva); (5) iconclass, para mapeamento ao padr\u00E3o internacional (sugerir c\u00F3digos, exportar classifica\u00E7\u00F5es); (6) matriz, para gest\u00E3o da matriz de evid\u00EAncias (adicionar entradas, analisar lacunas, exportar ABNT); (7) relatorio, para gera\u00E7\u00E3o de relat\u00F3rios consolidados; e (8) config, para configura\u00E7\u00E3o do ambiente de trabalho."));

children.push(p("A unifica\u00E7\u00E3o dos m\u00F3dulos em uma \u00FAnica CLI oferece tr\u00EAs vantagens pr\u00E1ticas. Primeira, reduz a curva de aprendizado: o pesquisador n\u00E3o precisa memorizar scripts separados para cada opera\u00E7\u00E3o. Segunda, garante consist\u00EAncia de dados: todos os m\u00F3dulos operam sobre o mesmo diret\u00F3rio de trabalho e compartilham o mesmo corpus de dados, eliminando riscos de dessincronia. Terceira, facilita a documenta\u00E7\u00E3o e a reprodutibilidade: cada sess\u00E3o de trabalho pode ser registrada como uma sequ\u00EAncia de comandos CLI que outro pesquisador pode reexecutar integralmente."));

children.push(p("Exemplos de fluxos de trabalho t\u00EDpicos ilustram a integra\u00E7\u00E3o entre os m\u00F3dulos. Um fluxo inicial de constitui\u00E7\u00E3o do corpus compreenderia: (a) python main.py corpus add --file imagem.jpg --country FR --figure Marianne --year 1792 --support moeda; (b) python main.py corpus validate; (c) python main.py corpus checkpoint. Um fluxo de codifica\u00E7\u00E3o incluiria: (a) python main.py codificar --image FR_Marianne_1792_moeda_001; (b) python main.py kappa calculate; (c) python main.py kappa drift. E um fluxo de an\u00E1lise final compreenderia: (a) python main.py estatistica describe; (b) python main.py estatistica test --hypothesis H1; (c) python main.py estatistica plot --type heatmap; (d) python main.py relatorio generate."));

children.push(p("A CLI tamb\u00E9m inclui funcionalidades auxiliares como ajuda contextual (flag --help em qualquer n\u00EDvel), modo verboso (flag --verbose para diagn\u00F3stico), e exporta\u00E7\u00E3o em m\u00FAltiplos formatos (CSV, JSON, XLSX). Estas funcionalidades asseguram que o toolkit \u00E9 utiliz\u00E1vel tanto por pesquisadores com familiaridade t\u00E9cnica quanto por aqueles que necessitam de orienta\u00E7\u00E3o passo a passo."));


// ── Section 10: Limita\u00E7\u00F5es e Desenvolvimentos Futuros ──
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading1("10. Limita\u00E7\u00F5es e Desenvolvimentos Futuros"));

children.push(p("O toolkit apresenta limita\u00E7\u00F5es que devem ser explicitadas com transpar\u00EAncia. A primeira \u00E9 a aus\u00EAncia de uma interface gr\u00E1fica (GUI): toda a intera\u00E7\u00E3o ocorre via linha de comando, o que pode constituir uma barreira para pesquisadores sem experi\u00EAncia em programa\u00E7\u00E3o. A segunda \u00E9 o armazenamento baseado em arquivos (JSON/CSV): para corpus de grande escala (acima de 1.000 imagens), um banco de dados relacional ofereceria desempenho e integridade superiores. A terceira limita\u00E7\u00E3o \u00E9 a aus\u00EAncia de integra\u00E7\u00E3o com APIs de reconhecimento de imagem (como Google Vision ou CLIP), que poderiam auxiliar na codifica\u00E7\u00E3o preliminar, embora n\u00E3o substituam o julgamento humano para indicadores teoricamente fundamentados."));

children.push(p("Uma quarta limita\u00E7\u00E3o concerne a especificidade do sistema de codifica\u00E7\u00E3o: os dez indicadores foram desenhados para o objeto espec\u00EDfico desta tese (alegorias femininas na cultura jur\u00EDdica) e n\u00E3o s\u00E3o diretamente transfer\u00EDveis para outros dom\u00EDnios iconogr\u00E1ficos sem adapta\u00E7\u00E3o. Por fim, o toolkit n\u00E3o incorpora an\u00E1lise autom\u00E1tica de imagens (computer vision), operando exclusivamente com codifica\u00E7\u00E3o humana assistida por \u00E1rvores de decis\u00E3o. Esta \u00E9, paradoxalmente, tanto uma limita\u00E7\u00E3o (menor velocidade) quanto uma for\u00E7a (maior profundidade interpretativa), alinhando-se com a tradi\u00E7\u00E3o iconol\u00F3gica que privilegia a an\u00E1lise humana sobre a automa\u00E7\u00E3o."));

children.push(p("Os desenvolvimentos futuros planejados incluem: (a) implementa\u00E7\u00E3o de uma interface gr\u00E1fica web utilizando framework como Streamlit ou Flask, tornando o toolkit acess\u00EDvel a pesquisadores sem conhecimento de programa\u00E7\u00E3o; (b) migra\u00E7\u00E3o do armazenamento para SQLite ou PostgreSQL, melhorando o desempenho e a integridade referencial; (c) integra\u00E7\u00E3o com APIs de reconhecimento de imagem para pr\u00E9-codifica\u00E7\u00E3o assistida, gerando sugest\u00F5es que o codificador humano aceita ou rejeita; (d) conectores com reposit\u00F3rios digitais (Europeana, Digital Public Library of America, Brasiliana Iconogr\u00E1fica) para facilitar a constitui\u00E7\u00E3o do corpus; e (e) publica\u00E7\u00E3o do toolkit como pacote Python (pip install) com documenta\u00E7\u00E3o completa e testes automatizados."));

children.push(p("A adaptabilidade do toolkit para outros projetos de pesquisa \u00E9 uma aspira\u00E7\u00E3o expl\u00EDcita. Embora os indicadores atuais sejam espec\u00EDficos da tese, a arquitetura modular permite que pesquisadores substituam os dez indicadores por outros adequados a seus objetos de estudo, mantendo toda a infraestrutura de gest\u00E3o de corpus, confiabilidade inter-codificadores, an\u00E1lise estat\u00EDstica e integra\u00E7\u00E3o Iconclass. Projetos poss\u00EDveis incluem: an\u00E1lise de representa\u00E7\u00F5es de masculinidade no direito penal; iconografia de fronteiras e migra\u00E7\u00E3o; alegorias de soberania em contextos p\u00F3s-coloniais; e representa\u00E7\u00F5es visuais de direitos humanos em organiza\u00E7\u00F5es internacionais."));

children.push(p("Em s\u00EDntese, o toolkit aqui documentado constitui um aparato metodol\u00F3gico inovador que busca responder \u00E0 escassez de ferramentas computacionais para a an\u00E1lise iconol\u00F3gica no direito. Suas limita\u00E7\u00F5es s\u00E3o reconhecidas e endere\u00E7adas em um roteiro de desenvolvimento que se estende al\u00E9m do horizonte temporal da tese, visando contribuir de forma duradoura para o campo emergente das humanidades jur\u00EDdicas digitais."));


// ── Refer\u00EAncias Bibliogr\u00E1ficas ──
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(heading1("Refer\u00EAncias Bibliogr\u00E1ficas"));

const refs = [
  "AGULHON, Maurice. Marianne au combat: l\u2019imagerie et la symbolique r\u00E9publicaines de 1789 \u00E0 1880. Paris: Flammarion, 1979.",
  "COHEN, Jacob. A Coefficient of Agreement for Nominal Scales. Educational and Psychological Measurement, v. 20, n. 1, p. 37\u201346, 1960.",
  "DIDI-HUBERMAN, Georges. L\u2019image survivante: histoire de l\u2019art et temps des fant\u00F4mes selon Aby Warburg. Paris: Minuit, 2002.",
  "GOODRICH, Peter. Legal Emblems and the Art of Law: Obiter Depicta as the Vision of Governance. Cambridge: Cambridge University Press, 2014.",
  "LANDIS, J. Richard; KOCH, Gary G. The Measurement of Observer Agreement for Categorical Data. Biometrics, v. 33, n. 1, p. 159\u2013174, 1977.",
  "MILLS, Charles W. The Racial Contract. Ithaca: Cornell University Press, 1997.",
  "MONDZAIN, Marie-Jos\u00E9. Image, ic\u00F4ne, \u00E9conomie: les sources byzantines de l\u2019imaginaire contemporain. Paris: Seuil, 1996. [Tradu\u00E7\u00E3o inglesa: Image, Icon, Economy: The Byzantine Origins of the Contemporary Imaginary. Stanford: Stanford University Press, 2005.]",
  "PATEMAN, Carole. The Sexual Contract. Stanford: Stanford University Press, 1988.",
  "WARBURG, Aby. Bilderatlas Mnemosyne [1929]. In: WARNKE, Martin; BRINK, Claudia (Orgs.). Der Bilderatlas Mnemosyne. Berlin: Akademie Verlag, 2000.",
  "WARNER, Marina. Monuments and Maidens: The Allegory of the Female Form. London: Weidenfeld & Nicolson, 1985.",
];

refs.forEach(ref => {
  children.push(p(ref, { alignment: AlignmentType.LEFT, indent: { left: 720, hanging: 720 }, after: 120, line: 240 }));
});


// ── Build Document ──────────────────────────────────────────────────────────

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: FONT, size: 22 }, // 11pt
      },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONT, color: "1a1a2e" },
        paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: FONT, color: "16213e" },
        paragraph: { spacing: { before: 300, after: 200 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, italics: true, font: FONT, color: "1a1a2e" },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 2 },
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: PAGE_WIDTH, height: PAGE_HEIGHT },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              alignment: AlignmentType.RIGHT,
              children: [
                new TextRun({ text: "Ap\u00EAndice Metodol\u00F3gico \u2014 Toolkit Computacional", font: FONT, size: 16, italics: true, color: "888888" }),
              ],
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [
                new TextRun({ text: "P\u00E1gina ", font: FONT, size: 16, color: "888888" }),
                new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: "888888" }),
              ],
            }),
          ],
        }),
      },
      children,
    },
  ],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/user/workspace/atlas-iconocratico-toolkit/apendice_metodologico.docx", buffer);
  console.log("Document created successfully!");
  console.log("Size:", buffer.length, "bytes");
});
