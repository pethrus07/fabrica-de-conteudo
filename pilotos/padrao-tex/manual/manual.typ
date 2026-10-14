// Manual do Padrão TEX (v3): tudo o que o pacote do cliente explica, no fluxo em que o integrador trabalha:
// o equipamento → conhecer o padrão → levar para o projeto → comunicar (Modbus TCP ou Profinet) → consultar →
// operar pelo CLP → operar pela IHM. O capítulo do equipamento vem do site da Tex (pedido do cliente, 02/10 16:43).
// Compilar da raiz do piloto:  typst compile --root . --font-path marca/fontes --pdf-standard ua-1 manual/manual.typ ...
#import "tema.typ": *

#let d = json("../dados/padrao-tex.json")
#let mk = json("../trabalho/marcas.json")
#let pasta = "../trabalho/"
#let fonte = "../fonte/padrao-tex_2026-10-02/"
#let ent(g) = d.entradas.filter(p => p.grupo == g)
#let sai(g) = d.saidas.filter(p => p.grupo == g)
#let proc(id) = d.procedimentos.find(p => p.id == id)
#let bloco(nome) = d.blocos_g4.find(b => b.nome == nome)
#let cab(..h) = table.header(..h.pos().map(x => text(white, weight: 600, size: 8.5pt, x)))
#let tabela(cols, ..linhas) = block(breakable: false, width: 100%)[
  #set par(justify: false)
  #table(columns: cols, stroke: (x, y) => if y > 0 { (bottom: 0.5pt + linha) }, fill: (x, y) => if y == 0 { azul },
    inset: (x: 7pt, y: 6pt), ..linhas)
]

#show: documento.with(d, titulo-doc: "Manual", foto: "../marca/tex/fotos/g4-perspectiva.jpg",subtitulo-doc: "Do projeto ao teste: levar o padrão para o seu projeto, comunicar por Modbus TCP ou Profinet e operar pelo CLP ou pela IHM.")

#page(header: none)[
  #v(6mm)
  #text(font: "IBM Plex Sans", stretch: 75%, size: 25pt, weight: 700, fill: azul)[Sumário]
  #v(8pt)
  // cabe numa página só: o sumário com 10 capítulos transbordava 3 linhas
  #set text(size: 9.2pt)
  #show outline.entry.where(level: 1): set block(above: 1.05em)
  #show outline.entry.where(level: 1): set text(weight: 700, fill: tinta)
  #outline(title: none, depth: 2, indent: 1.4em)
]

= Antes de começar

== Para quem é este manual
#d.publico.quem #d.publico.sabe

No fim do manual você consegue: *#(lower(d.publico.consegue_no_fim.first()) + d.publico.consegue_no_fim.slice(1))*

#d.introducao.texto

== O que você precisa
#for r in d.requisitos.itens [- #r \ ]

== Como ler este manual
- Nomes de pinos, blocos e valores aparecem em fonte de código, como Start ou true.
- Os procedimentos têm sempre a mesma forma: o que precisa estar pronto antes, os passos numerados e o resultado esperado.
- Os avisos marcados como #text(weight: 700, fill: azul, size: 8.5pt, tracking: 1pt)[AVISO] indicam o que pode atrapalhar a comunicação ou o projeto.
- Os termos técnicos estão explicados no Glossário, no fim do manual.

= O equipamento Tex G4
#let eq = d.equipamento
#let foto(k, largura: 100%) = {
  let f = eq.fotos.at(k)
  image("../" + f.arquivo, width: largura, alt: f.legenda)
}

== A Tex
#eq.empresa.texto

#block(breakable: false, width: 100%)[
  #set par(justify: false)
  #grid(columns: (auto, 1fr), column-gutter: 12pt, row-gutter: 8pt,
    ..eq.empresa.marcos.map(m => (
      text(font: "IBM Plex Sans", stretch: 75%, size: 14pt, weight: 700, fill: azul)[#m.ano],
      pad(top: 2.5pt, m.texto))).flatten())
]

== O que o equipamento faz
#grid(columns: (1fr, 38%), column-gutter: 16pt, align: top,
  [
    O Tex G4 faz o teste de estanqueidade: verifica se uma peça vaza. #eq.o_que_faz.texto

    #eq.o_que_faz.resultado
  ],
  figure(caption: eq.fotos.perspectiva.legenda, foto("perspectiva")))

== A linha G4
#eq.linha_g4.texto Alguns deles:

