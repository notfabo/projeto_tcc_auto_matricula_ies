from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
import boto3
import json
import os
import tempfile
import requests
from apis.ai_rg import processar_rg
from apis.ai_historico_escolar import processar_historico_escolar
# from apis.ai_conclusao_em import processar_conclusao_em
from apis.ai_comprovante_residencial import processar_comprovante_residencial
from apis.ai_reservista import processar_reservista
from apis.ai_certidao_nascimento import processar_certidao_nascimento
from apis.ai_enem import processar_enem

app = Flask(__name__)

s3_client = boto3.client('s3', region_name='us-east-1')
sqs_client = boto3.client('sqs', region_name='us-east-1')

BUCKET_NAME = os.getenv('S3_BUCKET_NAME') 
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')  
BACKEND_URL = os.getenv('BACKEND_URL')  
API_KEY = os.getenv('API_KEY')  

print(f"Configurações carregadas:")
print(f"  - S3 Bucket: {BUCKET_NAME}")
print(f"  - SQS Queue: {SQS_QUEUE_URL}")

def baixar_arquivo_s3(caminho_arquivo):
    """Baixa um arquivo do S3 para um arquivo temporário local"""
    try:
        ext = os.path.splitext(caminho_arquivo)[1] or '.pdf'
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        temp_path = temp_file.name
        temp_file.close()
        
        s3_client.download_file(BUCKET_NAME, caminho_arquivo, temp_path)
        print(f"Arquivo baixado do S3: {caminho_arquivo} -> {temp_path}")
        
        return temp_path
    except Exception as e:
        print(f"Erro ao baixar arquivo do S3: {e}")
        raise

def atualizar_status_backend(resultado):

    if not resultado.get("documentoId"):
        print("Erro Crítico: Tentativa de atualizar status sem documentoId.")
        return False
    try:
        url = f"{BACKEND_URL}/api/documentos/atualizar-status"
        
        payload = {
            "documentoId": resultado["documentoId"],
            "status": resultado["status"]
        }
        
        if "dadosExtraidos" in resultado and resultado["dadosExtraidos"]:
            payload["dadosExtraidos"] = json.dumps(resultado["dadosExtraidos"])
        
        if "motivoErro" in resultado and resultado["motivoErro"]:
            motivo_erro_obj = {"mensagem": resultado["motivoErro"]}
            payload["motivoErro"] = json.dumps(motivo_erro_obj)
        
        print(f"Atualizando status no backend: {payload}")
        
        headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"Status atualizado com sucesso: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro de comunicação com o backend: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado ao atualizar status no backend: {e}")
        return False

def escolher_pipeline(payload):
    documento_id = payload["documentoId"]

    try:
        tipo = payload.get("tipoDocumento", "").lower()
        subtipo = payload.get("subtipo")
        caminho = payload["caminhoArquivo"]
        documento_id = payload["documentoId"]
        
        print(f"Processando documento ID: {documento_id}")
        print(f"Tipo: {tipo}, Subtipo: {subtipo}, Caminho: {caminho}")
        
        arquivo_local = None
        resultado = None

            
        try:
            arquivo_local = baixar_arquivo_s3(caminho)

            if "identidade" in tipo:
                if subtipo == "rg":
                    resultado = processar_rg(arquivo_local)
                elif subtipo == "cin":
                    # TODO: Implementar processamento de CIN
                    return {
                        "documentoId": documento_id, 
                        "status": "erro", 
                        "motivoErro": "CIN não implementado ainda"
                    }
                else:
                    return {
                        "documentoId": documento_id, 
                        "status": "erro", 
                        "motivoErro": f"Subtipo '{subtipo}' não reconhecido para documentos de identidade"
                    }
            # elif "conclusao_em" in tipo or "certificado" in tipo:
            #     resultado = processar_conclusao_em(arquivo_local)
            elif "histórico escolar" in tipo:
                resultado = processar_historico_escolar(arquivo_local)
            elif "comprovante de residência" in tipo:
                resultado = processar_comprovante_residencial(arquivo_local)
            elif "certificado de reservista (obrigatório para homens)" in tipo:
                resultado = processar_reservista(arquivo_local)
            elif "certidão de nascimento ou casamento" in tipo:
                resultado = processar_certidao_nascimento(arquivo_local)
            elif "boletim do enem (obrigatório para alunos que entram pelo sisu ou pela nota do enem)" in tipo:
                resultado = processar_enem(arquivo_local)
            else:
                resultado = {"status": "erro", "motivoErro": f"Tipo de documento '{tipo}' não reconhecido."}
        finally:
            if arquivo_local and os.path.exists(arquivo_local):
                os.remove(arquivo_local)
                print(f"Arquivo temporário removido: {arquivo_local}")            
    except Exception as e:
        print(f"Erro no processamento do documento {documento_id}: {e}")
        resultado = {
            "status": "erro",
            "motivoErro": f"Erro inesperado no pipeline: {str(e)}"
        }
    resultado["documentoId"] = documento_id
    atualizar_status_backend(resultado)
    return resultado

