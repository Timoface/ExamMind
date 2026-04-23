import aiohttp
import os
import logging
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

class APIClient:
    def __init__(self):
        self.base_url = API_URL

    async def generate_question(self, direction: str, level: str, q_type: str):
        url = f"{self.base_url}/generate-question"
        payload = {
            "direction": direction,
            "level": level,
            "type": q_type
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("question", "Ошибка генерации вопроса")
                    return "Ошибка сервера API"
        except Exception as e:
            logging.error(f"API Error: {e}")
            return "Не удалось связаться с ИИ-мозгом."

    async def evaluate_answer(self, context_type: str, question: str, answer: str, direction: str, level: str):
        url = f"{self.base_url}/evaluate"
        payload = {
            "context_type": context_type,
            "question": question,
            "answer": answer,
            "direction": direction,
            "level": level
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return {"score": 0, "feedback": "Ошибка API", "correct_answer": "-"}
        except Exception as e:
            logging.error(f"Evaluation Error: {e}")
            return {"score": 0, "feedback": "Сервис оценки недоступен", "correct_answer": "-"}