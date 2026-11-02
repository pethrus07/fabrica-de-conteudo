# Estúdio de Máquinas · Celiware

Formulário onde o cliente junta o que tem de uma máquina (texto, fotos, vídeos, áudios, documentos) e gera um `.zip` para a produção de vídeos e manuais.

- **Um arquivo só:** `site/index.html`, sem build. Publicado no Cloudflare Pages (`npm run deploy`).
- **Blocos ajustáveis:** modelo de partida (completa / só vídeo / em branco); dá para remover, reordenar, renomear, duplicar e adicionar blocos, inclusive o "Bloco livre".
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

## Próximas melhorias

- **Colar imagem com Ctrl+V** (pedido do cliente na reunião de 05/10/2026): a captura do Windows entra
  no bloco como arquivo original, sem recompressão, e vai para o `.zip` como as outras mídias.
  Prometido a ele como melhoria, sem data.

## Teste

```
npm install
PLAYWRIGHT_BROWSERS_PATH=%LOCALAPPDATA%\ms-playwright npm test
```

Preenche uma máquina num Pixel 7 emulado (microfone falso), recarrega, gera o `.zip`, reabre num contexto limpo e confere as contagens.
