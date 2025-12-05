import os
from dotenv import load_dotenv
import json
import fitz
import tempfile
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

PROMPT_ANALISAR_RG = """
Você é um especialista em análise de documentos de identificação brasileiros, focado em RGs.
Sua tarefa é analisar a imagem enviada, EXTRAIR todos os dados relevantes de um RG,
VALIDAR esses dados e, em seguida, organizá-los em um objeto JSON.

**Critérios de Validação para um RG Brasileiro:**
1. Campos essenciais:
   - Nome Completo
   - CPF (formatos válidos XXX.XXX.XXX-XX ou XXXXXXXXX/XX)
   - Data de Nascimento (formato DD/MM/AAAA)
   - Registro Geral (RG, formato XX.XXX.XXX-X ou 9 dígitos)
   - Data de Expedição (formato DD/MM/AAAA)
   - Filiação (Nome do Pai e da Mãe, ou um só nome como FILIAÇÃO)
   - Naturalidade (Cidade - UF)
2. A Data de Nascimento deve ser anterior à Data de Expedição.

Não confunda o número do RG com o CPF. Ambos são obrigatórios.
Se for um RG válido, retorne todos os dados organizados.
Se não for, marque como inválido e explique os motivos.

Responda **apenas** em JSON no seguinte formato:

{
  "eh_rg_valido": boolean,
  "motivos": [
    "Motivo 1...",
    "Motivo 2..."
  ],
  "dados_organizados": {
    "nome": "string ou null",
    "cpf": "string ou null",
    "data_nascimento": "string (DD/MM/AAAA) ou null",
    "registro_geral": "string ou null",
    "data_expedicao": "string (DD/MM/AAAA) ou null",
    "filiacao": "string ou null",
    "naturalidade": "string ou null",
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


def analisar_documento_rg(file_path: str):
    imagens = carregar_arquivos_para_vision(file_path)

    response = client.responses.create(
        model="gpt-5-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": PROMPT_ANALISAR_RG},
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
            "eh_rg_valido": False,
            "motivos": ["Erro: resposta não pôde ser convertida em JSON."],
            "dados_organizados": {}
        }

    return result

if __name__ == "__main__":
    resultado = analisar_documento_rg("./docs/rg-verso.png")
    print("\nResultado estruturado:\n", json.dumps(resultado, indent=2, ensure_ascii=False))
