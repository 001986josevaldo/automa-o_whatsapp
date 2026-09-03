
import os
import requests


class Waha:

    def __init__(self):
        self.__api_url = 'http://waha:3000'
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": os.getenv("WAHA_API_KEY", "")
        }

    def send_message(self, chat_id, message, session='default'):
        url = f'{self.__api_url}/api/sendText'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'session': session,
            'chatId': chat_id,
            'text': message,
        }
        return requests.post(
            url=url,
            json=payload,
            headers=self.headers,
        )

    def start_typing(self, chat_id, session='default'):
        url = f'{self.__api_url}/api/startTyping'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'chatId': chat_id,
            'session': session,
        }
        return requests.post(
            url=url,
            json=payload,
            headers=self.headers,
        )

    def stop_typing(self, chat_id, session='default'):
        url = f'{self.__api_url}/api/stopTyping'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'session': session,
            'chatId': chat_id,
        }
        return requests.post(
            url=url,
            json=payload,
            headers=self.headers,
        )
