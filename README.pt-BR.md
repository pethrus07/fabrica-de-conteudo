[English](README.md)

# Fábrica de Conteúdo

Um experimento: o material técnico de uma máquina industrial entra uma vez e saem manual, guias rápidos e vídeo de treinamento. Cada peça é gerada de um único arquivo de dados e auditada antes da entrega; auditoria reprovada para o build.

## Status

Experimento, pausado (11/2026). Um piloto pago entregue em 10/2026 para um cliente do setor de automação industrial (manual, três guias rápidos e um vídeo de 13 minutos). Sem produção em andamento.

## O problema

Quem constrói máquina termina todo projeto com manual, vídeo e treinamento, e essa fase atrasa a entrega. O conhecimento está em fotos, capturas de tela, programa de CLP e explicação falada, não num documento. A fábrica junta esse material num formulário e transforma em peças prontas sem ninguém redigitar texto técnico.

## Como funciona

1. **Estúdio de Máquinas** (`estudio/`): formulário web de um arquivo só. O cliente junta texto, fotos, vídeos, áudios e documentos por bloco e baixa um `.zip` com a mídia original.
2. **Dados**: um script lê o pacote para um único JSON. Cada pino, passo, aviso e termo aponta de onde veio (áudio e minuto, captura de tela, texto do formulário, página pública).
3. **Peças**: o Typst gera o manual e os guias (PDF/UA-1); o vídeo é renderizado quadro a quadro com telas, voz sintetizada e ffmpeg. Nada de vídeo generativo.
4. **Auditorias**: fonte embutida, todo número rastreável aos dados, termos proibidos, vocabulário controlado, legibilidade, ortografia (LanguageTool) e, no vídeo, loudness, transcrição reversa contra o roteiro e limites de legenda. Qualquer reprovação aborta.

## Pastas

```
estudio/                  Estúdio de Máquinas (formulário → .zip), no Cloudflare Pages; teste e2e com Playwright
pilotos/<piloto>/         uma pasta por entrega: dados, build.py, manual (Typst), vídeo, auditorias
exemplos/sv660n-guia/     exemplo: guia técnico de 8 páginas feito só com a documentação pública do fabricante
teste-qa-plc/             teste de QA: duas versões de um comparativo de CLPs, mesmos dados, uma neutra e uma enviesada sem dado falso
docs/arquitetura/         diagramas (UML, BPMN, C4)
index.html                página de conceito da fábrica
```

As saídas geradas (`pilotos/*/entrega/`, `teste-qa-plc/saida/`, PDF, MP4, DOCX) não ficam no git; cada build recria.

## Rodar

```bash
# Estúdio de Máquinas, teste local (Playwright)
cd estudio && npm install && npm test

# um piloto: só documentos (~2 min) ou tudo com vídeo (~20 min)
cd pilotos/<piloto> && python build.py --sem-video

# guia SV660N (precisa do Google Chrome)
cd exemplos/sv660n-guia && bash build.sh
```

O build do piloto precisa de Typst, Python 3, ffmpeg, Node e um LanguageTool local. O pacote de entrada do cliente e a marca do cliente não fazem parte da árvore pública.

## Decisões e limites conhecidos

- As peças saem na marca do cliente final, não na da fábrica. As capturas de marca e do site são coletadas por script e ficam fora do git.
- Testado em um piloto só. O passo de "pacote" para "arquivo de dados" ainda é um script por versão do pacote.
- O Estúdio de Máquinas não foi testado em iPhone físico.

## Roadmap

[docs/ROADMAP.md](docs/ROADMAP.md)

## Licença

Todos os direitos reservados.
