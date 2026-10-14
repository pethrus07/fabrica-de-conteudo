"""Desenha o bloco G4_ModbusTCP em vetor, a partir de dados/padrao-tex.json.

Por que redesenhar em vez de usar a captura: as capturas têm ~580 px de largura e ficam borradas
ampliadas no PDF e no vídeo 1080p. O desenho sai dos MESMOS dados do manual (nomes, ordem, grupos,
exemplos) e a auditoria confere nome e ordem contra o OCR da tela real — então ele não pode divergir
do TIA Portal sem o build reprovar.

Saídas (trabalho/svg/):
  bloco.svg            com os exemplos de ligação à esquerda (como no projeto de exemplo)
  bloco-vazio.svg      só o bloco (para a referência rápida)
Cada pino é um <g id="pin-<Nome>"> com um retângulo .hl (destaque) que o vídeo acende por CSS.
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
D = json.loads((RAIZ / "dados" / "padrao-tex.json").read_text(encoding="utf-8"))
OUT = RAIZ / "trabalho" / "svg"
OUT.mkdir(parents=True, exist_ok=True)

NAVY, NAVY2, ORANGE, INK, MUT, LINE, FOG, BOX = "#003895", "#002566", "#D32E12", "#0F1B26", "#566676", "#C3CDD8", "#E8EFF5", "#F4F7FA"
SANS = "IBM Plex Sans"
MONO = "IBM Plex Mono"
RH = 27          # altura da linha de pino
TOP = 96         # topo da primeira linha (abaixo do cabeçalho do bloco)


def entradas_profinet():
    """Entradas do G4_Profinet: as do Modbus sem IP/Port/Connect, mais PN_IN e PN_OUT no fim (ordem da tela 17)."""
    pf = D["profinet"]["bloco"]
    ent = [dict(p) for p in D["entradas"] if p["nome"] not in pf["retiradas"]]
    for p in ent:
        if p["nome"] == "Name":
            p["exemplo"] = pf["nome_exemplo"]
    return ent + pf["novas"]


def entradas_de(variante):
    """Entradas de cada um dos 4 blocos G4, sempre derivadas das do G4_ModbusTCP (telas 10, 19, 20 e 21)."""
    basic = next(b for b in D["blocos_g4"] if b["nome"] == "G4_ModbusTCP_Basic")["retiradas"]
    if variante == "modbus":
        return D["entradas"]
    if variante == "profinet":
        return entradas_profinet()
    if variante == "modbus_basic":
        return [p for p in D["entradas"] if p["nome"] not in basic]
    if variante == "profinet_basic":
        return [p for p in entradas_profinet() if p["nome"] not in basic]


# cabeçalho de cada bloco: instância e número como aparecem nas telas do projeto de exemplo
CABECALHO = {
    "modbus": ("#Equipamento1", "%FB1030", "G4_ModbusTCP"),
    "profinet": ("#Equipamento2", "%FB1033", "G4_Profinet"),
    "modbus_basic": ("#Equipamento3", "%FB1031", "G4_ModbusTCP_Basic"),
    "profinet_basic": ("#Equipamento4", "%FB1034", "G4_Profinet_Basic"),
}


def svg_bloco(com_exemplos: bool, com_grupos: bool = True, variante: str = "modbus") -> str:
    lista = entradas_de(variante)
    ent = [{"nome": "EN", "grupo": None, "exemplo": ""}] + lista
    sai = [{"nome": "ENO", "grupo": None}] + D["saidas"]
    instancia, numero, titulo = CABECALHO[variante]
    n = max(len(ent), len(sai))
    # colunas, da esquerda para a direita: rótulo do grupo | barra | exemplo | fio | bloco | fio | barra | rótulo
    barra_e = 150                                   # barra vermelha do grupo (entradas)
    vx = barra_e + 250 if com_exemplos else barra_e + 10   # borda direita da coluna de exemplos
    bx0 = vx + 58                                   # caixa do bloco
    bx1 = bx0 + 340
    rx = bx1 + 58                                   # fim do fio de saída
    W = rx + 175
    H = TOP + n * RH + 26
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{SANS}">',
         '<style>.hl{fill:#D32E12;opacity:0} .on .hl{opacity:.22} .on .pn{fill:#002566;font-weight:700}</style>']
    # cabeçalho: instância e nome do bloco
    s.append(f'<text x="{(bx0+bx1)/2}" y="28" text-anchor="middle" font-size="14" fill="{MUT}">{instancia}</text>')
    s.append(f'<rect x="{bx0}" y="38" width="{bx1-bx0}" height="{TOP-38 + n*RH + 6}" rx="6" fill="{BOX}" stroke="{NAVY}" stroke-width="1.6"/>')
    s.append(f'<rect x="{bx0}" y="38" width="{bx1-bx0}" height="46" rx="6" fill="{NAVY}"/>')
    s.append(f'<rect x="{bx0}" y="70" width="{bx1-bx0}" height="14" fill="{NAVY}"/>')
    s.append(f'<text x="{(bx0+bx1)/2}" y="58" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="#BFD3E3">{numero}</text>')
    s.append(f'<text x="{(bx0+bx1)/2}" y="77" text-anchor="middle" font-size="16" font-weight="700" fill="#FFFFFF">{titulo}</text>')

    def linha(i):
        return TOP + i * RH + RH / 2

    # entradas
    for i, p in enumerate(ent):
        y = linha(i)
        s.append(f'<g id="pin-{p["nome"]}">')
        s.append(f'<rect class="hl" x="{barra_e + 8}" y="{y - RH/2 + 1}" width="{(bx0 + 175) - (barra_e + 8)}" height="{RH - 2}" rx="4"/>')
        s.append(f'<line x1="{vx + 6}" y1="{y}" x2="{bx0}" y2="{y}" stroke="{NAVY}" stroke-width="1.4"/>')
        if com_exemplos and p.get("exemplo"):
            s.append(f'<text x="{vx}" y="{y + 4.5}" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="#2F6FA8">{escape(p["exemplo"])}</text>')
        s.append(f'<text class="pn" x="{bx0 + 12}" y="{y + 5}" font-size="14.5" font-weight="500" fill="{INK}">{escape(p["nome"])}</text>')
        s.append('</g>')
    # saídas
    for i, p in enumerate(sai):
        y = linha(i)
        s.append(f'<g id="pin-{p["nome"]}">')
        s.append(f'<rect class="hl" x="{bx1 - 175}" y="{y - RH/2 + 1}" width="{175 + 70}" height="{RH - 2}" rx="4"/>')
        s.append(f'<line x1="{bx1}" y1="{y}" x2="{rx}" y2="{y}" stroke="{NAVY}" stroke-width="1.4"/>')
        s.append(f'<text class="pn" x="{bx1 - 12}" y="{y + 5}" text-anchor="end" font-size="14.5" font-weight="500" fill="{INK}">{escape(p["nome"])}</text>')
        s.append('</g>')

    # chaves de grupo: uma barra por trecho contíguo do mesmo grupo
    if com_grupos:
        def chaves(lista, lado):
            i = 1
            while i < len(lista):
                g = lista[i]["grupo"]; j = i
                while j + 1 < len(lista) and lista[j + 1]["grupo"] == g:
                    j += 1
                y0, y1 = TOP + i * RH + 4, TOP + (j + 1) * RH - 4
                ym = (y0 + y1) / 2
                rot = D["grupos"][g]
                if lado == "e":
                    x = barra_e
                    s.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round"/>')
                    s.append(f'<text x="{x - 10}" y="{ym + 4}" text-anchor="end" font-size="12" font-weight="600" fill="{NAVY2}">{escape(rot)}</text>')
                else:
                    x = rx + 14
                    s.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round"/>')
                    s.append(f'<text x="{x + 10}" y="{ym + 4}" font-size="12" font-weight="600" fill="{NAVY2}">{escape(rot)}</text>')
                i = j + 1
        chaves(ent, "e"); chaves(sai, "d")
    s.append("</svg>")
    svg = "\n".join(s)
    # recorta a margem esquerda que sobrou quando os grupos ficam fora
    return svg


def grava(nome, svg):
    # só grava se mudou: o build compara datas (vídeo mais velho que o diagrama = defasado)
    alvo = OUT / nome
    if not alvo.exists() or alvo.read_text(encoding="utf-8") != svg:
        alvo.write_text(svg, encoding="utf-8")


def main():
    grava("bloco.svg", svg_bloco(com_exemplos=True))
    grava("bloco-vazio.svg", svg_bloco(com_exemplos=False))
    grava("bloco-profinet.svg", svg_bloco(com_exemplos=True, variante="profinet"))
    grava("bloco-modbus-basic.svg", svg_bloco(com_exemplos=True, variante="modbus_basic"))
    grava("bloco-profinet-basic.svg", svg_bloco(com_exemplos=True, variante="profinet_basic"))
    print("svg ok:", ", ".join(p.name for p in OUT.glob("*.svg")))


if __name__ == "__main__":
    main()
