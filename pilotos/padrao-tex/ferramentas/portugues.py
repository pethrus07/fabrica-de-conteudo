"""Revisão de português com o LanguageTool LOCAL (servidor em localhost:8081; o texto não sai da máquina).

Confere duas fontes:
  1. cada frase dos dados (dados/padrao-tex.json), isolada — é onde o erro de verdade mora;
  2. o texto extraído dos PDFs, com a hifenização desfeita — pega o que só existe na diagramação.
Ortografia reprova o build. Gramática e estilo saem como aviso para revisão humana.
Uso: python portugues.py trabalho/integracao.txt trabalho/referencia.txt
"""
import json, re, sys, urllib.parse, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
D = json.loads((RAIZ / "dados" / "padrao-tex.json").read_text(encoding="utf-8"))
ACEITAS = {p["nome"] for p in D["entradas"] + D["saidas"]} | {b["nome"] for b in D["biblioteca"]} | {
    "Tex", "TexG4", "COSMO", "Instruments", "type", "Siemens", "Profinet", "Modbus", "TCP", "Library", "Main", "OB1", "FB10", "DB1", "DB20",
    "DB2", "FB_Tex", "DB_Parts", "HMI_Link", "G4", "CLP", "IHM", "network", "networks", "upload", "download", "true",
    "false", "TRUE", "FALSE", "BCD", "Debug", "Tex1", "NewBCD", "UploadAll", "DownloadAll", "Equipamento1", "struct",
    "DC", "1211C", "Peça", "reset", "Reset", "TIA", "Portal", "FB", "FC", "DB", "OB", "Sweep", "Cycle", "Program",
    "escape", "Ethernet",
    # v2: tipos de dado do TIA Portal e nomes do Profinet
    "Int", "Real", "Array", "Struct", "GSD", "TEX-G4", "KTP700", "PN", "IE_1", "gateway", "Gateway", "Devices", "networks",
    "tags", "PLC", "UDT", "RSW", "Basic",
    # v3: menus do TIA Portal citados como aparecem na tela
    "types", "Screens", "data", "blocks", "HMI", "Program"}
# regras que só disparam por artefato da tabela extraída do PDF (nome do pino colado em "sim/não")
# e as do sumário (pontilhado) e da numeração de seção ("3.1" não é decimal)
ARTEFATO_PDF = {"VERB_COMMA_CONJUNCTION", "DECIMAL_COMMA", "SPACE_BEFORE_PUNCTUATION2", "COMMA_PARENTHESIS_WHITESPACE"}
# "status" é o nome técnico do pino e o termo que o integrador usa
ACEITAS_ESTILO = {"PT_BARBARISMS_REPLACE_STATUS"}
SOFT_HYPHEN = "­"


def limpa(texto):
    texto = re.sub(SOFT_HYPHEN + r"\s*", "", texto)                 # "equi­\npamento" → "equipamento"
    texto = re.sub(r"(?<!\S)(?:\w ){3,}\w(?!\S)", " ", texto)       # títulos com espaçamento de letra
    return texto


def frases_dos_dados():
    out = []
    def junta(x):
        if isinstance(x, str) and len(x.split()) >= 3:
            out.append(x)
        elif isinstance(x, dict):
            for k, v in x.items():
                if k not in ("origem", "_leia", "pendencias", "exemplo", "arquivo") and not k.endswith("_origem"):
                    junta(v)
        elif isinstance(x, list):
            for v in x:
                junta(v)
    junta(D)
    return "\n\n".join(out)


def checa(nome, texto, do_pdf):
    texto = limpa(texto)
    dados = urllib.parse.urlencode({"text": texto, "language": "pt-BR",
                                    "disabledRules": "WHITESPACE_RULE,UPPERCASE_SENTENCE_START,DASH_RULE"}).encode()
    r = json.load(urllib.request.urlopen("http://localhost:8081/v2/check", dados, timeout=900))
    erros, avisos = [], []
    for m in r["matches"]:
        trecho = texto[m["offset"]: m["offset"] + m["length"]]
        palavras = trecho.split() or [trecho]
        if (do_pdf and m["rule"]["id"] in ARTEFATO_PDF) or m["rule"]["id"] in ACEITAS_ESTILO or trecho in ACEITAS or palavras[0] in ACEITAS \
                or re.fullmatch(r"[A-Za-z]+[A-Z_0-9]\w*", trecho) or re.search(r"[_\[\]#\"']", trecho) \
                or re.fullmatch(r"[IQ]\d+\.\d+", trecho):          # endereços de E/S do CLP: I308.0, Q308.0
            continue
        ctx = m["context"]["text"].replace("\n", " ")
        item = f"{nome}: «{trecho}» — {m['message']} [{m['rule']['id']}] em «{ctx}»"
        (erros if m["rule"]["issueType"] == "misspelling" else avisos).append(item)
    return erros, avisos


if __name__ == "__main__":
    E, A = [], []
    e, w = checa("dados", frases_dos_dados(), do_pdf=False); E += e; A += w
    for a in sys.argv[1:]:
        e, w = checa(Path(a).stem, Path(a).read_text(encoding="utf-8"), do_pdf=True); E += e; A += w
    for w in A:
        print("  aviso:", w)
    for e in E:
        print("  ✗", e)
    print(f"\nortografia: {len(E)} erro(s) · gramática/estilo: {len(A)} aviso(s)")
    sys.exit(1 if E else 0)
