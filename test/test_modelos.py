import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Localiza o arquivo .env na pasta anterior (diretório pai)
env_path = Path(__file__).resolve().parent.parent / ".env"

# Carrega as variáveis do arquivo .env encontrado
load_dotenv(dotenv_path=env_path)

# Recupera a chave
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    print(f"❌ Erro: Não foi possível encontrar a chave no caminho: {env_path}")
    exit(1)

print(f"✅ Arquivo .env carregado de: {env_path}")

if not api_key:
    print(f"❌ Erro: Chave não encontrada no caminho: {env_path}")
    exit(1)


# Inicializa o cliente com a chave
client = genai.Client(api_key=api_key)

print("🔍 Buscando modelos disponíveis na sua conta...\n")

try:
    modelos_validos = []
    for model in client.models.list():
        methods = getattr(model, "supported_generation_methods", []) or []
        if "generateContent" in methods:
            nome_modelo = model.name.replace("models/", "")
            modelos_validos.append(nome_modelo)

    print("=== MODELOS DISPONÍVEIS ===")
    for m in modelos_validos:
        print(f" • {m}")

    # Testa o envio com o modelo recomendado
    modelo_teste = "gemini-1.5-flash-latest" if "gemini-1.5-flash-latest" in modelos_validos else modelos_validos[0]
    print(f"\n⚡ Testando envio de mensagem usando '{modelo_teste}'...")

    response = client.models.generate_content(
        model=modelo_teste,
        contents="Responda apenas: CONEXAO_OK"
    )
    print(f"✅ Sucesso! Resposta da IA: {response.text.strip()}")

except Exception as e:
    print(f"❌ Erro na comunicação com a API: {e}")