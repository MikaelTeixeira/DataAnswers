# Mensagens Automaticas

Projeto simples com FastAPI, login/registro e MySQL. As respostas padrao ficam no codigo da aplicacao, e as respostas personalizadas do usuario ficam apenas no navegador via `localStorage`.

## FastAPI vale a pena aqui?

Sim, vale. Mesmo sendo um site simples, login, registro, sessoes e MySQL ja colocam o projeto no territorio de uma aplicacao web real. FastAPI entrega isso com pouca estrutura, boa organizacao e espaco para crescer sem virar bagunca. Fazer sem framework exigiria reimplementar roteamento, formularios, sessoes e seguranca basica.

## Como rodar

1. Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instale as dependencias:

```powershell
pip install -r requirements.txt
```

3. Copie o arquivo de ambiente:

```powershell
Copy-Item .env.example .env
```

4. Ajuste o `DATABASE_URL` no `.env` com o usuario e senha do MySQL local:

```env
DATABASE_URL=mysql+pymysql://root:sua_senha@localhost:3306/mensagens_automaticas
```

Ao iniciar, a aplicacao cria o banco `mensagens_automaticas` e as tabelas se eles ainda nao existirem.

5. Rode o servidor pelo ambiente virtual:

```powershell
.\venv\Scripts\uvicorn.exe app.main:app --reload
```

Depois acesse `http://127.0.0.1:8000`.

## Estrutura

```text
app/
  auth.py
  config.py
  database.py
  main.py
  models.py
  static/
    css/styles.css
    js/messages.js
  templates/
    base.html
    dashboard.html
    login.html
    register.html
```
