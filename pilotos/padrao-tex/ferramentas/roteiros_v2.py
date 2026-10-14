"""Leva os roteiros dos vídeos para a v2 (blocos 11–17 do pacote do cliente) e registra o vocabulário falado novo.
Toda frase sai de dados/padrao-tex.json (que aponta áudio/tela). Roda uma vez."""
import json
from pathlib import Path

V = Path(__file__).resolve().parent.parent / "video"
R = json.loads((V / "roteiros.json").read_text(encoding="utf-8"))
P = json.loads((V / "pronuncia.json").read_text(encoding="utf-8"))

# vocabulário falado medido em 02/10 (2 rodadas de transcrição reversa)
P["termos"].update({
    "Rework": {"fala": "Riwork", "ouvido": "rework", "estado": "ok"},
    "Profinet": {"fala": "Prófinéti", "ouvido": "Profinet", "estado": "ok"},
    "G4_Profinet": {"fala": "G4 Prófinéti", "ouvido": "", "estado": "derivado"},
    "G4_Profinet_Basic": {"fala": "G4 Prófinéti Bêisic", "ouvido": "", "estado": "derivado"},
    "G4_ModbusTCP_Basic": {"fala": "G4 Mód bâs TCP Bêisic", "ouvido": "G4 Modbus TCP Basic", "estado": "ok"},
    "PN_IN": {"fala": "P N In", "ouvido": "PNI", "estado": "aceitável"},
    "PN_OUT": {"fala": "P N Aut", "ouvido": "PNAUT", "estado": "aceitável"},
    "IN_TexB": {"fala": "In Tex B", "ouvido": "Intex-B", "estado": "aceitável"},
    "OUT_TexB": {"fala": "Out Tex B", "ouvido": "Alt-Tex B", "estado": "aceitável"},
    "UDT_TexRegisters": {"fala": "UDT Tex Registers", "ouvido": "UDT-TEX Registers", "estado": "ok"},
    "TEX-G4": {"fala": "Tex G4", "ouvido": "Tex G4", "estado": "ok"},
    "GSD": {"fala": "GSD", "ouvido": "GSD", "estado": "ok"},
    "1.5": {"fala": "um ponto cinco", "ouvido": "1.5", "estado": "ok"},
})
(V / "pronuncia.json").write_text(json.dumps(P, ensure_ascii=False, indent=2), encoding="utf-8")

v1, v2 = R["videos"]
cenas = v1["cenas"]
# depois do Main: escolher o bloco (os 4 blocos G4, áudio 13)
escolha = {"tipo": "escolha", "segmentos": [
    {"texto": "Antes de montar, escolha o bloco. Existem quatro blocos de comunicação G4.", "foco": "card:0"},
    {"texto": "O G4_ModbusTCP é o completo: comandos, leituras e os dados das peças.", "foco": "card:1"},
    {"texto": "O G4_ModbusTCP_Basic faz só o básico, sem upload nem download das peças.", "foco": "card:2"},
    {"texto": "O G4_Profinet é completo como o Modbus, mas fala Profinet.", "foco": "card:3"},
    {"texto": "E o G4_Profinet_Basic é o Profinet sem os parâmetros do equipamento.", "foco": "card:4"},
    {"texto": "Primeiro, você monta o Modbus TCP. Depois, o Profinet."}]}
idx_main = next(i for i, c in enumerate(cenas) if c.get("figura") == "main")
if not any(c["tipo"] == "escolha" for c in cenas):
    cenas.insert(idx_main + 1, escolha)
