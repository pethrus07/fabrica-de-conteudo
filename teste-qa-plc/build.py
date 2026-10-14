# -*- coding: utf-8 -*-
"""
Monta os dois comparativos em PDF (A: neutro, B: puxado para o Easy521) com
identidade Celiware, e AUDITA cada um. Se a auditoria reprovar, o build aborta
e o PDF não chega na pasta saida/.

Rodar:  ~/.venvs/faster-whisper/Scripts/python.exe build.py
"""
import io, json, os, re, shutil, subprocess, sys

import dados as D

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "saida")
TMP = os.path.join(AQUI, "_tmp")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PAGS = 6


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fontes_css():
    with io.open(os.path.join(AQUI, "fontes", "fontes.json"), encoding="utf-8") as fh:
        faces = json.load(fh)
    return "".join(
        "@font-face{font-family:'%s';font-style:normal;font-weight:%d;"
        "src:url(data:font/ttf;base64,%s) format('truetype')}"
        % (f["familia"], f["peso"], f["b64"]) for f in faces.values()
    )


# ==================================================================== estilo
CSS = """
@page{size:A4;margin:0}
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
html,body{margin:0;padding:0}
body{font-family:'Inter',sans-serif;font-weight:400;color:#0E1B2E;background:#fff;
     font-size:9.5pt;line-height:1.5}
.page{width:210mm;height:296mm;display:flex;flex-direction:column;background:#fff}

.mast{flex-shrink:0;color:#fff;padding:9mm 14mm 8mm;
      background:linear-gradient(112deg,#14416E 0%,#0C2440 58%,#0A1E38 100%),#0C2440;
      display:flex;align-items:flex-start;justify-content:space-between;gap:8mm}
.wm{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:13pt;
    letter-spacing:-.02em;line-height:1}
.wm i{font-style:normal;color:#4FA3F0}
.tag{font-size:6.7pt;font-weight:600;color:#8FB6DE;margin-top:2.4mm}
.rt{text-align:right;font-size:7.3pt;color:#A9C4E0;line-height:1.45;padding-top:.6mm}
.rt b{color:#fff;font-weight:600;display:block}

.cover .mast{padding:15mm 14mm 13mm;display:block}
.cover h1{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:23.5pt;
          line-height:1.12;letter-spacing:-.025em;margin:8mm 0 0;color:#fff;max-width:160mm}
.cover h1 em{font-style:normal;color:#4FA3F0}
.lede{font-size:10pt;color:#BBD3EA;margin-top:4.4mm;max-width:150mm;line-height:1.5}

.body{flex:1;padding:8mm 14mm 0}
.foot{flex-shrink:0;padding:4mm 14mm 6mm;border-top:.35mm solid #E8EDF4;display:flex;
      justify-content:space-between;align-items:baseline;font-size:6.8pt;color:#8A9CB3}
.foot b{font-weight:600;color:#475569}
.foot .pg{font-weight:600;color:#1565C0}

h2{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:14.5pt;
   letter-spacing:-.02em;margin:0 0 1.6mm;color:#0C2440}
.sub{font-size:8.8pt;color:#475569;margin:0 0 6mm;max-width:155mm;line-height:1.45}
h3{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:10.4pt;margin:0 0 2mm;
   color:#0C2440;letter-spacing:-.01em}
p{margin:0 0 3mm}
.eyebrow{font-size:6.7pt;font-weight:600;color:#1565C0;margin-bottom:2.4mm}

.duo{display:flex;gap:5mm;margin-top:2mm}
.pcard{flex:1;border:.35mm solid #E8EDF4;border-radius:3mm;overflow:hidden;background:#FBFCFE}
.pcard .top{padding:4mm 5mm 3.4mm;background:#F1F5FA;border-bottom:.35mm solid #E8EDF4}
.pcard .marca{font-size:6.7pt;font-weight:600;color:#1565C0}
.pcard .mod{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:13.5pt;
            color:#0C2440;letter-spacing:-.02em;margin-top:1mm;line-height:1}
.pcard .lin{font-size:7.4pt;color:#8A9CB3;margin-top:1.4mm}
.pcard .grid{padding:4mm 5mm 4.4mm;display:flex;flex-wrap:wrap}
.pcard .cel{width:50%;margin-bottom:3.2mm}
.pcard .cel .v{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:11pt;
               color:#1565C0;line-height:1.05;letter-spacing:-.02em}
.pcard .cel .k{font-size:6.9pt;color:#8A9CB3;margin-top:.9mm;line-height:1.3;padding-right:3mm}

.resumo{margin-top:6mm;border-left:1mm solid #1565C0;background:#F5F9FE;
        border-radius:0 3mm 3mm 0;padding:5mm 6mm}
.resumo.amb{border-left-color:#F59E0B;background:#FEFBF3}
.resumo .eyebrow{color:#0C2440}
.resumo p{font-size:9pt;line-height:1.5}
.resumo p:last-child{margin-bottom:0}

.legenda{display:flex;gap:4mm;margin-top:6mm}
.lg{flex:1;border:.35mm solid #E8EDF4;border-radius:3mm;padding:4mm 4.4mm;background:#FBFCFE}
.lg .t{font-weight:600;font-size:8.6pt;color:#0C2440;margin-bottom:1.4mm}
.lg p{font-size:7.9pt;color:#8A9CB3;margin:0;line-height:1.4}

table{width:100%;border-collapse:collapse;font-size:8.3pt}
thead th{background:#0C2440;color:#fff;font-weight:600;text-align:left;padding:2.6mm 3mm;
         font-size:7.3pt}
tbody td{padding:2.4mm 3mm;border-bottom:.3mm solid #EDF1F7;vertical-align:top;line-height:1.4}
tbody tr.grp td{background:#F1F5FA;font-weight:600;color:#0C2440;font-size:7.4pt;
                padding:2.2mm 3mm;border-bottom:.3mm solid #DCE5F0}
td.it{width:32%;color:#475569}
td.va,td.vb{width:27%}
td.src{width:14%;font-size:6.8pt;color:#A6B4C6}
.win{font-weight:600;color:#0C2440}
.ni{color:#A6B4C6}
.dot{display:inline-block;width:1.5mm;height:1.5mm;border-radius:50%;background:#22C55E;
     margin-right:1.4mm;vertical-align:.35mm}

.blocos{display:flex;flex-wrap:wrap;gap:4mm}
.bl{width:calc(50% - 2mm);border:.35mm solid #E8EDF4;border-radius:3mm;padding:4.2mm 4.6mm;
    background:#FBFCFE}
.bl.wide{width:100%}
.bl h3{font-size:9.4pt;margin-bottom:1.8mm}
.bl p{font-size:8.3pt;margin:0;color:#475569;line-height:1.45}
.bl .lab{font-size:6.5pt;font-weight:600;margin-bottom:1.6mm}
.bl.e{background:#F5F9FE;border-color:#DCE5F0}
.bl.e .lab{color:#1565C0}
.bl.t{background:#FEFBF3;border-color:#F3E3C4}
.bl.t .lab{color:#B5710A}
.bl.n .lab{color:#8A9CB3}

.escolha{display:flex;gap:4mm;margin-top:5mm}
.esc{flex:1;border-radius:3mm;padding:4.4mm 5mm;background:#F5F9FE;border:.35mm solid #DCE5F0}
.esc.b{background:#FEFBF3;border-color:#F3E3C4}
.esc h3{font-size:9.4pt;margin-bottom:2mm}
.esc ul{margin:0;padding-left:4mm;font-size:8.2pt;color:#475569;line-height:1.5}
.esc li{margin-bottom:1.2mm}

.aviso{margin-top:5mm;border:.35mm solid #F3E3C4;background:#FEFBF3;border-radius:3mm;
       padding:4.4mm 5mm}
.aviso .lab{font-size:6.7pt;font-weight:600;color:#B5710A;margin-bottom:2mm}
.aviso p{font-size:8.4pt;color:#475569;margin:0;line-height:1.5}

.fonte{border-top:.3mm solid #E8EDF4;padding:3.4mm 0}
.fonte:first-of-type{border-top:0;padding-top:0}
.sg{display:inline-block;background:#1565C0;color:#fff;font-size:6.5pt;font-weight:600;
    padding:.9mm 2.2mm;border-radius:1.2mm;margin-right:2.4mm;vertical-align:.7mm}
.fonte .tt{font-weight:600;font-size:8.9pt;color:#0C2440}
.fonte p{font-size:8.2pt;color:#475569;margin:1.6mm 0 0;line-height:1.45}
.derv{margin-top:4mm;background:#F8FAFC;border-radius:3mm;padding:4mm 5mm}
.derv .lab{font-size:6.7pt;font-weight:600;color:#1565C0;margin-bottom:2mm}
.derv div{font-size:8.1pt;color:#475569;margin-bottom:1.4mm;line-height:1.4}
.derv div:last-child{margin-bottom:0}
"""


