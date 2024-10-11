from flask import Flask, render_template, request, send_file, make_response
import os
import pandas as pd
import pdfplumber
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)

# Configurações
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Verifica se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função atualizada para extrair dados de um PDF
def extract_data_from_pdf(pdf_path):
    data = {
        'Código': None,
        'Nome do Imóvel Rural': None,
        'CNPJs/CPFs': [],
        'Nomes': []
    }

    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

        # Extrair "Registro no CAR:"
        pattern_car = r'Registro no CAR:\s*([A-Z0-9.-]+)'
        match_car = re.search(pattern_car, full_text)
        if match_car:
            code = match_car.group(1)
            code_no_dots = code.replace('.', '')
            data['Código'] = code_no_dots

        # Extrair "Nome do Imóvel Rural:"
        pattern_nome_imovel = r'Nome do Imóvel Rural:\s*(.+)'
        match_nome_imovel = re.search(pattern_nome_imovel, full_text)
        if match_nome_imovel:
            nome_imovel = match_nome_imovel.group(1).strip()
            data['Nome do Imóvel Rural'] = nome_imovel

        # Extrair "IDENTIFICAÇÃO DO PROPRIETÁRIO/POSSUIDOR"
        proprietarios_text = ''
        pattern_proprietarios_section = r'IDENTIFICAÇÃO DO PROPRIETÁRIO/POSSUIDOR(.*?)(?=\n[A-Z]+\n|\Z)'
        match_proprietarios_section = re.search(pattern_proprietarios_section, full_text, re.DOTALL)
        if match_proprietarios_section:
            proprietarios_text = match_proprietarios_section.group(1)

            # Encontrar a primeira ocorrência de "CNPJ:" ou "CPF:" e "Nome:"
            pattern_cnpj_cpf_nome = r'(CNPJ|CPF):\s*([\d./-]+).*?Nome:\s*(.+?)(?=\n|$)'
            match = re.search(pattern_cnpj_cpf_nome, proprietarios_text, re.DOTALL)
            if match:
                cnpj_cpf_value = match.group(2).strip()
                nome_value = match.group(3).strip()
                data['CNPJs/CPFs'].append(cnpj_cpf_value)
                data['Nomes'].append(nome_value)

        else:
            # Caso não encontre via texto, tenta extrair as tabelas
            found_owner = False
            for page in pdf.pages:
                page_text = page.extract_text()
                if 'IDENTIFICAÇÃO DO PROPRIETÁRIO/POSSUIDOR' in page_text:
                    tables = page.extract_tables()
                    for table in tables:
                        headers = table[0]
                        headers_lower = [header.lower() if header else '' for header in headers]
                        if any('cnpj' in h or 'cpf' in h for h in headers_lower) and 'nome' in headers_lower:
                            for row in table[1:]:
                                row_data = dict(zip(headers_lower, row))
                                cnpj_cpf = row_data.get('cnpj') or row_data.get('cpf')
                                nome = row_data.get('nome')
                                if cnpj_cpf and nome:
                                    data['CNPJs/CPFs'].append(cnpj_cpf.strip())
                                    data['Nomes'].append(nome.strip())
                                    found_owner = True
                                    break  # Para após encontrar o primeiro proprietário
                            if found_owner:
                                break  # Sai do loop de tabelas
                    if found_owner:
                        break  # Sai do loop de páginas
    return data



# Rota principal
@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return 'Nenhum arquivo selecionado', 400
        files = request.files.getlist('files[]')
        data_list = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                data_extracted = extract_data_from_pdf(filepath)
                if data_extracted:
                    data_row = {
                        'Arquivo': filename,
                        'Código': data_extracted.get('Código', 'Não encontrado'),
                        'Nome do Imóvel Rural': data_extracted.get('Nome do Imóvel Rural', 'Não encontrado'),
                        'CNPJs/CPFs': ', '.join(data_extracted.get('CNPJs/CPFs', [])),
                        'Nomes': ', '.join(data_extracted.get('Nomes', []))
                    }
                    data_list.append(data_row)
                else:
                    data_list.append({
                        'Arquivo': filename,
                        'Código': 'Não encontrado',
                        'Nome do Imóvel Rural': 'Não encontrado',
                        'CNPJs/CPFs': 'Não encontrado',
                        'Nomes': 'Não encontrado'
                    })
        # Organiza os dados em um DataFrame
        df = pd.DataFrame(data_list)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.xlsx')
        df.to_excel(output_path, index=False)

        # Preparar a resposta para incluir o header 'Content-Disposition'
        response = make_response(send_file(output_path, as_attachment=True, download_name='output.xlsx'))
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response
    return render_template('index.html')

if __name__ == '__main__':
    # Cria os diretórios se não existirem
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
