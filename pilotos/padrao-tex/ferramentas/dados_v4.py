"""Leva dados/padrao-tex.json para o pacote final do cliente (zip 3, 30 blocos) e às regras do WhatsApp de 02/10:
"Não usar nada da Celiware" (16:06) e "Busque logo da Tex... tudo do site deles pode usar... fazer uma explicação
do equipamento antes" (16:43).

1. Reescreve TODO caminho de origem pelo mapa de conteúdo v3→v4 (trabalho/mapa_v3_v4.json): blocos renumerados,
   arquivos byte a byte os mesmos. Faz o mesmo nos scripts que citam telas pelo caminho (marcas.py, auditar_docs.py).
2. Acrescenta o que é novo: bloco 07 (DB Tex), bloco 23 (usar dados dos G4 no programa) e o equipamento,
   tirado do site da Tex (origem "site" = página coletada em marca/tex/site/).
Roda uma vez."""
import json, re
from pathlib import Path

R = Path(__file__).resolve().parent.parent
P = R / "dados" / "padrao-tex.json"
MAPA = json.loads((R / "trabalho" / "mapa_v3_v4.json").read_text(encoding="utf-8"))
PASTAS = {}
for velho, novo in MAPA.items():
    if "/" in velho:
        PASTAS[velho.split("/")[0]] = novo.split("/")[0]

# os caminhos de arquivo já trocados contêm a pasta nova; a troca de pasta solta só pega o que sobrou.
# Para não trocar duas vezes, a 1ª etapa já leva a pasta: então aplicamos só a 2ª etapa num texto em que os
# caminhos completos foram protegidos.
if '"equipamento"' in P.read_text(encoding="utf-8"):
    # a renumeração é em cadeia (07→08, 08→09...): rodar duas vezes deslocaria tudo de novo
    raise SystemExit("dados já estão na v4: não rode de novo (o original da v3 está em trabalho/padrao-tex_v3.json)")

def remapeia_seguro(txt):
    marcas = {}
    def protege(m):
        k = f"\x00{len(marcas)}\x00"; marcas[k] = MAPA[m.group(0)]; return k
    alt = "|".join(re.escape(v) for v in sorted((k for k in MAPA if "/" in k), key=len, reverse=True))
    txt = re.sub(alt, protege, txt)
    alt2 = "|".join(re.escape(v) for v in sorted(PASTAS, key=len, reverse=True))
    txt = re.sub(rf"(?<![\w-])({alt2})(?![\w-])", lambda m: PASTAS[m.group(1)], txt)
    for k, v in marcas.items():
        txt = txt.replace(k, v)
    return txt

for arq in (P, R / "ferramentas" / "marcas.py", R / "ferramentas" / "auditar_docs.py"):
    arq.write_text(remapeia_seguro(arq.read_text(encoding="utf-8")), encoding="utf-8")

d = json.loads(P.read_text(encoding="utf-8"))
A = lambda arq, t: {"audio": arq, "t": t}
SITE = lambda pag: {"site": f"https://tex.com.br/{pag}", "coleta": f"marca/tex/site/{pag.strip('/').replace('/', '_') or 'home'}.txt"}

d["produto"]["fabricante"] = "Tex Equipamentos Eletrônicos"
d["produto"]["fabricante_origem"] = SITE("empresa/")
d["regra_marca"] = {"texto": "O material usa só a identidade da Tex: a marca, as informações e as imagens do site tex.com.br.",
                    "origem": {"texto": "WhatsApp do cliente, 02/10/2026 16:06 e 16:43"}}

# --- introdução (bloco 02, áudio)
d["introducao"] = {"texto": "Neste material você aprende a configurar, no TIA Portal, os blocos que comunicam o CLP com o equipamento Tex G4.",
                   "origem": A("02-introducao/audio-01.webm", "00:01")}

