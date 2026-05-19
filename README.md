# Ursula Reply

Ursula Reply e uma aplicacao web para gerar respostas de atendimento escolar com apoio de IA. O sistema foi pensado para agilizar mensagens relacionadas a plataformas educacionais, acessos, senhas, orientacoes e comunicacoes com responsaveis.

## Como funciona

O usuario informa o nome do responsavel, o nome do aluno, a plataforma e a situacao do atendimento. A aplicacao envia essas informacoes para a API de IA configurada no ambiente e retorna uma mensagem pronta para copiar.

Administradores podem cadastrar plataformas e estruturas de texto. Essas estruturas servem como base para a IA, especialmente quando houver passo a passo, orientacoes fixas ou regras especificas de uma plataforma.

## Perfis de usuario

O sistema possui dois tipos de perfil:

- Administrador: gerencia plataformas, usuarios e estruturas globais.
- Usuario comum: gera respostas e pode criar estruturas proprias.

Estruturas criadas por administradores ficam disponiveis para todos os usuarios. Estruturas criadas por usuarios comuns ficam disponiveis apenas para a propria conta.

## Dados e configuracao

Usuarios, plataformas e estruturas ficam salvos em banco de dados MySQL. Chaves de API, senha do banco e outros dados sensiveis devem ficar apenas no arquivo `.env`, que nao deve ser enviado ao GitHub.

O arquivo `.env.example` serve apenas como modelo de configuracao e nao deve conter credenciais reais.

## Autoria e uso autorizado

Desenvolvido por Mikael.

Uso autorizado para o Colegio Santa Ursula.

Este projeto e disponibilizado para uso interno autorizado pelo Colegio Santa Ursula. A copia, redistribuicao, revenda ou uso por terceiros nao esta autorizada sem permissao expressa do autor.
