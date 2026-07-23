# ReplyFlow

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-eea94b)
![Version](https://img.shields.io/badge/version-1.0.0-0d5c63)
![Language](https://img.shields.io/badge/python-3.11%2B-3776ab)
![Framework](https://img.shields.io/badge/FastAPI-0.115-009688)

An AI-assisted web application for organizing service responses, reusable templates and communication styles.

---

## Language Index

- [English version](#english-version) — you are here
- [Versão em português](#versão-em-português)

---

## English version

### Index

- [Description](#description)
- [Features](#features)
- [Architecture and design](#architecture-and-design)
- [Motivation](#motivation)
- [Installation](#installation)
- [Contributing](#contributing)

### Description

ReplyFlow helps support teams turn incoming requests into clear, consistent replies. Users can organize communication channels, create reusable response structures, define writing personalities and generate contextual drafts with AI.

### Features

- AI-assisted reply generation
- Reusable response structures by channel or platform
- Configurable tokens filled from the generation prompt
- Custom writing personalities
- Administrator and standard user roles
- Account approval workflow
- Shared and private templates
- Searchable response library
- MySQL persistence with SQLAlchemy

### Architecture and design

Main components:

- `app/main.py` — FastAPI routes and application workflows
- `app/models.py` — SQLAlchemy data models
- `app/database.py` — database initialization and default data
- `app/ai.py` — server-side integration with the configured AI provider
- `app/templates/` — Jinja2 user interface
- `app/static/` — styles, scripts and visual assets

General flow:

```text
Browser → FastAPI routes → business rules → SQLAlchemy → MySQL
                         ↘ AI provider API
```

### Motivation

- Reduce repetitive work in customer support
- Keep answers consistent without losing context
- Practice a complete Python web architecture
- Provide a reusable foundation for different service scenarios

### Installation

#### Requirements

- Python 3.11 or newer
- MySQL 8 or Docker
- An API key for the configured AI provider

#### Running the project

```bash
git clone https://github.com/MikaelTeixeira/ReplyFlow.git
cd ReplyFlow
python -m venv venv
```

Windows:

```bat
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
docker compose up -d
uvicorn app.main:app --reload
```

Linux or macOS:

```bash
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d
uvicorn app.main:app --reload
```

Update `.env` with a strong `SECRET_KEY`, valid database credentials and your AI API key. The first registered account becomes the approved administrator; later accounts require administrator approval.

Never commit `.env` or production credentials.

### Contributing

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Open a pull request.

---

## Versão em português

### Índice

- [Descrição](#descrição)
- [Funcionalidades](#funcionalidades)
- [Arquitetura e design](#arquitetura-e-design)
- [Motivação](#motivação)
- [Instalação](#instalação)
- [Contribuição](#contribuição)

### Descrição

O ReplyFlow ajuda equipes de atendimento a transformar solicitações recebidas em respostas claras e consistentes. Os usuários podem organizar canais de comunicação, criar estruturas reutilizáveis, definir personalidades de escrita e gerar rascunhos contextualizados com IA.

### Funcionalidades

- Geração de respostas com apoio de IA
- Estruturas reutilizáveis por canal ou plataforma
- Tokens configuráveis preenchidos pelo contexto informado no gerador
- Personalidades de escrita personalizadas
- Perfis de administrador e usuário comum
- Fluxo de aprovação de contas
- Modelos compartilhados e privados
- Biblioteca de respostas com busca
- Persistência em MySQL com SQLAlchemy

### Arquitetura e design

Componentes principais:

- `app/main.py` — rotas FastAPI e fluxos da aplicação
- `app/models.py` — modelos de dados do SQLAlchemy
- `app/database.py` — inicialização do banco e dados padrão
- `app/ai.py` — integração server-side com o provedor de IA configurado
- `app/templates/` — interface em Jinja2
- `app/static/` — estilos, scripts e recursos visuais

Fluxo geral:

```text
Navegador → rotas FastAPI → regras da aplicação → SQLAlchemy → MySQL
                               ↘ API do provedor de IA
```

### Motivação

- Reduzir trabalho repetitivo em operações de atendimento
- Manter respostas consistentes sem perder o contexto
- Praticar uma arquitetura web completa em Python
- Oferecer uma base reutilizável para diferentes cenários de suporte

### Instalação

#### Requisitos

- Python 3.11 ou mais recente
- MySQL 8 ou Docker
- Uma chave de API para o provedor de IA configurado

#### Rodando o projeto

```bat
git clone https://github.com/MikaelTeixeira/ReplyFlow.git
cd ReplyFlow
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
docker compose up -d
uvicorn app.main:app --reload
```

Preencha o `.env` com uma `SECRET_KEY` forte, credenciais válidas do banco e sua chave da API de IA. A primeira conta cadastrada se torna administradora aprovada; as seguintes dependem de aprovação.

Nunca envie o `.env` ou credenciais de produção ao repositório.

### Contribuição

1. Faça um fork do repositório.
2. Crie uma branch para sua alteração.
3. Implemente e teste a melhoria.
4. Abra um pull request.

---

Desenvolvido por Mikael Teixeira.
