import requests
import time

# URL do endpoint local
URL = "http://localhost:5000/chatbot/webhook/"

def testar_mensagem_valida():
    print("1. Testando envio de MENSAGEM VÁLIDA (Aguarde de 3 a 10s pelo sleep do app)...")
    payload = {
        "event": "message",
        "payload": {
            "from": "5511999999999@c.us",
            "body": "Olá, qual é o seu horário de funcionamento?"
        }
    }
    
    inicio = time.time()
    response = requests.post(URL, json=payload)
    duracao = round(time.time() - inicio, 2)

    print(f"   Status Code: {response.status_code}")
    print(f"   Resposta: {response.json()}")
    print(f"   Tempo de resposta: {duracao}s\n")

def testar_evento_ignorado():
    print("2. Testando EVENTO DIFERENTE DE MENSAGEM (Deve ignorar com status 200)...")
    payload = {
        "event": "session.status",
        "payload": {
            "status": "WORKING"
        }
    }
    
    response = requests.post(URL, json=payload)
    print(f"   Status Code: {response.status_code}")
    print(f"   Resposta: {response.json()}\n")

def testar_estrutura_invalida():
    print("3. Testando ESTRUTURA INVÁLIDA (Faltando 'from'/'body' - Deve retornar 400)...")
    payload = {
        "event": "message",
        "payload": {}
    }
    
    response = requests.post(URL, json=payload)
    print(f"   Status Code: {response.status_code}")
    print(f"   Resposta: {response.json()}\n")

if __name__ == "__main__":
    print("🚀 Iniciando testes na API Flask...\n")
    testar_evento_ignorado()
    testar_estrutura_invalida()
    testar_mensagem_valida()