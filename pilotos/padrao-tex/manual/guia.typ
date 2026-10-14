// Guias rápidos do Padrão TEX (v3 do pedido: 3 guias). Um arquivo, três guias:
//   typst compile ... --input guia=modbus   manual/guia.typ  → Entradas de um bloco Modbus
//   typst compile ... --input guia=profinet manual/guia.typ  → Entradas de um bloco Profinet
//   typst compile ... --input guia=ihm      manual/guia.typ  → Como controlar o Tex pela IHM
// Cada guia cabe em 2 páginas (a auditoria reprova se passar).
#import "tema.typ": *

#let d = json("../dados/padrao-tex.json")
#let mk = json("../trabalho/marcas.json")
#let pasta = "../trabalho/"
#let qual = sys.inputs.at("guia", default: "modbus")
#let pf = d.profinet
#let bloco(nome) = d.blocos_g4.find(b => b.nome == nome)
#let basic = bloco("G4_ModbusTCP_Basic").retiradas
// no exemplo Profinet o equipamento se chama 'Tex B' (tela 19), não 'Tex A' como no Modbus
#let entradas-profinet = d.entradas.filter(p => p.nome not in pf.bloco.retiradas).map(p => if p.nome == "Name" { p + (exemplo: pf.bloco.nome_exemplo) } else { p }) + pf.bloco.novas
#let titulos = (modbus: "Entradas de um bloco Modbus", profinet: "Entradas de um bloco Profinet", ihm: "Como controlar o Tex pela IHM")

#show: documento.with(d, titulo-doc: "Guia rápido · " + titulos.at(qual), capa: false)

#let faixa(t, sub) = block(width: 100%, fill: azul, inset: (x: 14pt, y: 12pt), radius: 6pt, below: 12pt)[
  #grid(columns: (auto, 1fr, auto), column-gutter: 12pt, align: horizon,
    box(fill: white, radius: 6pt, inset: (x: 7pt, y: 5pt), logo(20pt)),
    [#text(fill: white.transparentize(15%), size: 8.5pt, weight: 600, tracking: 1.4pt)[GUIA RÁPIDO · PADRÃO TEX] \
     #text(font: "IBM Plex Sans", stretch: 75%, fill: white, size: 19pt, weight: 700, hyphenate: false)[#t]],
    align(right, text(fill: white.transparentize(25%), size: 8.5pt)[#sub]),
  )
]

// tabela compacta de pinos com o grupo como subtítulo
#let compacta(lista, grupos) = {
  set par(justify: false)
  for g in grupos {
    let l = lista.filter(p => p.grupo == g)
    if l.len() > 0 {
      block(breakable: false, below: 6pt)[
        #text(size: 9.5pt, weight: 700, fill: azul)[#d.grupos.at(g)]
        #v(-3pt)
        #table(columns: (27%, 13%, 1fr), stroke: (x, y) => (bottom: 0.4pt + linha), inset: (x: 4pt, y: 3.6pt),
          ..l.map(p => (
            [#mono(text(size: 8.3pt, weight: 600, fill: azul2, p.nome)) #if "exemplo" in p [\ #text(font: "IBM Plex Mono", size: 6.6pt, fill: mut, p.exemplo)]],
            text(size: 7.6pt, fill: mut, p.tipo),
            text(size: 8.2pt, p.descricao))).flatten())
      ]
    }
  }
}

