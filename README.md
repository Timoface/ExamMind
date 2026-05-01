**ExamMind** — это интеллектуальная платформа для подготовки к техническим собеседованиям. Система использует мощь локальных языковых моделей (через Ollama) для генерации вопросов по теории, задач на кодинг и мгновенной оценки ответов пользователя.

Проект включает в себя:
* **Backend API**: Ядро системы на FastAPI, взаимодействующее с LLM.
* **Web Dashboard**: Ссайт на Streamlit с регистрацией и историей сессий.
* **Telegram Bot**: Удобный бот на Aiogram для тренировок "на ходу".

---

## Технологический стек

- **Язык**: Python 3.10+
- **AI Engine**: [Ollama](https://ollama.com/) (модель Llama 3)
- **Backend**: FastAPI, Uvicorn, HTTPX
- **Frontend**: Streamlit
- **Telegram**: Aiogram 3.x
- **Database**: SQLite (хранение пользователей)

---

## Установка и запуск проекта

### 1. 
Убедитесь, что у вас установлена модель Ollama (Llama 3)
```bash
ollama pull llama3
```
Клонируйте репозиторий и установите зависимости:
```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения
Создайте файл .env в корневом каталоге:
```
PROXY=ваш_прокси_для_запуска_телеграм_бота
API_URL=http://localhost:8000
BOT_TOKEN=ваш_токен_телеграм_бота
```

### 3. Запуск компонентов
Нужно запустить три разных терминала

#### Первый:
```bash
cd backend
python backend_api.py
```

#### Второй:
```bash
cd frontend
streamlit run site.py
```

#### Третий:
```bash
cd telegram_bot
python bot.py
```
