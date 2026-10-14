"""Transcreve todos os áudios do pacote do cliente com o large-v3-turbo na GPU.

Saída em ../trabalho/transcricao/: um .json por áudio (segmentos + palavras com tempo e
probabilidade) e um TRANSCRICAO.md legível, em ordem de bloco. Palavra com probabilidade
baixa sai marcada [?] para revisão — termo técnico mal transcrito é o erro mais caro aqui.
"""
import json, os, site, sys, time
from pathlib import Path

# as DLLs do cuBLAS/cuDNN vêm dos pacotes pip nvidia-*-cu12: o Windows só as acha se a pasta entrar no caminho
# (mesma solução do projeto Atas, local/transcribe.py)
for sp in site.getsitepackages():
    for b in (Path(sp) / "nvidia").glob("*/bin"):
        os.add_dll_directory(str(b)); os.environ["PATH"] = str(b) + os.pathsep + os.environ["PATH"]
from faster_whisper import WhisperModel

AQUI = Path(__file__).resolve().parent
PACOTE = next((AQUI.parent / "fonte").glob("padrao-tex_*"))
SAIDA = AQUI.parent / "trabalho" / "transcricao"
SAIDA.mkdir(parents=True, exist_ok=True)

# vocabulário tirado das capturas de tela: ajuda o modelo a escrever o termo como aparece no TIA Portal
VOCAB = ("TIA Portal, Siemens, CLP, CPU 1211C, Modbus TCP, Profinet, FB_Tex, FB10, DB1, DB_Parts, DB20, "
         "G4_ModbusTCP, FB1030, G4_ModbusTCP_Basic, G4_Profinet, Main OB1, Debug DB2, Network, bloco de função, "
         "ReadyToTest, Busy, Connected, ActualBCD, ResultOK, ResultNOK, Retrabalho, Escape, ChamberNum, TestNum, "
         "BlockExhaust, BCD, Reset, UploadAllFromTex, DownloadAllToTex, UploadOne, DownloadOne, Chamber, Part, "
         "HMI_Link, Automatic, Start, Stop, Pressure, Leak, DiffPressure, ReturnPressure, AutoCheck, Diagnostic, "
         "Error, estanqueidade, Tex G4, porta 502, endereço IP, integrador.")

def main():
    t0 = time.time()
    m = WhisperModel("large-v3-turbo", device="cuda", compute_type="int8_float16")
    audios = sorted(PACOTE.rglob("*.webm"))
    md = ["# Transcrição dos áudios — Padrão TEX", "", f"Modelo: faster-whisper large-v3-turbo (GPU). Palavras com probabilidade < 0,5 marcadas [?].", ""]
    for a in audios:
        rel = a.relative_to(PACOTE).as_posix()
        segs, info = m.transcribe(str(a), language="pt", beam_size=5, vad_filter=True,
                                  word_timestamps=True, initial_prompt=VOCAB, condition_on_previous_text=False)
        segs = list(segs)
        dados = {"arquivo": rel, "duracao_s": round(info.duration, 1), "segmentos": [
            {"ini": round(s.start, 2), "fim": round(s.end, 2), "texto": s.text.strip(),
             "palavras": [{"p": w.word, "ini": round(w.start, 2), "fim": round(w.end, 2), "prob": round(w.probability, 3)} for w in (s.words or [])]}
            for s in segs]}
        (SAIDA / (rel.replace("/", "__").replace(".webm", ".json"))).write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
        md += [f"## {rel}  ({info.duration:.0f} s)", ""]
        for s in segs:
            txt = "".join((w.word if w.probability >= 0.5 else f"{w.word}[?]") for w in (s.words or [])).strip()
            md.append(f"`{int(s.start//60):02d}:{int(s.start%60):02d}` {txt}")
        md.append("")
        print(f"{rel}: {info.duration:.0f}s, {len(segs)} segmentos", flush=True)
    (SAIDA / "TRANSCRICAO.md").write_text("\n".join(md), encoding="utf-8")
    print(f"pronto em {time.time()-t0:.0f}s")

if __name__ == "__main__":
    main()
