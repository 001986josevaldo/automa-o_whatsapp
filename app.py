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

@app.route('/chatbot/webhook', methods=['POST'])
def webhook():
    data = request.json or {}

    # ==========================================
    # 1. DADOS DO EVENTO
    # ==========================================

    event_id = data.get("id")
   
    session = data.get("session", "default")
    event = data.get("event")

    payload = data.get("payload") or {}

    chat_id = payload.get("from")
    #print(f"Chat ID: {chat_id}")

    chat_id = waha.resolve_lid_to_phone(chat_id, session=session)
    print(f"Real Chat ID: {chat_id}")

    received_message = payload.get("body", "")

    if isinstance(received_message, str):
        received_message = received_message.strip()
    else:
        received_message = ""

    # ==========================================
    # 2. DEBUG
    # ==========================================

    print("========== EVENTO RECEBIDO ==========")
    print(f"ID:       {event_id}")
    print(f"SESSÃO:   {session}")
    print(f"EVENTO:   {event}")
    print(f"Contato:  {chat_id}")
    print(f"Mensagem: {received_message}")
    print("=====================================")

    # ==========================================
    # 3. IGNORA EVENTOS QUE NÃO SÃO MENSAGENS
    # ==========================================

    if event != "message":
        return jsonify({
            "status": "ignored",
            "reason": "not_a_message_event"
        }), 200

    # ==========================================
    # 4. IGNORA MENSAGEM DO PRÓPRIO BOT
    # ==========================================

    if payload.get("fromMe"):
        return jsonify({
            "status": "ignored",
            "reason": "message_sent_by_me"
        }), 200

    # ==========================================
    # 5. VALIDA CONTATO
    # ==========================================

    if not chat_id:
        print("⚠️ Evento sem contato.")
        return jsonify({
            "status": "ignored",
            "reason": "missing_chat_id"
        }), 200

    # ==========================================
    # 6. VALIDA MENSAGEM
    # ==========================================

    if not received_message:
        print("⚠️ Mensagem vazia. Ignorando evento.")
        return jsonify({
            "status": "ignored",
            "reason": "empty_message"
        }), 200

    # ==========================================
    # 7. PROCESSAMENTO
    # ==========================================

    try:

        # --------------------------------------
        # Verifica se atendimento humano está ativo
        # --------------------------------------

        if is_human_active(chat_id):
            return jsonify({
                "status": "ignored",
                "reason": "human_mode_active"
            }), 200

        # --------------------------------------
        # Verifica intenção de atendimento humano
        # --------------------------------------

        if any(
            keyword in received_message.lower()
            for keyword in HUMAN_INTENTS
        ):

            set_human_active(chat_id)

            waha.send_message(
                chat_id=chat_id,
                message=(
                    "Entendido! Seu atendimento está sendo transferido "
                    "para um de nossos especialistas. Lembramos que nossa "
                    "equipe atende em horário comercial. Assim que possível, "
                    "entraremos em contato. Por favor, aguarde um momento. ⏳"
                ),
                session=session
            )

            notify_support_team(
                chat_id=chat_id,
                last_message=received_message,
                canal=2
            )

            return jsonify({
                "status": "transferred_to_human"
            }), 200

        # ======================================
        # 8. DIGITANDO
        # ======================================

        waha.start_typing(
            chat_id=chat_id,
            session=session
        )
        #
        # ======================================
        # 9. HISTÓRICO LIMPO
        # ======================================

        raw_history = waha.get_history_messages(
            chat_id=chat_id,
            limit=5,
            session=session
        )

        history_messages = []

        for msg in raw_history:
            body = msg.get("body")
            if not body or not str(body).strip():
                continue

            role = "assistant" if msg.get("fromMe") else "user"
            history_messages.append({
                "role": role,
                "content": str(body).strip()
            })

        # Deixa na ordem cronológica (mais antiga → mais recente)
        history_messages = list(reversed(history_messages))

        print("========== HISTÓRICO ==========")
        for m in history_messages:
            print(f"{m['role'].upper():<10} | {m['content']}")
        print("===============================")






        # ======================================
        # 10. IA / RAG / GROQ
        # ======================================

        response = ai_bot.invoke(
            history_messages=history_messages,
            question=received_message
        )

        # ======================================
        # 11. SIMULA DIGITAÇÃO
        # ======================================

        time.sleep(random.randint(2, 4))

        # ======================================
        # 12. ENVIA RESPOSTA
        # ======================================

        waha.send_message(
            chat_id=chat_id,
            message=response,
            session=session
        )

        print(
            f"✅ RESPOSTA ENVIADA PARA {chat_id}: {response}"
        )

        return jsonify({
            "status": "success"
        }), 200

    except Exception as e:

        print(
            f"❌ Erro ao gerar/enviar resposta: {e}"
        )

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:

        try:
            waha.stop_typing(
                chat_id=chat_id,
                session=session
            )
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