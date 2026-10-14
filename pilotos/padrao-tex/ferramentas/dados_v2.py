"""Aplica ao dados/padrao-tex.json o que a 2ª versão do pacote do cliente trouxe (blocos 11 a 17).
Roda uma vez; deixa registrado o que mudou da v1 para a v2. Cada item novo aponta a origem."""
import json
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "dados" / "padrao-tex.json"
d = json.loads(P.read_text(encoding="utf-8"))
A = lambda arq, t: {"audio": arq, "t": t}

d["produto"]["versao_documento"] = "2.0"
d["produto"]["subtitulo"] = "Comunicação entre CLP Siemens e equipamentos Tex G4 de teste de estanqueidade, por Modbus TCP ou Profinet"

# --- Retrabalho → Rework: as telas das 07:26 e das 15:23 já mostram Rework (a das 07:00 mostrava Retrabalho)
for s in d["saidas"]:
    if s["nome"] == "Retrabalho":
        s["nome"] = "Rework"
        s["nome_antigo"] = "Retrabalho"
        s["descricao"] = "Fica true quando a peça está marcada como retrabalho."
        s["origem"]["tela"] = "17-bloco-profinet/foto-01_captura-de-tela-2026-10-02-152306.png"

# --- os 4 blocos G4 (áudio 13 + tela 13)
d["blocos_g4"] = [
    {"nome": "G4_ModbusTCP", "numero": "FB1030", "protocolo": "Modbus TCP", "pecas": True,
     "descricao": "O completo: comandos, leituras e upload e download dos dados das peças.", "origem": A("13-blocos-de-comunicacao-g4/audio-01.webm", "00:04")},
    {"nome": "G4_ModbusTCP_Basic", "numero": "FB1031", "protocolo": "Modbus TCP", "pecas": False,
     "descricao": "Só o básico do teste: Start, Stop, escolher a peça e ler a pressão e o vazamento. Não faz upload nem download das peças.", "origem": A("13-blocos-de-comunicacao-g4/audio-01.webm", "00:10")},
    {"nome": "G4_Profinet", "numero": "FB1020", "protocolo": "Profinet", "pecas": True,
     "descricao": "Completo como o G4_ModbusTCP, mas falando Profinet.", "origem": A("13-blocos-de-comunicacao-g4/audio-01.webm", "00:37")},
    {"nome": "G4_Profinet_Basic", "numero": "FB1021", "protocolo": "Profinet", "pecas": False,
     "descricao": "O G4_Profinet sem a comunicação com os parâmetros do equipamento.", "origem": A("13-blocos-de-comunicacao-g4/audio-01.webm", "01:02")},
]
d["blocos_g4_origem"] = {"tela": "13-blocos-de-comunicacao-g4/foto-01_captura-de-tela-2026-10-02-131213.png"}

