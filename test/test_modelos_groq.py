import os
import requests
from decouple import config  # ou use os.getenv se preferir

# Carrega a chave da Groq
API_KEY = config("GROQ_API_KEY")  # ou o nome da variável que você usa no .env

print(f"Chave carregada: {API_KEY[:8]}...{API_KEY[-5:] if API_KEY else 'NENHUMA'}")
print(f"Tamanho da chave: {len(API_KEY) if API_KEY else 0}\n")

url = "https://api.groq.com/openai/v1/models"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    models = data.get("data", [])

    print(f"Total de modelos disponíveis na Groq: {len(models)}\n")
    print("-" * 60)

    # Ordena por ID
    for model in sorted(models, key=lambda x: x.get("id", "")):
        model_id = model.get("id", "N/A")
        owned_by = model.get("owned_by", "N/A")
        context = model.get("context_window", "N/A")
        active = model.get("active", "N/A")

        print(f"ID: {model_id}")
        print(f"  Owned by: {owned_by}")
        print(f"  Context window: {context}")
        print(f"  Active: {active}")
        print("-" * 60)

except requests.exceptions.HTTPError as e:
    print(f"Erro HTTP: {e}")
    print(f"Resposta: {response.text}")
except Exception as e:
    print(f"Erro: {e}")