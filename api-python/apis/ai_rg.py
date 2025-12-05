import os
from dotenv import load_dotenv
import json
import fitz
import tempfile
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

PROMPT_ANALISAR_RG = """
Você é um especialista em análise de documentos de identificação brasileiros (RGs).
Sua tarefa é analisar **a imagem enviada**, avaliando se **ela é visualmente um RG autêntico** (mesmo que fictício para teste), e **somente então** extrair e validar os dados.

IMPORTANTE: 
- Você **NÃO** deve aprovar documentos que são prints de tela, capturas de texto, JSONs, PDFs de formulários, planilhas ou qualquer coisa que **não tenha aparência visual de um RG real físico**.
- Se o documento parecer texto digitalizado (como código, JSON, planilha, formulário ou relatório), ele **NÃO é um RG válido**, mesmo que contenha dados corretos.
- A decisão deve ser baseada **principalmente no conteúdo visual da imagem**, não no texto que ela contém.

---

### CRITÉRIOS PARA SER UM RG BRASILEIRO VÁLIDO:

#### 1. Integridade visual e autenticidade:
- **Foto do titular** visível (rosto humano).
- **Assinatura** visível (ou campo indicando “Não alfabetizado”).
- **Layout típico de RG:** blocos e campos com títulos como "Nome", "Filiação", "Data de Nascimento", "Número", "Data de Expedição", "Secretaria de Segurança Pública" etc.
- **Padrão visual de documento físico:** fundo com textura, brasão da república, caixas, selos, fontes impressas.
- **Ausência de elementos suspeitos:** prints de JSON, tabelas, formatações de código, interfaces de computador ou capturas de aplicativos.

#### 2. Campos essenciais (devem existir e estar legíveis):
- Nome completo
- CPF (XXX.XXX.XXX-XX ou XXXXXXXXX/XX)
- Data de nascimento (DD/MM/AAAA)
- Registro Geral (XX.XXX.XXX-X ou 9 dígitos)
- Data de expedição (DD/MM/AAAA)
- Filiação (pai e mãe)
- Naturalidade (Cidade - UF)

#### 3. Validação lógica:
- Data de nascimento deve ser anterior à data de expedição.
- CPF e RG devem estar nos formatos corretos.
- Foto e assinatura devem estar visíveis.
- Se o documento parecer incompleto, ilegível, digital ou for um print textual → deve ser rejeitado.

---

### INSTRUÇÕES DE SAÍDA

Responda **somente em JSON**, no seguinte formato:

{
  "eh_rg_valido": boolean,
  "motivoErro": [
    "Motivo 1 (ex: Documento é um print de tela com texto, não um RG físico)",
    "Motivo 2 (ex: Foto do titular ausente)",
    "Motivo 3 (ex: Layout não corresponde a um RG brasileiro)"
  ],
  "dados_organizados": {
    "nome": "string ou null",
    "cpf": "string ou null",
    "data_nascimento": "string (DD/MM/AAAA) ou null",
    "registro_geral": "string ou null",
    "data_expedicao": "string (DD/MM/AAAA) ou null",
    "filiacao": {
      "mae": "string ou null",
      "pai": "string ou null"
    },
    "naturalidade": "string ou null"
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
            "motivoErro": ["Erro: resposta não pôde ser convertida em JSON."],
            "dados_organizados": {}
        }

    return result

def processar_rg(file_path: str) -> dict:
    try:
        resultado_ia = analisar_com_ia(file_path)

        if resultado_ia.get("eh_rg_valido"):
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
