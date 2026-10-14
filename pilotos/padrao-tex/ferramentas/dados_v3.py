"""Leva dados/padrao-tex.json para a v3 do pacote do cliente (28 blocos; pedido novo: 1 vídeo, 1 manual, 3 guias).

1. Reescreve TODO caminho de origem pelo mapa de conteúdo v2→v3 (trabalho/mapa_v2_v3.json): os blocos foram
   renumerados, mas os arquivos são byte a byte os mesmos.
2. Acrescenta o que é novo: biblioteca atual, DB Debug, blocos Basic, IHM, copiar para o projeto.
Cada item novo aponta a origem (áudio/tela/texto da v3)."""
import json, re
from pathlib import Path

R = Path(__file__).resolve().parent.parent
P = R / "dados" / "padrao-tex.json"
MAPA = json.loads((R / "trabalho" / "mapa_v2_v3.json").read_text(encoding="utf-8"))
txt = P.read_text(encoding="utf-8")
for velho, novo in sorted(MAPA.items(), key=lambda kv: -len(kv[0])):
    txt = txt.replace(velho, novo)
# origens que citam só a pasta do bloco (sem o arquivo): renumeração das pastas
PASTAS = {}
for velho, novo in MAPA.items():
    PASTAS[velho.split("/")[0]] = novo.split("/")[0]
for velho, novo in sorted(PASTAS.items(), key=lambda kv: -len(kv[0])):
    txt = re.sub(rf"(?<![\w-]){re.escape(velho)}(?![\w-])", novo, txt)
txt = txt.replace('"10-comando-de-como-iniciar-os-testes (campo Conteúdo)"', '"12-comando-de-como-iniciar-os-testes (campo Conteúdo)"')
txt = txt.replace('"14-rede-para-comunicar-profinet (campo Conteúdo)"', '"16-rede-para-comunicar-profinet (campo Conteúdo)"')
d = json.loads(txt)
A = lambda arq, t: {"audio": arq, "t": t}

d["produto"]["versao_documento"] = "3.0"
d["publico"]["consegue_no_fim"] = "Levar o Padrão TEX para o seu projeto, ligar um equipamento Tex G4 ao CLP por Modbus TCP ou Profinet, comandar o teste pelo CLP ou pela IHM e ler o resultado."
d["pedido_v3"] = {
    "texto": "Manual completo, bem estruturado, visualmente atraente, com imagens e textos bem colocados explicando o passo a passo. Vídeo profissional, claro, objetivo e rico, para os clientes do fornecedor do equipamento. Pode dividir um conteúdo em duas sessões.",
    "origem": A("01-o-pedido/audio-01.webm", "00:01")}

# --- biblioteca atual (tela 04): Profinet passou a FB1033/FB1034
NUM = {"G4_Profinet": 1033, "G4_Profinet_Basic": 1034}
for b in d["biblioteca"]:
    b["numero"] = NUM.get(b["nome"], b["numero"])
for b in d["blocos_g4"]:
    if b["nome"] in NUM:
        b["numero"] = f"FB{NUM[b['nome']]}"
d["biblioteca_origem"] = {"tela": "04-bibliotecas/foto-01_captura-de-tela-2026-10-02-162316.png"}
d["biblioteca_regra"] = {"texto": "Mantenha os blocos da pasta 9 - Library como vieram no Padrão TEX mais atual que você baixou.",
                         "origem": A("04-bibliotecas/audio-01.webm", "00:00")}

# --- blocos Basic (áudios 20 e 21, telas 20 e 21)
BASIC_FORA = ["UploadAllFromTex", "DownloadAllToTex", "UploadOne", "DownloadOne", "Chamber", "Test"]
for b in d["blocos_g4"]:
    if b["nome"] == "G4_ModbusTCP_Basic":
        b["descricao"] = "Igual ao G4_ModbusTCP, sem as 6 entradas de upload e download das peças. Faz os comandos básicos e tem todas as saídas, mas não lê nem altera os dados das peças."
        b["origem"] = A("20-bloco-modbustcp-basic/audio-01.webm", "00:02")
        b["tela"] = "20-bloco-modbustcp-basic/foto-01_captura-de-tela-2026-10-02-160836.png"
        b["retiradas"] = BASIC_FORA
    if b["nome"] == "G4_Profinet_Basic":
        b["descricao"] = "Igual ao G4_Profinet, sem as 6 entradas de upload e download das peças."
        b["origem"] = A("21-bloco-profinet-basic/audio-01.webm", "00:01")
        b["tela"] = "21-bloco-profinet-basic/foto-01_captura-de-tela-2026-10-02-161431.png"
        b["retiradas"] = BASIC_FORA

