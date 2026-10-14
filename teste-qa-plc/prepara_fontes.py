# -*- coding: utf-8 -*-
"""
Baixa as fontes do Google Fonts, congela cada peso em TTF estatico e grava
os base64 em fontes/fontes.json.

Motivo: o Chrome nao sub-embute fonte variavel no PDF -- ele rasteriza os
glifos como Type3, o texto deixa de ser selecionavel e alguns leitores
tratam mal. Congelando em estatico, todas as faces saem Type0.

Rodar com o python do venv que tem fontTools:
  ~/.venvs/faster-whisper/Scripts/python.exe prepara_fontes.py
"""
import base64, io, json, os, re, urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# (familia no CSS, nome na URL do Google, peso)
FACES = [
    ("Space Grotesk", "Space+Grotesk", 700),
    ("Inter",         "Inter",         400),
    ("Inter",         "Inter",         600),
]

AQUI = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(AQUI, "fontes")


def baixa(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def url_do_subset_latin(familia_url, peso):
    css = baixa(f"https://fonts.googleapis.com/css2?family={familia_url}:wght@{peso}").decode("utf-8")
    # cada bloco vem precedido de um comentario com o nome do subset
    blocos = re.split(r"/\*\s*([a-z0-9-]+)\s*\*/", css)
    for i in range(1, len(blocos) - 1, 2):
        if blocos[i] == "latin":
            m = re.search(r"src:\s*url\((https://[^)]+\.woff2)\)", blocos[i + 1])
            if m:
                return m.group(1)
    raise RuntimeError(f"subset latin nao encontrado para {familia_url} {peso}")


def main():
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    os.makedirs(DEST, exist_ok=True)
    saida = {}

    for familia, familia_url, peso in FACES:
        chave = f"{familia.replace(' ', '')}-{peso}"
        url = url_do_subset_latin(familia_url, peso)
        woff2 = baixa(url)

        f = TTFont(io.BytesIO(woff2))
        if "fvar" in f:                      # variavel -> congela no peso pedido
            f = instancer.instantiateVariableFont(f, {"wght": peso}, updateFontNames=True)
        f.flavor = None                      # woff2 -> ttf cru

        buf = io.BytesIO()
        f.save(buf)
        ttf = buf.getvalue()

        with open(os.path.join(DEST, chave + ".ttf"), "wb") as fh:
            fh.write(ttf)

        saida[chave] = {
            "familia": familia,
            "peso": peso,
            "b64": base64.b64encode(ttf).decode("ascii"),
        }
        print(f"  {chave:24s} {len(ttf)/1024:7.1f} KB   (fvar: {'sim' if 'fvar' in TTFont(io.BytesIO(woff2)) else 'nao'})")

    with io.open(os.path.join(DEST, "fontes.json"), "w", encoding="utf-8") as fh:
        json.dump(saida, fh)
    print(f"\nfontes/fontes.json gravado com {len(saida)} faces")


if __name__ == "__main__":
    main()
