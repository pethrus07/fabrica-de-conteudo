"""Folha de contato das páginas de um PDF, para revisão visual (não vai para a entrega).
    python folha_paginas.py trabalho/manual.pdf [1-6,12]   → trabalho/revisao/<nome>-folha.png
Sem a lista de páginas, monta todas. Cada página sai a 70 dpi numa grade de 4 colunas."""
import sys
from pathlib import Path
import fitz
from PIL import Image

pdf = Path(sys.argv[1])
doc = fitz.open(pdf)
if len(sys.argv) > 2:
    pags = []
    for parte in sys.argv[2].split(","):
        a, _, b = parte.partition("-")
        pags += list(range(int(a), int(b or a) + 1))
else:
    pags = list(range(1, doc.page_count + 1))
ims = []
for n in pags:
    pix = doc[n - 1].get_pixmap(dpi=70)
    ims.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
w, h = ims[0].size
col = 4
folha = Image.new("RGB", (col * (w + 12) + 12, ((len(ims) + col - 1) // col) * (h + 12) + 12), "#9aa4ae")
for k, im in enumerate(ims):
    folha.paste(im, (12 + (k % col) * (w + 12), 12 + (k // col) * (h + 12)))
saida = pdf.parent / "revisao" / f"{pdf.stem}-folha.png"
saida.parent.mkdir(exist_ok=True)
folha.save(saida)
print(saida, len(ims), "páginas")
