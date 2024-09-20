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
    """Gera um relatório em HTML das vulnerabilidades com CSS aprimorado."""
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Vulnerabilidades</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f9f9f9;
                margin: 0;
                padding: 0;
            }
            header {
                background-color: #343a40;
                color: #fff;
                padding: 20px;
                text-align: center;
            }
            .container {
                margin: 20px auto;
                max-width: 1200px;
                padding: 20px;
                background-color: #fff;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #343a40;
            }
            .vulnerability {
                border-bottom: 1px solid #ddd;
                padding: 20px 0;
            }
            .vulnerability:last-child {
                border-bottom: none;
            }
            h2 {
                color: #dc3545;
                margin-top: 0;
            }
            pre {
                background: #f1f1f1;
                padding: 15px;
                overflow: auto;
                border-radius: 5px;
            }
            .details, .code, .suggestion {
                margin-bottom: 20px;
            }
            .details p, .code p, .suggestion p {
                margin: 5px 0;
            }
            .label {
                font-weight: bold;
                color: #343a40;
            }
            footer {
                text-align: center;
                padding: 20px;
                background-color: #343a40;
                color: #fff;
                margin-top: 40px;
            }
            a {
                color: #007bff;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            @media (max-width: 768px) {
                .container {
                    margin: 10px;
                    padding: 15px;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Relatório de Vulnerabilidades</h1>
        </header>
        <div class="container">
    """

    for idx, vulnerabilidade in enumerate(vulnerabilidades, 1):
        detalhes = vulnerabilidade.get('details', 'Detalhes não encontrados')
        codigo = vulnerabilidade.get('code', 'Código não encontrado')
        sugestao = vulnerabilidade.get('sugestao', 'Sugestão não disponível')

        # Convertendo a sugestão de Markdown para HTML
        sugestao_html = markdown.markdown(sugestao)

        html += f"""
        <div class="vulnerability">
            <h2>Vulnerabilidade {idx}</h2>
            <div class="details">
                <p class="label">Detalhes:</p>
                <p>{detalhes}</p>
            </div>
            <div class="code">
                <p class="label">Código Vulnerável:</p>
                <pre><code>{codigo}</code></pre>
            </div>
            <div class="suggestion">
                <p class="label">Sugestão de Correção:</p>
                {sugestao_html}
            </div>
        </div>
        """

    html += """
        </div>
        <footer>
            <p>Gerado por OpenFixAI</p>
        </footer>
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

def create_pull_request(code_pr, detalhes, file_path):
    """Cria um pull request no GitHub com a correção proposta."""
    if not code_pr or not file_path:
        print("Código ou caminho inválido, PR não criado.")
        return None

    cleaned_path = re.sub(r'\.horusec/[0-9a-fA-F-]+/', '', file_path)

    try:
        # Autenticação
        g = Github(GIT_TOKEN)
        repo = g.get_repo(REPO_NAME)

        # Criar um novo branch para a correção
        main_branch = repo.get_branch('main')
        try:
            repo.create_git_ref(ref=f'refs/heads/{BRANCH_NAME}', sha=main_branch.commit.sha)
            print(f"Branch criado: {BRANCH_NAME}")
        except Exception as e:
            print(f"Branch {BRANCH_NAME} já existe ou erro ao criar o branch: {e}")

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
            title=f'Correção de código {file}',
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

        create_pull_request(code_pr, detalhes, file_path)

    relatorio_html = gerar_relatorio_html(vulnerabilidades)
    try:
        with open('relatorio_vulnerabilidades.html', 'w', encoding='utf-8') as arquivo_html:
            arquivo_html.write(relatorio_html)
        print("Relatório de vulnerabilidades gerado com sucesso: relatorio_vulnerabilidades.html")
    except Exception as e:
        print(f"Erro ao salvar o relatório HTML: {e}")

if __name__ == "__main__":
    main()
