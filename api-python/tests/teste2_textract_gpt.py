import boto3
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF
from datetime import datetime, date
from openai import OpenAI
from typing import Dict, Any, List, Tuple
import json

load_dotenv()
textract = boto3.client('textract', region_name='us-east-1')

OpenAI.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OpenAI.api_key)


KEY_MAPPING = {
    'nome': ['NOME', 'NOME COMPLETO'],
    'filiacao': ['FILIAÇÃO', 'FILIACAO', 'NOME DO PAI', 'NOME DA MAE', 'PAI', 'MAE', 'FILIAÇÃO:', 'FILIACAO:', 'PAI:', 'MAE:', 'NOME DO PAI:', 'NOME DA MAE:'],
    'naturalidade': ['NATURALIDADE', 'LOCAL DE NASCIMENTO'],
    'data_nascimento': ['DATA DE NASCIMENTO', 'NASCIMENTO'],
    'registro_geral': ['REGISTRO GERAL', 'RG', 'IDENTIDADE', 'NUMERO DE IDENTIDADE'],
    'documento_origem': ['DOC ORIGEM', 'DOCUMENTO DE ORIGEM', 'ORIGEM', 'REGISTRO CIVIL'],
    'cpf': ['CPF', 'C.P.F.', 'CADASTRO DE PESSOA FISICA'],
    'data_expedicao': ['DATA DE EXPEDICAO', 'EXPEDICAO', 'DATA DE EMISSAO', 'EMISSAO'],
    'frase_legal_obrigatoria': [
        'VÁLIDA EM TODO O TERRITÓRIO NACIONAL',
        'VALIDA EM TODO O TERRITORIO NACIONAL'
    ],
    'lei': [
        'LEI N° 7.116 DE 29/08/83',
        'LEI Nº 7.116 DE 29/08/83',
        'LEI NO 7.116 DE 29/08/83',
        'LEI 7.116 DE 29/08/83'
    ]
}

def processar_forms_textract(response):
    extracted_data = {}
    key_values = {}
    
    blocks_by_id = {block['Id']: block for block in response.get('Blocks', [])}

    for block in response.get('Blocks', []):
        if block['BlockType'] == 'KEY_VALUE_SET':
            if 'KEY' in block['EntityTypes'] and 'Relationships' in block:
                key_text = ""
                for relationship in block['Relationships']:
                    if relationship['Type'] == 'CHILD':
                        for child_id in relationship['Ids']:
                            word_block = blocks_by_id.get(child_id)
                            if word_block and word_block['BlockType'] == 'WORD':
                                key_text += word_block['Text'] + " "
                
                key_text = key_text.strip().upper()

                value_text = ""
                for relationship in block['Relationships']:
                    if relationship['Type'] == 'VALUE':
                        for value_id in relationship['Ids']:
                            value_block = blocks_by_id.get(value_id)
                            if value_block:
                                if value_block['BlockType'] == 'WORD' or value_block['BlockType'] == 'LINE':
                                    value_text += value_block['Text'] + " "
                                elif 'Relationships' in value_block:
                                    for value_rel in value_block['Relationships']:
                                        if value_rel['Type'] == 'CHILD':
                                            for child_id in value_rel['Ids']:
                                                word_block = blocks_by_id.get(child_id)
                                                if word_block and word_block['BlockType'] == 'WORD':
                                                    value_text += word_block['Text'] + " "
                
                if key_text and value_text:
                    key_values[key_text] = value_text.strip()
    
    for standard_key, variations in KEY_MAPPING.items():
        for var in variations:
            if var.upper() in key_values:
                extracted_data[standard_key] = key_values[var.upper()]
                break
    
    return extracted_data


def analisar_documento(textract_response):
    extracted_data_from_textract = processar_forms_textract(textract_response)
    
    full_text_lines = [b['Text'] for b in textract_response.get('Blocks', []) if b['BlockType'] == 'LINE']
    full_text = " ".join(full_text_lines)
    
    return extracted_data_from_textract, full_text


