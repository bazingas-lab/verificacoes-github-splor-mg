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

def get_github_members(organization, token=None):
    """
    Obtém todos os membros de uma organização do GitHub
    """
    members = []
    page = 1
    per_page = 100  # Máximo por página
    
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
        print(f"🔑 Usando token: {token[:8]}...")
    else:
        print("⚠️  Nenhum token fornecido - acesso limitado")
    
    while True:
        url = f'https://api.github.com/orgs/{organization}/members'
        params = {
            'page': page,
            'per_page': per_page
        }
        
        print(f"📄 Buscando página {page} de membros...")
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar a API do GitHub: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            break
        
        page_members = response.json()
        print(f"✅ Página {page}: {len(page_members)} membros encontrados")
        
        if not page_members:
            print("📄 Fim das páginas")
            break
            
        members.extend(page_members)
        page += 1
        
        # Verifica se há mais páginas
        if 'next' not in response.links:
            print("📄 Última página alcançada")
            break
    
    print(f"📊 Total de membros coletados: {len(members)}")
    return members

def get_member_details(members, organization, token=None):
    """
    Obtém detalhes adicionais de cada membro
    """
    detailed_members = []
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
    
    for i, member in enumerate(members, 1):
        print(f"🔍 Obtendo detalhes do membro {i}/{len(members)}: {member['login']}")
        
        # Obter informações detalhadas do usuário
        user_url = f"https://api.github.com/users/{member['login']}"
        user_response = requests.get(user_url, headers=headers)
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            
            # Obter informações da organização (tipo de usuário, 2FA, etc.)
            org_url = f"https://api.github.com/orgs/{organization}/memberships/{member['login']}"
            org_response = requests.get(org_url, headers=headers)
            
            org_data = {}
            if org_response.status_code == 200:
                org_data = org_response.json()
                print(f"    👤 Role na org: {org_data.get('role')}, State: {org_data.get('state')}")
            else:
                print(f"    ⚠️  Erro ao buscar membership: {org_response.status_code}")
            
            # Obter times do usuário na organização
            teams = []
            
            # Tentativa 1: API específica da organização (mais precisa)
            teams_url = f"https://api.github.com/orgs/{organization}/members/{member['login']}/teams"
            teams_response = requests.get(teams_url, headers=headers)
            
            if teams_response.status_code == 200:
                teams = teams_response.json()
                print(f"    📋 Times encontrados (API org): {len(teams)}")
            else:
                print(f"    ⚠️  Erro ao buscar times via API org: {teams_response.status_code}")
                
                # Tentativa 2: Buscar todos os times da organização e verificar membros
                org_teams_url = f"https://api.github.com/orgs/{organization}/teams"
                org_teams_response = requests.get(org_teams_url, headers=headers)
                
                if org_teams_response.status_code == 200:
                    all_org_teams = org_teams_response.json()
                    user_teams = []
                    
                    # Para cada time da organização, verificar se o usuário é membro
                    for team in all_org_teams:
                        team_members_url = f"https://api.github.com/teams/{team['id']}/members"
                        team_members_response = requests.get(team_members_url, headers=headers)
                        
                        if team_members_response.status_code == 200:
                            team_members = team_members_response.json()
                            # Verificar se o usuário atual está na lista de membros
                            if any(team_member['login'] == member['login'] for team_member in team_members):
                                user_teams.append(team)
                    
                    teams = user_teams
                    print(f"    📋 Times encontrados (verificação manual): {len(teams)}")
                else:
                    print(f"    ⚠️  Erro ao buscar times da organização: {org_teams_response.status_code}")
            
            # Obter roles do usuário na organização
            # A API de roles pode não estar disponível, vamos usar uma abordagem alternativa
            # Verificando se o usuário é owner/admin através do membership
            is_owner = False
            if org_response.status_code == 200:
                org_data = org_response.json()
                # Verificar se é owner através do campo 'role' e 'state'
                is_owner = org_data.get('role') == 'admin' and org_data.get('state') == 'active'
            
            # Para roles, vamos verificar se é owner (que tem permissões especiais)
            roles_count = 1 if is_owner else 0
            
            # Determinar o tipo de usuário correto
            user_type = 'Member'
            if org_data.get('role') == 'admin':
                user_type = 'Owner'  # Na interface do GitHub, admin aparece como "Owner"
            
            detailed_member = {
                'github_profile': member['login'],
                'url_perfil': f"https://github.com/orgs/{organization}/people/{member['login']}",
                'two_factor_auth': user_data.get('two_factor_authentication', False),
                'tipo_usuario': user_type,
                'qtd_teams': len(teams),
                'qtde_roles': roles_count
            }
            
            detailed_members.append(detailed_member)
        else:
            print(f"⚠️  Erro ao obter detalhes de {member['login']}: {user_response.status_code}")
    
    return detailed_members

def export_to_csv(members, filename):
    """
    Exporta os membros para um arquivo CSV
    """
    if not members:
        print("Nenhum membro encontrado.")
        return
    
    # Define as colunas do CSV conforme especificado
    fieldnames = [
        'github_profile', 'url_perfil', 'two_factor_auth', 
        'tipo_usuario', 'qtd_teams', 'qtde_roles'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for member in members:
            writer.writerow(member)
    
    print(f"Arquivo '{filename}' criado com sucesso!")
    print(f"Total de membros exportados: {len(members)}")

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
    
    print(f"Buscando membros da organização: {organization}")
    
    # Obtém os membros básicos
    members = get_github_members(organization, github_token)
    
    if members:
        # Obtém detalhes adicionais de cada membro
        detailed_members = get_member_details(members, organization, github_token)
        
        # Cria o diretório docs se não existir
        docs_dir = 'docs'
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            print(f"📁 Diretório '{docs_dir}' criado")
        
        # Define o caminho do arquivo na pasta docs
        filename = os.path.join(docs_dir, 'members_list.csv')
        
        # Exporta para CSV
        export_to_csv(detailed_members, filename)
        
        # Mostra alguns exemplos
        print("\nPrimeiros 5 membros encontrados:")
        for member in detailed_members[:5]:
            print(f"- {member['github_profile']} ({member['tipo_usuario']}) - {member['qtd_teams']} times, {member['qtde_roles']} roles")
    else:
        print("Nenhum membro encontrado ou erro na requisição.")

if __name__ == "__main__":
    main()
