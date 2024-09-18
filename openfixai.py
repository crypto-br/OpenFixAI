import os
import re
import markdown
from dotenv import load_dotenv
from github import Github
from openai import OpenAI

# Importando variáveis de ambiente
load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')
GIT_TOKEN = os.getenv('GIT_TOKEN')
REPO_NAME = os.getenv('REPO_NAME')
BRANCH_NAME = os.getenv('BRANCH_NAME')

# Inicializando o cliente OpenAI
client = OpenAI(api_key=API_KEY)

def ler_arquivo_log(caminho_arquivo):
    """Lê o arquivo de log do Horusec."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            return arquivo.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
    except Exception as e:
        print(f"Erro ao ler o arquivo {caminho_arquivo}: {e}")
    return None

def extrair_vulnerabilidades(log):
    """Extrai vulnerabilidades do log."""
    if not log:
        print("Log vazio ou inválido.")
        return []

    padrao = re.compile(
        r'Language: (?P<language>.*?)\n'
        r'Severity: (?P<severity>.*?)\n'
        r'Line: (?P<line>.*?)\n'
        r'Column: (?P<column>.*?)\n'
        r'SecurityTool: (?P<security_tool>.*?)\n'
        r'Confidence: (?P<confidence>.*?)\n'
        r'File: (?P<file>.*?)\n'
        r'Code: (?P<code>.*?)\n'
        r'RuleID: (?P<rule_id>.*?)\n'
        r'Type: (?P<type>.*?)\n'
        r'ReferenceHash: (?P<reference_hash>.*?)\n'
        r'Details: (?P<details>.*?)\n',
        re.DOTALL
    )
    return [m.groupdict() for m in padrao.finditer(log)]

def consultar_openai(vulnerabilidade):
    """Consulta a API da OpenAI para obter sugestões de correção."""
    prompt = (
        f"Aqui está uma vulnerabilidade encontrada pelo Horusec:\n"
        f"{vulnerabilidade}\n"
        "Como posso corrigir essa vulnerabilidade?"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro ao consultar a API da OpenAI: {e}")
        return "Erro ao gerar sugestão de correção."

def gerar_relatorio_html(vulnerabilidades):
    """Gera um relatório em HTML das vulnerabilidades."""
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Vulnerabilidades</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h2 { color: #2F4F4F; }
            pre { background: #f4f4f4; padding: 10px; border: 1px solid #ddd; }
            .vulnerability { margin-bottom: 20px; }
            hr { border: 0; height: 1px; background: #ddd; margin-top: 20px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>Relatório de Vulnerabilidades</h1>
    """

    for vulnerabilidade in vulnerabilidades:
        detalhes = vulnerabilidade.get('details', 'Detalhes não encontrados')
        codigo = vulnerabilidade.get('code', 'Código não encontrado')
        sugestao = vulnerabilidade.get('sugestao', 'Sugestão não disponível')

        html += f"""
        <div class="vulnerability">
            <h2>Vulnerabilidade Encontrada</h2>
            <p><strong>Detalhes:</strong> {detalhes}</p>
            <p><strong>Código Vulnerável:</strong></p>
            <pre>{codigo}</pre>
            <p><strong>Sugestão de Correção:</strong></p>
            <pre>{markdown.markdown(sugestao)}</pre>
        </div>
        <hr>
        """

    html += """
    </body>
    </html>
    """
    return html

def extrair_codigo_corrigido(sugestao):
    """Extrai o código corrigido da sugestão fornecida pela OpenAI."""
    prompt = f"Extraia apenas o código corrigido da seguinte sugestão, mantendo a formatação de código:\n\n{sugestao}"
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro ao extrair código corrigido: {e}")
        return None

def create_pull_request(code_pr, detalhes, cleaned_path):
    """Cria um pull request no GitHub com a correção proposta."""
    if not code_pr or not cleaned_path:
        print("Código ou caminho inválido, PR não criado.")
        return None

    try:
        # Autenticação
        g = Github(GIT_TOKEN)
        repo = g.get_repo(REPO_NAME)

        # Criar um novo branch para a correção
        main_branch = repo.get_branch('main')
        repo.create_git_ref(ref=f'refs/heads/{BRANCH_NAME}', sha=main_branch.commit.sha)

        # Obter o arquivo atual do repositório
        file = repo.get_contents(cleaned_path, ref=BRANCH_NAME)

        # Atualizar o arquivo no novo branch
        repo.update_file(
            path=file.path,
            message='Sugestão de correção de código',
            content=code_pr,
            sha=file.sha,
            branch=BRANCH_NAME
        )

        # Criar um pull request
        pr = repo.create_pull(
            title='Correção de código',
            body=detalhes,
            head=BRANCH_NAME,
            base='main'
        )

        print(f"Pull Request criado: {pr.html_url}")
        return pr.html_url
    except Exception as e:
        print(f"Erro ao criar Pull Request: {e}")
        return None

def main():
    caminho_arquivo = "report.txt"
    log = ler_arquivo_log(caminho_arquivo)
    if not log:
        print("Nenhuma vulnerabilidade encontrada ou erro ao ler o arquivo de log.")
        return

    vulnerabilidades = extrair_vulnerabilidades(log)
    if not vulnerabilidades:
        print("Nenhuma vulnerabilidade encontrada.")
        return

    for vulnerabilidade in vulnerabilidades:
        detalhes = vulnerabilidade.get('details', 'Detalhes não encontrados')
        sugestao = consultar_openai(vulnerabilidade)
        vulnerabilidade['sugestao'] = sugestao

        code_pr = extrair_codigo_corrigido(sugestao)
        file_path = vulnerabilidade.get('file')
        cleaned_path = re.sub(r'\.horusec/[0-9a-fA-F-]+/', '', file_path) if file_path else None

        create_pull_request(code_pr, detalhes, cleaned_path)

    relatorio_html = gerar_relatorio_html(vulnerabilidades)
    try:
        with open('relatorio_vulnerabilidades.html', 'w', encoding='utf-8') as arquivo_html:
            arquivo_html.write(relatorio_html)
        print("Relatório de vulnerabilidades gerado com sucesso: relatorio_vulnerabilidades.html")
    except Exception as e:
        print(f"Erro ao salvar o relatório HTML: {e}")

if __name__ == "__main__":
    main()