def analisar_com_ia(dados_extraidos_textract: Dict[str, Any], texto_completo: str) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Analisa os dados brutos do Textract e o texto completo usando IA generativa
    para validar se é um RG e organizar os dados.
    """
    dados_extraidos_textract_str = json.dumps(dados_extraidos_textract, indent=2, ensure_ascii=False)

    prompt = f"""
    Você é um especialista em análise de documentos de identificação brasileiros, focado em RGs.
    Sua tarefa é analisar o `texto_completo_documento` abaixo para EXTRAIR todos os dados relevantes de um RG,
    VALIDAR esses dados e, em seguida, organizá-los em um objeto JSON.

    Os 'dados_extraidos_pelo_textract' são fornecidos como uma *referência secundária* do que uma ferramenta de OCR identificou.
    Eles podem estar incompletos, fora de ordem ou com formatação imperfeita.
    **SUA PRIORIDADE é escanear o `texto_completo_documento` para encontrar e extrair as informações corretas e completas.**
    Use o `dados_extraidos_pelo_textract` apenas para *confirmar* ou *auxiliar* na identificação se tiver dúvidas.

    Dados extraídos pelo Textract (pode estar incompleto ou misturado):
    {dados_extraidos_textract_str}

    Texto completo do documento (SUA FONTE PRIMÁRIA PARA EXTRAÇÃO E VALIDAÇÃO):
    {texto_completo}

    Com base na sua análise do TEXTO COMPLETO, determine se o documento é um RG válido e organize os dados.
    **Critérios de Validação para um RG Brasileiro:**
    1.  **Presença e Validade dos Campos Essenciais**:
        * **Nome Completo**: Deve ser um nome próprio.
        * **CPF**: **EXTRAIA E VALIDE O FORMATO**. Deve conter 11 dígitos numéricos. Limpe pontos e traços, retornando apenas os 11 dígitos. Se o formato não for de 11 dígitos numéricos, é inválido.
        * **Data de Nascimento**: **EXTRAIA E VALIDE O FORMATO**. Deve estar no formato DD/MM/AAAA. Se não for esse formato, é inválido.
        * **Registro Geral (RG/Identidade)**: **EXTRAIA E VALIDE O FORMATO**. Deve seguir um padrão comum de RG brasileiro (ex: XX.XXX.XXX-X ou só números, pode conter pontos e traços).
        * **Data de Expedição**: **EXTRAIA E VALIDE O FORMATO**. Deve estar no formato DD/MM/AAAA. Se não for esse formato, é inválido.
        * **Filiação (Nome do Pai e da Mãe)**: **EXTRAIA**. Tente identificar o nome do pai e da mãe. Se conseguir, formate como "PAI: Nome do Pai / MÃE: Nome da Mãe". Se houver apenas um nome ou não for possível distinguir, use "FILIAÇÃO: Nome Completo da Filiação".
        * **Naturalidade**: **EXTRAIA**. Cidade e Estado (UF, ex: SÃO PAULO - SP).
        * **Documento de Origem**: **EXTRAIA**. Informações de registro civil (ex: Livro, Folha, Termo, Cartório).
    2.  **Consistência dos Dados**:
        * A Data de Nascimento deve ser uma data válida e anterior à Data de Expedição. Se não for, é inválido.
    3.  **Frases e Leis Obrigatórias**:
        * **Presença da frase legal obrigatória**: "VÁLIDA EM TODO O TERRITÓRIO NACIONAL" (ou variações próximas, como "VALIDA EM TODO O TERRITORIO NACIONAL"). Verifique se ela está presente no `texto_completo_documento`.
        * **Presença da lei obrigatória**: Menção à "LEI Nº 7.116 DE 29/08/83" (ou variações, como "LEI N° 7.116 DE 29/08/83", "LEI NO 7.116 DE 29/08/83", "LEI 7.116 DE 29/08/83"). Verifique se ela está presente no `texto_completo_documento`.

    Se um campo obrigatório for ausente ou tiver um formato inválido, ou se a consistência for violada, inclua um motivo específico.

    Retorne um JSON com a seguinte estrutura:
    {{
        "eh_rg_valido": boolean,
        "motivos": [
            "Motivo 1: [Descrição clara e concisa do problema, ex: Campo 'CPF' não encontrado ou inválido].",
            "Motivo 2: [Descrição, ex: Data de nascimento (DD/MM/AAAA) não está no formato correto ou é inconsistente].",
            "Motivo 3: [Descrição, ex: Frase legal 'VÁLIDA EM TODO O TERRITÓRIO NACIONAL' ausente]."
        ],
        "dados_organizados": {{
            "nome": "string (Nome completo extraído) ou null",
            "cpf": "string (CPF limpo, 11 dígitos numéricos, ex: 12345678900) ou null",
            "data_nascimento": "string (DD/MM/AAAA) ou null",
            "registro_geral": "string (RG no formato original, ex: 12.345.678-9 ou só números) ou null",
            "data_expedicao": "string (DD/MM/AAAA) ou null",
            "filiacao": "string (Nomes dos pais, ex: PAI: Nome do Pai / MÃE: Nome da Mãe. Se apenas um: FILIAÇÃO: Nome) ou null",
            "naturalidade": "string (Cidade - UF, ex: SÃO PAULO - SP) ou null",
            "documento_origem": "string (Informações de registro civil, ex: Livro X, Folha Y, Termo Z) ou null",
            "frase_legal_obrigatoria_presente": boolean,
            "lei_7116_presente": boolean
        }}
    }}
    Se um campo não for encontrado ou for inválido, use `null` para o valor correspondente em `dados_organizados`.
    Garanta que todas as informações relevantes do `texto_completo_documento` sejam extraídas e validadas.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        resultado_str = response.choices[0].message.content

        resultado_str = response.choices[0].message.content
        print("\n--- Resposta Bruta da IA ---")
        print(resultado_str)
        print("----------------------------\n")
        
        resultado_dict = json.loads(resultado_str)
        
        eh_rg_valido = resultado_dict.get("eh_rg_valido", False)
        motivos = resultado_dict.get("motivos", [])
        dados_organizados = resultado_dict.get("dados_organizados", {})

        return eh_rg_valido, motivos, dados_organizados

    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da IA: {e}")
        print(f"Resposta da IA que causou o erro: '{resultado_str}'")
        return False, [f"Erro na análise com IA: Resposta inválida - {str(e)}"], dados_extraidos_textract
    except Exception as e:
        print(f"Erro inesperado na análise com IA: {str(e)}")
        return False, [f"Erro na análise com IA: {str(e)}"], dados_extraidos_textract