# --- DB Debug (áudio 06, tela 06)
d["debug"] = {
    "bloco": "Debug [DB2]", "estrutura": "Tex1",
    "campos": [{"nome": n, "tipo": t} for n, t in [
        ("Automatic", "Bool"), ("Start", "Bool"), ("Stop", "Bool"), ("BlockExhaust", "Bool"), ("NewBCD", "Int"),
        ("UploadAll", "Bool"), ("DownloadAll", "Bool"), ("DownloadOne", "Bool"), ("UploadOne", "Bool"),
        ("Chamber", "Int"), ("Test", "Int"), ("numTestes", "Int"), ("Camara", "Int"), ("Teste", "Int"), ("PecaDB", "Int"), ("Reset", "Bool")]],
    "explica": "O Debug [DB2] tem uma estrutura que simula as entradas do bloco, para testes. No seu projeto, troque essas variáveis pela lógica de acionamento da sua máquina, com cada comando no momento certo.",
    "origem": {"audio": "06-db-debug-para-testes/audio-01.webm", "t": "00:01", "tela": "06-db-debug-para-testes/foto-01_captura-de-tela-2026-10-02-161808.png"}}

# --- copiar o padrão para o projeto oficial (texto + áudio + 5 telas do bloco 28)
d["copiar"] = {
    "pastas": [
        {"onde": "Program blocks", "tela": "28-copiar-do-padrao-tex-para-o-projeto-oficial/foto-01_captura-de-tela-2026-10-02-160001.png"},
        {"onde": "PLC tags", "tela": "28-copiar-do-padrao-tex-para-o-projeto-oficial/foto-02_captura-de-tela-2026-10-02-160111.png"},
        {"onde": "PLC data types", "tela": "28-copiar-do-padrao-tex-para-o-projeto-oficial/foto-03_captura-de-tela-2026-10-02-160220.png"},
        {"onde": "Screens (na IHM)", "tela": "28-copiar-do-padrao-tex-para-o-projeto-oficial/foto-04_captura-de-tela-2026-10-02-160304.png"},
        {"onde": "HMI tags (na IHM)", "tela": "28-copiar-do-padrao-tex-para-o-projeto-oficial/foto-05_captura-de-tela-2026-10-02-160515.png"}],
    "origem": {"texto": "28-copiar-do-padrao-tex-para-o-projeto-oficial (campo Conteúdo)", "audio": "28-copiar-do-padrao-tex-para-o-projeto-oficial/audio-01.webm", "t": "00:00"}}

# --- IHM (texto do 23, áudios 22–27, telas 22–27)
d["ihm"] = {
    "resumo": "A IHM tem uma pasta TexG4 com as quatro telas principais. Uma tela só controla e monitora vários equipamentos: o HMI_Link dos blocos faz a indexação.",
    "resumo_origem": A("22-ihm-padrao-tex/audio-01.webm", "00:01"),
    "modelo": "KTP700 Basic PN",
    "telas_projeto": ["G4_Diagnostico", "G4_IOS", "G4_Operação", "G4_ParametrizacaoRemota"],
    "telas_origem": {"tela": "22-ihm-padrao-tex/foto-01_captura-de-tela-2026-10-02-162721.png"},
    "manual": "Para comandar e ler o G4 pela IHM, o bloco do G4 no CLP precisa estar em modo manual (Automatic em false).",
    "manual_origem": {"texto": "23-ihm-tela-do-equipamento (campo Conteúdo)"},
    "telas": [
        {"id": "operacao", "titulo": "Operação",
         "descricao": "Escolha um dos Tex listados na FB_Tex e comande: Start, Stop e bloqueio do escape. A tela mostra a pressão atual, o vazamento, o BCD, a câmara e o teste em andamento. As setas trocam o BCD.",
         "origem": {"audio": "23-ihm-tela-do-equipamento/audio-01.webm", "t": "00:00", "tela": "23-ihm-tela-do-equipamento/foto-01_captura-de-tela-2026-10-02-153634.png"}},
        {"id": "menu", "titulo": "Menu",
         "descricao": "O botão MENU abre três botões: IOS, DIAGNÓSTICOS e PARAMETRIZAÇÃO REMOTA.",
         "origem": {"audio": "24-ihm-menu/audio-01.webm", "t": "00:00", "tela": "24-ihm-menu/foto-01_captura-de-tela-2026-10-02-154557.png"}},
        {"id": "ios", "titulo": "Entradas e saídas",
         "descricao": "Mostra o estado de cada entrada e saída do equipamento naquele momento, com a função de cada uma.",
         "entradas": ["BCD 0", "BCD 1", "PARADA", "INÍCIO", "BCD 2 / SENSOR DE REFUGO", "BCD 3 / PEÇA ANTERIOR", "BCD 4 / PRÓXIMA PEÇA", "BLOQUEIA ESCAPE"],
         "saidas": ["DIGITAL 1", "APROVA", "REPROVA TESTE", "DIGITAL 2 / REPROVA REF.", "DIGITAL 3 / FALHA", "RETRABALHO", "ESCAPE EXTERNO", "BUSY"],
         "origem": {"audio": "25-ihm-tela-ios/audio-01.webm", "t": "00:01", "tela": "25-ihm-tela-ios/foto-01_captura-de-tela-2026-10-02-154647.png"}},
        {"id": "diagnostico", "titulo": "Diagnósticos",
         "descricao": "Mostra cada sinal do autoteste (válvulas, sensor diferencial ou de fluxo, sensor de pressão de teste) e quais saídas estão com problema.",
         "origem": {"audio": "26-ihm/audio-01.webm", "t": "00:00", "tela": "26-ihm/foto-01_captura-de-tela-2026-10-02-154844.png"}},
        {"id": "parametrizacao", "titulo": "Parametrização",
         "descricao": "Acessa os dados guardados no equipamento. Escolha o BCD, a câmara e o teste. UPLOAD CONFIG ATUAL traz os dados daquela peça; DOWNLOAD CONFIG ATUAL envia o que você alterou. Dá para ajustar pressões, vazões, tempos, tipo de teste, unidades, volumes, material e retrabalho.",
         "origem": {"audio": "27-ihm-parametrizacao-remota/audio-01.webm", "t": "00:00", "tela": "27-ihm-parametrizacao-remota/foto-01_captura-de-tela-2026-10-02-155107.png"}}],
}