#let foto-de = (("G4-SE"): "frente", ("G4-DF"): "df", ("G4-HD"): "hd", ("G4-VZ"): "vz")
#block(breakable: false, width: 100%)[
  #set par(justify: false)
  #grid(columns: (1fr,) * 4, column-gutter: 10pt,
    ..eq.linha_g4.modelos.map(m => block(width: 100%, radius: 6pt, clip: true, stroke: 0.6pt + linha)[
      #set text(hyphenate: false)
      #box(width: 100%, height: 92pt, clip: true, foto(foto-de.at(m.sigla)))
      #block(inset: (x: 8pt, top: 6pt, bottom: 9pt))[
        #text(weight: 700, fill: azul)[#m.sigla] \
        #text(size: 8.8pt, weight: 600, fill: tinta)[#m.nome] \
        #text(size: 8.5pt, fill: mut)[#m.como]
      ]
    ]))
]

== Recursos
#for r in eq.recursos.itens [- #r \ ]
#text(size: 8.8pt, fill: mut)[#eq.recursos.nota]

== Onde entra o Padrão TEX
#grid(columns: (38%, 1fr), column-gutter: 16pt, align: top,
  figure(caption: eq.fotos.traseira.legenda, foto("traseira")),
  [
    #eq.papel_do_padrao.texto

    Com ele, o seu programa liga o equipamento, escolhe a peça, inicia o teste e lê a pressão, o vazamento e o resultado. Também traz e envia os parâmetros de teste de cada peça. O padrão vem com as telas de uma IHM, que comandam e acompanham os equipamentos sem programação nova.

    A comunicação é por #d.produto.protocolos.join(" ou "). Cada protocolo tem o seu capítulo neste manual.
  ])

= Conhecendo o Padrão TEX

== A estrutura do projeto
Tudo o que comanda e lê os equipamentos Tex fica na pasta TexG4, dentro dos blocos de programa do CLP.

#marcada(mk.arvore, pasta, largura: 58%)

#tabela((34%, 1fr), cab([Item], [Para que serve]),
  ..d.estrutura.map(e => (text(weight: 600, fill: tinta, e.item), e.papel)).flatten())

== A biblioteca
A pasta 9 - Library traz os blocos que fazem a comunicação. #d.editavel.texto

#grid(columns: (52%, 1fr), column-gutter: 14pt, align: top,
  marcada(mk.biblioteca, pasta, largura: 100%),
  tabela((1fr, auto), cab([Bloco], [Número]),
    ..d.biblioteca.map(b => (mono(b.nome), text(size: 9pt)[#b.tipo#b.numero])).flatten()))

#aviso("Aviso")[#d.avisos.at(0).texto]

== Escolher o bloco do equipamento
Existem quatro blocos de comunicação G4. Escolha pelo protocolo da sua rede e pelo que você precisa fazer com os dados das peças.

#tabela((27%, 14%, 13%, 1fr), cab([Bloco], [Protocolo], [Dados das peças], [O que faz]),
  ..d.blocos_g4.map(b => (mono(text(weight: 600, b.nome)), text(size: 9pt, b.protocolo), text(size: 9pt, if b.pecas [sim] else [não]), text(size: 9.5pt, b.descricao))).flatten())

== O DB Debug, para testes
#d.debug.explica

#marcada(mk.debug, pasta, largura: 60%)

== O Tex [DB1]
#let dbt = d.db_tex
#dbt.explica #dbt.acesso

#marcada(mk.dbtex, pasta, largura: 74%)

#tabela((24%, 30%, 1fr), cab([Elemento], [Tipo], [Para que serve]),
  ..dbt.campos.map(c => (mono(text(weight: 600, c.nome)), mono(text(size: 8.5pt, c.tipo)), text(size: 9.5pt, c.papel))).flatten())

= Levar o Padrão TEX para o seu projeto

== Copiar as pastas TexG4
#procedimento(proc("copiar"))

#figure(caption: [As cinco pastas TexG4 que vão para o seu projeto.],
  block(width: 100%, breakable: false)[
    #set par(justify: false)
    #grid(columns: (1fr, 1fr, 1fr), column-gutter: 10pt, row-gutter: 10pt,
      ..d.copiar.pastas.enumerate().map(((i, p)) => block(width: 100%)[
        #box(stroke: 0.6pt + linha, image(fonte + p.tela, width: 100%, alt: "Pasta TexG4 em " + p.onde))
        #v(-2pt)
        #text(size: 8.5pt)[#num-passo(i + 1) #h(4pt) #p.onde]
      ]))
  ])

