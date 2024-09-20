# OpenFixAI

Uma ferramenta que automatiza a correção de vulnerabilidades identificadas pelo Horusec, utilizando o OpenAI GPT-4 para sugerir correções, gerando relatório e criando pull requests no GitHub com as alterações propostas.

## Sumário

- [Visão Geral](#visão-geral)
- [Recursos](#recursos)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Relatório HTML](#relatório-html)
- [Resolução de Problemas](#resolução-de-problemas)
- [Contribuição](#contribuição)
- [Licença](#licença)
- [Contato](#contato)

## Visão Geral

O **Horusec Vulnerability Auto-Fixer** é uma ferramenta que automatiza o processo de identificação e correção de vulnerabilidades em projetos de código aberto ou privado. Ele integra o scanner de segurança Horusec com a API da OpenAI para gerar sugestões de correção, cria relatórios HTML estilizados e abre pull requests automaticamente no GitHub com as correções propostas.

## Recursos

- **Leitura de Relatórios do Horusec**: Analisa o relatório de vulnerabilidades gerado pelo Horusec.
- **Extração de Vulnerabilidades**: Utiliza expressões regulares para extrair detalhes das vulnerabilidades encontradas.
- **Consulta à OpenAI**: Envia as vulnerabilidades para a API da OpenAI e recebe sugestões de correção.
- **Geração de Relatório HTML Aprimorado**: Cria um relatório detalhado em HTML com estilos CSS aprimorados para melhor visualização.
- **Extração de Código Corrigido**: Processa a sugestão para obter apenas o código corrigido.
- **Criação Automática de Pull Requests**: Cria um novo branch, atualiza o arquivo vulnerável com a correção e abre um pull request no GitHub.

## Pré-requisitos

- **Python 3.7** ou superior
- **Chave de API da OpenAI** com acesso ao modelo GPT-4
- **Token de Acesso Pessoal do GitHub** com permissões para criar branches e pull requests
- **Horusec** instalado para gerar o relatório de vulnerabilidades
- **Ambiente Virtual (opcional, mas recomendado)**

## Instalação

1. **Clone o repositório**

   ```bash
   git clone https://github.com/crypto-br/OpenFixAI.git
   cd OpenFixAI
   ```

2. **Crie e ative um ambiente virtual**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows use `venv\Scripts\activate`
   ```

3. **Instale as dependências necessárias**

   ```bash
   pip install -r requirements.txt
   ```

## Configuração

1. **Configure as variáveis de ambiente**

   Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis:

   ```env
   OPENAI_API_KEY=seu_openai_api_key
   GIT_TOKEN=seu_github_token
   REPO_NAME=seu_usuario/seu_repositorio
   BRANCH_NAME=auto-fix-vulnerabilities
   ```

   - **OPENAI_API_KEY**: Sua chave de API da OpenAI.
   - **GIT_TOKEN**: Seu token de acesso pessoal do GitHub.
   - **REPO_NAME**: Nome do repositório no formato `usuario/repo`.
   - **BRANCH_NAME**: Nome do branch que será criado para as correções.

2. **Verifique o arquivo `requirements.txt`**

   Certifique-se de que o arquivo contém as seguintes dependências:

   ```
   openai
   PyGithub
   python-dotenv
   markdown
   ```

## Uso

1. **Gere um relatório de vulnerabilidades com o Horusec**

   Execute o Horusec para escanear seu código e gerar o `report.txt`:

   ```bash
   horusec start -p ./ --output-format=text --output-file=report.txt
   ```

2. **Execute a ferramenta**

   ```bash
   python openfixai.py
   ```

3. **Verifique o relatório gerado**

   Após a execução, um relatório HTML chamado `relatorio_vulnerabilidades.html` será criado no diretório do projeto. Abra-o em um navegador para visualizar as vulnerabilidades encontradas e as sugestões de correção.

4. **Revise o Pull Request**

   A ferramenta criará um novo branch e abrirá um pull request no seu repositório GitHub com as correções propostas. Revise as mudanças antes de fazer o merge.

## Relatório HTML

O relatório HTML gerado apresenta:

- **Detalhes das Vulnerabilidades**: Informações detalhadas sobre cada vulnerabilidade encontrada.
- **Código Vulnerável**: Trechos de código que contêm as vulnerabilidades.
- **Sugestões de Correção**: Orientações fornecidas pela OpenAI para corrigir as vulnerabilidades.

## Resolução de Problemas

- **Erro 401 "Bad credentials"**: Verifique se o `GIT_TOKEN` está correto e tem as permissões necessárias.
- **Erro 404 "Not Found"**: Certifique-se de que o `REPO_NAME` e o `cleaned_path` estão corretos e que o arquivo existe no repositório.
- **Erros ao ler o relatório**: Verifique se o arquivo `report.txt` existe e foi gerado corretamente pelo Horusec.
- **Erros na API da OpenAI**: Confirme se a sua chave de API é válida e tem acesso ao modelo especificado.
- **Dependências não encontradas**: Execute `pip install -r requirements.txt` para instalar as dependências necessárias.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).
