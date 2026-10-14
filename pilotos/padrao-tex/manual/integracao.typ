// Manual 1 · Guia de integração do Padrão TEX
// Compilar da raiz do piloto:  typst compile --root . --font-path marca/fontes manual/integracao.typ entrega/...
#import "tema.typ": *

#let d = json("../dados/padrao-tex.json")
#let mk = json("../trabalho/marcas.json")
#let pasta = "../trabalho/"
#let ent(g) = d.entradas.filter(p => p.grupo == g)
#let sai(g) = d.saidas.filter(p => p.grupo == g)
#let proc(id) = d.procedimentos.find(p => p.id == id)

#show: documento.with(d, titulo-doc: "Guia de integração", subtitulo-doc: "Como ligar um equipamento Tex G4 ao CLP, comandar o teste e ler o resultado.")

// ---------- sumário ----------
#page(header: none)[
  #v(6mm)
  #text(font: "IBM Plex Sans", stretch: 75%, size: 25pt, weight: 700, fill: azul)[Sumário]
  #v(8pt)
  #show outline.entry.where(level: 1): set block(above: 1.3em)
  #show outline.entry.where(level: 1): set text(weight: 700, fill: tinta)
  #outline(title: none, depth: 2, indent: 1.4em)
]

= Antes de começar

== Para quem é este guia
#d.publico.quem #d.publico.sabe

No fim do guia você consegue: *#(lower(d.publico.consegue_no_fim.first()) + d.publico.consegue_no_fim.slice(1))*

== O que é o Padrão TEX
O Padrão TEX é um conjunto de blocos prontos para o TIA Portal. Ele faz a comunicação entre um CLP Siemens e os equipamentos Tex G4 de teste de estanqueidade, por #d.produto.protocolos.join(" ou ").

Com ele, o seu programa liga o equipamento, escolhe a peça, inicia o teste e lê a pressão, o vazamento e o resultado. Também traz e envia os parâmetros de teste de cada peça.

== O que você precisa
#for r in d.requisitos.itens [- #r \ ]

== Como ler este guia
- Nomes de pinos, blocos e valores aparecem em fonte de código, como Start ou true.
- Os procedimentos têm sempre a mesma forma: o que precisa estar pronto antes, os passos numerados e o resultado esperado.
- Os avisos marcados como #text(weight: 700, fill: azul, size: 8.5pt, tracking: 1pt)[AVISO] indicam o que pode atrapalhar a comunicação ou o projeto.
- Os termos técnicos estão explicados no Glossário, no fim do guia.

= Conhecendo o Padrão TEX

== A estrutura do projeto
Tudo o que comanda e lê os equipamentos Tex fica na pasta TexG4, dentro dos blocos de programa do CLP.

#marcada(mk.arvore, pasta, largura: 62%)

#table(
  columns: (34%, 1fr), stroke: (x, y) => if y > 0 { (bottom: 0.5pt + linha) }, fill: (x, y) => if y == 0 { azul },
  inset: (x: 7pt, y: 6.5pt),
  table.header(text(white, weight: 600, size: 8.5pt)[Item], text(white, weight: 600, size: 8.5pt)[Para que serve]),
  ..d.estrutura.map(e => (text(weight: 600, fill: tinta, e.item), e.papel)).flatten(),
)

#aviso("Aviso")[#d.avisos.at(0).texto]

== Os blocos da biblioteca
A pasta 9 - Library traz os blocos que fazem a comunicação. #d.editavel.texto

#table(
  columns: (1fr, auto, auto), stroke: (x, y) => if y > 0 { (bottom: 0.5pt + linha) }, fill: (x, y) => if y == 0 { azul },
  inset: (x: 7pt, y: 5.5pt), align: (left, center, center),
  table.header(..("Bloco", "Tipo", "Número").map(h => text(white, weight: 600, size: 8.5pt, h))),
  ..d.biblioteca.map(b => (mono(b.nome), text(size: 9pt, b.tipo), text(size: 9pt)[#b.tipo#b.numero])).flatten(),
)

== Escolher o bloco do equipamento
Existem quatro blocos de comunicação G4. Escolha pelo protocolo da sua rede e pelo que você precisa fazer com os dados das peças.

#block(breakable: false)[
#set par(justify: false)
#table(
  columns: (27%, 15%, 14%, 1fr), stroke: (x, y) => if y > 0 { (bottom: 0.5pt + linha) }, fill: (x, y) => if y == 0 { azul },
  inset: (x: 7pt, y: 6.5pt), align: (x, y) => if x == 2 { center + horizon } else { left + horizon },
  table.header(..("Bloco", "Protocolo", "Upload e download", "O que faz").map(h => text(white, weight: 600, size: 8.5pt, h))),
  ..d.blocos_g4.map(b => (mono(text(weight: 600, b.nome)), text(size: 9pt, b.protocolo), text(size: 9pt, if b.pecas [sim] else [não]), text(size: 9.5pt, b.descricao))).flatten(),
)]

= Comunicação por Modbus TCP

== Chamar o Padrão TEX no seu programa
#procedimento(proc("chamar"))
#marcada(mk.main, pasta, largura: 92%)

== Colocar um equipamento na FB_Tex
#procedimento(proc("montar"))
#marcada(mk.fbvazia, pasta, largura: 92%)
#marcada(mk.adicionando, pasta, largura: 92%)

== Preencher a comunicação e as ligações
As cinco primeiras entradas dizem com qual equipamento o bloco vai conversar. As duas últimas ligam o banco de peças e a IHM. Os valores abaixo são os do projeto de exemplo; a descrição completa de cada pino está no capítulo 5.

