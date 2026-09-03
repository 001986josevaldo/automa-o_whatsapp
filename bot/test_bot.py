import sys
from ai_bot import AIBot  # Substitua 'ai_bot' pelo nome do seu arquivo .py

def executar_teste_real():
    print("🤖 Inicializando AIBot...")
    
    try:
        bot = AIBot()
        frase_teste = "Olá, boa tarde! Gostaria de fazer um pedido de pizza."
        
        print(f"\n[ENVIADO]: {frase_teste}")
        resposta = bot.invoke(frase_teste)
        
        print(f"[TRADUÇÃO]:\n{resposta}\n")
        
        assert isinstance(resposta, str) and len(resposta) > 0, "A resposta não pode ser vazia."
        print("✅ Teste integrado executado com sucesso!")

    except Exception as erro:
        print(f"❌ Falha no teste: {erro}")

if __name__ == "__main__":
    executar_teste_real()