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

def get_github_teams(organization, token=None):
    """
    Obtém todos os times de uma organização do GitHub
    """
    teams = []
    page = 1
    per_page = 100  # Máximo por página
    
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
        print(f"🔑 Usando token: {token[:8]}...")
    else:
        print("⚠️  Nenhum token fornecido - acesso limitado")
    
    while True:
        url = f'https://api.github.com/orgs/{organization}/teams'
        params = {
            'page': page,
            'per_page': per_page
        }
        
        print(f"📄 Buscando página {page} de times...")
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar a API do GitHub: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            break
        
        page_teams = response.json()
        print(f"✅ Página {page}: {len(page_teams)} times encontrados")
        
        if not page_teams:
            print("📄 Fim das páginas")
            break
            
        teams.extend(page_teams)
        page += 1
        
        # Verifica se há mais páginas
        if 'next' not in response.links:
            print("📄 Última página alcançada")
            break
    
    print(f"📊 Total de times coletados: {len(teams)}")
    return teams

def get_team_details(teams, organization, token=None):
    """
    Obtém detalhes adicionais de cada time
    """
    detailed_teams = []
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
    
    for i, team in enumerate(teams, 1):
        print(f"🔍 Obtendo detalhes do time {i}/{len(teams)}: {team['name']}")
        
        # Obter membros do time
        members_url = f"https://api.github.com/teams/{team['id']}/members"
        members_response = requests.get(members_url, headers=headers)
        
        members = []
        if members_response.status_code == 200:
            members = members_response.json()
            print(f"    👥 Membros encontrados: {len(members)}")
        else:
            print(f"    ⚠️  Erro ao buscar membros: {members_response.status_code}")
        
        # Obter repositórios do time
        repos_url = f"https://api.github.com/teams/{team['id']}/repos"
        repos_response = requests.get(repos_url, headers=headers)
        
        repos = []
        if repos_response.status_code == 200:
            repos = repos_response.json()
            print(f"    📚 Repositórios encontrados: {len(repos)}")
        else:
            print(f"    ⚠️  Erro ao buscar repositórios: {repos_response.status_code}")
        
        # Obter permissões do time
        permissions_url = f"https://api.github.com/teams/{team['id']}/repos"
        permissions_response = requests.get(permissions_url, headers=headers)
        
        permissions = []
        if permissions_response.status_code == 200:
            permissions = permissions_response.json()
            # Extrair permissões únicas
            unique_permissions = list(set([repo.get('permissions', {}).get('admin', False) for repo in permissions]))
            print(f"    🔐 Permissões encontradas: {len(unique_permissions)} tipos")
        else:
            print(f"    ⚠️  Erro ao buscar permissões: {permissions_response.status_code}")
        
        detailed_team = {
            'team_name': team['name'],
            'privacy': team.get('privacy', ''),
            'members_count': len(members),
            'repos_count': len(repos)
        }
        
        detailed_teams.append(detailed_team)
    
    return detailed_teams

def export_to_csv(teams, filename):
    """
    Exporta os times para um arquivo CSV
    """
    if not teams:
        print("Nenhum time encontrado.")
        return
    
    # Define as colunas do CSV
    fieldnames = [
        'team_name', 'privacy', 'members_count', 'repos_count'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for team in teams:
            writer.writerow(team)
    
    print(f"Arquivo '{filename}' criado com sucesso!")
    print(f"Total de times exportados: {len(teams)}")

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
    
    print(f"Buscando times da organização: {organization}")
    
    # Obtém os times básicos
    teams = get_github_teams(organization, github_token)
    
    if teams:
        # Obtém detalhes adicionais de cada time
        detailed_teams = get_team_details(teams, organization, github_token)
        
        # Cria o diretório docs se não existir
        docs_dir = 'docs'
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            print(f"📁 Diretório '{docs_dir}' criado")
        
        # Define o caminho do arquivo na pasta docs
        filename = os.path.join(docs_dir, 'teams_list.csv')
        
        # Exporta para CSV
        export_to_csv(detailed_teams, filename)
        
        # Mostra alguns exemplos
        print("\nPrimeiros 5 times encontrados:")
        for team in detailed_teams[:5]:
            print(f"- {team['team_name']} ({team['privacy']}) - {team['members_count']} membros, {team['repos_count']} repos")
    else:
        print("Nenhum time encontrado ou erro na requisição.")

if __name__ == "__main__":
    main()
