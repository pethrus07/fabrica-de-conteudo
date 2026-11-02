# Estúdio de Máquinas

Formulário em que o fabricante de uma máquina junta o que tem dela (texto, fotos, vídeos, áudios, documentos) e gera um `.zip` que a Fábrica de Conteúdo usa para produzir vídeos e manuais. É a entrada da esteira.

Até 01/11/2026 vivia no repositório próprio `celiware-estudio`; foi trazido para cá com o histórico (`git subtree add`). O histórico antigo está no segundo pai do commit `b925c6c` (`git log b925c6c^2`).

- **Um arquivo só:** `site/index.html`, sem build.
- **Blocos ajustáveis:** modelo de partida (completa, só vídeo, em branco); dá para remover, reordenar, renomear, duplicar e adicionar blocos, inclusive o "Bloco livre".
- **Mídia na qualidade original:** os arquivos ficam no IndexedDB do aparelho como chegaram e entram no `.zip` byte a byte (modo STORE, ZIP64 acima de 4 GB). O `.zip` é montado por referência aos arquivos, sem carregá-los na memória, para o celular aguentar vídeo grande.
- **Áudio:** gravação no navegador (Opus/WebM 128 kbps, sem cancelamento de eco, supressão de ruído nem ganho automático), por bloco, por item e na narração geral. A gravação é copiada a cada 5 s; se a página cair, é recuperada na próxima abertura.
- **Outro aparelho:** "Máquinas › Continuar de um .zip" reabre um pacote gerado, com todos os arquivos.

## Pacote

```
<maquina>_<data>/
  LEIA-PRIMEIRO.md   regras de leitura para a produção
  RESUMO.md          tudo o que foi escrito, bloco por bloco
  pedido.json        o mesmo, estruturado (+ _estado para reabrir)
  00-narracao/       áudios gerais
  NN-<bloco>/        um por bloco, na ordem; itens em subpasta
```

## Publicação

Está no ar no Cloudflare Pages, projeto `celiware-estudio` (`celiware-estudio.pages.dev`). O deploy é manual, a partir **desta pasta** (o caminho antigo `~/Projetos/celiware-estudio` não tem mais o site):

```
cd fabrica-de-conteudo/estudio
npm install
npm run deploy      # wrangler pages deploy site --project-name=celiware-estudio --branch=main
```

Conferido em 01/11/2026: o `index.html` no ar é igual ao `site/index.html` desta pasta (só muda o fim de linha). A mudança de pasta não mexeu no site.

## Teste

```
npm install
PLAYWRIGHT_BROWSERS_PATH=%LOCALAPPDATA%\ms-playwright npm test
```

Preenche uma máquina fictícia num Pixel 7 emulado (microfone falso), recarrega, gera o `.zip`, reabre num contexto limpo e confere as contagens. As fixtures (fotos, vídeo, PDF) são criadas pelo próprio teste em `test/out/`, que é ignorado pelo git.

## Próximas melhorias

- **Colar imagem com Ctrl+V:** a captura do Windows entra no bloco como arquivo original, sem recompressão, e vai para o `.zip` como as outras mídias. Pedido do cliente em 05/10/2026, sem data.
