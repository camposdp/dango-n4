# Dango N4 - ダン語 N4

Aplicativo web de flashcards para treinar vocabulário do livro **Nihongo Challenge Kotoba N4**.

Criado por Daniel Prado de Campos.

## Rodar localmente

```bash
npm install
npm run dev
```

## Gerar a base

O PDF escaneado fica fora do Git. Para recriar a transcrição:

```bash
python -m pip install -r requirements-ocr.txt
npm run ocr
npm run build:data
```

O app carrega `public/study-data.json`. Esse arquivo está versionado para que o deploy no Vercel carregue todos os 32 capítulos.

## Vercel

O projeto está pronto para Vercel com:

- Build command: `npm run build`
- Output directory: `dist`
- Framework: Vite

## Progresso

O progresso é salvo automaticamente no `localStorage` do navegador. No app, os botões de exportar/importar geram e leem um arquivo `.dango`, útil para mover o estado entre celular e computador.

## Organização

O filtro principal mostra as 32 unidades do livro. A interface pública está focada em flashcards; os exercícios gerados permanecem no arquivo de dados para uso futuro, mas não aparecem na página.
