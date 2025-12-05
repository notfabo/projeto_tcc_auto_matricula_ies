import os
from dotenv import load_dotenv
import json
import fitz
import tempfile
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

PROMPT_ANALISAR = """
Você é um especialista em análise de documentos de registro civil, focado em comprovante de residência. Sua tarefa é analisar a imagem enviada se é um documento de comprovante de residência, ANALISAR E IDENTIFICAR todos os dados relevantes de um comprovante de residência, VALIDAR esses dados e, em seguida, organizar em um objeto JSON apenas com os campos necessários, caso contrário retorne {"eh_comprovante_valido": false, "motivos": ["Documento não é um Comprovante de Residência original."], "dados_organizados": {}}

### Critérios de identificação, análise e validação para um Comprovante de Residência:###

1. Presença obrigatória de termos como:
- Nome Completo do Titular: Deve ser um nome próprio.
- Endereço Completo: Deve ser capaz de reconstruir um endereço completo válido, incluindo:
    - Rua/Avenida: Identificar o logradouro.
    - Número: Identificar o número do imóvel.
    - Bairro: Identificar o bairro.
    - Cidade: Identificar a cidade.
    - Estado (UF): Identificar a UF, preferencialmente no formato de duas letras (ex: SP, RJ).
    - CEP: **EXTRAIA E VALIDE O FORMATO**. Deve conter 8 dígitos numéricos. Limpe pontos e traços, retornando apenas os 8 dígitos. Se o formato não for de 8 dígitos numéricos, é inválido.
- Data de Emissão: Deve ser uma data válida no formato DD/MM/AAAA ou similar, e deve ser recente (normalmente dentro dos últimos 3 meses).
- Nome da Empresa/Instituição Emissora: Nome da empresa ou instituição que emitiu o comprovante (ex: companhia de água, luz, telefone, banco, etc.).
- CPF: **EXTRAIA E VALIDE O FORMATO** (se presente). Deve conter 11 dígitos numéricos. Limpe pontos e traços, retornando apenas os 11 dígitos. Se o formato não for de 11 dígitos numéricos, é inválido. **Este campo é desejável, mas sua ausência não invalida o comprovante por si só.**

2. Campos essenciais:
- Nome Completo do Titular
- Rua/Avenida
- Número
- Bairro
- Cidade
- Estado (UF)
- CEP
- Data de Emissão
- Nome da Empresa/Instituição Emissora
- CPF (se presente)
- Tipo de Documento

3.  Identificação do Tipo de Documento:
Deve haver evidências no texto que sugiram que é um comprovante de residência (ex: "conta de água", "conta de luz", "fatura", "demonstrativo", "consumo", nomes de concessionárias de serviços públicos)

### Consistência dos Dados:###
- Se um campo obrigatório for ausente ou tiver um formato inválido/inconsistente, inclua um motivo específico.
- Retorne motivos apenas se o documento não for uma certidão de nascimento ou/e se houver problemas de validação.


Responda apenas em JSON no seguinte formato, o JSON deve retornar apenas os campos abaixo:

JSON
{
  "eh_comprovante_valido": boolean,
  "motivoErro": [
    "Motivo 1...",
    "Motivo 2..."
  ],
  "dados_organizados": {
        "nome_titular": "string (Nome completo extraído) ou null",
        "rua_avenida": "string (Rua/Avenida) ou null",
        "numero_endereco": "string (Número) ou null",
        "bairro": "string (Bairro) ou null",
        "cidade": "string (Cidade) ou null",
        "estado_uf": "string (UF, ex: SP) ou null",
        "cep": "string (CEP limpo, 8 dígitos numéricos, ex: 12345678) ou null",
        "data_emissao": "string (DD/MM/AAAA) ou null",
        "empresa_emissora": "string (Nome da empresa) ou null",
        "cpf_vinculado": "string (CPF limpo, 11 dígitos numéricos, ex: 12345678900) ou null",
        "tipo_documento": "string (Tipo de documento identificado, ex: conta de água, luz, telefone, etc.) ou null"
  }
}
"""

def carregar_arquivos_para_vision(file_path: str):
    input_content = []
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        print(f"📄 Processando PDF: {file_path}")
        doc = fitz.open(file_path)

        for page_num, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image_bytes = pix.tobytes("png")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(image_bytes)
                tmp_file_path = tmp_file.name

            with open(tmp_file_path, "rb") as f:
                file_obj = client.files.create(file=f, purpose="vision")
                input_content.append({"type": "input_image", "file_id": file_obj.id})

            print(f"✅ Página {page_num} convertida e enviada")

            os.remove(tmp_file_path)
    else:
        print(f"🖼 Processando imagem: {file_path}")
        with open(file_path, "rb") as f:
            file_obj = client.files.create(file=f, purpose="vision")
            input_content.append({"type": "input_image", "file_id": file_obj.id})

    return input_content


def analisar_com_ia(file_path: str):
    imagens = carregar_arquivos_para_vision(file_path)

    response = client.responses.create(
        # model="gpt-5-nano",
        model="gpt-5-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": PROMPT_ANALISAR},
                *imagens
            ]
        }]
    )

    raw_output = response.output_text
    print("\nResposta bruta do GPT:\n", raw_output)

    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        result = {
            "eh_comprovante_valido": False,
            "motivoErro": ["Erro: resposta não pôde ser convertida em JSON."],
            "dados_organizados": {}
        }

    return result

def processar_comprovante_residencial(file_path: str) -> dict:
    try:
        resultado_ia = analisar_com_ia(file_path)

        if resultado_ia.get("eh_comprovante_valido"):
            status = "aprovado"
            motivo_erro = None
        else:
            status = "reprovado"
            motivo_erro = ", ".join(resultado_ia.get("motivoErro", ["Motivo não especificado."]))

        return {
            "status": status,
            "dadosExtraidos": resultado_ia.get("dados_organizados", {}),
            "motivoErro": motivo_erro
        }

    except Exception as e:
        print(f"Erro crítico ao processar RG: {e}")
        return {
            "status": "erro",
            "dadosExtraidos": {},
            "motivoErro": f"Erro inesperado no módulo de IA: {str(e)}"
        }
