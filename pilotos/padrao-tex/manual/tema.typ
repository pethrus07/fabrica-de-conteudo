// Tema dos documentos técnicos do Padrão TEX (manual e guias rápidos), na identidade da Tex.
// Cores medidas no logo do site tex.com.br (azul #003895, vermelho #D32E12). Fonte IBM Plex, em TTF estático.
// Regra do cliente (02/10/2026): nada da Celiware no material. Vermelho sobre o azul não tem contraste (2:1):
// sobre o azul o texto é branco, e o vermelho entra só como filete.
// Tudo o que é conteúdo técnico vem de dados/padrao-tex.json; este arquivo só sabe COMO mostrar.

#let azul = rgb("#003895")
#let azul2 = rgb("#002566")
#let destaque = rgb("#D32E12")   // vermelho do logo: marcas, números e detalhes (texto sobre ele vai em branco)
#let tinta = rgb("#0F1B26")
#let corpo-cor = rgb("#2B3A48")
#let mut = rgb("#566676")
#let linha = rgb("#DDE3EA")
#let fog = rgb("#E8EFF5")
#let poco = rgb("#F4F7FA")

#let logo(h) = image("../marca/tex/original/TEX-logo.png", height: h, alt: "Logotipo da Tex")

#let mono(x) = text(font: "IBM Plex Mono", size: 0.9em, x)  // herda a cor: legível no corpo e sobre o azul

// nomes que aparecem em fonte de código onde quer que estejam no texto (vêm dos dados)
#let identificadores(d) = {
  let fora = ("IP",)  // em frase é sigla, não nome de pino
  let base = (d.entradas.map(p => p.nome) + d.saidas.map(p => p.nome)).filter(n => n not in fora) + d.biblioteca.map(b => b.nome)
  // v2: pinos e tags do Profinet, tipos UDT e campos do banco de peças também são nomes do TIA Portal
  let extra = ()
  if "profinet" in d {
    extra += d.profinet.bloco.novas.map(p => p.nome) + d.profinet.tags.itens.map(t => t.nome) + d.profinet.tags.itens.map(t => t.tipo)
  }
  if "db_parts" in d {
    extra += (d.db_parts.tipo,) + (d.db_parts.campos_peca + d.db_parts.campos_camara + d.db_parts.campos_teste).map(c => c.nome)
  }
  // pacote final: elementos do Tex [DB1] e o exemplo de uso na lógica
  if "db_tex" in d {
    extra += d.db_tex.campos.map(c => c.nome) + d.db_tex.campos.map(c => c.tipo) + ("FinalizarSequencia",)
  }
  base + extra + ("FB_Tex", "DB_Parts", "HMI_Link", "true", "false", "TRUE", "FALSE")
}

#let aplica-mono(d, corpo) = {
  // ordem decrescente de tamanho: "UploadOne" antes de "Upload" etc.; \b evita casar dentro de palavra
  let nomes = identificadores(d).dedup().sorted(key: n => -n.len())
  let alt = nomes.map(n => n.replace("_", "\_")).join("|")
  show regex("\b(" + alt + ")\b"): it => mono(it.text)
  corpo
}

// ---------- blocos de conteúdo ----------

// AVISO = dano a equipamento ou procedimento (sem risco de lesão): pela ANSI Z535.6 / ISO 3864-2
// não leva o símbolo de alerta de segurança. Fundo azul-claro, faixa marinho.
#let aviso(nivel, corpo) = block(
  width: 100%, fill: fog, inset: (left: 14pt, right: 12pt, y: 10pt), radius: (right: 4pt),
  stroke: (left: 3.5pt + azul), breakable: false, above: 14pt, below: 14pt,
)[
  #text(weight: 700, fill: azul, size: 8.5pt, tracking: 1pt)[#upper(nivel)]
  #v(-4pt)
  #corpo
]

#let num-passo(n) = box(
  width: 17pt, height: 17pt, radius: 50%, fill: azul,
  align(center + horizon, text(white, weight: 700, size: 8.5pt)[#n]),
)

#let procedimento(p) = block(width: 100%, above: 12pt, below: 16pt, breakable: false)[
  #block(fill: poco, inset: (x: 12pt, y: 9pt), radius: 4pt, width: 100%)[
    #text(weight: 600, fill: tinta)[Antes de começar:] #p.condicao
  ]
  #v(4pt)
  #grid(columns: (17pt, 1fr), column-gutter: 9pt, row-gutter: 9pt, align: (center + top, left + top),
    ..p.passos.enumerate().map(((i, t)) => (num-passo(i + 1), pad(top: 1.5pt, t))).flatten())
  #v(2pt)
  #grid(columns: (17pt, 1fr), column-gutter: 9pt,
    box(width: 17pt, height: 17pt, radius: 50%, fill: destaque, align(center + horizon, text(white, weight: 700, size: 9pt)[✓])),
    pad(top: 1.5pt)[#text(weight: 600, fill: tinta)[Resultado:] #p.resultado])
  #if "variacao" in p [
    #v(6pt)
    #text(fill: mut)[#p.variacao]
  ]
]