# =============================================================== construtores
def mast():
    return ('<header class="mast"><div><div class="wm">CELI<i>WARE</i></div>'
            '<div class="tag">Comparativo técnico de controladores</div></div>'
            f'<div class="rt"><b>Preparado por Celiware</b>{D.DATA}</div></header>')


def foot(n, var):
    return ('<footer class="foot">'
            f'<span><b>Celiware</b> &middot; Easy521 e TS621 &middot; {D.DATA}</span>'
            f'<span class="pg">{n}/{PAGS}</span><span>{var}</span></footer>')


def pag(n, var, corpo):
    return f'<section class="page">{mast()}<div class="body">{corpo}</div>{foot(n, var)}</section>'


def card(p, celulas):
    cels = "".join(f'<div class="cel"><div class="v">{esc(v)}</div>'
                   f'<div class="k">{esc(k)}</div></div>' for v, k in celulas)
    return (f'<div class="pcard"><div class="top">'
            f'<div class="marca">{esc(p["marca"])}</div>'
            f'<div class="mod">{esc(p["nome"])}</div>'
            f'<div class="lin">{esc(p["linha"])} &middot; código {esc(p["codigo"])}</div></div>'
            f'<div class="grid">{cels}</div></div>')


CARD_EASY = [("8 / 8", "entradas e saídas integradas"),
             ("EtherCAT", "barramento em tempo real"),
             ("200 k", "passos de programa"),
             ("8", "eixos, EtherCAT e pulso")]
