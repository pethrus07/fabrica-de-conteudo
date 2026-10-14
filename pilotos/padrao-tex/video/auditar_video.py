"""Auditoria dos vídeos do Padrão TEX. Mede o ARQUIVO entregue; reprovou = o build aborta.

Eu não tenho audição: o que substitui o ouvido é instrumento (ver memória conferir-audio-e-video).
  formato      1920x1080, H.264, 30 fps, AAC 48 kHz; duração = linha do tempo (±0,15 s)
  volume       −16 LUFS integrado (±1) e pico real ≤ −1 dBTP (ebur128)
  fala         transcrição reversa (faster-whisper large-v3-turbo) contra o roteiro falado:
               ≥ 97% das palavras em português presentes, e a última frase inteira (pega fala decepada)
  imagem       freezedetect: imagem parada ≤ 55% e maior trecho ≤ 4 s, contando o congelamento
               que vai até o fim do arquivo (o furo que escondia o defeito na esteira da Mettria)
  legenda      até 2 linhas de 42 caracteres; ritmo ≤ 17 caracteres/s (Netflix pt-BR) — acima de 20 reprova
  conteudo     números da narração existem nos dados; termos proibidos não aparecem
Uso: python auditar_video.py video-1 video-2
"""
import difflib, json, os, re, site, subprocess, sys, unicodedata
from pathlib import Path

for sp in site.getsitepackages():
    for b in (Path(sp) / "nvidia").glob("*/bin"):
        os.add_dll_directory(str(b)); os.environ["PATH"] = str(b) + os.pathsep + os.environ["PATH"]
from faster_whisper import WhisperModel

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
D = json.loads((RAIZ / "dados" / "padrao-tex.json").read_text(encoding="utf-8"))
PRON = json.loads((AQUI / "pronuncia.json").read_text(encoding="utf-8"))
falhas, avisos = [], []
NOMES = {unicodedata.normalize("NFD", w.lower()).encode("ascii", "ignore").decode()
         for p in D["entradas"] + D["saidas"] for w in re.findall(r"[A-Za-z]+", p["nome"])} | {
    "tex", "fb", "db", "parts", "true", "false", "modbus", "tcp", "profinet", "tia", "portal", "clp", "ihm", "bcd", "main",
    "library", "siemens", "network", "ok", "nok"}
_modelo = None


def modelo():
    global _modelo
    if _modelo is None:
        _modelo = WhisperModel("large-v3-turbo", device="cuda", compute_type="int8_float16")
    return _modelo


def sem_acento(s):
    return unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()


def palavras_pt(texto):
    """Palavras comparáveis: tira nomes de pino (e a grafia falada deles), números e pontuação.
    Nome de pino é conferido à parte — a transcrição escreve 'Red to Test' onde o roteiro tem ReadyToTest."""
    for nome, t in PRON["termos"].items():
        texto = texto.replace(t["fala"], " ").replace(nome, " ")
    texto = re.sub(r"\b[A-Za-z]*[A-Z][a-z]+[A-Z]\w*\b|\b\w*_\w*\b|\b[A-Z]{2,}\w*\b|\d+", " ", texto)
    # nomes de produto e de pino em QUALQUER grafia (o Whisper escreve "TEX", "FB-Tex", "true"): não são português
    return [w for w in re.findall(r"[a-z]+", sem_acento(texto)) if len(w) > 1 and w not in NOMES]


def probe(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(arq)], capture_output=True, text=True)
    return json.loads(r.stdout)


def loudness(arq):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", str(arq), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", txt).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", txt).group(1))
    return i, tp


def congelamento(arq, dur):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", str(arq), "-vf", "freezedetect=n=0.002:d=1.0", "-map", "0:v", "-f", "null", "-"],
                       capture_output=True, text=True)
    ini = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", r.stderr)]
    fim = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", r.stderr)]
    trechos = [(a, fim[k] if k < len(fim) else dur) for k, a in enumerate(ini)]   # sem fim = vai até o fim do arquivo
    total = sum(b - a for a, b in trechos)
    maior = max([b - a for a, b in trechos], default=0)
    return 100 * total / dur, maior, trechos


