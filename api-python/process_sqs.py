from dotenv import load_dotenv
load_dotenv()
import boto3
import json
import os
import time
import sys
from server import escolher_pipeline

sqs_client = boto3.client('sqs', region_name='us-east-1')

SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')

print(f"Iniciando processador SQS...")
print(f"  - SQS Queue: {SQS_QUEUE_URL}")
print(f"  - Pressione Ctrl+C para parar")
print("-" * 50)

def processar_mensagem_sqs():
    """Processa uma mensagem da fila SQS"""
    try:
        response = sqs_client.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20 
        )
        
        if 'Messages' in response:
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            print(f"[SQS] Mensagem recebida: {message['Body']}")
            
            try:
                payload = json.loads(message['Body'])
                print(f"[SQS] Iniciando processamento do documento ID: {payload.get('documentoId')}")
                print(f"[SQS] Tipo: {payload.get('tipoDocumento')}, Subtipo: {payload.get('subtipo')}")
                
                resultado = escolher_pipeline(payload)
                print(f"[SQS] Resultado do processamento: {json.dumps(resultado, ensure_ascii=False)}")
                
                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=receipt_handle
                )
                print(f"[SQS] Mensagem removida da fila.")
                
                if resultado.get('status') == 'erro':
                    print(f"[SQS] Erro detectado: {resultado.get('motivoErro')}")
                
                return resultado
                
            except Exception as e:
                print(f"[SQS] Erro ao processar mensagem: {e}")
                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=receipt_handle
                )
                print(f"[SQS] Mensagem removida da fila após erro.")
                return {
                    "status": "erro",
                    "motivoErro": f"Erro ao processar mensagem: {str(e)}"
                }
        else:
            return None
            
    except Exception as e:
        print(f"Erro ao acessar SQS: {e}")
        return {
            "status": "erro",
            "motivoErro": f"Erro ao acessar SQS: {str(e)}"
        }

def main():
    """Loop principal para processar mensagens continuamente"""
    mensagens_processadas = 0
    erros = 0
    
    try:
        while True:
            try:
                resultado = processar_mensagem_sqs()
                
                if resultado:
                    mensagens_processadas += 1
                    if resultado.get('status') == 'erro':
                        erros += 1
                    
                    print(f"[SQS] Estatísticas: Processadas={mensagens_processadas}, Erros={erros}, Sucesso={(mensagens_processadas - erros)}, Taxa de sucesso={((mensagens_processadas - erros) / mensagens_processadas * 100):.1f}%")
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print(f"\n[SQS] Interrompido pelo usuário.")
                print(f"[SQS] Total de mensagens processadas: {mensagens_processadas}")
                print(f"[SQS] Total de erros: {erros}")
                sys.exit(0)
                
            except Exception as e:
                print(f"Erro inesperado no loop principal: {e}")
                time.sleep(5)  
                
    except Exception as e:
        print(f"Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
