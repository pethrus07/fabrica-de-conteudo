"""Exporta as legendas da linha do tempo em SRT e WebVTT (para YouTube, plataforma de curso, player com CC).
No MP4 a legenda já vai queimada (o WhatsApp não mostra legenda separada).
Uso: python legendas.py video-1 video-2
"""
import json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def ts(t, sep):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}{sep}{int(round((s - int(s)) * 1000)):03d}"


for vid in sys.argv[1:]:
    tl = json.loads((AQUI / "trabalho" / vid / "timeline.json").read_text(encoding="utf-8"))
    blocos = [l for c in tl["cenas"] for s in c["segmentos"] for l in s["legendas"]]
    srt, vtt = [], ["WEBVTT", ""]
    for k, l in enumerate(blocos, 1):
        txt = "\n".join(l["linhas"])
        srt += [str(k), f"{ts(l['ini'], ',')} --> {ts(l['fim'], ',')}", txt, ""]
        vtt += [f"{ts(l['ini'], '.')} --> {ts(l['fim'], '.')}", txt, ""]
    (AQUI / "trabalho" / vid / f"{vid}.srt").write_text("\n".join(srt), encoding="utf-8")
    (AQUI / "trabalho" / vid / f"{vid}.vtt").write_text("\n".join(vtt), encoding="utf-8")
    print(f"{vid}: {len(blocos)} legendas")
