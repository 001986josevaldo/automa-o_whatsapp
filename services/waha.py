import os
import requests

class Waha:
    def __init__(self):
        self.url = os.getenv("WAHA_API_URL", "http://waha:3000")
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": os.getenv("WAHA_API_KEY", "")
        }

    def start_typing(self, chat_id, session="default"):
        if "@lid" in chat_id:
            return None

        url = f"{self.url}/api/startTyping"
        payload = {"chatId": chat_id, "session": session}

        try:
            res = requests.post(url, json=payload, headers=self.headers, timeout=2)
            return res
        except Exception as e:
            print(f"⚠️ Falha no startTyping: {e}")
            return None

    def stop_typing(self, chat_id, session="default"):
        # Ignora @lid para evitar erros 404/422 no webhook
        if "@lid" in chat_id:
            return None

        url = f"{self.url}/api/stopTyping"
        payload = {"chatId": chat_id, "session": session}

        try:
            return requests.post(url, json=payload, headers=self.headers, timeout=2)
        except Exception:
            return None

    def send_message(self, chat_id, message, session="default"):
        url = f"{self.url}/api/sendText"
        payload = {"chatId": chat_id, "text": message, "session": session}
        return requests.post(url, json=payload, headers=self.headers, timeout=10)

    def get_history_messages(self, chat_id, limit=10, session="default"):
        url = f"{self.url}/api/messages"
        params = {
            "chatId": chat_id,
            "limit": limit,
            "session": session,
            "downloadMedia": "false"
        }
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    return data.get("messages", data.get("data", []))
                if isinstance(data, list):
                    return data
            return []
        except Exception as e:
            print(f"⚠️ Erro ao buscar histórico no WAHA: {e}")
            return []