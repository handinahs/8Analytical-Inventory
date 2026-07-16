# 8Analytical Inventory

Sistema simples de controle de estoque, inventário e relatórios para almoxarifado.

O app foi feito em Python com Streamlit e usa um banco SQLite chamado `estoque.db`.

## Principais funções

- Cadastro de produtos
- Entrada de estoque
- Saída de estoque
- Estoque atual
- Ajuste de saldo
- Ajuste de posição/localização
- Histórico de movimentações
- Cancelamento de movimentações
- Requisição de compras em Excel
- Relatório de estoque em Excel
- Desativar e reativar produtos
- Backup do banco de dados

## Requisitos

Antes de rodar o app, a máquina precisa ter:

- Python instalado
- As dependências do arquivo `requirements.txt`

## Como instalar as dependências

Abra o terminal na pasta do projeto e rode:

```bash
python -m pip install -r requirements.txt
```

## Como rodar o app

Na pasta do projeto, rode:

```bash
python -m streamlit run app.py
```

Ou, no Windows, dê dois cliques no arquivo:

```txt
abrir_app.bat
```

Esse arquivo executa automaticamente o comando acima.

## Banco de dados

O app usa o arquivo:

```txt
estoque.db
```

Esse arquivo deve ficar na mesma pasta do `app.py`.

Se o `estoque.db` não existir, o app cria as tabelas principais ao iniciar, mas o banco começará vazio.

## Atenção: não subir o banco para o GitHub

O arquivo `estoque.db` contém os dados reais do estoque. Por segurança, ele não deve ser enviado para o GitHub.

O arquivo `.gitignore` já está configurado para ignorar:

```gitignore
estoque.db
backups/
__pycache__/
*.pyc
.env
.venv/
.codex/
```

Antes de fazer `git push`, confira com:

```bash
git status
```

Verifique se `estoque.db` e a pasta `backups/` não aparecem na lista de arquivos que serão enviados.

## Backup

A página **Backup do Banco** permite:

- criar uma cópia local do `estoque.db` na pasta `backups`;
- baixar uma cópia do banco pelo navegador;
- consultar os backups salvos.

Recomendação: antes de grandes ajustes de estoque, crie um backup.

## Como usar em outra máquina

1. Baixe o projeto pelo GitHub.
2. Extraia a pasta.
3. Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

4. Coloque um arquivo `estoque.db` na mesma pasta do `app.py`.
5. Rode o app:

```bash
python -m streamlit run app.py
```

Ou use o `abrir_app.bat`.

## Estrutura principal

```txt
app.py                  # Tela principal / dashboard
pages/                  # Páginas do Streamlit
utils/                  # Funções auxiliares
migrations/             # Ajustes de banco
assets/                 # Logo e imagens
requirements.txt        # Dependências do projeto
abrir_app.bat           # Atalho para abrir o app no Windows
```

## Observação

Este app foi pensado para uso interno em um almoxarifado pequeno, priorizando simplicidade, segurança dos dados e facilidade de operação.