# --- o equipamento (site da Tex, coletado em 02/10/2026)
d["equipamento"] = {
    "empresa": {
        "nome": "Tex Equipamentos Eletrônicos",
        "texto": "A Tex fabrica equipamentos eletrônicos de medição e de teste de vazamento. Foi fundada em 1997, em São Paulo, e hoje fica em Itupeva (SP).",
        "marcos": [
            {"ano": "1997", "texto": "Fundação, em São Paulo, com os primeiros equipamentos eletrônicos de teste de estanqueidade."},
            {"ano": "2008", "texto": "Mudança para Itupeva, na região de Jundiaí."},
            {"ano": "2009", "texto": "Parceria com a COSMO Instruments, do Japão."},
            {"ano": "2015", "texto": "Lançamento da 4ª geração de equipamentos: a linha G4."}],
        "origem": SITE("")},
    "o_que_faz": {
        "texto": "No G4-SE, por exemplo, o equipamento pressuriza a peça, espera a pressão estabilizar e mede a variação durante um tempo. Depois compara a medida com os limites configurados e aprova ou reprova a peça sozinho.",
        "resultado": "O resultado aparece na tela do equipamento e nas saídas digitais. Pela rede, o CLP lê o mesmo resultado.",
        "origem": SITE("produtos/teste-de-estanqueidade-tex-g4-se/")},
    "linha_g4": {
        "texto": "A linha G4 tem vários modelos, um para cada tipo de teste.",
        "modelos": [
            {"sigla": "G4-SE", "nome": "Teste de estanqueidade", "como": "mede a queda de pressão na peça", "origem": SITE("produtos/teste-de-estanqueidade-tex-g4-se/")},
            {"sigla": "G4-DF", "nome": "Diferencial de pressão", "como": "compara a pressão da peça com a de uma referência", "origem": SITE("produtos/diferencial-de-pressao-tex-g4-df/")},
            {"sigla": "G4-HD", "nome": "Micro diferencial de pressão", "como": "mede vazamentos muito pequenos", "origem": SITE("produtos/micro-diferencial-de-pressao-tex-g4-hd/")},
            {"sigla": "G4-VZ", "nome": "Teste de vazão volumétrica", "como": "mede a vazão que passa pela peça", "origem": SITE("produtos/teste-de-vazao-volumetrica-tex-g4-vz/")}],
        "origem": SITE("categoria-produtos/")},
    "recursos": {
        "itens": [
            "Tela colorida de 5 polegadas, sensível ao toque.",
            "Comunicação Ethernet: Modbus TCP, Profinet ou EtherNet/IP, conforme o modelo.",
            "Cadastro de até 1000 peças, com até 16 receitas cada.",
            "Porta USB para pendrive: resultados, backup e atualização.",
            "Calibração acreditada, com certificado no próprio equipamento."],
        "nota": "Os recursos dependem do modelo.",
        "origem": SITE("produtos/teste-de-estanqueidade-tex-g4-se/")},
    "fotos": {
        "frente": {"arquivo": "marca/tex/original/envato-labs-image-edit-2025-10-21T093129.441.png", "legenda": "Tex G4-SE: a tela de toque fica na frente do equipamento.", "origem": SITE("produtos/teste-de-estanqueidade-tex-g4-se/")},
        "perspectiva": {"arquivo": "marca/tex/original/envato-labs-image-edit-2025-10-21T093718.876.png", "legenda": "Tex G4-SE.", "origem": SITE("produtos/teste-de-estanqueidade-tex-g4-se/")},
        "traseira": {"arquivo": "marca/tex/original/envato-labs-image-edit-2025-10-21T093848.836.png", "legenda": "Traseira do Tex G4: a porta Ethernet, no canto superior direito, liga o equipamento à rede do CLP.", "origem": SITE("produtos/teste-de-estanqueidade-tex-g4-se/")},
        "df": {"arquivo": "marca/tex/original/envato-labs-image-edit-2025-10-16T153941.209.png", "legenda": "Tex G4-DF.", "origem": SITE("produtos/diferencial-de-pressao-tex-g4-df/")},
        "vz": {"arquivo": "marca/tex/original/envato-labs-image-edit-2025-10-21T100729.975.png", "legenda": "Tex G4-VZ.", "origem": SITE("produtos/teste-de-vazao-volumetrica-tex-g4-vz/")},
        "hd": {"arquivo": "marca/tex/original/envato-labs-image-edit-2025-10-21T091239.439.png", "legenda": "Tex G4-HD.", "origem": SITE("produtos/micro-diferencial-de-pressao-tex-g4-hd/")}},
    "papel_do_padrao": {
        "texto": "O Padrão TEX é um projeto de TIA Portal com os blocos que comunicam o CLP Siemens com um ou mais equipamentos G4. Com ele, o CLP comanda o teste e lê o resultado pela rede.",
        "origem": A("02-introducao/audio-01.webm", "00:01")},
}