# --- Profinet (texto do bloco 14, áudios 15–17, telas 14–17)
d["profinet"] = {
    "resumo": "Para comunicar por Profinet, inclua o GSD do Tex no TIA Portal e coloque o equipamento na rede junto com o CLP. No padrão, a IHM também está na rede.",
    "resumo_origem": {"texto": "14-rede-para-comunicar-profinet (campo Conteúdo)"},
    "rede": {"subrede": "PN/IE_1", "dispositivos": [
        {"nome": "PLC_Tex", "tipo": "CPU 1211C"}, {"nome": "TEX-G4", "tipo": "TEX-G4 PROFINET GATEWAY"}, {"nome": "HMI", "tipo": "KTP700 Basic PN"}],
        "origem": {"tela": "14-rede-para-comunicar-profinet/foto-01_captura-de-tela-2026-10-02-142228.png"}},
    "gsd": {"modulo": "RSW:3 Input:256Bytes Output:256Bytes", "i_endereco": "300...555", "q_endereco": "300...555", "bytes": 256,
            "ip_gateway": "192.168.0.208", "mascara": "255.255.255.0", "ip_equipamento": "192.168.0.205",
            "explica": "O gateway Profinet do TEX-G4 fica no IP 192.168.0.208 e conversa por Modbus com o equipamento Tex, no IP 192.168.0.205.",
            "origem": {"audio": "15-configurando-o-gsd/audio-01.webm", "t": "00:00", "tela": "15-configurando-o-gsd/foto-01_captura-de-tela-2026-10-02-142745.png"}},
    "tags": {"tabela": "IO_TexG4", "itens": [
        {"nome": "IN_TexB", "tipo": "UDT_TexRegisters", "endereco": "%I308.0"},
        {"nome": "OUT_TexB", "tipo": "UDT_TexRegisters", "endereco": "%Q308.0"}],
        "explica": "As entradas e saídas do GSD começam no endereço 300; os dados do Tex são lidos a partir do 308.",
        "origem": {"audio": "16-plc-tags/audio-01.webm", "t": "00:10", "tela": "16-plc-tags/foto-01_captura-de-tela-2026-10-02-143446.png"}},
    "bloco": {"nome": "G4_Profinet", "instancia": "#Equipamento2", "nome_exemplo": "'Tex B'",
              "retiradas": ["IP", "Port", "Connect"],
              "novas": [
                  {"nome": "PN_IN", "grupo": "ligacao", "tipo": "estrutura", "exemplo": "P#I308.0 \"IN_TexB\"", "descricao": "A entrada do mapa Profinet do G4: a tag IN_TexB."},
                  {"nome": "PN_OUT", "grupo": "ligacao", "tipo": "estrutura", "exemplo": "P#Q308.0 \"OUT_TexB\"", "descricao": "A saída do mapa Profinet do G4: a tag OUT_TexB."}],
              "explica": "No bloco Profinet saem as entradas IP, Port e Connect, que só servem ao Modbus, e entram as duas do mapa Profinet do G4.",
              "origem": {"audio": "17-bloco-profinet/audio-01.webm", "t": "00:00", "tela": "17-bloco-profinet/foto-02_captura-de-tela-2026-10-02-152438.png"}},
}

# --- estrutura do DB_Parts (tela 12) e o upload de exemplo (antes/depois)
d["db_parts"] = {
    "peca": "Peça[1]", "tipo": "UDT_TexPart",
    "campos_peca": [{"nome": "BCD", "tipo": "Int"}, {"nome": "NumChamber", "tipo": "Int"}, {"nome": "Chamber", "tipo": "Array[0..3] of Struct"}],
    "campos_camara": [{"nome": n, "tipo": t} for n, t in [("TestVolume", "Real"), ("RefVolume", "Real"), ("MaterialType", "Int"), ("NumTest", "Int"), ("Test", "Array[0..3]")]],
    "campos_teste": [{"nome": n, "tipo": t} for n, t in [
        ("TestType", "Int"), ("Digital1Autom", "Int"), ("Digital2Autom", "Int"), ("Digital3Autom", "Int"), ("PartPressureUnit", "Int"),
        ("PressureMax", "Real"), ("TestPressure", "Real"), ("PressureMin", "Real"), ("PartLeakUnit", "Int"), ("OffsetLeak", "Real"),
        ("LeakMax", "Real"), ("ReworkLeakMax", "Real"), ("ReworkLeakMin", "Real"), ("LeakMin", "Real"), ("TimeUnit", "Int"),
        ("FillTime", "Real"), ("EquaTime", "Real"), ("StabTime", "Real"), ("MeasTime", "Real"), ("ExhaTime", "Real"), ("ExpertParam", "Int")]],
    "limites": "Cada peça tem até 4 câmaras (Chamber[0] a Chamber[3]) e cada câmara até 4 testes (Test[0] a Test[3]).",
    "exemplo_upload": [{"campo": "BCD", "antes": "0", "depois": "1"}, {"campo": "NumChamber", "antes": "0", "depois": "3"},
                       {"campo": "NumTest", "antes": "0", "depois": "3"}, {"campo": "TestType", "antes": "0", "depois": "1"},
                       {"campo": "PartPressureUnit", "antes": "0", "depois": "4"}, {"campo": "PressureMax", "antes": "0.0", "depois": "1.5"}],
    "origem": {"audio": "12-banco-de-dados-das-pecas/audio-01.webm", "t": "00:00",
               "tela": "12-banco-de-dados-das-pecas/foto-01_captura-de-tela-2026-10-02-133210.png + foto-02_captura-de-tela-2026-10-02-133320.png"},
}