CARD_TS = [("16 / 16", "entradas e saídas integradas"),
           ("OPC UA", "sobre as duas portas Ethernet"),
           ("128 k", "passos de programa"),
           ("8", "canais pulso e direção")]

LEGENDA = """<div class="legenda">
<div class="lg"><div class="t">Ponto verde</div><p>Marca o lado que leva vantagem na linha,
só quando as duas fontes permitem a comparação.</p></div>
<div class="lg"><div class="t">Não informado</div><p>A fonte consultada não traz o dado.
Não é o mesmo que o produto não ter o recurso.</p></div>
<div class="lg"><div class="t">Coluna Fonte</div><p>Cada linha carrega a sigla de onde o valor
saiu. As quatro fontes estão descritas na página 6.</p></div>
</div>"""


def capa(var, titulo, lede, resumo):
    return (f'<section class="page cover"><header class="mast">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8mm">'
            f'<div><div class="wm">CELI<i>WARE</i></div>'
            f'<div class="tag">Comparativo técnico de controladores</div></div>'
            f'<div class="rt"><b>Preparado por Celiware</b>{D.DATA}</div></div>'
            f'<h1>{titulo}</h1><div class="lede">{lede}</div></header>'
            f'<div class="body"><div class="duo">{card(D.EASY, CARD_EASY)}'
            f'{card(D.TS, CARD_TS)}</div>{resumo}{LEGENDA}</div>{foot(1, var)}</section>')


