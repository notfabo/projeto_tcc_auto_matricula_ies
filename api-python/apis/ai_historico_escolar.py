import os
from dotenv import load_dotenv
import json
import fitz
import tempfile
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

PROMPT_ANALISAR = """
Você é um especialista em análise de documentos acadêmicos, focado em históricos escolares.
Sua tarefa é analisar a imagem enviada se é um documento de histórico escolar, ANALISAR E IDENTIFICAR todos os dados relevantes de um histórico escolar,
VALIDAR esses dados e, em seguida, organizar em um objeto JSON apenas com os campos necessários, caso contrário retorne {"eh_historico_valido": false, "motivos": ["Documento não é um histórico escolar original."], "dados_organizados": {}}

**Critérios de identificação, análise e validação para um Histórico Escolar:**
1. Presença obrigatória de termos como:
   - Nome Completo do Aluno: Deve ser um nome próprio.
   - Nome da Instituição de Ensino: Nome de uma escola ou instituição de ensino.
   - Nº da Matrícula: Deve ser um número ou código de matrícula.
   - Nível de Ensino: Deve indicar o nível de ensino (ex: Ensino Fundamental, Ensino Médio, Ensino Técnico).
   - Anos Cursados: Deve identificar os anos ou séries cursadas (ex: "1º Ano do Ensino Médio", "Ensino Fundamental").
   - Tempo Letivo: Deve ser um ano ou intervalo de anos (ex: "2020", "2019-2021").
   - Disciplinas Cursadas**: Deve ser uma lista de objetos, onde cada objeto representa uma disciplina e contém:
        * `nome disciplina`: string (nome da disciplina).
        * `carga horária (ch)`: string (ex: "80h", "60 horas", "2 unidades").
        * `média ou nota`: string (ex: "7.5", "Aprovado", "B").
   - Nome do Responsável: Nome completo de um responsável (pode ser o diretor, secretário, etc.).
   - Cidade: Nome da cidade onde a instituição está localizada.
   - Estado: Sigla do estado (UF, ex: "SP", "RJ", "MG").
   - Certificação de Conclusão: Deve conter uma declaração de conclusão do ensino, dando a intenção de que o aluno concluiu o curso e pode dar continuidade aos estudos em níveis superiores.

2. Campos essenciais:
   - Nome Completo do Aluno
   - Nome da Instituição de Ensino
   - Nível de Ensino
   - Tempo Letivo
   - Cidade
   - Estado (UF)
   - Possui Certificação de Conclusão

3.  **Consistência dos Dados**:
    - O `Tempo Letivo` deve ser um ano plausível e, se houver datas no documento, as datas de conclusão/emissão devem ser consistentes com os anos letivos.
    - As disciplinas, notas e carga horária devem estar logicamente associadas, se encontradas.
    - Nome de responsável normalmente é o diretor ou secretário da instituição. Seguindo de uma assinatura.

    Se um campo obrigatório for ausente ou tiver um formato inválido/inconsistente, inclua um motivo específico.
    Retorne motivos apenas se o documento não for um histórico escolar ou/e se houver problemas de validação.

Responda **apenas** em JSON no seguinte formato, o JSON deve retornar apenas os campos abaixo:

{
  "eh_historico_valido": boolean,
  "motivoErro": [
    "Motivo 1...",
    "Motivo 2..."
  ],
  "dados_organizados": {
    "nome_aluno": "string (Nome completo do aluno) ou null",
    "nivel_ensino": "string (Nível de ensino) ou null",
    "instituicao_ensino": "string (Nome da instituição de ensino) ou null",
    "tempo_letivo": "string (AAAA - AAAA) ou null",
    "cidade": "string (Cidade) ou null",
    "estado": "string (Estado/UF) ou null",
    "certificacao_conclusao": boolean
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
            "eh_historico_valido": False,
            "motivoErro": ["Erro: resposta não pôde ser convertida em JSON."],
            "dados_organizados": {}
        }

    return result

def processar_historico_escolar(file_path: str) -> dict:
    try:
        resultado_ia = analisar_com_ia(file_path)

        if resultado_ia.get("eh_historico_valido"):
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
        print(f"Erro crítico ao processar histórico escolar: {e}")
        return {
            "status": "erro",
            "dadosExtraidos": {},
            "motivoErro": f"Erro inesperado no módulo de IA: {str(e)}"
        }
