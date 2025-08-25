# Verificações GitHub

Scripts para extrair e sincronizar informações de organizações GitHub.

## Scripts Disponíveis

### 1. Listar Repositórios
```bash
python scripts/repos_list.py
```
Gera `docs/repos_list.csv` com todos os repositórios da organização.

### 2. Listar Membros
```bash
python scripts/members.py
```
Gera `docs/members_list.csv` com todos os membros da organização.

### 3. Listar Times
```bash
python scripts/teams.py
```
Gera `docs/teams_list.csv` com todos os times da organização.

### 4. Sincronizar Labels
```bash
python scripts/labels_sync.py
```
Sincroniza labels em todos os repositórios baseado em `docs/labels.yaml`.

## Configuração

1. **Criar arquivo `.env`** na raiz do projeto:
```bash
GITHUB_TOKEN=seu_token_aqui
```

2. **Gerar token GitHub** em: Settings → Developer settings → Personal access tokens
   - Escopo: `repo` (para acesso aos repositórios)

## Instalação

```bash
pip install -r requirements.txt
```

## Organização

- **`scripts/`**: Scripts Python para extração de dados
- **`docs/`**: Arquivos CSV gerados e templates YAML
- **`.github/workflows/`**: Workflows GitHub Actions para automação