== Chamar o Padrão TEX no seu programa
#procedimento(proc("chamar"))
#marcada(mk.main, pasta, largura: 92%)

= Comunicação por Modbus TCP

== Colocar um equipamento na FB_Tex
#procedimento(proc("montar"))
#marcada(mk.fbvazia, pasta, largura: 92%)
#marcada(mk.adicionando, pasta, largura: 92%)

== Preencher a comunicação e as ligações
As cinco primeiras entradas dizem com qual equipamento o bloco vai conversar. As duas últimas ligam o banco de peças e a IHM. Os valores abaixo são os do projeto de exemplo; a descrição completa de cada pino está no capítulo Referência dos blocos.

#procedimento((
  condicao: [O bloco G4_ModbusTCP está na network, com as entradas vazias.],
  passos: (ent("comunicacao") + ent("ligacao")).map(p => [Em #mono(text(weight: 600, p.nome)), coloque #mono(p.exemplo). #p.descricao]),
  resultado: [Com Connect em true, o bloco liga a conexão. A saída Connected fica true quando o equipamento está conectado.],
))

== A versão Basic
#bloco("G4_ModbusTCP_Basic").descricao Saem as entradas #bloco("G4_ModbusTCP_Basic").retiradas.map(n => mono(n)).join(", ", last: " e ").

#marcada(mk.basicmb, pasta, largura: 60%)

= Comunicação por Profinet
#let pf = d.profinet
#pf.resumo O bloco Profinet não usa IP: a comunicação passa pelo gateway Profinet do TEX-G4. A cópia das pastas, a chamada no Main e a FB_Tex são as mesmas dos capítulos anteriores.

#procedimento(proc("profinet"))

== A rede
#marcada(mk.rede, pasta, largura: 80%)

== Configurar o TEX-G4 (GSD)
#pf.gsd.explica

#tabela((34%, 1fr), cab([Item], [Valor do projeto de exemplo]),
  text(weight: 600, fill: tinta)[Módulo], mono(pf.gsd.modulo),
  text(weight: 600, fill: tinta)[Endereços de entrada (I)], mono(pf.gsd.i_endereco),
  text(weight: 600, fill: tinta)[Endereços de saída (Q)], mono(pf.gsd.q_endereco),
  text(weight: 600, fill: tinta)[IP do gateway], mono(pf.gsd.ip_gateway),
  text(weight: 600, fill: tinta)[Máscara], mono(pf.gsd.mascara),
  text(weight: 600, fill: tinta)[IP do equipamento Tex], mono(pf.gsd.ip_equipamento))
#marcada(mk.gsd, pasta, largura: 100%)

#block(breakable: false)[
== Criar as tags
#pf.tags.explica
#marcada(mk.tags, pasta, largura: 62%)
]

== O bloco G4_Profinet
#pf.bloco.explica

#tabela-pinos(pf.bloco.novas, com-exemplo: true)
#marcada(mk.pnbloco, pasta, largura: 58%)

== A versão Basic
#bloco("G4_Profinet_Basic").descricao

#marcada(mk.basicpn, pasta, largura: 60%)

= Referência dos blocos

== Que entradas cada bloco tem
As saídas são as mesmas nos quatro blocos. As entradas mudam:

#let todas = d.entradas.map(p => p.nome) + pf.bloco.novas.map(p => p.nome)
#let tem(b, n) = {
  let basic = bloco("G4_ModbusTCP_Basic").retiradas
  let pn = b.contains("Profinet")
  if n in pf.bloco.retiradas and pn { false }
  else if n in pf.bloco.novas.map(p => p.nome) and not pn { false }
  else if n in basic and b.ends-with("Basic") { false }
  else { true }
}
#let nomes = ("G4_ModbusTCP", "G4_ModbusTCP_Basic", "G4_Profinet", "G4_Profinet_Basic")
#block(breakable: false)[
#set par(justify: false)
#table(columns: (28%, 1fr, 1fr, 1fr, 1fr), stroke: (x, y) => if y > 0 { (bottom: 0.4pt + linha) }, fill: (x, y) => if y == 0 { azul } else if x > 0 and calc.odd(y) { poco },
  inset: (x: 5pt, y: 3.6pt), align: (x, y) => if x == 0 { left + horizon } else { center + horizon },
  table.header(text(white, weight: 600, size: 8pt)[Entrada], ..nomes.map(n => text(white, weight: 600, size: 7pt, n.replace("_", "_\u{200B}")))),
  ..todas.map(n => (mono(text(size: 8.5pt, weight: 600, n)), ..nomes.map(b => if tem(b, n) { text(fill: azul, weight: 700, size: 9pt)[✓] } else { text(fill: mut, size: 9pt)[–] }))).flatten())]

