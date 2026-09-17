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
        # WAHA não mostra typing em @lid
        if "@lid" in chat_id:
            print(f"⚠️ Ignorando startTyping para {chat_id} (é @lid)")
            return None

        # 1. Tenta o endpoint clássico
        url = f"{self.url}/api/startTyping"
        payload = {
            "chatId": chat_id,
            "session": session
        }

        try:
            res = requests.post(url, json=payload, headers=self.headers, timeout=8)
            
            if res.status_code in (200, 201):
                print(f"✅ startTyping OK → {chat_id}")
                return res
            
            # Se falhou, tenta o endpoint de presence (mais confiável)
            print(f"⚠️ startTyping falhou ({res.status_code}), tentando presence...")
            
        except Exception as e:
            print(f"⚠️ Erro no startTyping: {e}")

        # 2. Fallback usando presence (recomendado pela documentação)
        try:
            url_presence = f"{self.url}/api/{session}/presence"
            payload_presence = {
                "chatId": chat_id,
                "presence": "typing"
            }
            res2 = requests.post(url_presence, json=payload_presence, headers=self.headers, timeout=8)
            
            if res2.status_code in (200, 201):
                print(f"✅ presence=typing OK → {chat_id}")
                return res2
            else:
                print(f"❌ presence também falhou: {res2.status_code} - {res2.text}")
                return None
                
        except Exception as e:
            print(f"❌ Falha no presence: {e}")
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


    def resolve_lid_to_phone(self, chat_id, session="session_01m2kmx093svxyhx77wpyq91vw"):
        """
        Converte @lid para o número real (@c.us).
        Retorna o chat_id original se não conseguir resolver.
        """
        # Proteção contra None / vazio
        if not chat_id or not isinstance(chat_id, str):
            return chat_id

        if "@lid" not in chat_id:
            return chat_id  # Já é @c.us ou grupo

        # Remove o @lid para montar a URL
        lid_id = chat_id.replace("@lid", "")
        
        url = f"{self.url}/api/{session}/lids/{lid_id}"
        
        try:
            res = requests.get(url, headers=self.headers, timeout=8)
            
            if res.status_code == 200:
                data = res.json()
                phone = data.get("pn") or data.get("phoneNumber")
                
                if phone:
                    if not str(phone).endswith("@c.us"):
                        phone = f"{phone}@c.us"
                    print(f"✅ LID resolvido: {chat_id} → {phone}")
                    return phone
            
            print(f"⚠️ Não foi possível resolver LID: {chat_id} → {res.text}")
            return chat_id
            
        except Exception as e:
            print(f"❌ Erro ao resolver LID {chat_id}: {e}")
            return chat_id