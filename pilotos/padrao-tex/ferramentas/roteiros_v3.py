"""Monta o roteiro do VÍDEO ÚNICO pedido na v3 (01-o-pedido: "1 vídeo com toda explicação... Modbus e Profinet";
o áudio do pedido autoriza dividir o conteúdo em sessões → 6 partes com cartão de capítulo e capítulos no MP4).
Reaproveita as cenas já aprovadas dos vídeos 1 e 2 da v2 e acrescenta as novas.
Pacote final (zip 3 + WhatsApp do cliente, 02/10): capítulo 1 apresenta o equipamento com fotos do site da Tex,
e entram o DB Tex (bloco 07) e o uso dos dados na lógica (bloco 23). Pode rodar de novo: refaz o video-completo."""
import copy, json
from pathlib import Path

V = Path(__file__).resolve().parent.parent / "video"
R = json.loads((V / "roteiros.json").read_text(encoding="utf-8"))
P = json.loads((V / "pronuncia.json").read_text(encoding="utf-8"))
P["termos"].update({
    "PLC data types": {"fala": "PLC dêita táips", "ouvido": "PLC Data Types", "estado": "ok"},
    "Screens": {"fala": "Scríns", "ouvido": "screens", "estado": "ok"},
    "HMI tags": {"fala": "HMI tégs", "ouvido": "HMI Tags", "estado": "ok"},
    "Equipamento4": {"fala": "Equipamento quatro", "ouvido": "equipamento 4", "estado": "ok"},
    "G4-SE": {"fala": "G quatro S E", "ouvido": "G4-SE", "estado": "ok"},
    "G4-DF": {"fala": "G quatro D F", "ouvido": "G4-DF", "estado": "ok"},
    "G4-HD": {"fala": "G quatro H D", "ouvido": "G4-HD", "estado": "ok"},
    "G4-VZ": {"fala": "G quatro V Z", "ouvido": "G4-VZ", "estado": "ok"},
})
(V / "pronuncia.json").write_text(json.dumps(P, ensure_ascii=False, indent=2), encoding="utf-8")

v1 = next(v for v in R["videos"] if v["id"] == "video-1")
v2 = next(v for v in R["videos"] if v["id"] == "video-2")
de = lambda v, **k: copy.deepcopy(next(c for c in v["cenas"] if all(c.get(a) == b for a, b in k.items())))
blocos_v1 = [copy.deepcopy(c) for c in v1["cenas"] if c["tipo"] == "bloco" and c.get("diagrama") != "profinet"]
blocos_v2 = [copy.deepcopy(c) for c in v2["cenas"] if c["tipo"] == "bloco"]
cap = lambda n, t: {"tipo": "capitulo", "parte": n, "titulo": t, "segmentos": [{"texto": f"Parte {n}: {t[0].lower() + t[1:]}."}]}

rede = de(v1, figura="rede")
rede["segmentos"][0]["texto"] = "Inclua o GSD do Tex no TIA Portal."
escolha = de(v1, tipo="escolha")
escolha["segmentos"][-1]["texto"] = "Primeiro, o Modbus TCP. Depois, o Profinet."