#if qual == "modbus" [
  #faixa(titulos.modbus, [G4_ModbusTCP · FB1030 \ e G4_ModbusTCP_Basic · FB1031])
  #figure(caption: [O G4_ModbusTCP do projeto de exemplo: #d.entradas.len() entradas e #d.saidas.len() saídas.],
    image("../trabalho/svg/bloco.svg", width: 88%, alt: "Diagrama do bloco G4_ModbusTCP com as entradas e as saídas agrupadas por função."))
  #v(2pt)
  #compacta(d.entradas, ("comunicacao", "comando"))
  #compacta(d.entradas, ("pecas", "ligacao"))
  #block(width: 100%, fill: poco, radius: 4pt, inset: (x: 10pt, y: 8pt))[
    #set text(size: 8.5pt)
    #set par(justify: false)
    *No G4_ModbusTCP_Basic* saem as 6 entradas de dados das peças: #basic.map(n => mono(n)).join(", ", last: " e "). As outras são iguais.
  ]
  #aviso("Aviso")[#d.avisos.at(2).texto]
]

#if qual == "profinet" [
  #faixa(titulos.profinet, [G4_Profinet · FB1033 \ e G4_Profinet_Basic · FB1034])
  #figure(caption: [O G4_Profinet do projeto de exemplo: #entradas-profinet.len() entradas e #d.saidas.len() saídas.],
    image("../trabalho/svg/bloco-profinet.svg", width: 88%, alt: "Diagrama do bloco G4_Profinet com as entradas e as saídas agrupadas por função."))
  #grid(columns: (1fr, 1fr), column-gutter: 10pt,
    block(width: 100%, fill: poco, radius: 4pt, inset: (x: 10pt, y: 8pt))[
      #set text(size: 8.5pt)
      #set par(justify: false)
      #text(weight: 700, fill: azul)[O que muda do Modbus] \
      Saem #pf.bloco.retiradas.map(n => mono(n)).join(", ", last: " e "). Entram #mono("PN_IN") e #mono("PN_OUT"), ligadas nas tags do GSD.
    ],
    block(width: 100%, fill: poco, radius: 4pt, inset: (x: 10pt, y: 8pt))[
      #set text(size: 8.5pt)
      #set par(justify: false)
      #text(weight: 700, fill: azul)[No projeto de exemplo] \
      Gateway em #mono(pf.gsd.ip_gateway) · E/S em #mono(pf.gsd.i_endereco) \
      #mono(pf.tags.itens.at(0).nome) em #mono(pf.tags.itens.at(0).endereco) · #mono(pf.tags.itens.at(1).nome) em #mono(pf.tags.itens.at(1).endereco)
    ])
  #v(2pt)
  #compacta(entradas-profinet, ("comunicacao", "comando"))
  #compacta(entradas-profinet, ("pecas", "ligacao"))
  #block(width: 100%, fill: poco, radius: 4pt, inset: (x: 10pt, y: 8pt))[
    #set text(size: 8.5pt)
    #set par(justify: false)
    *No G4_Profinet_Basic* saem as 6 entradas de dados das peças: #basic.map(n => mono(n)).join(", ", last: " e "). As outras são iguais.
  ]
]

#if qual == "ihm" [
  #let ihm = d.ihm
  #let tela(id) = ihm.telas.find(t => t.id == id)
  #faixa(titulos.ihm, [IHM #ihm.modelo \ telas da pasta TexG4])
  #aviso("Aviso")[#d.avisos.at(3).texto]
  #procedimento(d.procedimentos.find(p => p.id == "ihm"))
  #marcada(mk.operacao, pasta, largura: 74%)
  #pagebreak()
  #text(size: 13pt, weight: 700, fill: tinta)[As telas do Padrão TEX]
  #v(2pt)
  #grid(columns: (30%, 1fr), column-gutter: 14pt, align: top,
    marcada(mk.menu, pasta, largura: 100%),
    {
      set par(justify: false)
      set text(size: 9pt)
      for id in ("menu", "ios", "diagnostico", "parametrizacao") [
        #text(weight: 700, fill: azul)[#tela(id).titulo] \
        #tela(id).descricao
        #v(6pt)
      ]
    })
  #v(4pt)
  #grid(columns: (1fr, 1fr), column-gutter: 10pt,
    marcada(mk.ios, pasta, largura: 100%),
    marcada(mk.param, pasta, largura: 100%))
]
