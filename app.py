import time
import random

from flask import Flask, request, jsonify

from services.waha import Waha
from bot.ai_bot import AIBot
from services.state import is_human_active, set_human_active, set_bot_active
from services.alerta_equipe import notify_support_team


app = Flask(__name__)
waha = Waha()
ai_bot = AIBot()

# Palavras-chave que indicam necessidade de falar com humano
HUMAN_INTENTS = ["falar com atendente", "humano", "pessoa", "suporte humano", "falar com suporte", "atendente"]

@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.json or {}

    # apoenas para imprimir no console os dados recebidos do webhook
    print("==========EVENTO RECEBIDO=======:")
    event_id = data.get("id")
    session = data.get("session")
    body = data.get("payload", {}).get("body", "")
    contato = data.get("payload", {}).get("from", "")

    print(f"ID: {event_id}")
    print(f"SESSÃO: {session}")
    print(f"Contato: {contato}")
    print(f"Mensagem: {body}")
    
    print("=============================")

    #print(f'EVENTO RECEBIDO: {data}')
    print()

    # 1. Ignora eventos que não sejam mensagens de chat
    if data.get('event') != 'message':
        return jsonify({"status": "ignored", "reason": "not a message event"}), 200

    # 2. Extrai dados da mensagem e sessão
    try:
        payload = data.get('payload', {})
        
        # Ignora mensagens enviadas pelo próprio bot (evita loops)
        if payload.get('fromMe'):
            return jsonify({'status': 'ignored', 'reason': 'message sent by me'}), 200

        chat_id = payload['from']
        received_message = payload.get('body', '')
        session = data.get('session', 'default')

        # # 1. Se a conversa já está com humano, a IA ignora em silêncio
        if is_human_active(chat_id):
            return jsonify({"status": "ignored", "reason": "human_mode_active"}), 200

        # 2. Verifica se o cliente expressou necessidade de atendimento humano
        if any(keyword in received_message.lower() for keyword in HUMAN_INTENTS):
            set_human_active(chat_id)
            
            # Avisa o cliente e notifica a equipe interna
            waha.send_message(
                chat_id=chat_id, 
                message="Entendido! Estou transferindo seu atendimento para uma pessoa da nossa equipe. Aguarde um momento. ⏳",
                session=data.get('session', 'default')
            )
            # Dispara alerta para a equipe (Telegram, Slack, Webhook do CRM)
            notify_support_team(chat_id=chat_id, last_message=received_message, canal=2)  # Canal 1 = Webhook, Canal 2 = Telegram
            return jsonify({"status": "transferred_to_human"}), 200




        

        # 3. Se não precisa de humano, o fluxo da IA/Gemini segue normalmente...
        # ...

    except KeyError as e:
        print(f"Erro de estrutura no payload: {e}")
        return jsonify({"status": "error", "message": "Invalid message structure"}), 400

    # 3. Processa a IA e envia a resposta
    try:
        # Ativa o "digitando..." passando a sessão atual
        waha.start_typing(chat_id=chat_id, session=session)

        # Busca o histórico do chat garantindo o envio da sessão
        history_messages = waha.get_history_messages(
            chat_id=chat_id,
            limit=10,
            session=session
        )
        
        # Processa a resposta via IA
        response = ai_bot.invoke(history_messages=history_messages, question=received_message)

        # Pausa para simular digitação humana
        time.sleep(random.randint(2, 4))

        # Envia a mensagem de volta
        waha.send_message(
            chat_id=chat_id,
            message=response,
            session=session
        )
        print(f"✅ RESPOSTA ENVIADA PARA {chat_id}: {response}")

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"❌ Erro ao gerar/enviar resposta: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        # Remove o indicador de digitação de forma segura
        try:
            waha.stop_typing(chat_id=chat_id, session=session)
        except Exception:
            pass

# Endpoint interno para seu CRM/Painel avisar que o atendimento humano acabou
@app.route('/api/chat/close-human', methods=['POST'])
def close_human_chat():
    data = request.json or {}
    chat_id = data.get("chat_id")
    
    if chat_id:
        set_bot_active(chat_id)
        return jsonify({"status": "success", "message": f"IA reativada para {chat_id}"}), 200
        
    return jsonify({"status": "error", "message": "chat_id ausente"}), 400






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)