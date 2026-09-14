import json
import os

DB_FILE = "human_chats.json"

# Executado uma única vez quando a aplicação sobe no container
def _reset_on_startup():
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print("🔄 [STARTUP] Todos os atendimentos foram resetados para a IA.")
        except Exception as e:
            print(f"⚠️ Erro ao resetar arquivo no startup: {e}")

_reset_on_startup()

def _load_chats():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r") as f:
        try:
            return set(json.load(f))
        except Exception:
            return set()

def _save_chats(chats):
    with open(DB_FILE, "w") as f:
        json.dump(list(chats), f)

def is_human_active(chat_id):
    return chat_id in _load_chats()

def set_human_active(chat_id):
    chats = _load_chats()
    chats.add(chat_id)
    _save_chats(chats)

def set_bot_active(chat_id):
    chats = _load_chats()
    chats.discard(chat_id)
    _save_chats(chats)