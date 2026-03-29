import aiohttp
import os


class APIClient:
    def __init__(self):
        self.base_url = os.getenv("API_URL", "http://localhost:8000/api")

    async def send_result(self, user_id: int, result: dict):
        print(f"Отправка результата для {user_id}: {result}")
        return {"status": "ok"}