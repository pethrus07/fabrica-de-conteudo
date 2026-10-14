"""Auditoria dos PDFs do Padrão TEX. Testa o DOCUMENTO, não o código. Reprovou = o build aborta.

Checagens:
  fontes       só IBM Plex embutida; nenhuma Type3 nem fonte substituta
  paginas      a referência rápida cabe em 2 páginas (cartão de consulta)
  pinos        todo pino dos dados aparece no PDF; a ORDEM dos dados é a ordem lida (OCR) na tela real
  numeros      todo número impresso existe nos dados, nas telas (OCR) ou é página/data/versão
  proibidas    termos que não podem sair (afirmação não confirmada, jargão, rascunho)
  termos       Vale com o vocabulário controlado (styles/Celiware)
  legibilidade índice de Flesch adaptado ao português (Martins et al., 1996) — informativo
Uso: python auditar_docs.py trabalho/integracao.pdf trabalho/referencia.pdf
"""
import json, re, subprocess, sys, unicodedata
from pathlib import Path
import fitz

RAIZ = Path(__file__).resolve().parent.parent
D = json.loads((RAIZ / "dados" / "padrao-tex.json").read_text(encoding="utf-8"))
OCR = RAIZ / "trabalho" / "ocr"
falhas, avisos = [], []

def norm(s):
    s = unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.replace("0", "o"))

def texto_pdf(pdf):
    doc = fitz.open(pdf)
    return doc, [p.get_text() for p in doc]

# ---------------------------------------------------------------------------
def checa_fontes(pdf, doc):
    for i, p in enumerate(doc):
        for f in p.get_fonts():
            nome, tipo = f[3], f[2]
            if tipo == "Type3" or "IBMPlex" not in nome:
                falhas.append(f"{pdf.name} p.{i+1}: fonte fora do padrão: {nome} ({tipo})")

def checa_pinos_no_pdf(pdf, paginas):
    corrido = norm(" ".join(paginas))
    for p in D["entradas"] + D["saidas"]:
        if norm(p["nome"]) not in corrido:
            falhas.append(f"{pdf.name}: pino {p['nome']} não aparece no documento")

def ordem_ocr(arquivo, x_min, x_max, nomes):
    """Lê a coluna de nomes de pino na captura e devolve os pinos na ordem vertical em que aparecem."""
    d = json.loads((OCR / (arquivo.replace("/", "__") + ".json")).read_text(encoding="utf-8"))
    # a caixa precisa ENCOSTAR na coluna: o OCR às vezes emenda rótulo e pino ("'DZ'—Modelo") numa caixa só
    col = sorted([i for i in d["itens"] if i["caixa"][2] >= x_min and i["caixa"][0] <= x_max], key=lambda i: i["caixa"][1])
    n2 = lambda s: norm(s).replace("l", "i")          # o OCR troca l por I ("ActuaIBCD")
    lidos = []
    for i in col:
        # primeiro o texto inteiro ("Uploa dAllFromT" tem espaço no meio do nome), depois as partes emendadas
        partes = [i["texto"]] + re.split(r"[—–\-\s]+", i["texto"])
        achou = False
        for parte in partes:
            if achou:
                break
            t = n2(parte)
            if len(t) < 2:
                continue
            # o OCR quebra rótulos longos ("UploadAllFromT" + "ex"): aceita prefixo de 6+ letras
            # nome antigo conta como o atual (a saída Retrabalho virou Rework no meio da manhã de 02/10)
            alvo = [ALIAS.get(n, n) for n in nomes if n2(n) == t or (len(t) >= 6 and n2(n).startswith(t))]
            if alvo:
                achou = parte is partes[0]
                if not lidos or lidos[-1] != alvo[0]:
                    lidos.append(alvo[0])
    return lidos

ALIAS = {p["nome_antigo"]: p["nome"] for p in D["saidas"] if "nome_antigo" in p}

def junta(a, b):
    """Emenda duas capturas do mesmo bloco que se sobrepõem: tira de b o maior começo que já é o fim de a."""
    for k in range(min(len(a), len(b)), 0, -1):
        if a[-k:] == b[:k]:
            return a + b[k:]
    return a + b