# --- DB Tex (bloco 07: áudio + tela)
d["db_tex"] = {
    "bloco": "Tex [DB1]",
    "caminho": "Program blocks > TexG4 > 1 - Controle Equipamentos > Tex [DB1]",
    "campos": [
        {"nome": "HMI_Link", "tipo": "UDT_TexHMILink", "papel": "Liga a IHM aos equipamentos. Faz a indexação: uma tela só conversa com vários equipamentos. Não altere."},
        {"nome": "Equipamento1", "tipo": "G4_ModbusTCP", "papel": "Ligado por Modbus TCP."},
        {"nome": "Equipamento2", "tipo": "G4_Profinet", "papel": "Ligado por Profinet."},
        {"nome": "Equipamento3", "tipo": "G4_ModbusTCP_Basic", "papel": "Ligado por Modbus TCP, sem os dados das peças."},
        {"nome": "Equipamento4", "tipo": "G4_Profinet_Basic", "papel": "Ligado por Profinet, sem os dados das peças."}],
    "explica": "O Tex [DB1] guarda tudo o que a FB_Tex usa: o HMI_Link e um elemento para cada equipamento. No exemplo são quatro, um de cada bloco.",
    "acesso": "Por esses elementos você acessa as entradas, as saídas e as outras propriedades de cada equipamento.",
    "origem": {**A("07-db-tex/audio-01.webm", "00:01"), "tela": "07-db-tex/foto-01_captura-de-tela-2026-10-02-163853.png"},
    "acesso_origem": A("07-db-tex/audio-01.webm", "00:47"),
}

# --- usar os dados no programa (bloco 23: áudio + tela)
d["usar_dados"] = {
    "explica": "Você pode usar as entradas e as saídas dos blocos em qualquer lógica do seu programa: para monitorar, seguir uma sequência ou mostrar o resultado ao operador.",
    "como": "Chame pelo DB, pelo equipamento e pela propriedade.",
    "exemplo": {"endereco": "\"Tex\".Equipamento4.ResultOK", "bloco": "Maquina [FB1]", "network": "Usar dados dos equipamentos nas lógicas",
                "bobina": "#FinalizarSequencia",
                "texto": "No exemplo, quando o Equipamento4 aprova a peça (ResultOK em true), a máquina finaliza a sequência."},
    "todas": "Todas as entradas e todas as saídas podem ser usadas assim.",
    "origem": {**A("23-usar-dados-dos-g4-no-programa/audio-01.webm", "00:01"), "tela": "23-usar-dados-dos-g4-no-programa/foto-01_captura-de-tela-2026-10-02-163500.png"},
    "todas_origem": A("23-usar-dados-dos-g4-no-programa/audio-01.webm", "00:38"),
}

# a estrutura cita o Tex [DB1] junto com a FB_Tex: agora ele tem seção própria
for e in d["estrutura"]:
    if e["item"] == "1 - Controle Equipamentos":
        e["papel"] = "FB_Tex [FB10] chama o bloco de cada equipamento; Tex [DB1] guarda os dados de todos eles. Uma FB_Tex pode ter um ou mais equipamentos."

d["glossario"].append({"termo": "UDT", "definicao": "Tipo de dado criado pelo usuário no TIA Portal (PLC data type). O HMI_Link é do tipo UDT_TexHMILink.", "origem": {"geral": True, "tela": "07-db-tex/foto-01_captura-de-tela-2026-10-02-163853.png"}})
d["glossario"].append({"termo": "Teste de vazamento a seco", "definicao": "Teste de estanqueidade feito com ar, sem mergulhar a peça em água.", "origem": SITE("")})

# pendência nova: o site lista os modelos; falta saber quais o Padrão TEX atende
for p in d["pendencias"]:
    if p["id"] == "modelos-g4":
        p["pergunta"] = "O site da Tex lista G4-SE, G4-DF, G4-HD, G4-VZ, G4-VE, G4-CB, G4-EC, G4-SH e G4-GV. O Padrão TEX atende todos? E quais duas letras vão na entrada Modelo de cada um?"

# fotos do site em JPEG (qualidade 90, tamanho original): o PNG de 900 KB por foto inchava o PDF e o vídeo
from PIL import Image
(R / "marca" / "tex" / "fotos").mkdir(parents=True, exist_ok=True)
for k, f in d["equipamento"]["fotos"].items():
    src = R / f.get("original", f["arquivo"]); dst = R / "marca" / "tex" / "fotos" / f"g4-{k}.jpg"
    im = Image.open(src); im.convert("RGB").save(dst, quality=90, optimize=True)
    f["original"] = src.relative_to(R).as_posix(); f["arquivo"] = dst.relative_to(R).as_posix(); f["largura"], f["altura"] = im.size

d["produto"]["versao_documento"] = "3.0"
P.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("dados v4:", len(d["pendencias"]), "pendências; equipamento, db_tex e usar_dados acrescentados")
