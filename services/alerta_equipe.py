import os
import requests
import threading
from html import escape

class AlertaEquipe:
    def __init__(self):
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    def _send_telegram(self, chat_id, last_message):
        if not self.telegram_bot_token or not self.telegram_chat_id:
            print("⚠️ Variáveis TELEGRAM_BOT_TOKEN e/ou TELEGRAM_CHAT_ID não estão configuradas.")
            return

        telegram_url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        
        text = (
            "🚨 <b>Atendimento Humano Solicitado</b>\n\n"
            f"📱 <b>Cliente:</b> <code>{escape(str(chat_id))}</code>\n"
            f"💬 <b>Última Mensagem:</b> {escape(str(last_message))}"
        )
        
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        try:
            # Timeout ajustado: 5s para conectar, 10s para receber resposta
            response = requests.post(telegram_url, json=payload, timeout=(5, 10))
            if response.status_code == 200:
                print("✅ Alerta enviado ao Telegram com sucesso.")
            else:
                error_message = response.json().get("description", response.text)
                if error_message == "Bad Request: chat not found":
                    print(
                        "⚠️ Telegram não encontrou o chat configurado. "
                        "Verifique TELEGRAM_CHAT_ID e envie /start ao bot "
                        "(ou adicione o bot ao grupo)."
                    )
                else:
                    print(f"⚠️ Telegram retornou status {response.status_code}: {error_message}")
        except Exception as e:
            print(f"⚠️ Falha ao notificar Telegram: {e}")

    def notify_support_team(self, chat_id, last_message, canal=2):
        print(f"🚨 [ALERTA TRANSBORDO] Cliente {chat_id} solicita atendimento humano!")
        
        # Dispara o envio em segundo plano para não travar a resposta da Flask/Webhook
        threading.Thread(
            target=self._send_telegram,
            args=(chat_id, last_message),
            daemon=True
        ).start()


# Instância global e atalho de função
_alerta_service = AlertaEquipe()

def notify_support_team(chat_id, last_message, canal=2):
    _alerta_service.notify_support_team(chat_id=chat_id, last_message=last_message, canal=canal)


