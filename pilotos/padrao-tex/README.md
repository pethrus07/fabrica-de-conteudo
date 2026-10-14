# Padrão TEX · material-modelo

Primeiro material da Fábrica de Conteúdo. Entrada: o `.zip` que o cliente gerou no Estúdio de Máquinas (`fonte/`, o
pacote final de 02/10/2026, 30 blocos). Saída: **1 manual, 3 guias rápidos e 1 vídeo** em `entrega/v3/`, como o
pedido final mandou. **Este piloto é o modelo dos próximos:** a próxima máquina troca os dados e as capturas, e
reaproveita o tema, o motor de vídeo e as auditorias.

**Identidade:** o material sai na identidade da **Tex**, não da Celiware (pedido do cliente no WhatsApp, 02/10 16:06:
"Não usar nada da Celiware"). Logo, cores (#003895 e #D32E12, medidas no logo) e fotos vêm de tex.com.br, coletados por
`video/coletar_tex.mjs` e `video/baixar_tex.mjs` em `marca/tex/` (o site recusa curl com 406; vai pelo Chromium).
As duas auditorias reprovam qualquer "Celiware" no texto e nos metadados do PDF e do MP4.

## Como reproduzir

```
python build.py                   # tudo: documentos + vídeo (~20 min, o render é quadro a quadro)
python build.py --sem-video       # só os documentos (~2 min)
python build.py --reusar-render   # documentos + auditoria do vídeo já renderizado (aborta se o MP4 estiver defasado)
```

Qualquer auditoria que reprovar aborta o build e `entrega/` não é tocada. Cada versão vai para a sua pasta
(`entrega/v1`, `v2`, `v3`): a anterior nunca é sobrescrita.

## Fonte única da verdade

`dados/padrao-tex.json`. Cada pino, passo, aviso e termo aponta **de onde veio**: áudio e minuto do cliente, captura
de tela, texto do formulário, página do site da Tex (`site`), ou "geral" para definição padrão de termo. Nenhum texto
técnico é digitado nas peças: manual, guias e vídeo leem daqui. As perguntas em aberto estão em `pendencias`.

Cada pacote novo do cliente passa por um script de versão (`ferramentas/dados_v2.py`, `dados_v3.py`, `dados_v4.py`):
compara os arquivos por hash, remapeia os caminhos renumerados e acrescenta só o que é novo. O `dados_v4.py` se recusa
a rodar duas vezes, porque a renumeração é em cadeia (07→08, 08→09...).

## Peças

| Peça | Gerada por | Conferida por |
|---|---|---|
| Manual (33 p.) | `manual/manual.typ` + `manual/tema.typ` (Typst, PDF/UA-1) | `ferramentas/auditar_docs.py`, `ferramentas/portugues.py` |
| Guia rápido · Entradas do bloco Modbus (2 p.) | `manual/guia.typ --input guia=modbus` | idem; reprova se passar de 2 páginas |
| Guia rápido · Entradas do bloco Profinet (2 p.) | `manual/guia.typ --input guia=profinet` | idem |
| Guia rápido · Controlar o Tex pela IHM (2 p.) | `manual/guia.typ --input guia=ihm` | idem |
| Vídeo · Do projeto ao teste (13 min, 7 capítulos no MP4) | `ferramentas/roteiros_v3.py` → `video/preparar.py` → `video/render.mjs` | `video/auditar_video.py` |

O guia de integração e a referência rápida da v1/v2 (`integracao.typ`, `referencia.typ`) ficam como histórico.

## O que cada auditoria garante

- **Documento:** só IBM Plex embutida (sem fonte substituta, sem Type3); todo pino dos dados aparece; a ordem dos pinos
  nos dados é a ordem lida por OCR nas telas reais do TIA Portal (Modbus, Profinet e os dois Basic); todo número impresso
  existe nos dados ou nas telas; termos proibidos (ex.: "pulso" junto de Start, ainda não confirmado; "Celiware");
  vocabulário controlado (Vale); legibilidade Flesch-Martins.
- **Português:** LanguageTool local sobre cada frase dos dados e sobre o texto do PDF. Ortografia reprova.
- **Vídeo:** 1080p H.264 30 fps; −16 LUFS e pico ≤ −1 dBTP; transcrição reversa ≥ 97% contra o roteiro falado, com a
  última frase inteira; imagem parada ≤ 55% e trecho ≤ 4 s; legenda ≤ 2×42 caracteres e ≤ 17 car/s (padrão Netflix pt-BR);
  metadados sem "Celiware".

A régua foi testada com erro injetado: fonte errada, número inventado e termo proibido reprovaram o build.

## Decisões que valem para os próximos

- **Diagrama do bloco redesenhado em vetor** (`ferramentas/diagrama.py`): captura de 580 px não aguenta zoom. O desenho sai
  dos dados e a auditoria o confronta com o OCR da tela, então não diverge do TIA Portal.
- **Marcas sobre as capturas vêm do OCR** (`ferramentas/marcas.py`): a posição é a do rótulo lido, nunca digitada.
- **Câmera presa à imagem:** nas telas, o enquadramento não passa da borda da captura (sem faixa vazia), e o número da
  marca compensa o zoom para ter sempre o mesmo tamanho. Captura muito pequena pode pedir `zoom_max` na cena.
- **Narração antes da imagem:** a duração de cada frase é o tempo da cena. Nunca `-shortest` no ffmpeg.
- **Vocabulário falado** (`video/pronuncia.json`): a voz lê grafia aportuguesada dos nomes em inglês, escolhida por
  transcrição reversa; a legenda mostra o nome exato.
- **Sem trilha musical:** em tutorial técnico a música é material supérfluo (princípio da coerência, Mayer).
- **Voz atual = edge-tts Francisca** (24 kHz). Trocar por voz paga (ElevenLabs/Azure) é mudar `video/preparar.py::sintetiza`.
- **Vermelho da Tex não vai sobre o azul** (contraste 2:1): sobre o azul o texto é branco e o vermelho entra como filete.
- **Geradores só gravam o que mudou** (`marcas.py`, `diagrama.py`): o build compara datas para saber se o vídeo está defasado.

## Ferramentas

Typst 0.15 · Vale 3.23 · LanguageTool 6.6 (local, Java 17) · RapidOCR (venv `tts`) · faster-whisper large-v3-turbo na GPU
(venv `faster-whisper`, DLLs CUDA via `add_dll_directory`) · edge-tts 7.2 · Playwright 1.62 · ffmpeg 9 · PyMuPDF
(AGPL: só uso interno, nunca vai junto da entrega).
