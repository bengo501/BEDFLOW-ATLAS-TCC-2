# guia de execução rápida

este ficheiro ficou como atalho. a documentação atualizada está em:

- português: [docs/pt/inicio.md](pt/inicio.md) · [docs/pt/README.md](pt/README.md) · [README.pt.md](../README.pt.md)
- english: [docs/en/getting-started.md](en/getting-started.md) · [README.md](../README.md)

## portas atuais

- backend: `http://127.0.0.1:8000` (swagger: `/docs`)
- frontend: `http://127.0.0.1:5173`

o vite faz proxy de `/api`, `/files` e `/generated` para a porta 8000.

## windows

1. clique duplo em `EXECUTAR_BEDFLOW-ATLAS.bat` na raiz (verifica e instala requisitos).
2. no wizard, escolha **2** para subir backend + frontend.

manual:

```bash
python bed_wizard.py

cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

cd frontend
npm install
npm run dev
```