// tabela de pinos: nome (+ exemplo de ligação), tipo, descrição
#let tabela-pinos(lista, com-exemplo: false) = block(breakable: lista.len() > 8, width: 100%, {
  set par(justify: false)
  table(
  columns: (32%, 12%, 1fr),
  stroke: (x, y) => if y > 0 { (bottom: 0.5pt + linha) },
  fill: (x, y) => if y == 0 { azul },
  inset: (x: 7pt, y: 6.5pt),
  align: (x, y) => left + horizon,
  table.header(..("Pino", "Tipo", "O que faz").map(h => text(white, weight: 600, size: 8.5pt, h))),
  ..lista.map(p => (
    [#mono(text(weight: 600, p.nome))#if com-exemplo and "exemplo" in p [ \ #text(font: "IBM Plex Mono", size: 7.5pt, fill: mut, p.exemplo)]],
    text(size: 8.8pt, fill: mut, p.tipo),
    text(size: 9.5pt, p.descricao),
  )).flatten(),
  )
})

// captura de tela com marcas numeradas (posições vindas do OCR em trabalho/marcas.json)
#let marcada(m, pasta, largura: 100%) = {
  let f = m
  figure(
    caption: f.legenda,
    block(width: largura, breakable: false)[
      #layout(size => {
        let w = size.width
        let h = w * f.altura / f.largura
        box(width: w, height: h, stroke: 0.6pt + linha, {
          place(top + left, image(pasta + f.arquivo, width: w, alt: f.legenda))
          for mk in f.marcas {
            let x0 = w * mk.x0 / 100
            let y0 = h * mk.y0 / 100
            let x1 = w * mk.x1 / 100
            let y1 = h * mk.y1 / 100
            place(top + left, dx: x0, dy: y0, rect(width: x1 - x0, height: y1 - y0, stroke: 1.6pt + destaque, radius: 2pt))
            let r = 7.5pt
            let bx = if x1 + 2 * r + 4pt < w { x1 + 3pt } else { x0 - 2 * r - 3pt }
            place(top + left, dx: bx, dy: (y0 + y1) / 2 - r,
              circle(radius: r, fill: destaque, stroke: 1.2pt + white, align(center + horizon, text(white, weight: 700, size: 8pt)[#mk.n])))
          }
        })
      })
      #v(4pt)
      #set text(size: 9pt)
      #set par(justify: false)
      #align(left, grid(columns: (auto, 1fr), column-gutter: 7pt, row-gutter: 5pt,
        ..f.marcas.map(mk => (
          circle(radius: 6.5pt, fill: destaque, align(center + horizon, text(white, weight: 700, size: 7pt)[#mk.n])),
          align(horizon + left, mk.legenda))).flatten()))
    ],
  )
}

// fluxo horizontal de etapas (sinal = valor), quebrando em linhas
#let fluxo(etapas) = {
  let caixa(e, i) = box(width: 100%, height: 50pt, inset: (x: 8pt, y: 7pt), radius: 4pt, fill: if i == etapas.len() - 1 { fog } else { poco }, stroke: 0.8pt + linha)[
    #set par(justify: false, leading: 0.5em)
    #text(size: 7.5pt, weight: 700, fill: destaque)[#(i + 1)] \
    #text(font: "IBM Plex Mono", size: 8.3pt, weight: 600, fill: azul2)[#e.sinal] \
    #text(size: 8.3pt, fill: corpo-cor)[#e.texto]
  ]
  let cols = 4
  grid(columns: (1fr, 10pt) * (cols - 1) + (1fr,), row-gutter: 8pt, align: horizon,
    ..etapas.enumerate().map(((i, e)) => {
      let seta = if calc.rem(i, cols) < cols - 1 { if i < etapas.len() - 1 { text(fill: destaque, weight: 700)[›] } else { [] } } else { none }
      if seta == none { (caixa(e, i),) } else { (caixa(e, i), seta) }
    }).flatten())
}

// ---------- página e tipografia ----------

#let documento(d, titulo-doc: "", subtitulo-doc: "", capa: true, foto: none, corpo) = {
  let primeira = if capa { 1 } else { 0 }  // com capa, a página 1 não leva cabeçalho nem rodapé
  set document(title: d.produto.titulo + " · " + titulo-doc, author: d.produto.fabricante, keywords: ("Padrão TEX", "Tex G4", "TIA Portal", "Modbus TCP"))
  set text(font: "IBM Plex Sans", size: 10pt, lang: "pt", region: "br", hyphenate: true, fill: corpo-cor)
  set par(justify: true, leading: 0.68em, spacing: 1.05em)
  set list(marker: text(fill: destaque)[•], indent: 2pt, body-indent: 8pt)
  set figure(supplement: "Figura", gap: 8pt)
  show figure.caption: it => text(size: 8.8pt, fill: mut)[#it.supplement #context it.counter.display(it.numbering) · #it.body]
  set heading(numbering: "1.1")
  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    v(4mm)
    block(below: 14pt)[
      #text(size: 10pt, weight: 600, fill: destaque, tracking: 1.2pt)[CAPÍTULO #counter(heading).display("1")]
      #v(-6pt)
      #text(font: "IBM Plex Sans", stretch: 75%, size: 25pt, weight: 700, fill: azul)[#it.body]
    ]
  }
  show heading.where(level: 2): it => block(above: 20pt, below: 9pt, breakable: false)[
    #text(size: 13.5pt, weight: 700, fill: tinta)[#counter(heading).display() #h(4pt) #it.body]
  ]
  show heading.where(level: 3): it => block(above: 14pt, below: 7pt)[#text(size: 11pt, weight: 600, fill: azul2)[#it.body]]

  set page(
    paper: "a4",
    margin: (top: 25mm, bottom: 22mm, x: 20mm),
    header: context {
      if counter(page).get().first() > primeira {
        let aqui = here().page()
        let nesta = query(heading.where(level: 1)).filter(h => h.location().page() == aqui)
        let antes = query(heading.where(level: 1).before(here()))
        let cap = if nesta.len() > 0 { nesta.first().body } else if antes.len() > 0 { antes.last().body } else { [] }
        set text(size: 8pt, fill: mut)
        grid(columns: (1fr, auto), [#text(weight: 600, fill: azul)[#d.produto.titulo] · #titulo-doc], cap)
        v(-5pt)
        line(length: 100%, stroke: 0.5pt + linha)
      }
    },
    footer: context {
      if counter(page).get().first() > primeira {
        set text(size: 8pt, fill: mut)
        grid(columns: (1fr, auto), [#d.produto.fabricante · versão #d.produto.versao_documento · #d.produto.data_br],
          [Página #counter(page).display() de #counter(page).final().first()])
      }
    },
  )

  // ---------- capa ----------
  if capa { page(margin: 0pt, header: none, footer: none)[
    #block(width: 100%, height: 62%, fill: azul, inset: (x: 22mm, top: 24mm, bottom: 18mm))[
      #box(fill: white, radius: 8pt, inset: (x: 12pt, y: 8pt), logo(34pt))
      #h(10pt) #box(baseline: -14pt, text(white.transparentize(20%), size: 10pt, weight: 600, tracking: 2pt)[#upper(d.produto.fabricante)])
      #v(1fr)
      #box(width: 34pt, height: 3pt, fill: destaque, radius: 1.5pt)
      #v(4pt)
      #text(fill: white.transparentize(10%), size: 10.5pt, weight: 600, tracking: 1.6pt)[#upper(titulo-doc)]
      #v(2pt)
      #text(font: "IBM Plex Sans", stretch: 75%, fill: white, size: 46pt, weight: 700)[#d.produto.titulo]
      #v(-10pt)
      #block(width: 80%, text(fill: white.transparentize(15%), size: 15pt, weight: 500)[#d.produto.subtitulo])
      #v(8pt)
      #text(fill: white.transparentize(30%), size: 10.5pt)[#subtitulo-doc]
    ]
    #let ficha = {
      set text(size: 9.5pt)
      set par(justify: false)
      grid(columns: (auto, 1fr), column-gutter: 14pt, row-gutter: 9pt,
        text(fill: mut)[Para quem], d.publico.quem,
        text(fill: mut)[No fim você consegue], d.publico.consegue_no_fim,
        text(fill: mut)[Plataforma], [#d.produto.plataforma · #d.produto.protocolos.join(" ou ")],
        text(fill: mut)[Versão], [#d.produto.versao_documento, de #d.produto.data_br],
      )
    }
    #block(inset: (x: 22mm, top: 10mm))[
      #if foto == none { ficha } else {
        grid(columns: (1fr, 52mm), column-gutter: 12mm, align: top, pad(top: 2mm, ficha),
          box(radius: 6pt, clip: true, image(foto, width: 52mm, alt: "Equipamento Tex G4")))
      }
    ]
  ] }
  aplica-mono(d, corpo)
}
