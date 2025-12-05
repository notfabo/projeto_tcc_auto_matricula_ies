import os
from dotenv import load_dotenv
import json
import fitz
import tempfile
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

PROMPT_ANALISAR = """
Você é um especialista em análise de documentos educacionais brasileiros, focado em Boletins de Desempenho do ENEM.
Sua tarefa é analisar a imagem enviada, EXTRAIR todos os dados relevantes de um Boletim do ENEM,
VALIDAR esses dados e, em seguida, organizá-los em um objeto JSON, caso contrário retorne {"eh_boletim_valido": false, "motivos": ["Documento não é um Boletim do Enem original."], "dados_organizados": {}}

**Critérios de Validação para um Boletim do ENEM:**

1. Presença obrigatória de termos como:
- Nome do Participante (nome completo)
- CPF deve estar em formato numérico com 11 dígitos, mesmo que contenha separadores incomuns (., -, /).
- Número de inscrição deve ter pelo menos 11 dígitos numéricos.
- Ano do ENEM (ex: 2022, 2023)
- Notas das Provas (todas devem estar presentes e ser valores numéricos válidos):
    * Linguagens, Códigos e suas Tecnologias
    * Ciências Humanas e suas Tecnologias
    * Ciências da Natureza e suas Tecnologias
    * Matemática e suas Tecnologias
    * Redação

2. Campos essenciais:
- Nome do Participante
- CPF 
- Ano do ENEM

2. Validações adicionais:
- O Número de Inscrição deve ter o formato esperado (geralmente 12 dígitos).
- O Ano do ENEM deve ser um ano válido (>= 1998).
- As notas devem ser números (floats). Se algum campo não for encontrado ou não for numérico, deve ser considerado inválido.
- Se faltar qualquer campo obrigatório, o boletim não é válido.

**Atenção:**
A imagem pode estar rotacionada (na vertical ou deitada).
Leia os campos independentemente da orientação do texto.
Se for um Boletim do ENEM válido, retorne todos os dados organizados.
Se não for, marque como inválido e explique os motivos.

Responda **apenas** em JSON no seguinte formato:

{
    "eh_boletim_valido": boolean,
    "motivoErro": [
        "Motivo 1...",
        "Motivo 2..."
    ],
    "dados_organizados": {
        "nome_participante": "string ou null",
        "cpf": "string (11 dígitos) ou null",
        "ano_enem": "integer ou null",
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

def processar_enem(file_path: str) -> dict:
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