== O bloco G4_ModbusTCP
O bloco tem #d.entradas.len() entradas e #d.saidas.len() saídas, além de EN e ENO. À esquerda, as ligações do projeto de exemplo.

#figure(caption: [O bloco G4_ModbusTCP, com as entradas e as saídas agrupadas.],
  image("../trabalho/svg/bloco.svg", width: 100%, alt: "Diagrama do bloco G4_ModbusTCP com todas as entradas à esquerda e todas as saídas à direita, agrupadas por função."))

== Entradas
#for g in ("comunicacao", "comando", "pecas", "ligacao") [
  === #d.grupos.at(g)
  #tabela-pinos(ent(g), com-exemplo: true)
]
#tabela-pinos(pf.bloco.novas, com-exemplo: true)

== Saídas
#for g in ("estado", "resultado", "medicao", "diagnostico") [
  === #d.grupos.at(g)
  #tabela-pinos(sai(g))
]

== Os outros três blocos
#figure(caption: [O bloco G4_Profinet do projeto de exemplo.],
  image("../trabalho/svg/bloco-profinet.svg", width: 92%, alt: "Diagrama do bloco G4_Profinet: as entradas do G4_ModbusTCP sem IP, Port e Connect, com PN_IN e PN_OUT, e as mesmas saídas."))
#figure(caption: [O bloco G4_ModbusTCP_Basic do projeto de exemplo.],
  image("../trabalho/svg/bloco-modbus-basic.svg", width: 92%, alt: "Diagrama do bloco G4_ModbusTCP_Basic: as entradas do G4_ModbusTCP sem as seis de upload e download, e as mesmas saídas."))
#figure(caption: [O bloco G4_Profinet_Basic do projeto de exemplo.],
  image("../trabalho/svg/bloco-profinet-basic.svg", width: 92%, alt: "Diagrama do bloco G4_Profinet_Basic: as entradas do G4_Profinet sem as seis de upload e download, e as mesmas saídas."))

= Operando pelo CLP

== Iniciar um teste de estanqueidade
#procedimento(proc("testar"))
#aviso("Aviso")[#d.avisos.at(1).texto]
#aviso("Aviso")[#d.avisos.at(2).texto]

=== A sequência dos sinais
#fluxo(proc("testar").fluxo + (proc("testar").fluxo_fim,))

#marcada(mk.monitorado, pasta, largura: 56%)

== Usar os dados do equipamento na sua lógica
#let ud = d.usar_dados
#ud.explica #ud.como

#block(width: 100%, fill: poco, radius: 4pt, inset: (x: 12pt, y: 10pt), breakable: false)[
  #set par(justify: false)
  #let parte(cor, t) = box(fill: cor, radius: 3pt, inset: (x: 7pt, y: 5pt), text(white, size: 10pt, weight: 600)[#mono(t)])
  #let ponto = text(fill: tinta, size: 12pt, weight: 700)[.]
  #let rot(t) = text(size: 8.5pt, fill: mut, t)
  #grid(columns: (auto,) * 5, column-gutter: 5pt, row-gutter: 5pt, align: center + horizon,
    parte(azul, "\"Tex\""), ponto, parte(azul2, "Equipamento4"), ponto, parte(destaque, "ResultOK"),
    rot[o DB], [], rot[o equipamento], [], rot[a entrada ou a saída])
]

#ud.exemplo.texto

#marcada(mk.usar, pasta, largura: 80%)

#ud.todas

== Alterar um parâmetro de teste de uma peça
Os parâmetros de teste de cada peça ficam guardados no equipamento Tex. Para mudar um deles pelo CLP, você traz os dados para o banco de dados, altera e envia de volta. Só os blocos completos fazem isso; os Basic não têm essas entradas.