def processar_documento_local(nome_arquivo):
    """
    Função principal que lê um arquivo local (imagem ou PDF),
    envia ao Textract e depois para a IA.
    """
    file_path = os.path.abspath(nome_arquivo)
    
    if not os.path.exists(file_path):
        print(f"ERRO: Arquivo não encontrado no caminho: {file_path}")
        return

    textract_response = {}
    full_extracted_text_raw = []

    try:
        if nome_arquivo.lower().endswith('.pdf'):
            print(f"Processando PDF: {nome_arquivo}")
            doc = fitz.open(file_path)
            if len(doc) == 0:
                raise ValueError("PDF vazio ou corrompido.")
            
            all_pages_blocks = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
                image_bytes = pix.tobytes("png")
                
                print(f"Enviando página {page_num + 1} para Textract analyze_document...")
                
                response_page = textract.analyze_document(
                    Document={'Bytes': image_bytes},
                    FeatureTypes=['FORMS', 'TABLES', 'SIGNATURES']
                )
                all_pages_blocks.extend(response_page['Blocks'])
                
                for block in response_page['Blocks']:
                    if block.get('BlockType') == 'LINE' and 'Text' in block and block['Text']:
                        full_extracted_text_raw.append(block['Text'])
            
            textract_response['Blocks'] = all_pages_blocks
            
        elif nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Processando imagem: {nome_arquivo}")
            with open(file_path, 'rb') as document:
                document_bytes = document.read()
            
            print("Enviando imagem para Textract analyze_document...")
            textract_response = textract.analyze_document(
                Document={'Bytes': document_bytes},
                FeatureTypes=['FORMS', 'TABLES', 'SIGNATURES']
            )
            for block in textract_response['Blocks']:
                if block.get('BlockType') == 'LINE' and 'Text' in block and 'Text' in block and block['Text']:
                    full_extracted_text_raw.append(block['Text'])
        
        else:
            print(f"ERRO: Formato de arquivo não suportado: {nome_arquivo}. Use .pdf, .png, .jpg ou .jpeg.")
            return

    except Exception as e:
        print(f"Erro no processamento de arquivo/Textract: {e}")
        print(f"Texto extraído bruto (se houver): {' '.join(full_extracted_text_raw)}")
        return

    extracted_data_textract_raw, full_text_for_gpt = analisar_documento(textract_response)
    
    is_rg_ia, reasons_ia, dados_organizados = analisar_com_ia(extracted_data_textract_raw, full_text_for_gpt)

    resultado_final = {
        'status': 'sucesso',
        'arquivo_processado': nome_arquivo,
        'documento_reconhecido_como_rg': is_rg_ia,
        'dados_extraidos_pelo_gpt': dados_organizados,
        'motivos_decisao_gpt': reasons_ia,
        'texto_completo_documento': full_text_for_gpt,
        'dados_iniciais_textract_bruto': extracted_data_textract_raw
    }

    print("\n--- RESULTADO FINAL DO PROCESSAMENTO ---")
    print(json.dumps(resultado_final, indent=4, ensure_ascii=False))
    print("----------------------------------------")


if __name__ == '__main__':
    NOME_ARQUIVO_RG = "rg_livia.png"
    print(f"--- Iniciando processamento do arquivo: {NOME_ARQUIVO_RG} ---")
    processar_documento_local(NOME_ARQUIVO_RG)
    print("--- Processamento concluído ---")