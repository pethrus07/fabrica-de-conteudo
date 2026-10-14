"""Build do material do Padrão TEX: gera tudo a partir de dados/padrao-tex.json, audita e só então entrega.

    python build.py              tudo (manual, 3 guias rápidos e o vídeo)
    python build.py --sem-video  só os documentos (o vídeo leva uns 20 minutos para renderizar)

Pedido final do cliente (zip 3, 02/10/2026): 1 vídeo, 1 manual e 3 guias rápidos, na identidade da Tex
(nada da Celiware). Ordem: diagrama → marcas (OCR) → documentos (Typst, PDF/UA-1) → auditoria dos documentos →
português (LanguageTool local) → narração e linha do tempo → render quadro a quadro → auditoria do vídeo →
legendas SRT/VTT → entrega/. Qualquer etapa que reprovar ABORTA e a pasta entrega/ não é tocada:
o que está lá é sempre a última versão que passou em tudo.
"""
import shutil, subprocess, sys, time, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
HOME = Path.home()
PY_FW = HOME / ".venvs" / "faster-whisper" / "Scripts" / "python.exe"     # PyMuPDF, faster-whisper (GPU)
PY_OCR = HOME / ".venvs" / "tts" / "Scripts" / "python.exe"              # RapidOCR
PY_SIS = "python"                                                         # edge-tts
TYPST = next(HOME.glob("AppData/Local/Microsoft/WinGet/Packages/Typst.Typst_*/typst-*/typst.exe"))
LT = next(HOME.glob("ferramentas/LanguageTool-*/languagetool-server.jar"))
ENV = {"PYTHONIOENCODING": "utf-8", "PLAYWRIGHT_BROWSERS_PATH": str(HOME / "AppData/Local/ms-playwright")}

# documento → (fonte Typst, --input, nome na entrega sem a versão)
DOCS = {
    "manual": ("manual/manual.typ", None, "Padrao-TEX_Manual"),
    "guia-modbus": ("manual/guia.typ", "guia=modbus", "Padrao-TEX_Guia-rapido_Entradas-do-bloco-Modbus"),
    "guia-profinet": ("manual/guia.typ", "guia=profinet", "Padrao-TEX_Guia-rapido_Entradas-do-bloco-Profinet"),
    "guia-ihm": ("manual/guia.typ", "guia=ihm", "Padrao-TEX_Guia-rapido_Controlar-o-Tex-pela-IHM"),
}
VIDEOS = {"video-completo": "Padrao-TEX_Video_Do-projeto-ao-teste"}


def etapa(nome, cmd, cwd=RAIZ):
    print(f"\n▶ {nome}", flush=True)
    import os
    r = subprocess.run([str(c) for c in cmd], cwd=cwd, env={**os.environ, **ENV})
    if r.returncode != 0:
        print(f"\n✗ ABORTADO em: {nome}. A pasta entrega/ não foi alterada.")
        sys.exit(1)


def languagetool_no_ar():
    try:
        urllib.request.urlopen("http://localhost:8081/v2/languages", timeout=3); return True
    except Exception:
        return False


def main():
    com_video = "--sem-video" not in sys.argv
    t0 = time.time()
    if not any((RAIZ / "trabalho" / "ocr").glob("*.json")):
        etapa("OCR das capturas", [PY_OCR, "ferramentas/ocr_telas.py"])
    etapa("Diagrama vetorial do bloco", [PY_FW, "ferramentas/diagrama.py"])
    etapa("Marcas sobre as capturas (OCR)", [PY_FW, "ferramentas/marcas.py"])
    for doc, (fonte, entrada, _) in DOCS.items():
        cmd = [TYPST, "compile", "--root", ".", "--font-path", "marca/fontes", "--ignore-system-fonts", "--pdf-standard", "ua-1"]
        if entrada:
            cmd += ["--input", entrada]
        etapa(f"Documento: {doc} (PDF/UA-1)", cmd + [fonte, f"trabalho/{doc}.pdf"])
    etapa("Auditoria dos documentos", [PY_FW, "-X", "utf8", "ferramentas/auditar_docs.py", *[f"trabalho/{d}.pdf" for d in DOCS]])
    if not languagetool_no_ar():
        subprocess.Popen(["java", "-cp", str(LT), "org.languagetool.server.HTTPServer", "--port", "8081"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=LT.parent)
        for _ in range(60):
            if languagetool_no_ar(): break
            time.sleep(1)
    etapa("Português (LanguageTool local)", [PY_FW, "-X", "utf8", "ferramentas/portugues.py", *[f"trabalho/{d}.txt" for d in DOCS]])
    if com_video:
        # --reusar-render: aproveita o MP4 já renderizado SÓ se ele for mais novo que tudo de que depende;
        # vídeo defasado aborta (mesma regra do PDF defasado por mtime)
        if "--reusar-render" in sys.argv:
            V = RAIZ / "video"
            for v in VIDEOS:
                mp4 = V / "trabalho" / v / f"{v}.mp4"
                deps = [V / "trabalho" / v / "timeline.json", V / "cena.html", V / "render.mjs", V / "roteiros.json",
                        RAIZ / "dados" / "padrao-tex.json", RAIZ / "trabalho" / "marcas.json",
                        RAIZ / "trabalho" / "svg" / "bloco.svg", RAIZ / "trabalho" / "svg" / "bloco-profinet.svg"]
                velha = [d.name for d in deps if not mp4.exists() or d.stat().st_mtime > mp4.stat().st_mtime]
                if velha:
                    print(f"\n✗ ABORTADO: {v}.mp4 é mais velho que {velha}. Rode sem --reusar-render.")
                    sys.exit(1)
            print("\n▶ Render reaproveitado: o MP4 é mais novo que roteiro, linha do tempo, cena, dados e marcas")
        else:
            etapa("Narração e linha do tempo", [PY_SIS, "video/preparar.py", *VIDEOS])
            for v in VIDEOS:
                etapa(f"Render {v}", ["node", "render.mjs", v], cwd=RAIZ / "video")
        etapa("Auditoria do vídeo", [PY_FW, "-X", "utf8", "video/auditar_video.py", *VIDEOS])
        etapa("Legendas SRT/VTT", [PY_FW, "video/legendas.py", *VIDEOS])

    # entrega: só chega aqui se tudo passou
    import json
    versao = json.loads((RAIZ / "dados" / "padrao-tex.json").read_text(encoding="utf-8"))["produto"]["versao_documento"]
    E = RAIZ / "entrega" / f"v{versao.split('.')[0]}"     # cada versão na sua pasta: a anterior nunca é sobrescrita
    E.mkdir(parents=True, exist_ok=True)
    for doc, (_, _, nome) in DOCS.items():
        shutil.copy2(RAIZ / "trabalho" / f"{doc}.pdf", E / f"{nome}_v{versao}.pdf")
    if com_video:
        for v, nome in VIDEOS.items():
            for ext in ("mp4", "srt", "vtt"):
                shutil.copy2(RAIZ / "video" / "trabalho" / v / f"{v}.{ext}", E / f"{nome}_v{versao}.{ext}")
    print(f"\n✓ APROVADO em tudo · entrega/ atualizada em {time.time() - t0:.0f} s")
    for f in sorted(E.iterdir()):
        print(f"   {f.stat().st_size / 1e6:6.1f} MB  {f.name}")


if __name__ == "__main__":
    main()