# Rota para verificar documentos
@app.route("/verify-docs", methods=["POST"])
def verify_docs():
    try:
        payload = request.get_json()
        if not payload or "matricula_id" not in payload:
            return jsonify({"erro": "ID da matrícula não fornecido"}), 400

        # Importa a função verify do módulo verify_docs
        from verify_docs import app as verify_workflow
        
        # Executa a verificação
        inputs = {"matricula_id": payload["matricula_id"]}
        final_state = None
        
        for state in verify_workflow.stream(inputs):
            final_state = state
            
        # Pega o resultado final
        result = final_state.get("END", {})
        
        response = {
            "status": result.get("final_status", "pendente"),
            "observacao": result.get("final_observation", "Erro na verificação")
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Erro ao verificar documentos: {e}")
        return jsonify({
            "status": "pendente",
            "observacao": f"Erro ao verificar documentos: {str(e)}"
        }), 500

def processar_mensagem_sqs():
    """Processa mensagens da fila SQS"""
    try:
        # Recebe mensagem da fila SQS
        response = sqs_client.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20  # Long polling
        )
        
        if 'Messages' in response:
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            
            try:
                # Parse do payload
                payload = json.loads(message['Body'])
                print(f"Mensagem recebida: {payload}")
                
                # Processa o documento
                resultado = escolher_pipeline(payload)
                
                # Remove a mensagem da fila
                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=receipt_handle
                )
                
                print(f"Resultado do processamento: {resultado}")
                return resultado
                
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
                # Remove a mensagem da fila mesmo em caso de erro para evitar loop infinito
                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=receipt_handle
                )
                return {
                    "status": "erro",
                    "motivoErro": f"Erro ao processar mensagem: {str(e)}"
                }
        else:
            print("Nenhuma mensagem na fila")
            return None
            
    except Exception as e:
        print(f"Erro ao acessar SQS: {e}")
        return {
            "status": "erro",
            "motivoErro": f"Erro ao acessar SQS: {str(e)}"
        }

# Endpoint para testes manuais (pode ser chamado pelo backend)
@app.route("/processar", methods=["POST"])
def processar():
    try:
        payload = request.get_json()
        resultado = escolher_pipeline(payload)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Endpoint para processar mensagens do SQS
@app.route("/processar-sqs", methods=["POST"])
def processar_sqs():
    try:
        resultado = processar_mensagem_sqs()
        if resultado:
            return jsonify(resultado)
        else:
            return jsonify({"mensagem": "Nenhuma mensagem na fila"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Endpoint de health check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok", 
        "mensagem": "Servidor de IA funcionando",
        "configuracoes": {
            "s3_bucket": BUCKET_NAME,
            "sqs_queue": SQS_QUEUE_URL
        }
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')
