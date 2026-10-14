// Manual 2 · Referência rápida do bloco G4_ModbusTCP (2 páginas, para deixar ao lado do TIA Portal)
#import "tema.typ": *

#let d = json("../dados/padrao-tex.json")
#let proc(id) = d.procedimentos.find(p => p.id == id)

#show: documento.with(d, titulo-doc: "Referência rápida", capa: false)

#let faixa = block(width: 100%, fill: azul, inset: (x: 14pt, y: 12pt), radius: 6pt, below: 14pt)[
  #grid(columns: (auto, 1fr, auto), column-gutter: 12pt, align: horizon,
    box(fill: white, radius: 6pt, inset: (x: 7pt, y: 5pt), logo(20pt)),
    [#text(fill: destaque, size: 8.5pt, weight: 600, tracking: 1.4pt)[REFERÊNCIA RÁPIDA] \
     #text(font: "IBM Plex Sans", stretch: 75%, fill: white, size: 20pt, weight: 700)[#d.produto.titulo · bloco #d.produto.bloco_principal]],
    align(right, text(fill: white.transparentize(25%), size: 8.5pt)[#d.produto.plataforma \ #d.produto.protocolos.join(" ou ")]),
  )
]

#faixa

#figure(caption: [O bloco #d.produto.bloco_principal: #d.entradas.len() entradas à esquerda e #d.saidas.len() saídas à direita, agrupadas por função.],
  image("../trabalho/svg/bloco.svg", width: 90%, alt: "Diagrama do bloco G4_ModbusTCP com as entradas e as saídas agrupadas por função."))

#v(6pt)
#text(size: 13pt, weight: 700, fill: tinta)[Iniciar um teste pelo CLP]
#v(2pt)
#fluxo(proc("testar").fluxo + (proc("testar").fluxo_fim,))
#v(4pt)
#set text(size: 9pt)
#aviso("Aviso")[#d.avisos.at(2).texto]

#let pf = d.profinet
#grid(columns: (1fr, 1fr), column-gutter: 10pt,
  block(width: 100%, fill: poco, radius: 4pt, inset: (x: 10pt, y: 8pt))[
    #set par(justify: false)
    #text(weight: 700, fill: azul)[Qual bloco usar] \
    #set text(size: 8.3pt)
    #grid(columns: (auto, 1fr), column-gutter: 6pt, row-gutter: 3pt,
      ..d.blocos_g4.map(b => (mono(text(weight: 600, b.nome)), text(fill: mut)[#b.protocolo, #if b.pecas [completo] else [sem peças]])).flatten())
  ],
  block(width: 100%, fill: poco, radius: 4pt, inset: (x: 10pt, y: 8pt))[
    #set par(justify: false)
    #text(weight: 700, fill: azul)[No G4_Profinet] \
    #set text(size: 8.3pt)
    Sem #pf.bloco.retiradas.map(n => mono(n)).join(", ", last: " e "). Com #mono("PN_IN") ← #mono(pf.tags.itens.at(0).nome) (#mono(pf.tags.itens.at(0).endereco)) e #mono("PN_OUT") ← #mono(pf.tags.itens.at(1).nome) (#mono(pf.tags.itens.at(1).endereco)). Gateway em #mono(pf.gsd.ip_gateway).
  ])

#pagebreak()

#let compacta(titulo, lista) = block(width: 100%)[
  #text(size: 11pt, weight: 700, fill: azul)[#titulo]
  #v(-2pt)
  #set par(justify: false)
  #table(columns: (36%, 1fr), stroke: (x, y) => (bottom: 0.4pt + linha), inset: (x: 4pt, y: 3.6pt),
    ..lista.map(p => (
      [#mono(text(size: 8pt, weight: 600, fill: azul2, p.nome)) \ #text(size: 6.8pt, fill: mut)[#p.tipo]],
      text(size: 7.8pt, p.descricao))).flatten())
]

#grid(columns: (1fr, 1fr), column-gutter: 16pt,
  compacta("Entradas", d.entradas),
  compacta("Saídas", d.saidas))

#v(1fr)
#block(width: 100%, fill: poco, radius: 4pt, inset: (x: 10pt, y: 8pt))[
  #set text(size: 8pt)
  Passo a passo, avisos e glossário: *Guia de integração do #d.produto.titulo*. Não altere os blocos da pasta 9 - Library.
]