# antes do fim: o caminho Profinet (texto do bloco 14, áudios 15–17, telas 14–17)
profinet = [
    {"tipo": "tela", "figura": "rede", "segmentos": [
        {"texto": "Agora, o Profinet. Inclua o GSD do Tex no TIA Portal."},
        {"texto": "Coloque o TEX-G4 na mesma rede do CLP.", "foco": "marca:2"},
        {"texto": "No padrão, a IHM também está nessa rede.", "foco": "marca:3"}]},
    {"tipo": "tela", "figura": "gsd", "segmentos": [
        {"texto": "No TEX-G4, o módulo tem 256 bytes de entrada e de saída.", "foco": "marca:1"},
        {"texto": "As entradas e as saídas começam no endereço 300.", "foco": "marca:2"},
        {"texto": "O gateway Profinet fica no IP final 208. Ele conversa por Modbus com o Tex, no 205.", "foco": "marca:3"}]},
    {"tipo": "tela", "figura": "tags", "segmentos": [
        {"texto": "Nas PLC tags, crie IN_TexB e OUT_TexB, do tipo UDT_TexRegisters.", "foco": "marca:1"},
        {"texto": "As duas começam no endereço 308.", "foco": "marca:2"}]},
    {"tipo": "bloco", "diagrama": "profinet", "segmentos": [
        {"texto": "Na FB_Tex, use o G4_Profinet. Ele não tem IP, Port nem Connect: isso é só do Modbus.", "foco": "grupo:comunicacao"},
        {"texto": "Ligue IN_TexB em PN_IN.", "foco": "pin:PN_IN"},
        {"texto": "E OUT_TexB em PN_OUT. As outras entradas são iguais às do Modbus TCP.", "foco": "pin:PN_OUT"}]},
]
if not any(c.get("figura") == "rede" for c in cenas):
    fim = next(i for i, c in enumerate(cenas) if c["tipo"] == "fim")
    cenas[fim:fim] = profinet
v1["titulo"] = "Montando a comunicação"
for c in cenas:
    if c["tipo"] == "titulo":
        c["segmentos"] = [{"texto": "Neste vídeo, você liga um equipamento Tex G4 a um CLP Siemens."},
                          {"texto": "Por Modbus TCP ou por Profinet, com o Padrão TEX, no TIA Portal."}]

# vídeo 2: Rework, pulso no upload/download (áudio 11) e o DB_Parts antes/depois (áudio 12, tela 12)
for c in v2["cenas"]:
    for s in c["segmentos"]:
        s["texto"] = s["texto"].replace("Retrabalho fica true", "Rework fica true")
        if s.get("foco") == "pin:Retrabalho":
            s["foco"] = "pin:Rework"
        if s.get("foco") == "troca:upload":
            s["texto"] = "Coloque em BCD o número da peça. Um pulso em UploadAllFromTex traz todos os dados para o DB_Parts."
        if s.get("foco") == "troca:download":
            s["texto"] = "Altere o que precisar. Um pulso em DownloadAllToTex envia de volta para o Tex."
dbparts = {"tipo": "tela", "figura": "dbparts", "segmentos": [
    {"texto": "Veja o upload da peça 1, no DB_Parts. Antes, ela estava toda zerada."},
    {"texto": "Depois do upload, BCD mostra 1.", "foco": "marca:1"},
    {"texto": "NumChamber e NumTest mostram 3.", "foco": "marca:2"},
    {"texto": "NumTest.", "foco": "marca:3"},
    {"texto": "E PressureMax mostra 1.5. Os valores vieram do equipamento.", "foco": "marca:4"}]}
# a marca 3 não precisa de frase própria: junta na 2
dbparts["segmentos"] = [s for s in dbparts["segmentos"] if s["texto"] != "NumTest."]
if not any(c.get("figura") == "dbparts" for c in v2["cenas"]):
    fim = next(i for i, c in enumerate(v2["cenas"]) if c["tipo"] == "fim")
    v2["cenas"].insert(fim, dbparts)
v2["titulo"] = "Operando pelo CLP"

(V / "roteiros.json").write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
print("vídeo 1:", len(v1["cenas"]), "cenas · vídeo 2:", len(v2["cenas"]), "cenas · termos falados:", len(P["termos"]))