cenas = [
    {"tipo": "titulo", "segmentos": [
        {"texto": "Neste vídeo, você conhece o equipamento Tex G4, leva o Padrão TEX para o seu projeto e liga o G4 ao CLP Siemens."},
        {"texto": "Por Modbus TCP ou por Profinet, e opera pelo CLP ou pela IHM."}]},
    # --- o equipamento (site da Tex): o cliente pediu "uma explicação do equipamento antes"
    cap(1, "O equipamento Tex G4"),
    {"tipo": "equip", "foto": "perspectiva", "kick": "Tex G4", "titulo": "Teste de estanqueidade", "itens": [
        "Verifica se a peça <b>vaza</b>",
        "Pressuriza, estabiliza e <b>mede</b> a variação",
        "<b>Aprova ou reprova</b> a peça sozinho"], "segmentos": [
        {"texto": "O Tex G4 é um equipamento de teste de estanqueidade: ele verifica se uma peça vaza.", "foco": "item:1"},
        {"texto": "No G4-SE, por exemplo, ele pressuriza a peça, espera a pressão estabilizar e mede a variação.", "foco": "item:2"},
        {"texto": "Depois, compara com os limites configurados e aprova ou reprova a peça sozinho.", "foco": "item:3"}]},
    {"tipo": "equip", "foto": "frente", "kick": "Tex Equipamentos Eletrônicos", "titulo": "Desde 1997", "itens": [
        "<b>1997</b> · Fundação, em São Paulo",
        "<b>2015</b> · Lançamento da linha G4"], "segmentos": [
        {"texto": "A Tex fabrica equipamentos de medição e de teste de vazamento desde 1997.", "foco": "item:1"},
        {"texto": "Em 2015, lançou a quarta geração dos seus equipamentos: a linha G4.", "foco": "item:2"}]},
    {"tipo": "linha", "titulo": "A linha G4: um modelo para cada tipo de teste", "segmentos": [
        {"texto": "A linha G4 tem vários modelos, um para cada tipo de teste."},
        {"texto": "O G4-SE mede a queda de pressão na peça.", "foco": "modelo:1"},
        {"texto": "O G4-DF compara a pressão da peça com a de uma referência.", "foco": "modelo:2"},
        {"texto": "O G4-HD é para vazamentos muito pequenos.", "foco": "modelo:3"},
        {"texto": "E o G4-VZ mede a vazão que passa pela peça.", "foco": "modelo:4"}]},
    {"tipo": "equip", "foto": "traseira", "kick": "Comunicação", "titulo": "Ligado ao CLP pela rede", "itens": [
        "Porta <b>Ethernet</b> na traseira",
        "<b>Modbus TCP</b> ou <b>Profinet</b>",
        "O CLP <b>comanda</b> o teste e <b>lê</b> o resultado"], "segmentos": [
        {"texto": "Na traseira, a porta Ethernet liga o equipamento à rede do CLP.", "foco": "item:1"},
        {"texto": "A comunicação é por Modbus TCP ou por Profinet, conforme o modelo.", "foco": "item:2"},
        {"texto": "Com o Padrão TEX, o CLP Siemens comanda o teste e lê o resultado pela rede.", "foco": "item:3"}]},
    cap(2, "Conhecendo o Padrão TEX"),
    de(v1, figura="arvore"),
    {"tipo": "tela", "figura": "biblioteca", "zoom_max": 3.0, "segmentos": [
        {"texto": "Na pasta Library ficam os blocos que fazem a comunicação."},
        {"texto": "Para Modbus TCP, o G4_ModbusTCP.", "foco": "marca:1"},
        {"texto": "Para Profinet, o G4_Profinet.", "foco": "marca:3"},
        # foco que não é marca: a câmera volta à imagem inteira e nenhum rótulo fica aceso
        {"texto": "Mantenha esses blocos como vieram no Padrão TEX mais atual que você baixou.", "foco": "tudo"}]},
    escolha,
    {"tipo": "tela", "figura": "debug", "segmentos": [
        {"texto": "O DB Debug simula as entradas do bloco, para testes.", "foco": "marca:1"},
        {"texto": "No seu projeto, troque essas variáveis pela lógica de acionamento da sua máquina.", "foco": "marca:2"}]},
    {"tipo": "tela", "figura": "dbtex", "segmentos": [
        {"texto": "O DB Tex guarda os dados de todos os equipamentos."},
        {"texto": "O HMI_Link liga a IHM aos equipamentos. Não altere essa variável.", "foco": "marca:1"},
        {"texto": "Depois vem um elemento para cada equipamento. No exemplo são quatro, um de cada bloco.", "foco": "marca:2"},
        {"texto": "O tipo de cada um é o bloco do equipamento.", "foco": "marca:3"},
        {"texto": "Por esses elementos, você acessa as entradas, as saídas e as outras propriedades.", "foco": "tudo"}]},
    cap(3, "Levar o padrão para o seu projeto"),
    {"tipo": "pastas", "segmentos": [
        {"texto": "Com os dois projetos abertos no TIA Portal, copie as pastas TexG4 para o seu projeto.", "foco": "pasta:0"},
        {"texto": "Copie a pasta TexG4 de Program blocks.", "foco": "pasta:1"},
        {"texto": "Depois, a de PLC tags.", "foco": "pasta:2"},
        {"texto": "E a de PLC data types.", "foco": "pasta:3"},
        {"texto": "Na IHM, copie a pasta TexG4 de Screens.", "foco": "pasta:4"},
        {"texto": "E a de HMI tags.", "foco": "pasta:5"}]},
    de(v1, figura="main"),
    cap(4, "Comunicação por Modbus TCP"),
    de(v1, figura="fbvazia"), de(v1, figura="adicionando"), *blocos_v1,
    {"tipo": "tela", "figura": "basicmb", "segmentos": [
        {"texto": "O G4_ModbusTCP_Basic é igual, sem as seis entradas de upload e download das peças.", "foco": "marca:1"},
        {"texto": "Depois de Reset, ele vai direto para Part e HMI_Link.", "foco": "marca:2"}]},
    cap(5, "Comunicação por Profinet"),
    rede, de(v1, figura="gsd"), de(v1, figura="tags"), de(v1, tipo="bloco", diagrama="profinet"),
    {"tipo": "tela", "figura": "basicpn", "segmentos": [
        {"texto": "O G4_Profinet_Basic também não tem as seis entradas de upload e download.", "foco": "marca:1"}]},
    cap(6, "Operando pelo CLP"),
    blocos_v2[0], de(v2, tipo="fluxo"), de(v2, figura="monitorado"), blocos_v2[1], de(v2, tipo="trocas"), de(v2, figura="dbparts"),
    {"tipo": "tela", "figura": "usar", "segmentos": [
        {"texto": "Você pode usar qualquer entrada ou saída dos blocos na lógica da sua máquina."},
        {"texto": "Chame pelo DB, pelo equipamento e pela propriedade: aqui, o ResultOK do Equipamento4.", "foco": "marca:1"},
        {"texto": "Quando a peça é aprovada, a máquina finaliza a sequência.", "foco": "marca:2"},
        {"texto": "Todas as entradas e saídas podem ser usadas assim.", "foco": "tudo"}]},
    cap(7, "Operando pela IHM"),
    {"tipo": "tela", "figura": "ihmtelas", "segmentos": [
        {"texto": "A IHM do padrão tem quatro telas, na pasta TexG4.", "foco": "marca:1"},
        {"texto": "Uma tela só controla vários equipamentos, pelo HMI_Link."}]},
    {"tipo": "tela", "figura": "operacao", "segmentos": [
        {"texto": "Para comandar pela IHM, o bloco do G4 no CLP precisa estar em modo manual."},
        {"texto": "Na tela Operação, escolha o equipamento.", "foco": "marca:1"},
        {"texto": "Escolha o BCD com as setas.", "foco": "marca:2"},
        {"texto": "Toque em START para iniciar o teste. STOP para o teste.", "foco": "marca:3"},
        {"texto": "A tela mostra a pressão atual", "foco": "marca:5"},
        {"texto": "e o vazamento.", "foco": "marca:6"},
        {"texto": "O botão MENU abre as outras telas.", "foco": "marca:7"}]},
    {"tipo": "tela", "figura": "ios", "segmentos": [
        {"texto": "A tela de IOs mostra cada entrada do equipamento, com a sua função.", "foco": "marca:1"},
        {"texto": "E, à direita, cada saída.", "foco": "marca:2"}]},
    {"tipo": "tela", "figura": "diag", "segmentos": [
        {"texto": "Em diagnósticos, você vê o autoteste das válvulas e dos sensores,", "foco": "marca:1"},
        {"texto": "e quais saídas estão com problema.", "foco": "marca:2"}]},
    {"tipo": "tela", "figura": "param", "segmentos": [
        {"texto": "Na parametrização, escolha o BCD, a câmara e o teste.", "foco": "marca:1"},
        {"texto": "UPLOAD CONFIG ATUAL traz os dados da peça.", "foco": "marca:5"},
        {"texto": "Altere o que precisar. DOWNLOAD CONFIG ATUAL envia ao equipamento.", "foco": "marca:4"}]},
    {"tipo": "fim", "segmentos": [
        {"texto": "Pronto: você levou o padrão para o seu projeto, ligou o Tex e operou o teste."},
        {"texto": "Os detalhes estão no manual e nos guias rápidos."}]},
]
R["videos"] = [v for v in R["videos"] if v["id"] != "video-completo"] + [
    {"id": "video-completo", "titulo": "Do projeto ao teste", "subtitulo": "Padrão TEX", "cenas": cenas}]
(V / "roteiros.json").write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
print("vídeo completo:", len(cenas), "cenas,", sum(len(c["segmentos"]) for c in cenas), "frases,", sum(c["tipo"] == "capitulo" for c in cenas), "capítulos")
