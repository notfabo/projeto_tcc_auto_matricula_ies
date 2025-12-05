import requests
import os

class RecognitionAPI:
    def __init__(self, api_key, model="TESTE"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://app.recognition-ia.com/recognition-api/api/v1/services"
        self.headers = {
            "Accept": "application/json",
            "RECOGNITION-SERVICE-API-KEY": self.api_key
        }

    def enviar_documento(self, caminho_arquivo):
        """
        Envia um documento para processamento na API de Recognition
        
        Args:
            caminho_arquivo (str): Caminho do arquivo a ser processado
            
        Returns:
            dict: Resposta da API com o ID do batch
        """
        url = f"{self.base_url}/batches?model={self.model}"
        
        try:
            with open(caminho_arquivo, "rb") as arquivo:
                files = {"files": arquivo}
                response = requests.post(url, headers=self.headers, files=files)
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar documento: {e}")
            return None

    def buscar_resultado(self, batch_id):
        """
        Busca o resultado do processamento de um documento
        
        Args:
            batch_id (str): ID do batch retornado pela API
            
        Returns:
            dict: Resultado do processamento
        """
        url = f"{self.base_url}/batches/{batch_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar resultado: {e}")
            return None

def main():
    api_key = "2c9f9652-da5b-4f15-8167-8e27c6a9afb2"
    recognition = RecognitionAPI(api_key)
    
    caminho_rg = os.path.join(os.path.dirname(__file__), "rg-verso.png")
    
    print("Enviando documento para processamento...")
    resultado_envio = recognition.enviar_documento(caminho_rg)
    
    if resultado_envio:
        print("Documento enviado com sucesso!")
        print("Resposta:", resultado_envio)
        
        batch_id = resultado_envio.get("id") 
        if batch_id:
            print("\nBuscando resultado do processamento...")
            resultado = recognition.buscar_resultado(batch_id)
            if resultado:
                print("Resultado encontrado:")
                print(resultado)

if __name__ == "__main__":
    main()