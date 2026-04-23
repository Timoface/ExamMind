import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

app = FastAPI(title="ExamMind AI Core")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"


class EvaluationRequest(BaseModel):
    context_type: str
    question: str
    answer: str
    direction: str
    level: str


class QuestionRequest(BaseModel):
    direction: str
    level: str
    type: str


async def call_ollama(prompt: str):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OLLAMA_URL, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Ollama Error")
        return response.json().get("response")


@app.post("/generate-question")
async def generate_question(req: QuestionRequest):
    prompt = f"""
    Ты - опытный IT-интервьюер. Сгенерируй один сложный вопрос для собеседования.
    Направление: {req.direction}
    Уровень: {req.level}
    Тип вопроса: {req.type}
    Верни ответ строго в формате JSON: {{"question": "текст вопроса"}}
    Генерируй ответ на русском языке
    """
    result = await call_ollama(prompt)
    return json.loads(result)


@app.post("/evaluate")
async def evaluate(req: EvaluationRequest):
    prompt = f"""
    Ты - технический интервьюер. Оцени ответ кандидата.
    Направление: {req.direction}, Уровень: {req.level}
    Тип проверки: {req.context_type}
    Вопрос: {req.question}
    Ответ кандидата: {req.answer}

    Верни ответ строго в формате JSON:
    {{
        "score": (число от 1 до 10),
        "feedback": "подробный разбор на русском языке",
        "correct_answer": "как стоило ответить идеально"
    }}
    Генерируй ответ на русском языке
    """
    result = await call_ollama(prompt)
    return json.loads(result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
