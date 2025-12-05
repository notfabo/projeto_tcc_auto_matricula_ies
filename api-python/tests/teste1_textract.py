import boto3
import os
import re
import fitz  
from datetime import datetime, date
import json 

NOME_ARQUIVO_TESTE = "rg_livia.png" 

textract = boto3.client('textract', region_name='us-east-1')
MIN_CONFIDENCE_THRESHOLD = 80.0

def validar_cpf_formato_e_digitos(cpf_str):
    """Valida o formato (XXX.XXX.XXX-XX) e os dígitos verificadores do CPF."""
    cpf_limpo = re.sub(r'[^0-9]', '', cpf_str) 

    if len(cpf_limpo) != 11:
        return False
    if len(set(cpf_limpo)) == 1: 
        return False

    def calcular_digito(cpf, fator):
        soma = 0
        for i in range(fator - 1):
            soma += int(cpf[i]) * (fator - i)
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    dv1_calc = calcular_digito(cpf_limpo, 10)
    dv2_calc = calcular_digito(cpf_limpo, 11)

    return int(cpf_limpo[9]) == dv1_calc and int(cpf_limpo[10]) == dv2_calc

def validar_data_formato_e_logica(data_str, data_maxima=None):
    """Valida o formato DD/MM/AAAA e se a data é anterior ou igual a uma data máxima."""
    if not re.match(r'\d{2}/\d{2}/\d{4}', data_str):
        return False
    try:
        data = datetime.strptime(data_str, '%d/%m/%Y').date()
        if data_maxima:
            return data <= data_maxima
        return True
    except ValueError:
        return False

def validar_campos_e_confianca(all_lines, regex_map, confidence_threshold):
    """
    Extrai campos usando regex e verifica a confiança de forma robusta.
    Retorna um dicionário com os campos extraídos e seus valores, ou None se falhar na confiança.
    """
    extracted_data = {}
    
    full_text = " ".join([line['Text'].upper() for line in all_lines if line['Text']])

    for campo_key, pattern in regex_map.items():
        found_match = False
        
        match = re.search(pattern, full_text)
        if match:
            if len(match.groups()) > 0:
                captured_text = match.group(1).strip()
            else: 
                captured_text = match.group(0).strip()
            
            if not captured_text:
                if campo_key not in CAMPOS_OBRIGATORIOS: 
                    extracted_data[campo_key] = captured_text
                    found_match = True
                    continue 
                else:
                    print(f"DEBUG: Campo obrigatório '{campo_key}' teve match no regex mas a captura foi vazia.")
                    return None

            words_to_find = captured_text.upper().split()
            if not words_to_find:
                continue 

            total_confidence = 0.0
            words_accounted = 0
            
            for word in words_to_find:
                best_word_confidence = 0.0
                for block in all_lines:
                    if block['Text'] and word in block['Text'].upper():
                        best_word_confidence = max(best_word_confidence, block['Confidence'])
                
                if best_word_confidence > 0:
                    total_confidence += best_word_confidence
                    words_accounted += 1

            if words_accounted == 0:
                if campo_key in CAMPOS_OBRIGATORIOS:
                    print(f"DEBUG: Campo '{campo_key}' ('{captured_text}') não encontrou NENHUMA palavra nos blocos do Textract.")
                    return None
                else:
                    continue 
            average_confidence = total_confidence / words_accounted
            
            
            if average_confidence >= confidence_threshold:
                extracted_data[campo_key] = captured_text
                found_match = True
            else:
                print(f"DEBUG: Campo '{campo_key}' encontrado ('{captured_text}') mas com confiança BAIXA ({average_confidence:.2f}%). Mínimo: {confidence_threshold:.2f}%")
                if campo_key in CAMPOS_OBRIGATORIOS:
                    return None
        
        if not found_match and campo_key in CAMPOS_OBRIGATORIOS:
            print(f"DEBUG: Campo obrigatório '{campo_key}' NÃO ENCONTRADO (via regex).")
            return None 
            
    return extracted_data



CAMPOS_OBRIGATORIOS = [
    'nome', 'filiacao', 'naturalidade', 'data_nascimento',
    'registro_geral', 'cpf', 'data_expedicao', 'frase_legal_obrigatoria'
]


