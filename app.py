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

    print(f'EVENTO RECEBIDO: {data}')

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
        received_message = payload['body']
        session = data.get('session', 'default')

    except KeyError as e:
        print(f"Erro de estrutura no payload: {e}")
        return jsonify({"status": "error", "message": "Invalid message structure"}), 400

    # 3. Processa a IA e envia a resposta
    try:
        # 1. Ativa o "digitando..." imediatamente ao receber a mensagem
        waha.start_typing(chat_id=chat_id)

        
        
        # 2. Processa a IA (o tempo de geração do Gemini serve como delay natural)
        response = ai_bot.invoke(question=received_message)

        # 3. Pequena pausa para simular digitação humana
        time.sleep(random.randint(2, 4))  # Simula tempo de "digitando..." para parecer mais humano

        # Dispara o envio do texto de volta ao WhatsApp
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
        # Garante que o indicador "digitando..." seja removido mesmo em caso de erro
        try:
            waha.stop_typing(chat_id=chat_id)
        except Exception:
            pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
