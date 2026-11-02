[Português](README.pt-BR.md)

# Content Factory

An experiment: the technical material of an industrial machine goes in once, and a manual, quick guides and a training video come out. Every piece is generated from one data file and audited before delivery; a failed audit stops the build.

## Status

Experiment, paused (2026-11). One paid pilot delivered in 2026-10 for a client in the industrial automation sector (manual, three quick guides and a 13 minute video). No ongoing production.

## The problem

Machine builders end every project with a manual, a video and a training session, and that phase delays delivery. The knowledge is in photos, screen captures, PLC programs and voice explanations, not in a document. The factory collects that material in a form and turns it into finished pieces without anyone retyping technical text.

## How it works

1. **Machine Studio** (`estudio/`): a single-file web form. The client gathers text, photos, videos, audio and documents per block and downloads a `.zip` with the original media.
2. **Data**: a script reads the package into one JSON file. Each pin, step, warning and term points to where it came from (audio and minute, screenshot, form text, public web page).
3. **Pieces**: Typst renders the manual and the guides (PDF/UA-1); the video is rendered frame by frame from screens plus text-to-speech and ffmpeg. Nothing is generative video.
4. **Audits**: fonts embedded, every number traceable to the data, forbidden terms, controlled vocabulary, readability, spelling (LanguageTool), and for video loudness, reverse transcription against the script, subtitle limits. Any failure aborts.

## Folders

```
estudio/                  Machine Studio (form → .zip), deployed on Cloudflare Pages; e2e test with Playwright
pilotos/<pilot>/          one folder per delivery: data, build.py, manual (Typst), video, audits
exemplos/sv660n-guia/     example: 8 page technical guide built only from the manufacturer's public docs
teste-qa-plc/             QA test: two versions of a PLC comparison, same data, one neutral and one biased without false data
docs/arquitetura/         diagrams (UML, BPMN, C4)
index.html                concept page of the factory
```

Generated outputs (`pilotos/*/entrega/`, `teste-qa-plc/saida/`, PDFs, MP4, DOCX) are not in git; each build recreates them.

## Run

```bash
# Machine Studio, local test (Playwright)
cd estudio && npm install && npm test

# a pilot: documents only (~2 min) or everything with video (~20 min)
cd pilotos/<pilot> && python build.py --sem-video

# SV660N guide (needs Google Chrome)
cd exemplos/sv660n-guia && bash build.sh
```

The pilot build needs Typst, Python 3, ffmpeg, Node and a local LanguageTool. The client input package and the client brand assets are not in the public tree.

## Decisions and known limits

- The pieces carry the end client's brand, not the factory's. Brand and site captures are collected by script and stay out of git.
- Tested on one pilot only. The step from "package" to "data file" is still a script per version of the package.
- Machine Studio was not tested on a physical iPhone.

## Roadmap

[docs/ROADMAP.md](docs/ROADMAP.md)

## License

All rights reserved.
