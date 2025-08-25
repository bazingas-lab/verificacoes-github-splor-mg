import requests
import csv
import os
from datetime import datetime

# Configurações
organization = 'bazingas-lab'

# Carregar variáveis de ambiente do arquivo .env
def load_env():
    """Carrega variáveis de ambiente do arquivo .env"""
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"📁 Carregando variáveis de {env_file}...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Variáveis de ambiente carregadas")
    else:
        print(f"⚠️  Arquivo {env_file} não encontrado")

def get_github_repos(organization, token=None):
    """
    Obtém todos os repositórios de uma organização do GitHub
    """
    repos = []
    page = 1
    per_page = 100  # Máximo por página
    
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
        print(f"🔑 Usando token: {token[:8]}...")
    else:
        print("⚠️  Nenhum token fornecido - acesso limitado")
    
    while True:
        url = f'https://api.github.com/orgs/{organization}/repos'
        params = {
            'page': page,
            'per_page': per_page,
            'type': 'all'  # Pega todos os tipos de repositórios
        }
        
        print(f"📄 Buscando página {page}...")
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar a API do GitHub: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            break
        
        page_repos = response.json()
        print(f"✅ Página {page}: {len(page_repos)} repositórios encontrados")
        
        if not page_repos:
            print("📄 Fim das páginas")
            break
            
        repos.extend(page_repos)
        page += 1
        
        # Verifica se há mais páginas
        if 'next' not in response.links:
            print("📄 Última página alcançada")
            break
    
    print(f"📊 Total de repositórios coletados: {len(repos)}")
    return repos

def export_to_csv(repos, filename):
    """
    Exporta os repositórios para um arquivo CSV
    """
    if not repos:
        print("Nenhum repositório encontrado.")
        return
    
    # Define as colunas do CSV
    fieldnames = [
        'name', 'archived'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for repo in repos:
            row = {field: repo.get(field, '') for field in fieldnames}
            writer.writerow(row)
    
    print(f"Arquivo '{filename}' criado com sucesso!")
    print(f"Total de repositórios exportados: {len(repos)}")

def main():
    # Carregar variáveis de ambiente
    load_env()
    
    # Opcional: Token do GitHub para aumentar limite de requisições
    # Gere um token em: https://github.com/settings/tokens
    github_token = os.getenv('GITHUB_TOKEN')  # Ou coloque seu token diretamente aqui
    
    if not github_token:
        print("❌ GITHUB_TOKEN não encontrado!")
        print("💡 Certifique-se de que o arquivo .env contém: GITHUB_TOKEN=seu_token_aqui")
        return
    
    print(f"Buscando repositórios da organização: {organization}")
    
    # Obtém os repositórios
    repos = get_github_repos(organization, github_token)
    
    if repos:
        # Cria o diretório docs se não existir
        docs_dir = 'docs'
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            print(f"📁 Diretório '{docs_dir}' criado")
        
        # Define o caminho do arquivo na pasta docs
        filename = os.path.join(docs_dir, 'repos_list.csv')
        
        # Exporta para CSV
        export_to_csv(repos, filename)
        
        # Mostra alguns exemplos
        print("\nPrimeiros 5 repositórios encontrados:")
        for repo in repos[:5]:
            print(f"- {repo['name']} ({repo.get('language', 'N/A')})")
    else:
        print("Nenhum repositório encontrado ou erro na requisição.")

if __name__ == "__main__":
    main()