# --- procedimentos novos
d["procedimentos"] = [p for p in d["procedimentos"] if p["id"] not in ("copiar", "ihm")] + [
    {"id": "copiar", "titulo": "Levar o Padrão TEX para o seu projeto",
     "condicao": "Os dois projetos estão abertos no TIA Portal: o Padrão TEX e o projeto da sua máquina.",
     "passos": [f"Copie a pasta TexG4 de {p['onde']} para o mesmo lugar no seu projeto." for p in d["copiar"]["pastas"]],
     "resultado": "Os blocos, as tags, os tipos de dado e as telas do Padrão TEX estão no seu projeto. Falta chamar a FB_Tex no Main.",
     "origem": d["copiar"]["origem"]},
    {"id": "ihm", "titulo": "Comandar um teste pela IHM",
     "condicao": "O bloco do G4 no CLP está em modo manual (Automatic em false).",
     "passos": [
         "Na tela OPERAÇÃO, escolha o equipamento na lista do canto (por exemplo, TEX 1).",
         "Use as setas para escolher o BCD da peça.",
         "Toque em START para iniciar o teste. STOP para o teste.",
         "Acompanhe a pressão atual e o vazamento na própria tela."],
     "resultado": "O teste roda com os parâmetros da peça escolhida, comandado pela IHM.",
     "origem": {"texto": "23-ihm-tela-do-equipamento (campo Conteúdo)", "audio": "23-ihm-tela-do-equipamento/audio-01.webm", "t": "00:00",
                "tela": "23-ihm-tela-do-equipamento/foto-01_captura-de-tela-2026-10-02-153634.png"}}]

# --- avisos
d["avisos"] = [a for a in d["avisos"] if "IHM precisa" not in a["texto"]] + [
    {"nivel": "AVISO", "texto": "Para comandar o Tex pela IHM, o bloco do G4 no CLP precisa estar em modo manual. Em automático, a IHM só mostra as leituras.",
     "origem": {"texto": "23-ihm-tela-do-equipamento (campo Conteúdo)", "audio": "09-entradas-de-comando/audio-01.webm", "t": "00:45"}}]
d["avisos"][0]["texto"] = "Não altere os blocos da pasta 9 - Library. Mantenha-os como vieram no Padrão TEX mais atual que você baixou."
d["avisos"][0]["origem"] = A("04-bibliotecas/audio-01.webm", "00:00")

# --- glossário
d["glossario"] = [g for g in d["glossario"] if g["termo"] != "DB Debug"] + [
    {"termo": "DB Debug", "definicao": "Bloco de dados do Padrão TEX que simula as entradas dos blocos para testes.", "origem": A("06-db-debug-para-testes/audio-01.webm", "00:01")}]

# --- pendências
resolvidas = {"fb-profinet", "importar", "biblioteca-12"}
d["pendencias"] = [p for p in d["pendencias"] if p["id"] not in resolvidas] + [
    {"id": "tia-versao", "pergunta": "Em qual versão do TIA Portal o Padrão TEX foi feito? O integrador precisa da mesma ou mais nova para abrir.", "afeta": ["requisitos"]},
    {"id": "fb-antigo", "pergunta": "Telas antigas mostravam G4_Profinet como FB1020 e a biblioteca atual mostra FB1033. Quem tem o padrão antigo precisa atualizar?", "afeta": ["biblioteca"]}]
for p in d["pendencias"]:
    if p["id"] == "unidades":
        p["pergunta"] = "A IHM mostra pressão em Pa, vazamento em mL/min e tempo em ms. As saídas Pressure, Leak e TimeElapsed vêm sempre nessas unidades ou na unidade configurada na peça?"
d["requisitos"]["itens"] = [r for r in d["requisitos"]["itens"] if "importado" not in r] + [
    "O projeto do Padrão TEX, para copiar as pastas TexG4 para o seu projeto.", "Para usar a IHM do padrão: uma IHM Siemens (o exemplo usa KTP700 Basic PN)."]

P.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
sobra = [m for m in re.findall(r'"(\d\d-[a-z0-9-]+/[^"]+)"', json.dumps(d, ensure_ascii=False))
         if not (R / "fonte" / "padrao-tex_2026-10-02" / m.split(" ")[0]).exists()]
print("dados v3 ·", len(d["pendencias"]), "pendências · caminhos sem arquivo:", sobra)
