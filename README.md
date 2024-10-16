
# PDF Data Extractor App

Este é um aplicativo web desenvolvido com Flask para fazer upload de arquivos PDF, extrair informações específicas (como código do CAR, nome do imóvel rural, CNPJ/CPF e nome do proprietário/possuidor) e gerar um arquivo Excel contendo os dados extraídos.

## Funcionalidades

- Permite o upload de arquivos PDF.
- Extrai dados específicos dos PDFs, incluindo:
  - Código do CAR
  - Nome do Imóvel Rural
  - CNPJ/CPF e Nome dos Proprietários/Possuidores
- Gera e permite o download de um arquivo Excel (`output.xlsx`) contendo os dados extraídos.
  
## Pré-requisitos

Antes de rodar o aplicativo, certifique-se de que as seguintes dependências estão instaladas:

- Python 3.8+
- Flask
- pandas
- pdfplumber
- Werkzeug

### Instalação de dependências

Você pode instalar as dependências com o comando:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

**Arquivo \`requirements.txt\`:**

\`\`\`txt
Flask
pandas
pdfplumber
Werkzeug
\`\`\`

## Estrutura do Projeto

\`\`\`bash
.
├── app.py                   # Código principal do aplicativo
├── templates
│   └── index.html            # Página HTML para upload de arquivos
├── uploads/                  # Diretório para armazenar arquivos PDF enviados
├── outputs/                  # Diretório para salvar o arquivo Excel gerado
├── requirements.txt          # Arquivo para gerenciar dependências
└── README.md                 # Descrição do projeto
\`\`\`

## Como Executar

1. Clone este repositório:

\`\`\`bash
git clone <URL_DO_REPOSITÓRIO>
cd <NOME_DO_REPOSITÓRIO>
\`\`\`

2. Crie os diretórios necessários:

\`\`\`bash
mkdir uploads outputs
\`\`\`

3. Execute o aplicativo:

\`\`\`bash
python app.py
\`\`\`

O aplicativo será executado no endereço [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Como Utilizar

1. Acesse a página inicial do aplicativo.
2. Faça upload de um ou mais arquivos PDF contendo os dados de imóveis rurais.
3. O aplicativo extrairá automaticamente os dados do PDF e gerará um arquivo Excel com os dados processados.
4. O arquivo Excel será baixado automaticamente pelo navegador.

## Personalização

- **UPLOAD_FOLDER**: Configuração para o diretório onde os PDFs serão armazenados.
- **OUTPUT_FOLDER**: Configuração para o diretório onde o arquivo Excel gerado será salvo.
- **ALLOWED_EXTENSIONS**: Defina as extensões de arquivo permitidas (atualmente, apenas PDFs são permitidos).

## Contribuição

Fique à vontade para abrir um pull request ou sugerir melhorias!