#figure(caption: [Upload traz os dados do Tex para o CLP. Download leva do CLP para o Tex.],
  block(width: 100%, breakable: false, inset: (y: 6pt))[
    #grid(columns: (1fr, 1.25fr, 1fr), align: center + horizon, column-gutter: 8pt,
      box(width: 100%, inset: 12pt, radius: 6pt, fill: azul)[#text(white, weight: 700)[Equipamento Tex] \ #text(white.transparentize(20%), size: 8.5pt)[peças configuradas]],
      [
        #text(size: 8.5pt)[#mono("UploadAllFromTex") · #mono("UploadOne")] \
        #text(fill: destaque, size: 16pt, weight: 700)[→] \
        #text(fill: destaque, size: 16pt, weight: 700)[←] \
        #text(size: 8.5pt)[#mono("DownloadAllToTex") · #mono("DownloadOne")]
      ],
      box(width: 100%, inset: 12pt, radius: 6pt, fill: fog, stroke: 0.8pt + azul)[#text(fill: azul, weight: 700)[CLP] \ #text(size: 8.5pt)[#mono("DB_Parts")]],
    )
  ])

#procedimento(proc("editar-peca"))

== O banco de dados das peças
#let db = d.db_parts
Cada posição do DB_Parts, como #mono(db.peca), é do tipo #mono(db.tipo). #db.limites

#let campos(t, l) = block(breakable: false, width: 100%)[
  #text(weight: 600, fill: azul2, size: 10pt)[#t]
  #v(-4pt)
  #set par(justify: false)
  #table(columns: (1fr, 1fr, 1fr), stroke: (x, y) => (bottom: 0.5pt + linha), inset: (x: 6pt, y: 4.5pt),
    ..l.map(c => [#mono(text(size: 8.5pt, weight: 600, c.nome)) #text(size: 7.5pt, fill: mut)[#c.tipo]]))
]
#campos([Em cada peça], db.campos_peca)
#v(4pt)
#campos([Em cada câmara (Chamber)], db.campos_camara)
#v(4pt)
#campos([Em cada teste (Test)], db.campos_teste)

=== Exemplo: o upload da peça 1
Antes do upload, a peça 1 do exemplo estava toda zerada. Depois de UploadAllFromTex, os valores vieram do equipamento:

#tabela((40%, 30%, 30%), cab([Campo], [Antes], [Depois]),
  ..db.exemplo_upload.map(e => (mono(e.campo), mono(e.antes), text(weight: 700, fill: azul2, mono(e.depois)))).flatten())
#marcada(mk.dbparts, pasta, largura: 88%)

= Operando pela IHM
#let ihm = d.ihm
#let tela(id) = ihm.telas.find(t => t.id == id)
#ihm.resumo

#grid(columns: (44%, 1fr), column-gutter: 14pt, align: top,
  marcada(mk.ihmtelas, pasta, largura: 100%),
  [#v(6pt) #ihm.manual])

#aviso("Aviso")[#d.avisos.at(3).texto]

== Comandar um teste pela IHM
#procedimento(proc("ihm"))

== A tela Operação
#tela("operacao").descricao
#marcada(mk.operacao, pasta, largura: 86%)

== O menu
#grid(columns: (34%, 1fr), column-gutter: 14pt, align: top,
  marcada(mk.menu, pasta, largura: 100%),
  [#v(8pt) #tela("menu").descricao])

== Entradas e saídas
#tela("ios").descricao
#marcada(mk.ios, pasta, largura: 80%)

== Diagnósticos
#tela("diagnostico").descricao
#marcada(mk.diag, pasta, largura: 80%)

== Parametrização
#tela("parametrizacao").descricao
#marcada(mk.param, pasta, largura: 90%)

= Glossário
#table(
  columns: (28%, 1fr), stroke: (x, y) => (bottom: 0.5pt + linha), inset: (x: 7pt, y: 5pt),
  ..d.glossario.map(g => (text(weight: 700, fill: tinta, g.termo), g.definicao)).flatten(),
)

#v(1fr)
#block(width: 100%, inset: (x: 12pt, y: 10pt), fill: poco, radius: 4pt)[
  #text(weight: 600, fill: tinta)[Histórico de revisões] \
  #text(size: 9pt)[Versão 1.0 · 02/10/2026 · Primeira edição: comunicação por Modbus TCP e operação pelo CLP.] \
  #text(size: 9pt)[Versão 2.0 · 02/10/2026 · Escolha do bloco, Profinet, saída de retrabalho renomeada para Rework e banco de dados das peças.] \
  #text(size: 9pt)[Versão 3.0 · 02/10/2026 · Apresentação do equipamento Tex G4, biblioteca atual, DB Debug, Tex [DB1], cópia para o projeto, blocos Basic, uso dos dados na lógica e operação pela IHM.]
]