def audita(vid):
    pasta = AQUI / "trabalho" / vid
    arq = pasta / f"{vid}.mp4"
    tl = json.loads((pasta / "timeline.json").read_text(encoding="utf-8"))
    if not arq.exists() or arq.stat().st_size < 100_000:
        falhas.append(f"{vid}: arquivo ausente ou ILEGÍVEL ({arq.stat().st_size if arq.exists() else 0} bytes)"); return
    p = probe(arq)
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    a = next(s for s in p["streams"] if s["codec_type"] == "audio")
    dur = float(p["format"]["duration"])
    if (v["width"], v["height"]) != (1920, 1080) or v["codec_name"] != "h264" or v["r_frame_rate"] != "30/1":
        falhas.append(f"{vid}: formato {v['codec_name']} {v['width']}x{v['height']} {v['r_frame_rate']}")
    if a["codec_name"] != "aac" or a["sample_rate"] != "48000":
        falhas.append(f"{vid}: áudio {a['codec_name']} {a['sample_rate']}")
    if abs(dur - tl["duracao"]) > 0.15:
        falhas.append(f"{vid}: dura {dur:.2f} s, a linha do tempo tem {tl['duracao']:.2f} s")

    # marca: o cliente pediu nada da Celiware no material (WhatsApp, 02/10 16:06), nem nos metadados do arquivo
    tags = json.dumps(p["format"].get("tags", {}), ensure_ascii=False)
    if re.search("celiware", tags, re.I):
        falhas.append(f"{vid}: metadados do MP4 citam a Celiware: {tags}")

    i, tp = loudness(arq)
    if abs(i + 16) > 1 or tp > -1.0:
        falhas.append(f"{vid}: volume {i} LUFS / pico {tp} dBTP (alvo −16 LUFS, pico ≤ −1)")

    # fala: o vídeo inteiro contra o roteiro falado, palavra por palavra
    segs, _ = modelo().transcribe(str(arq), language="pt", beam_size=5, vad_filter=True, condition_on_previous_text=False)
    ouvido = " ".join(s.text for s in segs)
    roteiro = " ".join(s["fala"] for c in tl["cenas"] for s in c["segmentos"])
    rp, op = palavras_pt(roteiro), palavras_pt(ouvido)
    sm = difflib.SequenceMatcher(a=rp, b=op, autojunk=False)
    casadas = sum(bl.size for bl in sm.get_matching_blocks())
    fid = 100 * casadas / max(1, len(rp))
    perdidas = [" ".join(rp[i1:i2]) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag in ("delete", "replace")]
    (pasta / "transcricao-reversa.txt").write_text(ouvido, encoding="utf-8")
    if fid < 97:
        falhas.append(f"{vid}: fidelidade da fala {fid:.1f}% (< 97%). Faltaram: {perdidas[:12]}")
    elif perdidas:
        avisos.append(f"{vid}: diferenças na fala (fidelidade {fid:.1f}%): {perdidas[:12]}")
    ultima = palavras_pt(tl["cenas"][-1]["segmentos"][-1]["fala"])
    if ultima and " ".join(ultima[-4:]) not in " ".join(op[-30:]):
        falhas.append(f"{vid}: a última frase não aparece inteira no fim do áudio — fala decepada? ({ultima[-4:]})")

    parado, maior, trechos = congelamento(arq, dur)
    if parado > 55 or maior > 4.0:
        falhas.append(f"{vid}: imagem parada {parado:.1f}% (máx. 55%), maior trecho {maior:.1f} s (máx. 4,0)")

    # legenda e conteúdo
    permitidos = set(re.findall(r"\d+", json.dumps(D, ensure_ascii=False)))
    # "Parte 7": o número do capítulo vem da própria linha do tempo, não dos dados
    permitidos |= {str(c["parte"]) for c in tl["cenas"] if c["tipo"] == "capitulo"}
    pior_cps = 0
    for c in tl["cenas"]:
        for s in c["segmentos"]:
            for n in re.findall(r"\d+", s["texto"]):
                if n not in permitidos and n not in {"1", "2"}:
                    falhas.append(f"{vid}: número {n} na narração não existe nos dados: «{s['texto']}»")
            # mesmas regras da v2 dos manuais: pulso só não pode estar ligado ao Start (não confirmado);
            # Retrabalho (maiúsculo) é o nome antigo da saída Rework
            if re.search(r"pulso[^.]{0,25}\bStart\b|\bStart\b[^.]{0,25}pulso|\bRetrabalho\b", s["texto"]) \
                    or re.search(r"p[âa]nico|garantid|celiware|\bo melhor", s["texto"], re.I):
                falhas.append(f"{vid}: termo proibido na narração: «{s['texto']}»")
            for l in s["legendas"]:
                if len(l["linhas"]) > 2 or any(len(x) > 42 for x in l["linhas"]):
                    falhas.append(f"{vid}: legenda fora do padrão (2×42): {l['linhas']}")
                cps = len(l["texto"]) / max(0.01, l["fim"] - l["ini"])
                pior_cps = max(pior_cps, cps)
                if cps > 20:
                    falhas.append(f"{vid}: legenda rápida demais ({cps:.1f} car/s): «{l['texto']}»")
                elif cps > 17:
                    avisos.append(f"{vid}: legenda acima de 17 car/s ({cps:.1f}): «{l['texto']}»")
    print(f"{vid}: {dur:.1f} s · {v['width']}x{v['height']} {v['codec_name']} · {i} LUFS / pico {tp} dBTP · "
          f"fala {fid:.1f}% ({len(rp)} palavras) · parado {parado:.1f}% (maior {maior:.1f} s) · legenda até {pior_cps:.1f} car/s")


if __name__ == "__main__":
    for vid in sys.argv[1:]:
        audita(vid)
    for a in avisos:
        print("  aviso:", a)
    if falhas:
        print(f"\nREPROVADO — {len(falhas)} falha(s):")
        for f in falhas:
            print("  ✗", f)
        sys.exit(1)
    print("\nAPROVADO")
