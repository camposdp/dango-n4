# Dango N4 - 段語 N4

Aplicativo web de flashcards para treinar vocabulário do livro **Nihongo Challenge Kotoba N4**.

Criado por Daniel Prado de Campos.

## Rodar localmente

```bash
npm install
npm run dev
```

## Gerar a base local

O PDF escaneado fica fora do Git. Para recriar a transcrição local:

```bash
python -m pip install -r requirements-ocr.txt
npm run ocr
npm run build:data
```

O app carrega `public/study-data.json` quando esse arquivo existe. Esse arquivo é gerado localmente e está no `.gitignore`, porque contém transcrição do material do livro.

## Vercel

O projeto está pronto para Vercel com:

- Build command: `npm run build`
- Output directory: `dist`
- Framework: Vite

Se você tiver autorização para publicar o conteúdo integral do livro, remova a regra de ignore de `public/study-data.json` ou configure esse arquivo como dado privado no seu fluxo de deploy.
