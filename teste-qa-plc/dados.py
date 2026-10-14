# -*- coding: utf-8 -*-
"""
A FONTE DA VERDADE deste comparativo.

Nenhum número aparece nos PDFs sem estar aqui. O auditor em build.py extrai
todos os números do PDF gerado e confere contra este arquivo — número que não
estiver aqui reprova o build e nada é publicado.

Cada valor carrega a sigla da fonte de onde saiu (ver FONTES no fim).
"""

# ---------------------------------------------------------------- produtos
EASY = {
    "nome": "Easy521-0808TN",
    "marca": "Inovance",
    "linha": "Série Easy500",
    "codigo": "01440385",
}

TS = {
    "nome": "TS-621",
    "marca": "INVT",
    "linha": "Série TS600",
    "codigo": "9495",
}

# ---------------------------------------------------------------- tabela
# (grupo, item, valor Easy521, fonte, valor TS621, fonte, favorecido)
#   favorecido: "easy" | "ts" | "=" | "?"   ("?" = não comparável / não informado)
NI = "não informado"

LINHAS = [
    ("Identificação", "Código do produto", "01440385", "MRO", "9495", "KAL", "="),
    ("Identificação", "Fabricante", "Inovance", "MRO", "INVT", "KAL", "="),

    ("Entradas e saídas", "Entradas digitais integradas", "8 (sink/source)", "MRO",
     "16 (NPN/PNP)", "KAL", "ts"),
    ("Entradas e saídas", "Saídas digitais integradas", "8 (NPN, transistor)", "MRO",
     "16 (NPN, transistor)", "KAL", "ts"),
    ("Entradas e saídas", "Módulos de expansão", "16 módulos GL20", "MRO+BRO",
     "16 módulos", "KAL", "="),
    ("Entradas e saídas", "Cartões de expansão no CPU", "2 slots (GE20)", "MRO+BRO",
     NI, "KAL", "?"),
    ("Entradas e saídas", "Pontos máximos com expansão", NI, "BRO",
     "1024 pontos", "KAL", "ts"),

    ("Redes", "Portas Ethernet", "2", "MRO", "2", "KAL", "="),
    ("Redes", "Protocolos sobre Ethernet", "Modbus TCP, EtherNet/IP", "MRO",
     "Modbus TCP/IP, OPC UA", "KAL", "?"),
    ("Redes", "EtherCAT", "1 porta dedicada", "MRO", NI, "KAL", "easy"),
    ("Redes", "Serial", "1 RS485 integrada, até 2 RS232/485 em cartão", "MRO",
     "2 portas Modbus RTU", "KAL", "?"),
    ("Redes", "CAN", "suportado", "MRO", NI, "KAL", "easy"),
    ("Redes", "Porta de programação", "USB tipo C", "MRO", NI, "KAL", "?"),

    ("Memória e desempenho", "Programa de usuário", "200 k passos", "MRO+MAN",
     "128 k passos", "KAL", "easy"),
    ("Memória e desempenho", "Memória de dados", "2 MB, 128 KB retentivos", "MRO+MAN",
     "60 K words", "KAL", "easy"),
    ("Memória e desempenho", "Tempo de execução", "20 k passos / 1,6 ms", "BRO",
     "40 k passos / ms", "KAL", "?"),
    ("Memória e desempenho", "Instrução simples", NI, "BRO",
     "LD 25 ns, MOV 0,15 µs", "KAL", "?"),
    ("Memória e desempenho", "Relógio de tempo real", "integrado", "MRO", NI, "KAL", "easy"),

    ("Movimento", "Eixos totais", "8 (EtherCAT e pulso)", "MRO",
     "8 canais pulso/direção", "KAL", "?"),
    ("Movimento", "Eixos sincronizados por barramento", "até 8 por EtherCAT", "MRO",
     NI, "KAL", "easy"),
    ("Movimento", "Saídas rápidas", "200 kHz PWM, 5 eixos", "MRO",
     "16 saídas de 200 kHz", "KAL", "ts"),
    ("Movimento", "Entradas rápidas", "8 canais de 200 kHz", "MRO",
     "16 canais de 200 kHz, 8 em A/B", "KAL", "ts"),
    ("Movimento", "Came eletrônico", "suportado", "MRO", NI, "KAL", "easy"),
    ("Movimento", "Interpolação", "linear e circular", "BRO",
     "linear e circular, 2 pares de coordenadas", "KAL", "ts"),

    ("Engenharia", "Software de programação", "AutoShop", "BRO", "Auto Station Pro", "KAL", "="),
    ("Engenharia", "Linguagens", "LD, SFC, ST, FB/FC", "BRO",
     "ladder e linguagem C", "KAL", "?"),
    ("Engenharia", "Simulação offline", "suportada", "BRO", NI, "KAL", "easy"),

    ("Físico e comercial", "Alimentação", "24 V CC", "MRO", NI, "KAL", "?"),
    ("Físico e comercial", "Dimensões (L x A x P)", "53 x 100 x 80 mm", "MAN+BRO",
     NI, "KAL", "?"),
    ("Físico e comercial", "Peso", "cerca de 197 g", "MAN", NI, "KAL", "?"),
    ("Físico e comercial", "Grau de proteção", "IP20", "MAN", NI, "KAL", "?"),
    ("Físico e comercial", "Garantia", "18 meses", "MRO+MAN", "12 meses", "KAL", "easy"),
    ("Físico e comercial", "Preço de referência", "US$ 476,75 (distribuidor EUA)", "MRO",
     "sob consulta", "KAL", "?"),
]

# ---------------------------------------------------------------- fontes
FONTES = {
    "BRO": ("Catálogo Easy Series PLC, Inovance",
            "Documento do fabricante, data code 19120266 V0.1, de 2023. Traz a família "
            "Easy (301, 302, 320, 502 e 523) e não lista o Easy521 — dele só se usou "
            "aqui o que o catálogo afirma para toda a linha Easy500."),
    "MRO": ("Ficha de distribuidor do part 01440385",
            "mrosupply.com, listagem do Easy521-0808TN. É fonte comercial, não documento "
            "do fabricante, e hoje é a mais completa disponível publicamente para este "
            "modelo específico."),
    "MAN": ("Manual do usuário Easy521/522/523, Inovance",
            "Consultado por resumo indexado, não pelo PDF original. Os três valores que "
            "vêm só daqui — dimensões, peso e grau de proteção — merecem conferência no "
            "manual antes de irem para uma proposta."),
    "KAL": ("Página do produto TS621, loja Kalatec",
            "loja.kalatec.com.br. É a única fonte usada para o TS621 e não informa "
            "alimentação, dimensões, peso, temperatura, grau de proteção, certificações "
            "nem preço."),
}

# lacunas conhecidas — entram no PDF como aviso, nunca como célula preenchida por estimativa
LACUNAS_TS = [
    "alimentação", "dimensões", "peso", "temperatura de operação",
    "grau de proteção", "certificações", "preço",
]

# ---------------------------------------------------------------- derivados
# Número calculado a partir de dois valores acima. A conta fica declarada para o
# auditor aceitar o número e para o leitor poder refazê-la.
DERIVADOS = [
    ("56", "200 k contra 128 k passos de programa: 1,5625 vezes, ou seja 56% a mais"),
    ("17", "2 MB contra 60 K words (120 KB) de dados: cerca de 17 vezes mais"),
    ("120", "60 K words a 16 bits equivalem a 120 KB"),
]

DATA = "18 de agosto de 2026"