def tabela(grupos):
    out = ['<table><thead><tr><th class="it">Item</th>',
           f'<th class="va">{esc(D.EASY["nome"])}</th>',
           f'<th class="vb">{esc(D.TS["nome"])}</th>',
           '<th class="src">Fonte</th></tr></thead><tbody>']
    atual = None
    for grupo, item, ve, fe, vt, ft, fav in D.LINHAS:
        if grupo not in grupos:
            continue
        if grupo != atual:
            out.append(f'<tr class="grp"><td colspan="4">{esc(grupo)}</td></tr>')
            atual = grupo

        def cel(v, lado):
            if v == D.NI:
                return f'<span class="ni">{esc(D.NI)}</span>'
            ponto = '<span class="dot"></span>' if fav == lado else ""
            cls = ' class="win"' if fav == lado else ""
            return f'{ponto}<span{cls}>{esc(v)}</span>'

        out.append(f'<tr><td class="it">{esc(item)}</td>'
                   f'<td class="va">{cel(ve, "easy")}</td>'
                   f'<td class="vb">{cel(vt, "ts")}</td>'
                   f'<td class="src">{esc(fe)} / {esc(ft)}</td></tr>')
    return "".join(out) + "</tbody></table>"


def pag_fontes(var, nota):
    fs = "".join(f'<div class="fonte"><span class="sg">{esc(k)}</span>'
                 f'<span class="tt">{esc(t)}</span><p>{esc(d)}</p></div>'
                 for k, (t, d) in D.FONTES.items())
    dv = "".join(f'<div>{esc(c)}</div>' for _, c in D.DERIVADOS)
    return pag(6, var,
               '<h2>Fontes e método</h2>'
               '<p class="sub">Toda célula da tabela carrega a sigla da fonte de onde o valor '
               'saiu. As quatro fontes usadas estão descritas abaixo, com o que cada uma '
               'cobre e o que ela não cobre.</p>'
               + fs
               + f'<div class="derv"><div class="lab">CONTAS FEITAS NESTE DOCUMENTO</div>{dv}</div>'
               + f'<div class="aviso"><div class="lab">NOTA DE MÉTODO</div><p>{nota}</p></div>')


# =============================================================== texto: versão A
TIT_A = 'Inovance <em>Easy521</em> e INVT <em>TS621</em>, lado a lado'
LEDE_A = ('Comparativo técnico entre dois controladores compactos de porte equivalente, '
          'montado a partir do que cada fabricante publica. Onde a informação não existe, '
          'está escrito que não existe.')

RESUMO_A = """<div class="resumo"><div class="eyebrow">RESUMO</div>
<p>Os dois são CLPs compactos da mesma faixa, e nenhum vence em tudo. O <b>TS621</b> entrega o
dobro de pontos integrados, o dobro de canais rápidos e uma velocidade de varredura declarada
mais alta. O <b>Easy521</b> responde com EtherCAT, CAN e EtherNet/IP, mais memória de programa
e de dados, e uma ficha técnica publicada por inteiro.</p>
<p>A escolha depende de uma pergunta só: <b>a máquina precisa de eixo sincronizado por
barramento, ou precisa de densidade de entradas e saídas?</b> As duas fichas também não têm a
mesma profundidade, e isso limita parte da comparação — a página 6 explica onde.</p></div>"""

