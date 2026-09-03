import time
import sys
from pathlib import Path

# Adiciona o diretório raiz ao caminho de busca do Python
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ_PROJETO))

from bot.ai_bot import AIBot

def testar_respostas_chat():
    print("🤖 INICIANDO TESTE DE RESPOSTAS DO CHAT\n" + "="*50)
    
    bot = AIBot()

    mensagens_teste = [
        "Olá, boa tarde! Como você funciona?",
        "Gostaria de saber o valor do plano mensal.",
        "Obrigado pela ajuda!",
    ]

    for index, mensagem in enumerate(mensagens_teste, start=1):
        print(f"\n[Mensagem {index}]: '{mensagem}'")
        
        tempo_inicio = time.time()
        try:
            resposta = bot.invoke(question=mensagem)
            duracao = round(time.time() - tempo_inicio, 2)

            print(f"⏱️ Tempo de geração: {duracao}s")
            print(f"💬 Resposta gerada:\n{resposta}")
            print("-" * 50)

            # Validação básica do retorno
            assert isinstance(resposta, str) and len(resposta.strip()) > 0, "Resposta vazia ou inválida"

        except Exception as erro:
            print(f"❌ Erro ao gerar resposta: {erro}")

if __name__ == "__main__":
    testar_respostas_chat()