import time
import random

from flask import Flask, request, jsonify

from services.waha import Waha
from bot.ai_bot import AIBot


app = Flask(__name__)
waha = Waha()
ai_bot = AIBot()


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)