ANALISE_A = """<h2>Onde cada um leva vantagem</h2>
<p class="sub">Separado por dimensão, usando só o que as fontes declaram. Item que uma das
fontes não informa não vira ponto para o outro lado: vira lacuna.</p>
<div class="blocos">
  <div class="bl e"><div class="lab">EASY521 LEVA</div><h3>Barramento e integração</h3>
    <p>É o único dos dois que declara EtherCAT, com até 8 eixos sincronizados no mesmo cabo,
    além de CAN e EtherNet/IP. Para máquina com servo coordenado isso muda a arquitetura:
    some a fiação de pulso e some o cartão de eixo.</p></div>
  <div class="bl t"><div class="lab">TS621 LEVA</div><h3>Densidade de entradas e saídas</h3>
    <p>16 entradas e 16 saídas integradas contra 8 e 8, com teto declarado de 1024 pontos na
    expansão. Em painel com muito sensor e pouca lógica de movimento, isso resolve sem
    comprar módulo.</p></div>
  <div class="bl e"><div class="lab">EASY521 LEVA</div><h3>Memória</h3>
    <p>200 k passos de programa contra 128 k, e 2 MB de dados contra 60 K words. Pesa em
    receita longa, rastreabilidade de lote e máquina com muita parametrização guardada.</p></div>
  <div class="bl t"><div class="lab">TS621 LEVA</div><h3>Canais rápidos</h3>
    <p>16 saídas e 16 canais de entrada de 200 kHz, contra 5 eixos de pulso e 8 canais de
    entrada. Para contagem e posicionamento por pulso, é mais canal no mesmo controlador.</p></div>
  <div class="bl n wide"><div class="lab">NÃO COMPARÁVEL COM ESTAS FONTES</div>
    <h3>Velocidade de varredura e preço</h3>
    <p>Os dois fabricantes publicam velocidade em unidades diferentes e sem dizer com que
    programa mediram: 20 k passos em 1,6 ms de um lado, 40 k passos por ms do outro. Pôr os
    dois números lado a lado sugere uma diferença que o método não sustenta. O preço tem o
    mesmo problema — há valor de distribuidor para o Easy521 e não há para o TS621.</p></div>
</div>
<div class="escolha">
  <div class="esc"><h3>Escolha o Easy521 quando</h3><ul>
    <li>a máquina tem servo coordenado ou came eletrônico</li>
    <li>já existem inversores e servos Inovance no parque</li>
    <li>o programa é grande ou guarda muita receita</li>
    <li>a compra exige ficha técnica e preço por escrito</li></ul></div>
  <div class="esc b"><h3>Escolha o TS621 quando</h3><ul>
    <li>o painel tem muito ponto discreto e pouco eixo</li>
    <li>o movimento é por pulso e precisa de muitos canais</li>
    <li>já existe base INVT instalada e assistência local</li>
    <li>o cliente pede OPC UA direto no controlador</li></ul></div>
</div>"""

NOTA_A = ('As duas fichas não têm a mesma profundidade. O Easy521 foi levantado em três '
          'fontes, uma delas comercial; o TS621 em uma só, que não informa sete itens '
          'básicos. Isso significa que a ausência de um dado do TS621 nesta tabela não prova '
          'que o produto não tenha o recurso — significa que a fonte consultada não diz. '
          'Antes de fechar compra, vale pedir a ficha completa do TS621 ao distribuidor e '
          'refazer as linhas marcadas como não informado.')

# =============================================================== texto: versão B
TIT_B = 'Quando a máquina tem movimento, o <em>Easy521</em> muda a conta'
LEDE_B = ('Comparativo técnico com o INVT TS621, a partir do que cada fabricante publica — '
          'e do que a arquitetura de cada um permite construir depois.')

RESUMO_B = """<div class="resumo amb"><div class="eyebrow">RESUMO</div>
<p>Os dois controladores ocupam a mesma faixa de tamanho e de preço, mas resolvem problemas
diferentes. O <b>Easy521</b> é o único dos dois que traz <b>EtherCAT</b>: barramento em tempo
real, até 8 eixos sincronizados e servo no mesmo cabo, sem cartão de eixo e sem fiação de
pulso. Soma a isso <b>56% mais memória de programa</b> e uma memória de dados cerca de
<b>17 vezes maior</b>.</p>
<p>E soma o que não cabe em tabela: ficha técnica completa e preço publicado, garantia de
18 meses contra 12, e um ecossistema de servos, inversores e I/O distribuído do mesmo
fabricante — que fecha a máquina inteira num fornecedor só.</p></div>"""