# --- procedimentos: alterar parâmetro agora com o pulso (confirmado no áudio 11) e um novo para Profinet
for pr in d["procedimentos"]:
    if pr["id"] == "editar-peca":
        pr["passos"] = [
            "Coloque em BCD o número da peça.",
            "Envie um pulso em UploadAllFromTex. Os dados da peça vêm para a posição do DB_Parts ligada em Part.",
            "Altere o parâmetro no DB_Parts.",
            "Envie um pulso em DownloadAllToTex para mandar os dados de volta ao Tex."]
        pr["condicao"] = "A entrada Part aponta para uma posição do DB_Parts."
        pr["variacao"] = "Para mexer em um teste só, escolha a câmara em Chamber e o teste em Test, e use UploadOne e DownloadOne."
        pr["origem"] = {"audio": "11-para-fazer-upload-dos-valores-pelo-clp/audio-01.webm", "t": "00:01"}
d["procedimentos"] = [p for p in d["procedimentos"] if p["id"] != "profinet"] + [{
    "id": "profinet", "titulo": "Montar a comunicação por Profinet",
    "condicao": "O GSD do Tex está instalado no TIA Portal.",
    "passos": [
        "Em Devices & networks, coloque o TEX-G4 na rede PN/IE_1, junto com o CLP.",
        "No TEX-G4, configure o IP do gateway e o módulo de entradas e saídas.",
        "Nas PLC tags, crie IN_TexB e OUT_TexB do tipo UDT_TexRegisters, a partir do endereço 308.",
        "Na FB_Tex, arraste o G4_Profinet para uma network vazia.",
        "Ligue IN_TexB em PN_IN e OUT_TexB em PN_OUT. As outras entradas são iguais às do Modbus TCP."],
    "resultado": "O bloco conversa com o Tex pela rede Profinet, sem IP, Port e Connect.",
    "origem": {"texto": "14-rede-para-comunicar-profinet (campo Conteúdo)", "audio": "15-configurando-o-gsd/audio-01.webm", "t": "00:00"}}]

# --- glossário
novos = [
    {"termo": "GSD", "definicao": "Arquivo que descreve um equipamento Profinet para o TIA Portal.", "origem": {"geral": True}},
    {"termo": "Gateway", "definicao": "No TEX-G4, a parte que recebe a comunicação Profinet do CLP e conversa por Modbus com o equipamento.", "origem": A("15-configurando-o-gsd/audio-01.webm", "00:28")},
    {"termo": "UDT", "definicao": "Tipo de dado criado pelo usuário no TIA Portal, como UDT_TexPart e UDT_TexRegisters.", "origem": {"geral": True}},
    {"termo": "Pulso", "definicao": "Ligar um sinal e desligar logo em seguida. É assim que se pede upload ou download ao Tex.", "origem": A("11-para-fazer-upload-dos-valores-pelo-clp/audio-01.webm", "00:15")}]
d["glossario"] = [g for g in d["glossario"] if g["termo"] not in {n["termo"] for n in novos}] + novos

# --- pendências: saem as respondidas, entram as novas
resp = {"basic", "profinet", "rotulo-retrabalho"}
d["pendencias"] = [p for p in d["pendencias"] if p["id"] not in resp] + [
    {"id": "rework", "pergunta": "Confirma que o nome atual da saída é Rework? As telas mais novas mostram Rework e as mais antigas Retrabalho. Passei a usar Rework.", "afeta": ["saida Rework"]},
    {"id": "fb-profinet", "pergunta": "O G4_Profinet aparece como FB1020 na pasta Library e como %FB1033 na network. Qual é o número certo?", "afeta": ["seção Escolher o bloco"]},
    {"id": "codigos-unidade", "pergunta": "PartPressureUnit, PartLeakUnit e TimeUnit são códigos (o upload trouxe PartPressureUnit = 4). Qual unidade cada código representa?", "afeta": ["DB_Parts", "saidas de medição"]},
    {"id": "endereco-308", "pergunta": "O GSD começa no endereço 300 e as tags no 308. Os 8 primeiros bytes têm outra função?", "afeta": ["Profinet tags"]}]
for p in d["pendencias"]:
    if p["id"] == "start-pulso":
        p["pergunta"] = "Upload e download são por pulso (áudio 11). E o Start: também é pulso, ou precisa ficar true até o Busy subir?"

P.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("dados v2:", len(d["pendencias"]), "pendências ·", len(d["procedimentos"]), "procedimentos ·", len(d["glossario"]), "termos")
