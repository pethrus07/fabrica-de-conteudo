"""Gera as marcas numeradas sobre as capturas de tela a partir do OCR (trabalho/ocr/*.json).

A posição de cada marca é a caixa do RÓTULO LIDO NA TELA — não é coordenada digitada à mão.
Se um rótulo não for encontrado, o script para com erro: marca no lugar errado é pior que
marca nenhuma. Saída: trabalho/marcas.json, em porcentagem da imagem (o manual e o vídeo
posicionam por proporção, em qualquer tamanho).
"""
import json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
OCR = RAIZ / "trabalho" / "ocr"

def norm(s):
    s = s.lower().replace("0", "o").replace("ç", "c").replace("ã", "a").replace("ä", "a")
    return re.sub(r"[^a-z0-9]", "", s)

# figura → (arquivo da captura, legenda, [(número, texto a achar, legenda da marca, filtro x mín/máx em px)], recorte)
# recorte = (x0, y0, x1, y1) em px da captura, ou None. ATENÇÃO: o filtro de x de cada marca é em coordenadas do RECORTE.
# Recortar no que importa aumenta as letras no PDF e no vídeo.
FIGURAS = {
    "arvore": ("03-elementos-do-padrao-tex/foto-01_arvoredoprojeto.png",
               "Árvore do projeto com o Padrão TEX.", [
        (1, "TexG4", "Pasta do Padrão TEX", None),
        (2, "Controle Equipamentos", "FB_Tex e DB Tex: chamam os equipamentos", None),
        (3, "Banco de dados pecas", "DB_Parts: dados das peças", None),
        (4, "Library", "Biblioteca pronta: não altere", None)], (0, 0, 405, 428)),   # corta a lista antiga (FB1020/FB1021)
    "main": ("05-bloco-main/foto-01_main.png",
             "O bloco Main chama a FB_Tex.", [
        (1, "Main [OB1]", "Bloco Main [OB1]", (0, 300)),
        (2, "%FB10", "Chamada da FB_Tex, com a DB Tex", (400, 700))], (0, 95, 860, 425)),
    "fbvazia": ("08-montando-a-fb-tex-com-os-equipamentos/foto-01_fb-texvazia.png",
                "A FB_Tex aberta, com as networks vazias.", [
        (1, "FB_Tex[FB10]", "FB_Tex [FB10] na árvore", (0, 300)),
        (2, "Network 1:", "Primeira network vazia", (400, 700))], (0, 95, 1040, 420)),
    "adicionando": ("08-montando-a-fb-tex-com-os-equipamentos/foto-02_adicionandomodbustcp.png",
                    "O bloco G4_ModbusTCP colocado na network 1.", [
        (1, "G4_ModbusTCP [FB1030]", "G4_ModbusTCP na pasta 9 - Library", (0, 330)),
        (2, '"G4_ModbusTCP"', "O bloco na network, pronto para preencher", (500, 800))], (0, 95, 1061, 727)),
    "monitorado": ("13-comando-de-como-iniciar-os-testes/foto-01_captura-de-tela-2026-10-02-072653.png",
                   "O bloco monitorado logo depois do Start: o equipamento está testando a peça 1.", [
        (1, "Automatic", "Automatic = TRUE", (150, 260)),
        (2, "Start", "Start = TRUE", (150, 260)),
        (3, "Busy", "Busy = TRUE: testando", (300, 380)),
        (4, "ActualBCD", "ActualBCD = 1: peça 1", (280, 380))], None),
    # --- v2: Profinet e banco de peças
    "rede": ("17-rede-para-comunicar-profinet/foto-01_captura-de-tela-2026-10-02-142228.png",
             "A rede Profinet do padrão: CLP, TEX-G4 e IHM na mesma sub-rede.", [
        (1, "PLC_Tex", "CLP: PLC_Tex, CPU 1211C", (0, 150)),
        (2, "TEX-G4", "TEX-G4, com o gateway Profinet", (390, 490)),
        (3, "HMI", "IHM: KTP700 Basic PN", (0, 150)),
        (4, "PN/IE_1", "Sub-rede PN/IE_1", None)], (150, 110, 900, 520)),
    "gsd": ("18-configurando-o-gsd/foto-01_captura-de-tela-2026-10-02-142745.png",
            "O TEX-G4 configurado pelo GSD: módulo de 256 bytes e IP do gateway.", [
        (1, "RSW:3 Input:256Bytes Output:256Bytes", "Módulo: 256 bytes de entrada e de saída", (500, 800)),
        (2, "300...555", "Entradas e saídas a partir do endereço 300", (850, 930)),
        (3, ".208", "IP do gateway: 192.168.0.208", None)], None),
    "tags": ("19-plc-tags/foto-01_captura-de-tela-2026-10-02-143446.png",
             "As tags do Profinet nas PLC tags do CLP.", [
        (1, "IN_TexB", "IN_TexB em %I308.0", None),
        (2, "OUT_TexB", "OUT_TexB em %Q308.0", None)], None),
    "pnbloco": ("20-bloco-profinet/foto-02_captura-de-tela-2026-10-02-152438.png",
                "As duas entradas do mapa Profinet no bloco G4_Profinet.", [
        (1, "PN_IN", "PN_IN ligada em IN_TexB", (110, 200)),
        (2, "pn_OuT", "PN_OUT ligada em OUT_TexB", (110, 200))], None),
    "dbparts": ("15-banco-de-dados-das-pecas/foto-02_captura-de-tela-2026-10-02-133320.png",
                "O DB_Parts depois do upload da peça 1: os valores vieram do equipamento.", [
        (1, "BCD", "BCD = 1", (100, 160)),
        (2, "NumChamber", "NumChamber = 3", (100, 220)),
        (3, "NumTest", "NumTest = 3", (140, 230)),
        (4, "PressureMax", "PressureMax = 1.5", (180, 280))], (0, 80, 846, 739)),
    # --- v3: biblioteca atual, debug, blocos Basic, IHM e cópia para o projeto
    "biblioteca": ("04-bibliotecas/foto-01_captura-de-tela-2026-10-02-162316.png",
                   "A pasta 9 - Library do Padrão TEX atual, com os 4 blocos G4.", [
        (1, "G4_ModbusTCP [FB1030]", "G4_ModbusTCP · FB1030", None),
        (2, "G4_ModbusTCP_Basic", "G4_ModbusTCP_Basic · FB1031", None),
        (3, "G4_Profinet[FB1033]", "G4_Profinet · FB1033", None),
        (4, "G4_Profinet Basic", "G4_Profinet_Basic · FB1034", None)], None),
    "debug": ("06-db-debug-para-testes/foto-01_captura-de-tela-2026-10-02-161808.png",
              "O Debug [DB2]: as variáveis que simulam as entradas do bloco nos testes.", [
        (1, "Tex1", "Estrutura Tex1: uma por equipamento de teste", (60, 140)),
        (2, "NewBCD", "Ex.: NewBCD simula a entrada BCD", (90, 200))], (0, 80, 771, 485)),
    "basicmb": ("21-bloco-modbustcp-basic/foto-01_captura-de-tela-2026-10-02-160836.png",
                "O G4_ModbusTCP_Basic: sem as 6 entradas de upload e download das peças.", [
        (1, '"G4_ModbusTCP_Basic"', "G4_ModbusTCP_Basic · FB1031", None),
        (2, "Reset", "Depois de Reset vêm direto Part e HMI_Link", (140, 220))], None),
    "basicpn": ("22-bloco-profinet-basic/foto-01_captura-de-tela-2026-10-02-161431.png",
                "O G4_Profinet_Basic: Profinet, sem as 6 entradas de upload e download.", [
        (1, '"G4_Profinet_Basic"', "G4_Profinet_Basic · FB1034", None),
        (2, "Reset", "Depois de Reset vêm Part, HMI_Link, PN_IN e PN_OUT", (140, 220))], None),
    "ihmtelas": ("24-ihm-padrao-tex/foto-01_captura-de-tela-2026-10-02-162721.png",
                 "As quatro telas do Padrão TEX na IHM, na pasta TexG4.", [
        (1, "TexG4", "Pasta TexG4 em Screens", None)], None),
    "operacao": ("25-ihm-tela-do-equipamento/foto-01_captura-de-tela-2026-10-02-153634.png",
                 "A tela OPERAÇÃO da IHM.", [
        (1, "TEX 1", "Escolha do equipamento", None),
        (2, "BCD", "BCD, câmara e teste (setas trocam o BCD)", (180, 260)),
        (3, "START", "START e STOP", None),
        (4, "BLOQUEIA", "Bloqueia o escape", None),
        (5, "PRESSAO ATUAL", "Pressão atual", None),
        (6, "VAZAMENTO", "Vazamento", None),
        (7, "MENU", "MENU: IOs, diagnósticos e parametrização", None)], None),
    "menu": ("26-ihm-menu/foto-01_captura-de-tela-2026-10-02-154557.png",
             "O MENU da IHM.", [
        (1, "SOI", "IOS: entradas e saídas", None),          # o OCR lê "IOS" como "SOI"; a posição é a do botão
        (2, "DIAGNOSTICOS", "DIAGNÓSTICOS", None),
        (3, "PARAMETRIZACAO", "PARAMETRIZAÇÃO REMOTA", None)], None),
    "ios": ("27-ihm-tela-ios/foto-01_captura-de-tela-2026-10-02-154647.png",
            "A tela ENTRADAS E SAÍDAS da IHM.", [
        (1, "ENTRADAS", "As 8 entradas do equipamento", (150, 300)),
        (2, "SAIDAS", "As 8 saídas do equipamento", (520, 640))], None),
    "diag": ("28-ihm/foto-01_captura-de-tela-2026-10-02-154844.png",
             "A tela DIAGNÓSTICOS da IHM.", [
        (1, "AUTO CHECK", "Autoteste: válvulas e sensores", None),
        (2, "DIAGNOSTICO", "Saídas com problema", (480, 660))], None),
    "param": ("29-ihm-parametrizacao-remota/foto-01_captura-de-tela-2026-10-02-155107.png",
              "A tela PARAMETRIZAÇÃO da IHM.", [
        (1, "BCD", "Escolha o BCD", (60, 140)),
        (2, "CAM", "Escolha a câmara", (60, 140)),
        (3, "TESTE", "Escolha o teste", (320, 410)),
        (4, "DOWNLOAD", "DOWNLOAD CONFIG ATUAL: envia ao equipamento", None),
        (5, "UPLOAD", "UPLOAD CONFIG ATUAL: traz do equipamento", (150, 220)),
        (6, "REWORK", "REWORK: retrabalho da peça", (660, 780))], None),
    # --- pacote final (zip 3): DB Tex e uso dos dados no programa
    "dbtex": ("07-db-tex/foto-01_captura-de-tela-2026-10-02-163853.png",
              "O Tex [DB1]: o HMI_Link e um elemento para cada equipamento.", [
        (1, "HMI_Link", "HMI_Link: liga a IHM aos equipamentos. Não altere", (60, 150)),
        (2, "Equipamento1", "Equipamento1 a Equipamento4: um por equipamento", (60, 180)),
        (3, '"G4_ModbusTCP"', "O tipo é o bloco do equipamento", (200, 330))], (0, 0, 848, 300)),
    "usar": ("23-usar-dados-dos-g4-no-programa/foto-01_captura-de-tela-2026-10-02-163500.png",
             "Uma saída do equipamento usada na lógica da máquina, no bloco Maquina [FB1].", [
        (1, "Equipamento4.", '"Tex".Equipamento4.ResultOK: a peça foi aprovada', (0, 200)),
        (2, "#FinalizarSequen", "A sua lógica: finaliza a sequência", (400, 667))], (0, 190, 667, 330)),
}

