# Guia Técnico SV660N — edição MVP

PDF de 8 páginas sobre o servo drive **Inovance SV660N**, para engenheiros e técnicos de automação.
Saída: `SV660N-Guia-Tecnico-MVP.pdf` (A4, 1,6 MB, texto pesquisável).

## Como reconstruir

```bash
bash build.sh
```

Renderiza `sv660n.html` via Chrome headless. Requisitos: Google Chrome instalado no caminho padrão do Windows.

## Estrutura

| Arquivo | O que é |
|---|---|
| `sv660n.html` | Fonte única do documento — 8 `<section class="page">`, uma por página |
| `build.sh` | Chrome headless → PDF |
| `fonts/` | IBM Plex Sans / Condensed / Mono em **TTF estático** |
| `img/` | Imagens já redimensionadas e comprimidas para o print |
| `img/orig/` | Originais em alta, caso precise re-exportar em outro tamanho |
| `img/credits.json` | Autoria e licença de cada foto |

## Decisões que não são óbvias (não desfaça sem motivo)

- **`@page` é `210mm × 296mm`**, não 297. Com 297 o Chrome estoura para 9 páginas por arredondamento.
- **Fontes precisam ser TTF estático.** A IBM Plex Sans no repositório do Google Fonts só existe como fonte
  variável, e fonte variável vira **Type3** no PDF do Chrome (texto borrado, não pesquisável). Os pesos aqui
  foram instanciados com `fontTools.varLib.instancer` a partir da variável.
- **Sem `filter:` CSS em imagem.** Qualquer filtro força o Chrome a rasterizar a imagem como PNG sem perdas —
  só a capa levava o PDF de 1,6 MB para 13 MB. O tratamento de cor da capa está gravado no próprio JPEG.
- **Glifos ausentes na Plex:** `▸` (U+25B8) e `⁻` (U+207B) não existem na fonte e caem em Times New Roman.
  O marcador triangular é feito com `border` em CSS e o expoente usa `<sup>−4</sup>`.
- Cada `.page` tem `overflow:hidden` — conteúdo que passar do limite **some sem aviso**. Depois de editar,
  rode a verificação abaixo.

## Verificação depois de editar

```bash
python - <<'EOF'
import fitz
d = fitz.open("SV660N-Guia-Tecnico-MVP.pdf")
print("páginas:", len(d))                    # tem que dar 8
print("fallback:", [(i+1, s['font'])
      for i in range(len(d)) for b in d[i].get_text('dict')['blocks']
      for l in b.get('lines', []) for s in l['spans']
      if 'Plex' not in s['font']] or "nenhum")
for i, p in enumerate(d):                    # inspeção visual página a página
    p.get_pixmap(dpi=104).save(f"pg{i+1}.png")
EOF
```

Conferir as imagens: nenhum texto pode encostar no rodapé e nenhuma página pode terminar com um bloco cortado.

## Fontes técnicas

Todos os números vêm da documentação oficial da Inovance (Advanced User Guide do SV660N, flyer L6210209 V0.6,
página de produto) e do registro do produto na EtherCAT Technology Group. As referências estão listadas na
p. 8 do próprio PDF. **Nenhuma especificação foi estimada.**
