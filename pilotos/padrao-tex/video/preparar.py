"""Estágio 1 do vídeo: narração → linha do tempo → trilha de áudio.

A narração vem ANTES da imagem: a duração de cada frase é o orçamento da cena (lição medida na
esteira da Mettria: gravar primeiro obriga a congelar quadro ou decepar fala).

Por segmento do roteiro:
  - o texto da legenda é o do roteiro (nome de pino exato);
  - a voz lê o mesmo texto com o vocabulário de pronuncia.json;
  - edge-tts devolve o tempo de cada palavra (WordBoundary), que posiciona legenda e destaques.
Saída em video/trabalho/<video>/: timeline.json (cenas, segmentos, focos, legendas) e narracao.wav
nivelada a −16 LUFS / −1 dBTP (loudnorm em duas passadas, linear).
Roda no Python do sistema (tem edge_tts):  python video/preparar.py
"""
import asyncio, hashlib, json, re, subprocess, sys
from pathlib import Path
import edge_tts

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
ROT = json.loads((AQUI / "roteiros.json").read_text(encoding="utf-8"))
PRON = json.loads((AQUI / "pronuncia.json").read_text(encoding="utf-8"))
CACHE = AQUI / "trabalho" / "cache-voz"
CACHE.mkdir(parents=True, exist_ok=True)

ENTRADA, SAIDA = 0.6, 1.0        # respiro no começo e no fim de cada cena (s)
PAUSA = 0.32                     # entre frases da mesma cena
ABERTURA_MIN = 4.0               # cartões de título e fim ficam no mínimo isso na tela
MAX_LINHA, MAX_LINHAS = 42, 2    # legenda: padrão Netflix pt-BR

TERMOS = sorted(PRON["termos"].items(), key=lambda kv: -len(kv[0]))


def falado(texto):
    """Troca cada nome escrito pela grafia que a voz pronuncia bem (palavra inteira, maior primeiro)."""
    for nome, t in TERMOS:
        texto = re.sub(rf"(?<![\w]){re.escape(nome)}(?![\w])", t["fala"], texto)
    return texto


async def sintetiza(fala, destino_mp3, destino_json):
    com = edge_tts.Communicate(fala, PRON["voz"], rate=PRON["ritmo"], boundary="WordBoundary")
    palavras = []
    with open(destino_mp3, "wb") as f:
        async for parte in com.stream():
            if parte["type"] == "audio":
                f.write(parte["data"])
            elif parte["type"] == "WordBoundary":
                palavras.append({"p": parte["text"], "t": parte["offset"] / 1e7, "d": parte["duration"] / 1e7})
    Path(destino_json).write_text(json.dumps(palavras, ensure_ascii=False), encoding="utf-8")