#procedimento((
  condicao: [O bloco G4_ModbusTCP está na network, com as entradas vazias.],
  passos: (ent("comunicacao") + ent("ligacao")).map(p => [Em #mono(text(weight: 600, p.nome)), coloque #mono(p.exemplo). #p.descricao]),
  resultado: [Com Connect em true, o bloco liga a conexão. A saída Connected fica true quando o equipamento está conectado.],
))

= Comunicação por Profinet
#let pf = d.profinet
#pf.resumo O bloco Profinet não usa IP: a comunicação passa pelo gateway Profinet do TEX-G4. A chamada no Main e a FB_Tex são as mesmas do capítulo 3.

#procedimento(proc("profinet"))

== A rede
#marcada(mk.rede, pasta, largura: 80%)

== Configurar o TEX-G4 (GSD)
#pf.gsd.explica

#block(breakable: false)[
#set par(justify: false)
#table(columns: (34%, 1fr), stroke: (x, y) => (bottom: 0.5pt + linha), inset: (x: 7pt, y: 6pt),
  text(weight: 600, fill: tinta)[Módulo], mono(pf.gsd.modulo),
  text(weight: 600, fill: tinta)[Endereços de entrada (I)], mono(pf.gsd.i_endereco),
  text(weight: 600, fill: tinta)[Endereços de saída (Q)], mono(pf.gsd.q_endereco),
  text(weight: 600, fill: tinta)[IP do gateway], mono(pf.gsd.ip_gateway),
  text(weight: 600, fill: tinta)[Máscara], mono(pf.gsd.mascara),
  text(weight: 600, fill: tinta)[IP do equipamento Tex], mono(pf.gsd.ip_equipamento),
)]
#marcada(mk.gsd, pasta, largura: 100%)

#block(breakable: false)[
== Criar as tags
#pf.tags.explica
#marcada(mk.tags, pasta, largura: 62%)
]

== O bloco G4_Profinet
#pf.bloco.explica

#tabela-pinos(pf.bloco.novas, com-exemplo: true)
#marcada(mk.pnbloco, pasta, largura: 62%)

= Referência dos blocos

== O bloco inteiro
O bloco tem #d.entradas.len() entradas e #d.saidas.len() saídas, além de EN e ENO. À esquerda, as ligações do projeto de exemplo.

#figure(caption: [O bloco G4_ModbusTCP, com as entradas e as saídas agrupadas.],
  image("../trabalho/svg/bloco.svg", width: 100%, alt: "Diagrama do bloco G4_ModbusTCP com todas as entradas à esquerda e todas as saídas à direita, agrupadas por função."))

== Entradas
#for g in ("comunicacao", "comando", "pecas", "ligacao") [
  === #d.grupos.at(g)
  #tabela-pinos(ent(g), com-exemplo: true)
]

== Saídas
#for g in ("estado", "resultado", "medicao", "diagnostico") [
  === #d.grupos.at(g)
  #tabela-pinos(sai(g))
]

== O bloco G4_Profinet
As saídas são as mesmas do G4_ModbusTCP. Nas entradas, saem #d.profinet.bloco.retiradas.map(n => mono(n)).join(", ", last: " e ") e entram #d.profinet.bloco.novas.map(p => mono(p.nome)).join(" e ").

#figure(caption: [O bloco G4_Profinet do projeto de exemplo.],
  image("../trabalho/svg/bloco-profinet.svg", width: 100%, alt: "Diagrama do bloco G4_Profinet: as mesmas entradas do G4_ModbusTCP sem IP, Port e Connect, com PN_IN e PN_OUT no fim, e as mesmas saídas."))

= Operando pelo CLP

== Iniciar um teste de estanqueidade
#procedimento(proc("testar"))
#aviso("Aviso")[#d.avisos.at(1).texto]
#aviso("Aviso")[#d.avisos.at(2).texto]

=== A sequência dos sinais
#fluxo(proc("testar").fluxo + (proc("testar").fluxo_fim,))

#marcada(mk.monitorado, pasta, largura: 56%)

== Alterar um parâmetro de teste de uma peça
Os parâmetros de teste de cada peça ficam guardados no equipamento Tex. Para mudar um deles pelo CLP, você traz os dados para o banco de dados, altera e envia de volta.

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

#block(breakable: false)[
#table(columns: (40%, 30%, 30%), stroke: (x, y) => if y > 0 { (bottom: 0.5pt + linha) }, fill: (x, y) => if y == 0 { azul },
  inset: (x: 7pt, y: 5pt), align: (left, center, center),
  table.header(..("Campo", "Antes", "Depois").map(h => text(white, weight: 600, size: 8.5pt, h))),
  ..db.exemplo_upload.map(e => (mono(e.campo), mono(e.antes), text(weight: 700, fill: azul2, mono(e.depois)))).flatten())]
#marcada(mk.dbparts, pasta, largura: 88%)

= Glossário
#table(
  columns: (28%, 1fr), stroke: (x, y) => (bottom: 0.5pt + linha), inset: (x: 7pt, y: 7pt),
  ..d.glossario.map(g => (text(weight: 700, fill: tinta, g.termo), g.definicao)).flatten(),
)

#v(1fr)
#block(width: 100%, inset: (x: 12pt, y: 10pt), fill: poco, radius: 4pt)[
  #text(weight: 600, fill: tinta)[Histórico de revisões] \
  #text(size: 9pt)[Versão 1.0 · 02/10/2026 · Primeira edição: comunicação por Modbus TCP e operação pelo CLP.] \
  #text(size: 9pt)[Versão 2.0 · 02/10/2026 · Escolha do bloco, comunicação por Profinet, saída de retrabalho renomeada para Rework e banco de dados das peças.]
]
