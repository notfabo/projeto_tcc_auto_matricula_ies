import os
from dotenv import load_dotenv
import json
import fitz
import tempfile
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

PROMPT_ANALISAR = """
Você é um especialista em análise de documentos militares brasileiros, focado em Certificados de Reservista.
Sua tarefa é analisar a imagem enviada, EXTRAIR todos os dados relevantes de um Certificado de Reservista,
VALIDAR esses dados e, em seguida, organizá-los em um objeto JSON. Caso imagem não aparente ser um Certificado de Reservista Original, retorne {"eh_certificado_reservista_valido": false, "motivos": ["Documento não é um Certificado de Reservista original."], "dados_organizados": {}}

**Critérios de Validação para um Certificado de Reservista:**
1. Presença obrigatória de termos como:
- “Certificado de Reservista” ou “Certificado de Dispensa de Incorporação (CDI)”
- “Serviço Militar”
- “Forças Armadas”, “Ministério da Defesa”, “Exército”, “Marinha” ou “Aeronáutica”
- Referência a uma Organização Militar (OM)
- Registro de Alistamento (RA, geralmente numérico com ou sem traço)
- Categoria (Apenas se for Certificado de Reservista ex: 1ª CATEGORIA, 2ª CATEGORIA, se for Certificado de Dispensa de Incorporação provavelmente não tem a categoria)
- Organização Militar (OM responsável)
- Data de Incorporação (formato DD/MM/AAAA)
- Data de Inclusão na Reserva (formato DD/MM/AAAA)
- Número do Certificado

2. Campos essenciais:
- Nome Completo
- CPF (formatos válidos XXX.XXX.XXX-XX ou XXXXXXXXX/XX)
- Filiação (Nome do Pai e da Mãe, ou um só nome como FILIAÇÃO)

3. Validações adicionais:
- Datas devem estar no formato DD/MM/AAAA.
- A Data de Incorporação deve ser anterior à Data de Reserva.
- Os campos devem estar consistentes com a terminologia militar.
- Se houver termos como “dispensado do serviço militar”, considerar como CDI.

Se for um Certificado de Reservista válido, retorne todos os dados organizados.
Se não for, marque como inválido e explique os motivos.

Responda **apenas** em JSON no seguinte formato:

{
    "eh_certificado_reservista_valido": boolean,
    "motivoErro": [
        "Motivo 1...",
        "Motivo 2..."
    ],
    "dados_organizados": {
        "nome": "string ou null",
        "cpf": "string ou null",
        "filiacao": {
            "mae": "string (Nome completo da mãe) ou null",
            "pai": "string (Nome completo do pai) ou null"
        }
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
            "eh_certificado_reservista_valido": False,
            "motivoErro": ["Erro: resposta não pôde ser convertida em JSON."],
            "dados_organizados": {}
        }

    return result

def processar_reservista(file_path: str) -> dict:
    try:
        resultado_ia = analisar_com_ia(file_path)

        if resultado_ia.get("eh_certificado_reservista_valido"):
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