def checa_ordem():
    tela = "11-entradas-para-aecssar-os-dados-das-pecas/foto-01_capturar.png"
    ent = [p["nome"] for p in D["entradas"]]
    sai = [p["nome"] for p in D["saidas"]]
    cand_sai = sai + list(ALIAS)
    le = ordem_ocr(tela, 150, 260, ent)
    ls = ordem_ocr(tela, 260, 352, cand_sai)
    if le != ent:
        falhas.append(f"ordem das entradas diverge da tela: dados={ent} tela={le}")
    if ls != sai:
        falhas.append(f"ordem das saídas diverge da tela: dados={sai} tela={ls}")
    # bloco Profinet: a tela 17 vem em 2 capturas (início e fim do bloco)
    pf = D["profinet"]["bloco"]
    ent_pf = [n for n in ent if n not in pf["retiradas"]] + [p["nome"] for p in pf["novas"]]
    t1, t2 = "20-bloco-profinet/foto-01_captura-de-tela-2026-10-02-152306.png", "20-bloco-profinet/foto-02_captura-de-tela-2026-10-02-152438.png"
    le_pf = junta(ordem_ocr(t1, 150, 260, ent_pf), ordem_ocr(t2, 115, 240, ent_pf))
    ls_pf = junta(ordem_ocr(t1, 260, 352, cand_sai), ordem_ocr(t2, 240, 340, cand_sai))
    if le_pf != ent_pf:
        falhas.append(f"ordem das entradas do G4_Profinet diverge da tela: dados={ent_pf} tela={le_pf}")
    if ls_pf != sai:
        falhas.append(f"ordem das saídas do G4_Profinet diverge da tela: dados={sai} tela={ls_pf}")
    # blocos Basic (v3): as mesmas entradas sem as 6 de upload/download — telas 20 e 21
    basic = next(b for b in D["blocos_g4"] if b["nome"] == "G4_ModbusTCP_Basic")["retiradas"]
    for nome, lista, tela in (("G4_ModbusTCP_Basic", [n for n in ent if n not in basic], "21-bloco-modbustcp-basic/foto-01_captura-de-tela-2026-10-02-160836.png"),
                              ("G4_Profinet_Basic", [n for n in ent_pf if n not in basic], "22-bloco-profinet-basic/foto-01_captura-de-tela-2026-10-02-161431.png")):
        lb = ordem_ocr(tela, 150, 262, lista)
        if lb != lista:
            falhas.append(f"ordem das entradas do {nome} diverge da tela: dados={lista} tela={lb}")
        sb = ordem_ocr(tela, 262, 352, cand_sai)
        if sb != sai:
            falhas.append(f"ordem das saídas do {nome} diverge da tela: dados={sai} tela={sb}")
    return len(le), len(ls), len(le_pf)

def numeros_permitidos(n_paginas):
    fontes = json.dumps(D, ensure_ascii=False)
    for f in OCR.glob("*.json"):
        fontes += " ".join(i["texto"] for i in json.loads(f.read_text(encoding="utf-8"))["itens"])
    ok = set(re.findall(r"\d+(?:[.,]\d+)*", fontes))
    # páginas, capítulos, passos, marcas e etapas: a maior enumeração do material é a lista de 20 saídas
    ok |= {str(i) for i in range(1, max(n_paginas, 25) + 1)}
    ok |= {"02/10/2026", "2026", "02", "10", "1.0", "1.1", "1.2", "1.3", "1.4"}
    return ok

def checa_numeros(pdf, paginas, permitidos):
    for i, t in enumerate(paginas):
        for m in re.finditer(r"\d+(?:[.,]\d+)*", t):
            n = m.group(0)
            if n in permitidos or re.fullmatch(r"\d\.\d", n):   # 2.1, 4.3: numeração de seção
                continue
            contexto = t[max(0, m.start() - 25): m.end() + 25].replace("\n", " ")
            falhas.append(f"{pdf.name} p.{i+1}: número sem origem: {n!r} em «…{contexto}…»")

PROIBIDAS = {
    # pulso está confirmado para upload/download (áudio 11); para o Start, ainda não (pendência start-pulso)
    r"pulso[^.]{0,25}\bStart\b|\bStart\b[^.]{0,25}pulso": "o Start é pulso ou nível ainda não foi confirmado pelo cliente (pendência start-pulso)",
    r"\bRetrabalho\b": "a saída agora se chama Rework (Retrabalho é o nome antigo)",
    r"p[âa]nico": "o nome é botão de emergência",
    r"\bTODO\b|\?\?\?|\bXXX\b|lorem|a confirmar": "marca de rascunho",
    r"garantid|100 ?% seguro|o melhor": "promessa que o material não sustenta",
    r"\bclique\b": "no TIA Portal se arrasta e se abre; 'clique' genérico confunde",
    r"celiware": "o cliente pediu: nada da Celiware no material (WhatsApp, 02/10 16:06)",
}

