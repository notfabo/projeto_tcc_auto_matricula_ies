import os
from dotenv import load_dotenv
import json
import fitz
import tempfile
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

PROMPT_ANALISAR = """
Você é um especialista em análise de documentos de registro civil, focado em certidões de nascimento. Sua tarefa é analisar a imagem enviada se é um documento de certidão de nascimento original, ANALISAR E IDENTIFICAR todos os dados relevantes de uma certidão de nascimento, VALIDAR esses dados e, em seguida, organizar em um objeto JSON apenas com os campos necessários, caso contrário retorne {"eh_certidao_valida": false, "motivos": ["Documento não é uma certidão de nascimento original."], "dados_organizados": {}}.

### Critérios de identificação, análise e validação para uma Certidão de Nascimento:###

1. Presença obrigatória de termos como:
- Nome Completo do Registrado: Deve ser um nome próprio.
- Filiação: Deve conter o nome da mãe e, se declarado, o nome do pai.
- Numeração de Folha, livro e termo: Deve seguir o formato padrão do cartório (livro, fls, termo).
- Data de Nascimento: Deve ser uma data válida no formato DD/MM/AAAA.
- Local de Nascimento: Deve indicar a cidade e o estado onde o nascimento ocorreu.
- Nome do Cartório: Nome do Cartório de Registro Civil das Pessoas Naturais.
- Data do Registro: A data em que o registro foi lavrado no cartório.
- Cidade do Cartório: Nome da cidade onde o cartório está localizado.
- Estado do Cartório: Sigla do estado (UF, ex: "SP", "RJ", "BA").

2. Campos essenciais:
   - Nome Registrado
   - Data de Nascimento
   - Local de Nascimento
   - Filiação (Nome da mãe, Nome do pai)

### Consistência dos Dados:###
- A Data do Registro deve ser igual ou posterior à Data de Nascimento.
- O Local de Nascimento deve ser um local geograficamente válido (Cidade - UF).
- Geralmente há o nome de um Oficial de Registro ou Escrevente Autorizado, seguido de uma assinatura ou selo do cartório.
- Se um campo obrigatório for ausente ou tiver um formato inválido/inconsistente, inclua um motivo específico.
- Retorne motivos apenas se o documento não for uma certidão de nascimento ou/e se houver problemas de validação.

Responda apenas em JSON no seguinte formato, o JSON deve retornar apenas os campos abaixo:

JSON
{
  "eh_certidao_valida": boolean,
  "motivoErro": [
    "Motivo 1...",
    "Motivo 2..."
  ],
  "dados_organizados": {
    "nome_registrado": "string (Nome completo do registrado) ou null",
    "data_nascimento": "string (DD/MM/AAAA) ou null",
    "local_nascimento": "string (Cidade - UF do nascimento) ou null",
    "filiacao": {
      "mae": "string (Nome completo da mãe) ou null",
      "pai": "string (Nome completo do pai) ou null"
    },
  }
}
"""

def carregar_arquivos_para_vision(file_path: str):
    input_content = []
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        print(f"Processando PDF: {file_path}")
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

            print(f"Página {page_num} convertida e enviada")

            os.remove(tmp_file_path)
    else:
        print(f"Processando imagem: {file_path}")
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
            "eh_certidao_valida": False,
            "motivoErro": ["Erro: resposta não pôde ser convertida em JSON."],
            "dados_organizados": {}
        }

    return result

def processar_certidao_nascimento(file_path: str) -> dict:
    try:
        resultado_ia = analisar_com_ia(file_path)

        if resultado_ia.get("eh_certidao_valida"):
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