ANALISE_B = """<h2>O que decide a escolha</h2>
<p class="sub">Quatro pontos em que a diferença entre os dois controladores aparece no
projeto, no prazo de montagem e no custo de manter a máquina rodando.</p>
<div class="blocos">
  <div class="bl e"><div class="lab">1 &middot; ARQUITETURA</div><h3>EtherCAT muda o painel</h3>
    <p>Com até 8 eixos sincronizados no barramento, o servo entra por cabo de rede em vez de
    par de pulso e direção. Menos fiação, menos ruído, menos ponto de falha, e a posição de
    cada eixo disponível no programa sem hardware extra. O TS621 não declara EtherCAT.</p></div>
  <div class="bl e"><div class="lab">2 &middot; FÔLEGO</div><h3>Memória que aguenta o projeto crescer</h3>
    <p>200 k passos contra 128 k, e 2 MB de dados contra 60 K words. É a diferença entre caber
    a receita de hoje e caber a família de produtos que o cliente vai pedir no ano que vem,
    sem trocar de controlador no meio do caminho.</p></div>
  <div class="bl e"><div class="lab">3 &middot; ECOSSISTEMA</div><h3>Um fornecedor para a máquina toda</h3>
    <p>Servos, inversores e I/O distribuído do mesmo fabricante, configurados na mesma
    ferramenta, com simulação offline antes de energizar o painel. Fechar a engenharia em um
    fornecedor só encurta o comissionamento e simplifica a peça de reposição.</p></div>
  <div class="bl e"><div class="lab">4 &middot; RISCO DE COMPRA</div><h3>O que está escrito, está escrito</h3>
    <p>Dimensões, peso, alimentação, grau de proteção, garantia de 18 meses e preço de
    referência: tudo publicado. Do outro lado, sete desses itens não aparecem na fonte
    consultada e o preço é sob consulta. Especificar o que não está documentado transfere
    risco para quem monta o painel.</p></div>
  <div class="bl t wide"><div class="lab">ONDE O TS621 LEVA</div><h3>Pontos integrados</h3>
    <p>O TS621 traz 16 entradas e 16 saídas integradas contra 8 e 8 do Easy521. Em painel com
    muito ponto discreto isso conta — e no Easy521 se resolve com módulo GL20, que entra no
    mesmo trilho e no mesmo barramento.</p></div>
</div>
<div class="escolha">
  <div class="esc"><h3>O Easy521 é a escolha certa quando</h3><ul>
    <li>a máquina tem servo, came eletrônico ou eixo coordenado</li>
    <li>o projeto vai crescer e não pode trocar de CPU no meio</li>
    <li>a manutenção precisa de peça e suporte de um fornecedor só</li>
    <li>a compra exige ficha técnica e preço por escrito</li></ul></div>
  <div class="esc b"><h3>Vale olhar o TS621 quando</h3><ul>
    <li>o painel é quase todo ponto discreto, sem eixo</li>
    <li>já existe base INVT instalada e assistência local</li>
    <li>o cliente pede OPC UA direto no controlador</li></ul></div>
</div>"""

NOTA_B = ('Os dados do Easy521 vieram de três fontes, incluindo o catálogo do fabricante e a '
          'ficha do distribuidor. Os do TS621 vieram da página pública do produto, que não '
          'informa alimentação, dimensões, peso, temperatura, grau de proteção, certificações '
          'nem preço. As linhas marcadas como não informado refletem a fonte consultada, não '
          'uma ausência do produto.')