def checa_proibidas(pdf, paginas):
    for i, t in enumerate(paginas):
        for pad, motivo in PROIBIDAS.items():
            # nomes de pino são sensíveis a maiúscula ("retrabalho" minúsculo é palavra, "Retrabalho" era pino)
            for m in re.finditer(pad, t, flags=0 if ("Retrabalho" in pad or "Start" in pad) else re.I):
                falhas.append(f"{pdf.name} p.{i+1}: termo proibido {m.group(0)!r} — {motivo}")

def checa_vale(pdf, paginas):
    txt = RAIZ / "trabalho" / f"{pdf.stem}.txt"
    txt.write_text("\n".join(paginas), encoding="utf-8")
    vale = list(Path.home().glob("AppData/Local/Microsoft/WinGet/Packages/errata-ai.Vale_*/vale.exe"))
    if not vale:
        falhas.append("Vale não encontrado"); return
    r = subprocess.run([str(vale[0]), "--config", str(RAIZ / "ferramentas" / "vale" / ".vale.ini"), "--output", "JSON", str(txt)],
                       capture_output=True, text=True, encoding="utf-8")
    try:
        res = json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        falhas.append(f"Vale falhou: {r.stderr[:300]}"); return
    for arq, alertas in res.items():
        for a in alertas:
            (falhas if a["Severity"] == "error" else avisos).append(f"{pdf.name} (Vale) linha {a['Line']}: {a['Message']}")

# Flesch adaptado (Martins, Ghiraldelo, Nunes e Oliveira Jr., 1996): F = 248,835 − 1,015·(pal/frase) − 84,6·(síl/pal)
VOG = "aeiouáéíóúâêôãõàü"
def silabas(p):
    p = p.lower()
    grupos = re.findall(rf"[{VOG}y]+", p)
    n = 0
    for g in grupos:
        # ditongo decrescente/crescente comum conta 1; hiato com acento ou 'ia/ea/oa' no fim conta 2 (aproximação)
        n += 1 + len(re.findall(r"[aeo][aeo]|[íú][aeo]|[aeo][íú]", g))
    return max(1, n)

def legibilidade(paginas):
    corpo = " ".join(paginas)
    corpo = re.sub(r"\b[A-Z][a-z]+[A-Z]\w*|\b\w*_\w*\b", "", corpo)   # nomes de pino não contam
    frases = [f for f in re.split(r"[.!?:]\s+", corpo) if len(f.split()) >= 4]
    pal = [w for f in frases for w in re.findall(r"[A-Za-zÀ-ÿ]+", f)]
    if not frases or not pal:
        return None
    return round(248.835 - 1.015 * (len(pal) / len(frases)) - 84.6 * (sum(map(silabas, pal)) / len(pal)), 1)

# ---------------------------------------------------------------------------
def main(pdfs):
    ne, ns, npf = checa_ordem()
    print(f"ordem: {ne} entradas e {ns} saídas (G4_ModbusTCP) e {npf} entradas (G4_Profinet) lidas na tela, conferidas contra os dados")
    for arg in pdfs:
        pdf = Path(arg)
        doc, paginas = texto_pdf(pdf)
        checa_fontes(pdf, doc)
        meta = " ".join(str(v) for v in doc.metadata.values() if v)
        if re.search("celiware", meta, re.I):
            falhas.append(f"{pdf.name}: metadados do PDF citam a Celiware: {meta}")
        # o manual e o guia Modbus têm de citar todos os pinos; o guia da IHM não é sobre pinos
        if pdf.stem in ("manual", "integracao", "referencia", "guia-modbus"):
            checa_pinos_no_pdf(pdf, paginas)
        checa_numeros(pdf, paginas, numeros_permitidos(doc.page_count))
        checa_proibidas(pdf, paginas)
        checa_vale(pdf, paginas)
        if (pdf.stem == "referencia" or pdf.stem.startswith("guia-")) and doc.page_count > 2:
            falhas.append(f"{pdf.name}: tem {doc.page_count} páginas; guia rápido precisa caber em 2")
        f = legibilidade(paginas)
        faixa = "muito fácil" if f >= 75 else "fácil" if f >= 50 else "difícil" if f >= 25 else "muito difícil"
        print(f"{pdf.name}: {doc.page_count} páginas · legibilidade {f} ({faixa}, Flesch-Martins aproximado)")
        if f < 40:
            avisos.append(f"{pdf.name}: legibilidade {f} abaixo de 40")
    for a in avisos:
        print("  aviso:", a)
    if falhas:
        print(f"\nREPROVADO — {len(falhas)} falha(s):")
        for x in falhas:
            print("  ✗", x)
        sys.exit(1)
    print("\nAPROVADO")

if __name__ == "__main__":
    main(sys.argv[1:])