def main():
    out = {}
    from PIL import Image
    pacote = next((RAIZ / "fonte").glob("padrao-tex_*"))
    rec_dir = RAIZ / "trabalho" / "recortes"; rec_dir.mkdir(exist_ok=True)
    for fid, (arq, legenda, marcas, recorte) in FIGURAS.items():
        d = json.loads((OCR / (arq.replace("/", "__") + ".json")).read_text(encoding="utf-8"))
        cx, cy = (recorte[0], recorte[1]) if recorte else (0, 0)
        im = Image.open(pacote / arq)
        if recorte:
            im = im.crop(recorte)
        W, H = im.size
        im.save(rec_dir / f"{fid}.png")
        for i in d["itens"]:
            i["caixa"] = [i["caixa"][0] - cx, i["caixa"][1] - cy, i["caixa"][2] - cx, i["caixa"][3] - cy]
        lista = []
        for n, alvo, leg, faixa in marcas:
            cand = [i for i in d["itens"] if norm(alvo) in norm(i["texto"])
                    and (faixa is None or faixa[0] <= i["caixa"][0] <= faixa[1])]
            if not cand:
                sys.exit(f"ERRO: '{alvo}' não foi lido em {arq} — marca cancelada")
            # o candidato mais justo (menos texto sobrando) é o rótulo, não uma frase que o contém
            c = min(cand, key=lambda i: len(norm(i["texto"])) - len(norm(alvo)))
            x0, y0, x1, y1 = c["caixa"]
            pad = 3
            lista.append({"n": n, "lido": c["texto"], "legenda": leg,
                          "x0": round(100 * (x0 - pad) / W, 2), "y0": round(100 * (y0 - pad) / H, 2),
                          "x1": round(100 * (x1 + pad) / W, 2), "y1": round(100 * (y1 + pad) / H, 2)})
        for m in lista:
            assert 0 <= m["x0"] and m["x1"] <= 100 and 0 <= m["y0"] and m["y1"] <= 100, f"marca {m['n']} de {fid} ficou fora do recorte"
        out[fid] = {"arquivo": f"recortes/{fid}.png", "original": arq, "recorte": recorte, "largura": W, "altura": H, "legenda": legenda, "marcas": lista}
        print(f"{fid}: {len(lista)} marcas — " + ", ".join(f"{m['n']}={m['lido']}" for m in lista))
    # só grava se mudou: o build compara datas (vídeo mais velho que as marcas = defasado)
    alvo, novo = RAIZ / "trabalho" / "marcas.json", json.dumps(out, ensure_ascii=False, indent=1)
    if not alvo.exists() or alvo.read_text(encoding="utf-8") != novo:
        alvo.write_text(novo, encoding="utf-8")

if __name__ == "__main__":
    main()