# =============================================================== documento
def documento(var, titulo, lede, resumo, analise, nota):
    lacunas = ", ".join(D.LACUNAS_TS)
    paginas = [
        capa(var, titulo, lede, resumo),
        pag(2, var, '<h2>Entradas, saídas e redes</h2>'
                    '<p class="sub">O ponto verde marca o lado que leva vantagem naquela '
                    'linha, quando as duas fontes permitem a comparação.</p>'
            + tabela(["Identificação", "Entradas e saídas", "Redes"])),
        pag(3, var, '<h2>Memória, desempenho e movimento</h2>'
                    '<p class="sub">Linhas sem ponto verde são as que os dois fabricantes '
                    'declaram em unidades diferentes, ou que uma das fontes não traz.</p>'
            + tabela(["Memória e desempenho", "Movimento"])),
        pag(4, var, '<h2>Engenharia, físico e comercial</h2>'
                    '<p class="sub">Ferramenta de programação, dados físicos e condições '
                    'comerciais.</p>'
            + tabela(["Engenharia", "Físico e comercial"])
            + f'<div class="aviso"><div class="lab">LACUNAS DA FONTE DO TS621</div>'
              f'<p>A página consultada do TS621 não informa: {lacunas}. Nenhuma dessas '
              f'linhas foi preenchida por estimativa.</p></div>'),
        pag(5, var, analise),
        pag_fontes(var, nota),
    ]
    return ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            '<title>Comparativo Easy521 e TS621</title><style>'
            + fontes_css() + CSS + '</style></head><body>'
            + "".join(paginas) + '</body></html>')


# =============================================================== render
def render(html, nome):
    os.makedirs(TMP, exist_ok=True)
    fh = os.path.join(TMP, nome + ".html")
    pdf = os.path.join(TMP, nome + ".pdf")
    with io.open(fh, "w", encoding="utf-8") as f:
        f.write(html)
    if os.path.exists(pdf):
        os.remove(pdf)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--run-all-compositor-stages-before-draw", "--virtual-time-budget=15000",
                    "--print-to-pdf=" + pdf, "file:///" + fh.replace("\\", "/")],
                   capture_output=True, timeout=180)
    if not os.path.exists(pdf):
        raise RuntimeError("Chrome não gerou " + pdf)
    return pdf


# =============================================================== auditoria
NUM = re.compile(r"\d+(?:[.,]\d+)?")


def norm(n):
    return n.replace(".", "").replace(",", ".")


def numeros_permitidos():
    ok = set()

    def colhe(txt):
        for m in NUM.findall(str(txt)):
            ok.add(norm(m))

    for g, i, ve, fe, vt, ft, fav in D.LINHAS:
        colhe(g); colhe(i); colhe(ve); colhe(vt)
    for p in (D.EASY, D.TS):
        for v in p.values():
            colhe(v)
    for n, conta in D.DERIVADOS:
        colhe(n); colhe(conta)
    for t, d in D.FONTES.values():
        colhe(t); colhe(d)
    colhe(D.DATA)
    colhe(" ".join(D.LACUNAS_TS))
    for n in range(1, PAGS + 1):
        ok.add(str(n))
    return ok


