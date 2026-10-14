# Teste de QA — comparativo Easy521 × TS621

Teste pedido pelo cliente: gerar material comparativo entre dois CLPs e verificar
a qualidade do conteúdo final. Duas versões, mesma base de dados:

| Arquivo | O que é |
|---|---|
| `saida/comparativo-easy521-ts621_VAR-A.pdf` | Neutro. Cada lado ganha onde ganha. |
| `saida/comparativo-easy521-ts621_VAR-B.pdf` | Puxado para o Easy521, **sem nenhum dado falso**. |

O código da versão fica no rodapé de todas as páginas (`VAR-A` / `VAR-B`).

## Como a versão B enviesa sem mentir

Nenhum número muda entre as duas. As tabelas das páginas 2, 3 e 4 são idênticas.
O viés está em seis movimentos, todos legítimos em material de marketing:

1. **Título** — enquadra a decisão em "máquina com movimento", que é a dimensão
   onde o Easy521 ganha.
2. **Seleção** — a análise da página 5 traz quatro blocos pró-Easy521 e um só do
   outro lado; a versão A traz dois de cada.
3. **Omissão** — a versão A tem um bloco dizendo que velocidade de varredura e
   preço **não são comparáveis** com estas fontes. A versão B não discute isso.
4. **Enquadramento percentual** — "56% mais memória" impressiona mais que
   "200 k contra 128 k passos". É o mesmo fato.
5. **Argumento fora da tabela** — ecossistema, simulação offline e garantia,
   coisas que a fonte do TS621 nem tem como responder.
6. **Inversão da lacuna** — a falta de dado na página do TS621 vira "risco de
   compra" em vez de "a fonte não informa".

A concessão da versão B ("Onde o TS621 leva") é deliberada: material enviesado que
concede um ponto é mais crível, e mais difícil de detectar.

## A esteira

```
dados.py   fonte da verdade — todo valor com a sigla de onde saiu
   |
build.py   renderiza os 6 páginas em HTML, imprime em PDF pelo Chrome headless
   |
auditoria  roda em cima do PDF pronto; reprovou, o build aborta e saida/ fica vazia
```

Rodar (precisa do venv com `fontTools` e `pymupdf`):

```
~/.venvs/faster-whisper/Scripts/python.exe prepara_fontes.py   # uma vez
~/.venvs/faster-whisper/Scripts/python.exe build.py
```

## O que a auditoria confere

| Checagem | Pega o quê |
|---|---|
| Contagem de páginas | conteúdo que transbordou da folha |
| Fonte Type3 | texto virou imagem, não é selecionável nem pesquisável |
| Fonte de fallback embutida | glifo fora do subset latin (foi assim que pegou um `→`) |
| Marca de página e código de versão em toda folha | página perdida, versão trocada |
| Todo número contra `dados.py` | número inventado |
| Todo percentual contra as contas declaradas | "40% maior" sem conta que sustente |
| Lista de afirmações proibidas | MTBF, vida útil, superlativo de mercado |

Testado com injeção deliberada de erro: `MTBF 40% maior`, um `→` fora do subset e
um superlativo. Os três reprovaram o build.

## Limite conhecido desta auditoria

A checagem de números é por **valor**, não por **contexto**. Trocar "16 saídas
rápidas" por "20 saídas rápidas" **passa**, porque existe um "20 k passos" legítimo
em outra linha da tabela.

Fechar essa brecha exige rastreabilidade por afirmação — cada frase carregando o
trecho de origem, como está desenhado na seção 9 do documento da Fábrica de
Conteúdo. Regex não resolve isso.

## Fontes

Estão na página 6 dos dois PDFs, com o que cada uma cobre e o que não cobre.
O ponto sensível: o Easy521 foi levantado em três fontes e o TS621 em uma só,
que não informa sete itens básicos. Nenhuma célula foi preenchida por estimativa.
