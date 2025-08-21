# GitHub Labels Sync Script

Script Python para sincronizar labels em todos os repositórios de uma organização GitHub.

## Funcionalidades

- ✅ Lista todos os repositórios de uma organização
- ✅ Cria/atualiza labels baseado em um template
- ✅ Remove labels que não estão no template
- ✅ Suporte a repositórios públicos e privados
- ✅ Tratamento de erros robusto
- ✅ Logs detalhados de todas as operações

## Instalação

1. Clone este repositório ou baixe os arquivos
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração

### 1. Criar Personal Access Token

1. Vá para **GitHub.com** → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Clique em **Generate new token (classic)**
3. Configure:
   - **Note**: `bazingas-lab-labels-sync`
   - **Expiration**: Escolha uma data futura
   - **Scopes**: 
     - `repo` (para acesso aos repositórios)
     - `workflow` (opcional, para workflows)

### 2. Preparar Template de Labels

Crie um arquivo `docs/labels-template` com o formato:

```
nome_label:descrição da label:cor_hex
bug:Problema ou erro no código:ff0000
feature:Nova funcionalidade:00ff00
documentation:Melhorias na documentação:0000ff
```

## Uso

### Uso Básico

```bash
python sync_labels.py --token SEU_TOKEN_AQUI --organization bazingas-lab
```

### Uso com Template Personalizado

```bash
python sync_labels.py --token SEU_TOKEN_AQUI --organization bazingas-lab --template caminho/para/template
```

### Parâmetros

- `--token`: GitHub Personal Access Token (obrigatório)
- `--organization`: Nome da organização (obrigatório)
- `--template`: Caminho para o arquivo de template (opcional, padrão: `docs/labels-template`)

## Exemplo de Execução

```bash
$ python sync_labels.py --token ghp_1234567890abcdef --organization bazingas-lab

Iniciando sincronização de labels para organização: bazingas-lab
Obtendo repositórios da organização: bazingas-lab
Encontrados 5 repositórios
Lendo template de labels de: docs/labels-template
Template carregado com 8 labels

Processando repositório: bazingas-lab/repo1
  Atualizando label: bug
  Atualizando label: feature
  Atualizando label: documentation
  Deletando label: old_label
  Mantendo label: bug
  Mantendo label: feature

Sincronização concluída para 5 repositórios!
```

## Vantagens sobre o GitHub Actions

- 🚀 **Execução local**: Não precisa esperar pela fila do GitHub Actions
- 🔧 **Debug fácil**: Logs detalhados e tratamento de erros
- 💻 **Controle total**: Execute quando quiser, pause, continue
- 🔒 **Segurança**: Token não fica exposto em logs públicos
- 📊 **Flexibilidade**: Fácil de modificar e adaptar

## Permissões Necessárias

Para que o script funcione, você precisa:

1. **Ser owner/admin** da organização, OU
2. **Ter permissão de admin** nos repositórios específicos

## Troubleshooting

### Erro: "Not Found" ao listar repositórios
- Verifique se o token tem permissão `repo`
- Confirme se você tem acesso à organização

### Erro: "Forbidden" ao criar labels
- Verifique se você tem permissão de admin no repositório
- Confirme se o token tem escopo `repo`

### Labels não são criadas
- Verifique o formato do arquivo de template
- Confirme se as cores são válidas (formato hex)

## Estrutura do Projeto

```
.
├── sync_labels.py          # Script principal
├── requirements.txt        # Dependências Python
├── README.md              # Este arquivo
└── docs/
    └── labels-template    # Template de labels
```