def audita(pdf, var, prosa):
    import fitz
    falhas = []
    doc = fitz.open(pdf)

    if doc.page_count != PAGS:
        falhas.append(f"páginas: esperado {PAGS}, gerado {doc.page_count} — "
                      f"conteúdo transbordou de alguma folha")

    texto_todo = ""
    for i, page in enumerate(doc, 1):
        t = page.get_text()
        texto_todo += t
        tipos = " ".join(str(f[2]) for f in page.get_fonts())
        nomes = " ".join(str(f[3]) for f in page.get_fonts())
        if "Type3" in tipos:
            falhas.append(f"p.{i}: fonte Type3 — texto rasterizado, não selecionável")
        for ruim in ("Segoe", "Arial", "TimesNewRoman", "Calibri"):
            if ruim in nomes:
                falhas.append(f"p.{i}: fonte de fallback embutida ({ruim}) — "
                              f"há glifo fora do subset latin")
        marca = t.replace(" ", "")
        if f"{i}/{PAGS}" not in marca:
            falhas.append(f"p.{i}: rodapé sem a marca de página {i}/{PAGS}")
        if var.replace("-", "") not in marca.replace("-", ""):
            falhas.append(f"p.{i}: rodapé sem o código de versão {var}")

    permitidos = numeros_permitidos()
    vistos = {}
    for m in NUM.finditer(texto_todo):
        if norm(m.group(0)) not in permitidos:
            ctx = texto_todo[max(0, m.start() - 36):m.end() + 26].replace("\n", " ")
            vistos.setdefault(m.group(0), " ".join(ctx.split()))
    for n, ctx in vistos.items():
        falhas.append(f'número sem fonte declarada: "{n}"  ...{ctx}...')

    plano = " ".join(texto_todo.split()).lower()

    # percentual so vale se a conta estiver declarada em DERIVADOS.
    # (o whitelist de numeros sozinho nao basta: "40% maior" passaria porque
    #  existe um "40 k passos" na tabela, em contexto totalmente diferente.)
    pct_ok = {n for n, conta in D.DERIVADOS if "%" in conta}
    for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*%", plano):
        if norm(m.group(1)) not in {norm(x) for x in pct_ok}:
            ctx = " ".join(plano[max(0, m.start() - 40):m.end() + 24].split())
            falhas.append(f'percentual sem conta declarada: "{m.group(0)}"  ...{ctx}...')

    # afirmacoes que nenhuma das fontes sustenta
    PROIBIDOS = [
        (r"\bmtbf\b", "MTBF"),
        (r"vida [úú]til", "vida útil"),
        (r"l[íi]der de mercado", "liderança de mercado"),
        (r"melhor (clp|controlador|do mercado)", "superlativo de mercado"),
        (r"imbat[íi]vel|insuper[áa]vel", "superlativo"),
        (r"garantia de \d+ anos", "garantia em anos"),
    ]
    for padrao, rotulo in PROIBIDOS:
        m = re.search(padrao, plano)
        if m:
            ctx = " ".join(plano[max(0, m.start() - 40):m.end() + 30].split())
            falhas.append(f'afirmação sem fonte ({rotulo})  ...{ctx}...')

    for termo in prosa:
        if termo.lower() not in plano:
            falhas.append(f'trecho esperado ausente: "{termo}"')

    doc.close()
    return falhas


# =============================================================== main
VARIANTES = [
    ("VAR-A", "comparativo-easy521-ts621_VAR-A", TIT_A, LEDE_A, RESUMO_A, ANALISE_A, NOTA_A,
     ["Onde cada um leva vantagem", "não comparável", "1024 pontos", "não informado"]),
    ("VAR-B", "comparativo-easy521-ts621_VAR-B", TIT_B, LEDE_B, RESUMO_B, ANALISE_B, NOTA_B,
     ["O que decide a escolha", "EtherCAT", "1024 pontos", "Onde o TS621 leva"]),
]


def main():
    if os.path.isdir(SAIDA):
        for f in os.listdir(SAIDA):
            if f.endswith(".pdf"):
                os.remove(os.path.join(SAIDA, f))

    prontos, problemas = [], []
    for var, nome, tit, lede, res, ana, nota, prosa in VARIANTES:
        pdf = render(documento(var, tit, lede, res, ana, nota), nome)
        falhas = audita(pdf, var, prosa)
        print(f"\n[{var}]  {os.path.basename(pdf)}")
        if falhas:
            problemas.append(var)
            for f in falhas:
                print("   REPROVOU  " + f)
        else:
            print("   auditoria ok")
            prontos.append((pdf, nome))

    if problemas:
        print(f"\nBUILD ABORTADO — {', '.join(problemas)} não passou na auditoria.")
        print("Nada foi publicado em saida/.")
        sys.exit(1)

    os.makedirs(SAIDA, exist_ok=True)
    for pdf, nome in prontos:
        shutil.copy2(pdf, os.path.join(SAIDA, nome + ".pdf"))
    print(f"\nOK — {len(prontos)} PDFs publicados em saida/")


if __name__ == "__main__":
    main()