def duracao(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def tempos_da_legenda(texto, palavras_faladas):
    """Dá a cada palavra ESCRITA o instante em que a voz começa a dizê-la.
    Um nome escrito pode virar várias palavras faladas ('ReadyToTest' → 'Rédi Tu Test')."""
    escritas = texto.split()
    out, cur = [], 0
    for w in escritas:
        n = max(1, len(falado(w).split()))
        t = palavras_faladas[min(cur, len(palavras_faladas) - 1)]["t"] if palavras_faladas else 0
        out.append((w, t))
        cur += n
    return out


def quebra_legenda(palavras_t, fim):
    """Agrupa em blocos de até 2 linhas × 42 caracteres, quebrando de preferência na pontuação."""
    blocos, atual = [], []
    def cabe(lista):
        linhas, linha = 1, ""
        for w, _ in lista:
            if len((linha + " " + w).strip()) > MAX_LINHA:
                linhas += 1; linha = w
            else:
                linha = (linha + " " + w).strip()
        return linhas <= MAX_LINHAS
    for k, (w, t) in enumerate(palavras_t):
        if atual and not cabe(atual + [(w, t)]):
            blocos.append(atual); atual = []
        atual.append((w, t))
        restam = len(palavras_t) - k - 1
        # fecha o bloco na pontuação só se o que sobra não vira um pedaço solto (mínimo 5 palavras)
        if re.search(r"[.!?:]$", w) and len(" ".join(x for x, _ in atual)) > 24 and (restam == 0 or restam >= 5):
            blocos.append(atual); atual = []
    if atual:
        blocos.append(atual)
    # rebalanceia: último bloco com menos de 4 palavras ("conectado.") puxa palavras do anterior
    while len(blocos) >= 2 and len(blocos[-1]) < 4 and len(blocos[-2]) > 4 and cabe([blocos[-2][-1]] + blocos[-1]):
        blocos[-1].insert(0, blocos[-2].pop())
    leg = []
    for i, b in enumerate(blocos):
        ini = b[0][1]
        f = blocos[i + 1][0][1] if i + 1 < len(blocos) else fim
        txt = " ".join(w for w, _ in b)
        leg.append({"ini": round(ini, 3), "fim": round(f, 3), "texto": txt, "linhas": linhas_equilibradas(txt)})
    return leg


# palavras que não podem ficar no fim da linha: artigo/preposição colado no que vem depois (Netflix pt-BR)
NAO_QUEBRA_DEPOIS = {"a", "o", "as", "os", "um", "uma", "de", "da", "do", "das", "dos", "e", "em", "no", "na", "nos", "nas",
                     "ao", "à", "com", "por", "para", "se", "que", "é"}


def linhas_equilibradas(txt):
    if len(txt) <= MAX_LINHA:
        return [txt]
    ws = txt.split()
    melhor = None
    for i in range(1, len(ws)):
        a, b = " ".join(ws[:i]), " ".join(ws[i:])
        if len(a) > MAX_LINHA or len(b) > MAX_LINHA:
            continue
        nota = abs(len(a) - len(b)) + (40 if ws[i - 1].lower().strip(",.") in NAO_QUEBRA_DEPOIS else 0)                - (12 if re.search(r"[,.:;]$", ws[i - 1]) else 0)
        if melhor is None or nota < melhor[0]:
            melhor = (nota, [a, b])
    return melhor[1] if melhor else [txt]


async def prepara(video):
    pasta = AQUI / "trabalho" / video["id"]
    pasta.mkdir(parents=True, exist_ok=True)
    cenas, pedacos, t = [], [], 0.0
    for ci, cena in enumerate(video["cenas"]):
        c = {**{k: v for k, v in cena.items() if k != "segmentos"}, "ini": round(t, 3), "segmentos": []}
        t += ENTRADA
        pedacos.append(("silencio", ENTRADA))
        for si, seg in enumerate(cena["segmentos"]):
            fala = falado(seg["texto"])
            chave = hashlib.sha1(f'{PRON["voz"]}|{PRON["ritmo"]}|{fala}'.encode()).hexdigest()[:16]
            mp3, js = CACHE / f"{chave}.mp3", CACHE / f"{chave}.json"
            if not mp3.exists() or not js.exists():
                await sintetiza(fala, mp3, js)
            dur = duracao(mp3)
            palavras = json.loads(js.read_text(encoding="utf-8"))
            leg = quebra_legenda([(w, t + tt) for w, tt in tempos_da_legenda(seg["texto"], palavras)], t + dur)
            c["segmentos"].append({"ini": round(t, 3), "fim": round(t + dur, 3), "texto": seg["texto"], "fala": fala,
                                   "foco": seg.get("foco"), "legendas": leg, "audio": mp3.name})
            pedacos.append(("audio", mp3))
            t += dur
            if si < len(cena["segmentos"]) - 1:
                pedacos.append(("silencio", PAUSA)); t += PAUSA
        resto = SAIDA
        if cena["tipo"] in ("titulo", "fim", "capitulo") and (t + resto - c["ini"]) < ABERTURA_MIN:
            resto = ABERTURA_MIN - (t - c["ini"])
        pedacos.append(("silencio", resto)); t += resto
        c["fim"] = round(t, 3)
        cenas.append(c)

    # trilha: decodifica cada pedaço para wav 48 kHz mono e concatena (sem recomprimir no meio)
    lista = pasta / "trilha.txt"
    linhas = []
    for k, (tipo, v) in enumerate(pedacos):
        w = pasta / f"p{k:03d}.wav"
        if tipo == "silencio":
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", f"{v:.3f}", str(w)], check=True)
        else:
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(v), "-ar", "48000", "-ac", "1", str(w)], check=True)
        linhas.append(f"file '{w.name}'")
    lista.write_text("\n".join(linhas), encoding="utf-8")
    bruto = pasta / "narracao-bruta.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(bruto)], check=True, cwd=pasta)
    for p in pasta.glob("p*.wav"):
        p.unlink()
    # loudnorm em duas passadas, linear: -16 LUFS, -1 dBTP, sem bombear o começo das frases
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(bruto), "-af", "loudnorm=I=-16:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"): r.stderr.rindex("}") + 1])
    filtro = (f"loudnorm=I=-16:TP=-1:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(bruto), "-af", filtro, "-ar", "48000", str(pasta / "narracao.wav")], check=True)

    total = round(t, 3)
    tl = {"id": video["id"], "titulo": video["titulo"], "subtitulo": video["subtitulo"], "duracao": total, "fps": 30, "cenas": cenas}
    (pasta / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{video['id']}: {total:.1f} s, {len(cenas)} cenas, {sum(len(c['segmentos']) for c in cenas)} frases")


async def main():
    for v in ROT["videos"]:
        await prepara(v)

if __name__ == "__main__":
    asyncio.run(main())
