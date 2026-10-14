"""Lê o texto de cada captura de tela e guarda a caixa de cada rótulo (coordenadas da imagem original).

Serve a duas coisas: (1) posicionar destaques e números por MEDIÇÃO, não por estimativa;
(2) provar que cada nome de pino citado no material aparece de fato na tela (a auditoria usa isso).
Roda no venv ~/.venvs/tts (Python 3.12), onde o RapidOCR está instalado.
"""
import json
from pathlib import Path
from PIL import Image
import numpy as np
from rapidocr_onnxruntime import RapidOCR

AQUI = Path(__file__).resolve().parent
PACOTE = next((AQUI.parent / "fonte").glob("padrao-tex_*"))
SAIDA = AQUI.parent / "trabalho" / "ocr"
SAIDA.mkdir(parents=True, exist_ok=True)
ESCALA = 2  # as capturas são pequenas (≈600 px); ampliar antes de ler melhora muito o acerto

ocr = RapidOCR()
for img in sorted(PACOTE.rglob("*.png")):
    im = Image.open(img).convert("RGB")
    big = im.resize((im.width * ESCALA, im.height * ESCALA), Image.LANCZOS)
    res, _ = ocr(np.array(big))
    itens = []
    for quad, txt, score in (res or []):
        xs = [p[0] / ESCALA for p in quad]; ys = [p[1] / ESCALA for p in quad]
        itens.append({"texto": txt, "caixa": [round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys))], "conf": round(float(score), 3)})
    rel = img.relative_to(PACOTE).as_posix()
    (SAIDA / (rel.replace("/", "__") + ".json")).write_text(json.dumps({"arquivo": rel, "largura": im.width, "altura": im.height, "itens": itens}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{rel}: {im.width}x{im.height}, {len(itens)} textos")