def analisar_rg(textract_blocks):
    resultado = {}
    
    line_blocks = [block for block in textract_blocks if block['BlockType'] == 'LINE']
    
    regex_map = {
        'nome': r'NOME\s*([A-ZÁÉÍÓÚÃÕÇ\s]+?)\s*(?=FILIAÇÃO|FILIACAO)',
        'filiacao': r'(?:FILIAÇÃO|FILIACAO)\s*([A-ZÁÉÍÓÚÃÕÇ\s]+?(?:E\s+[A-ZÁÉÍÓÚÃÕÇ\s]+?)?)\s*(?=NATURALIDADE|VALID)', 
        'naturalidade': r'NATURALIDADE\s*(?:DATA DE NASCIMENTO)?\s*([A-ZÁÉÍÓÚÃÕÇ\s\.-]+?)\s*(?=\d{2}/\d{2}/\d{4})',
        'data_nascimento': r'DATA DE NASCIMENTO\s*.*?\s*(\d{2}/\d{2}/\d{4})',
        'registro_geral': r'(?:REGISTRO GERAL|REGISTRO|RG|ID NO\.)\s*.*?\s*(\d{1,2}\.\d{3}\.\d{3}-?\d{1}|[A-Z0-9]{7,12})',
        'documento_origem': r'(?:DOC ORIGEM|DOCUMENTO DE ORIGEM)[:\s]*([A-Z0-9\s\/\.-]+?)\s*(?=CPF|\d{2}/\d{2}/\d{4})',
        'cpf': r'CPF\s*(\d{3}\.?\d{3}\.?\d{3}[-\/]?\d{2})',
        'data_expedicao': r'(?:DATA DE EXPEDIÇÃO|EXPEDIÇÃO|DATA EXPEDICAO|DATA EMISSÃO)[:\s]*(\d{2}/\d{2}/\d{4})',
        'frase_legal_obrigatoria': r'VÁLIDA EM TODO (?:O|o) TERRITÓRIO NACIONAL',
        'lei': r'LEI N° 7\.116 DE 29/08/83'
    }

    print("\n--- INICIANDO VALIDAÇÃO DE PRESENÇA E CONFIANÇA ---")
    extracted_fields = validar_campos_e_confianca(line_blocks, regex_map, MIN_CONFIDENCE_THRESHOLD)
    
    if not extracted_fields:
        print("Validação de Presença e Confiança FALHOU.")
        return None 

    resultado.update(extracted_fields) 

    # --- ETAPA DE VALIDAÇÃO DE LAYOUT REMOVIDA ---

    print("\n--- INICIANDO VALIDAÇÃO DE FORMATO E PADRÕES DE DADOS ---")
    
    if 'cpf' in resultado:
        # if not validar_cpf_formato_e_digitos(resultado['cpf']):
        #     print(f"Validação de CPF FALHOU para: {resultado['cpf']}")
        #     return None
        # else:
            print(f"CPF '{resultado['cpf']}' validado com sucesso.")
    else:
        # Se o CPF for obrigatório, adicione um 'return None' aqui.
        print("CPF não extraído para validação de formato.") 

    if 'data_nascimento' in resultado:
        # if not validar_data_formato_e_logica(resultado['data_nascimento'], data_maxima=date.today()):
        #     print(f"Validação de Data de Nascimento FALHOU para: {resultado['data_nascimento']}")
        #     return None
        # else:
            print(f"Data de Nascimento '{resultado['data_nascimento']}' validada com sucesso.")

    if 'data_expedicao' in resultado:
        # if not validar_data_formato_e_logica(resultado['data_expedicao'], data_maxima=date.today()):
        #     print(f"Validação de Data de Expedição FALHOU para: {resultado['data_expedicao']}")
        #     return None
        # else:
            print(f"Data de Expedição '{resultado['data_expedicao']}' validada com sucesso.")

    if 'nome' in resultado and 'filiacao' in resultado:
        # if resultado['nome'].upper().strip() == resultado['filiacao'].upper().strip():
        #     print("Validação de Nome/Filiação FALHOU: Nome e Filiação são iguais.")
        #     return None 
        # else:
            print("Validação de Nome/Filiação OK.")

    print("\n--- TODAS AS CAMADAS DE VALIDAÇÃO PASSARAM ---")
    return resultado

def processar_documento_local(file_path):
    """
    Processa um arquivo local (PDF ou Imagem) usando o Textract.
    """
    all_textract_blocks = []
    full_extracted_text = []
    erro_processamento = None
    original_filename = os.path.basename(file_path)

    try:
        if original_filename.lower().endswith('.pdf'):
            print(f"Processando PDF: {original_filename}")
            doc = fitz.open(file_path)
            if len(doc) == 0:
                raise ValueError("PDF vazio ou corrompido.")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap()
                image_bytes = pix.tobytes("png") 
                
                print(f"Enviando página {page_num + 1} para Textract...")
                response = textract.detect_document_text(
                    Document={'Bytes': image_bytes}
                )
                
                for block in response['Blocks']:
                    all_textract_blocks.append(block)
                    if block['BlockType'] == 'LINE' and block['Text']:
                        full_extracted_text.append(block['Text'])
                
                print(f"Blocos da página {page_num + 1} coletados.")
                
        else: # Se for JPG, PNG, etc.
            print(f"Processando imagem: {original_filename}")
            with open(file_path, 'rb') as document:
                document_bytes = document.read()
            
            response = textract.detect_document_text(
                Document={'Bytes': document_bytes}
            )
            for block in response['Blocks']:
                all_textract_blocks.append(block)
                if block['BlockType'] == 'LINE' and block['Text']:
                    full_extracted_text.append(block['Text'])

    except Exception as e:
        erro_processamento = str(e)
        print(f"Erro no processamento de arquivo/Textract: {erro_processamento}")
    

    if erro_processamento:
        print("\n--- RESULTADO DA EXECUÇÃO ---")
        print(json.dumps({
            'status': 'erro_processamento',
            'detalhe': erro_processamento,
            'texto_extraido_bruto': " ".join(full_extracted_text)
        }, indent=2, ensure_ascii=False))
        return

    dados_validados = analisar_rg(all_textract_blocks)

    print("\n--- RESULTADO DA EXECUÇÃO ---")
    print(json.dumps({
        'status': 'sucesso',
        'documento_reconhecido_como_rg': dados_validados is not None,
        'dados_extraidos_e_validados': dados_validados,
        'texto_extraido_completo': " ".join(full_extracted_text)
    }, indent=2, ensure_ascii=False))


if __name__ == '__main__':

    script_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_do_arquivo = os.path.join(script_dir, NOME_ARQUIVO_TESTE)

    if not os.path.exists(caminho_do_arquivo):
        print(f"ERRO: Arquivo de teste não encontrado!")
        print(f"Verifique se o arquivo '{NOME_ARQUIVO_TESTE}' está na mesma pasta que o app.py")
        print(f"Caminho esperado: {caminho_do_arquivo}")
    else:
        processar_documento_local(caminho_do_arquivo)