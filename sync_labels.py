#!/usr/bin/env python3
"""
Script para sincronizar labels em todos os repositórios de uma organização GitHub.
Replica a funcionalidade do workflow GitHub Actions labels-update.
"""

import os
import sys
import requests
import argparse
from typing import List, Dict, Optional
from pathlib import Path

class GitHubLabelsSync:
    def __init__(self, token: str, organization: str):
        self.token = token
        self.organization = organization
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
    
    def get_organization_repositories(self) -> List[str]:
        """Obtém lista de repositórios da organização."""
        print(f"Obtendo repositórios da organização: {self.organization}")
        
        repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f"{self.base_url}/orgs/{self.organization}/repos"
            params = {
                'page': page,
                'per_page': per_page,
                'type': 'all'  # Inclui privados e públicos
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Erro ao obter repositórios: {response.status_code}")
                print(response.text)
                break
            
            page_repos = response.json()
            
            if not page_repos:
                break
                
            for repo in page_repos:
                repos.append(repo['full_name'])
            
            page += 1
        
        print(f"Encontrados {len(repos)} repositórios")
        return repos
    
    def read_labels_template(self, template_path: str = "docs/labels-template") -> List[Dict]:
        """Lê o template de labels do arquivo."""
        print(f"Lendo template de labels de: {template_path}")
        
        if not os.path.exists(template_path):
            print(f"Erro: Arquivo de template não encontrado: {template_path}")
            return []
        
        labels = []
        
        with open(template_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Parse da linha no formato: nome:descrição:cor
                    parts = line.split(':')
                    if len(parts) >= 3:
                        name = parts[0].strip()
                        color = parts[-1].strip()
                        description = ':'.join(parts[1:-1]).strip()
                        
                        labels.append({
                            'name': name,
                            'description': description,
                            'color': color
                        })
                    else:
                        print(f"Aviso: Linha {line_num} mal formatada: {line}")
                except Exception as e:
                    print(f"Erro ao processar linha {line_num}: {line} - {e}")
        
        print(f"Template carregado com {len(labels)} labels")
        return labels
    
    def sync_labels_for_repository(self, repo: str, labels_template: List[Dict]):
        """Sincroniza labels para um repositório específico."""
        print(f"\nProcessando repositório: {repo}")
        
        # Criar/atualizar labels do template
        for label in labels_template:
            print(f"  Atualizando label: {label['name']}")
            
            # Tentar atualizar label existente
            update_success = self.update_label(repo, label)
            
            if not update_success:
                # Se falhar, criar nova label
                print(f"    Criando nova label: {label['name']}")
                self.create_label(repo, label)
        
        # Obter labels atuais
        current_labels = self.get_current_labels(repo)
        
        # Deletar labels que não estão no template
        template_label_names = {label['name'] for label in labels_template}
        
        for current_label in current_labels:
            if current_label not in template_label_names:
                print(f"  Deletando label: {current_label}")
                self.delete_label(repo, current_label)
            else:
                print(f"  Mantendo label: {current_label}")
    
    def update_label(self, repo: str, label: Dict) -> bool:
        """Atualiza uma label existente."""
        url = f"{self.base_url}/repos/{repo}/labels/{label['name']}"
        data = {
            'name': label['name'],
            'description': label['description'],
            'color': label['color']
        }
        
        response = requests.patch(url, headers=self.headers, json=data)
        return response.status_code == 200
    
    def create_label(self, repo: str, label: Dict) -> bool:
        """Cria uma nova label."""
        url = f"{self.base_url}/repos/{repo}/labels"
        data = {
            'name': label['name'],
            'description': label['description'],
            'color': label['color']
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.status_code == 201
    
    def get_current_labels(self, repo: str) -> List[str]:
        """Obtém lista de labels atuais do repositório."""
        url = f"{self.base_url}/repos/{repo}/labels"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"    Erro ao obter labels atuais: {response.status_code}")
            return []
        
        labels = response.json()
        return [label['name'] for label in labels]
    
    def delete_label(self, repo: str, label_name: str) -> bool:
        """Deleta uma label."""
        url = f"{self.base_url}/repos/{repo}/labels/{label_name}"
        response = requests.delete(url, headers=self.headers)
        return response.status_code == 204
    
    def run_sync(self, template_path: str = "docs/labels-template"):
        """Executa a sincronização completa."""
        print(f"Iniciando sincronização de labels para organização: {self.organization}")
        
        # Obter repositórios
        repos = self.get_organization_repositories()
        if not repos:
            print("Nenhum repositório encontrado. Verifique o token e permissões.")
            return
        
        # Ler template
        labels_template = self.read_labels_template(template_path)
        if not labels_template:
            print("Template de labels vazio. Verifique o arquivo de template.")
            return
        
        # Sincronizar cada repositório
        for repo in repos:
            try:
                self.sync_labels_for_repository(repo, labels_template)
            except Exception as e:
                print(f"Erro ao processar repositório {repo}: {e}")
                continue
        
        print(f"\nSincronização concluída para {len(repos)} repositórios!")

def main():
    parser = argparse.ArgumentParser(description='Sincronizar labels em repositórios de uma organização GitHub')
    parser.add_argument('--token', required=True, help='GitHub Personal Access Token')
    parser.add_argument('--organization', required=True, help='Nome da organização')
    parser.add_argument('--template', default='docs/labels-template', help='Caminho para o arquivo de template (padrão: docs/labels-template)')
    
    args = parser.parse_args()
    
    # Verificar se o arquivo de template existe
    if not os.path.exists(args.template):
        print(f"Erro: Arquivo de template não encontrado: {args.template}")
        sys.exit(1)
    
    # Criar instância e executar
    syncer = GitHubLabelsSync(args.token, args.organization)
    syncer.run_sync(args.template)

if __name__ == "__main__":
    main()
