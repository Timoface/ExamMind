import streamlit as st
import httpx
import asyncio
import sqlite3
import base64
import os
from passlib.hash import pbkdf2_sha256
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

API_URL = os.getenv("API_URL")

parent_path = Path.cwd().parent
data_path = parent_path / 'data'

st.set_page_config(
    page_title="ExamMind: Pro",
    page_icon=data_path / 'logo.ico',
    layout="wide"
)

def add_custom_style():
    st.markdown("""
        <style>
        /* Градиент на весь фон */
        .stApp {
            background: linear-gradient(135deg, #2c3e50 0%, #b13991 100%);
        }

        /* Стили для верхней плашки */
        .custom-header {
            display: flex;
            align-items: center;
            padding: 10px 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }

        .header-logo {
            width: 50px;
            margin-right: 15px;
        }

        .header-title {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin: 0;
        }
        </style>
    """, unsafe_allow_html=True)


add_custom_style()

try:
    with open(data_path / 'logo.ico', "rb") as f:
        image_data = f.read()
        base64_logo = base64.b64encode(image_data).decode()

    st.markdown(f"""
        <div class="custom-header">
            <img src="data:image/x-icon;base64,{base64_logo}" class="header-logo">
            <p class="header-title">ExamMind: Pro — Твой ИИ-наставник</p>
        </div>
    """, unsafe_allow_html=True)
except FileNotFoundError:
    st.markdown('<div class="custom-header"><p class="header-title">ExamMind: Pro</p></div>', unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect(data_path / 'users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()


def create_user(username, password):
    conn = sqlite3.connect(data_path / 'users.db')
    c = conn.cursor()
    hashed = pbkdf2_sha256.hash(password)
    try:
        c.execute("INSERT INTO users VALUES (?,?)", (username, hashed))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def verify_user(username, password):
    conn = sqlite3.connect(data_path / 'users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return pbkdf2_sha256.verify(password, result[0])
    return False


init_db()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

async def fetch_ai(endpoint, payload):
    timeout = httpx.Timeout(120.0, connect=60.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(f"{API_URL}/{endpoint}", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.ReadTimeout:
            return {
                "score": 0,
                "feedback": "ИИ не успел ответить вовремя (Timeout). Попробуйте еще раз.",
                "question": "Ошибка таймаута"
            }
        except Exception as e:
            return {
                "score": 0,
                "feedback": f"Произошла ошибка: {str(e)}",
                "question": "Ошибка связи"
            }


page = st.sidebar.selectbox("Навигация", ["Главная", "Интервью", "Контакты"])

if not st.session_state.authenticated:
    st.title("🔐 Вход в систему")
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])

    with tab1:
        u = st.text_input("Логин", key="login_u")
        p = st.text_input("Пароль", type="password", key="login_p")
        if st.button("Войти"):
            if verify_user(u, p):
                st.session_state.authenticated = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Неверный логин или пароль")

    with tab2:
        new_u = st.text_input("Придумайте логин")
        new_p = st.text_input("Придумайте пароль", type="password")
        if st.button("Зарегистрироваться"):
            if create_user(new_u, new_p):
                st.success("Аккаунт создан! Теперь войдите.")
            else:
                st.error("Пользователь уже существует")

else:
    if page == "Контакты":
        st.title("📬 Контакты создателя")
        st.markdown("""
        ### О разработчике
        Привет! Я создатель **ExamMind: Pro**. Моя цель — сделать подготовку к интервью доступной и эффективной с помощью ИИ.

        - **Telegram:** [@Djmix22]
        - **GitHub:** [github.com/Timoface]
        
        """)

    elif page == "Главная":
        st.title(f"👋 С возвращением, {st.session_state.username}!")
        st.write("Выберите раздел 'Интервью' в меню слева, чтобы начать тренировку.")
        if st.button("Выйти"):
            st.session_state.authenticated = False
            st.rerun()

    elif page == "Интервью":
        st.title("🚀 ИИ-Интервью")

        with st.sidebar:
            direction = st.selectbox("Направление", ["Python", "Java", "Frontend", "Go"])
            level = st.select_slider("Уровень", ["Junior", "Middle", "Senior"])
            if st.button("🔄 Сбросить сессию"):
                st.session_state.step = "start"
                st.rerun()

        if "step" not in st.session_state: st.session_state.step = "start"

        if st.session_state.step == "start":
            if st.button("Начать проверку знаний"):
                st.session_state.step = "loading_theory"
                st.rerun()

        if st.session_state.step == "loading_theory":
            with st.spinner("Генерирую вопрос по теории..."):
                res = asyncio.run(
                    fetch_ai("generate-question", {"direction": direction, "level": level, "type": "theory"}))
                st.session_state.theory_q = res.get("question")
                st.session_state.step = "theory_ask"
                st.rerun()

        if st.session_state.step == "theory_ask":
            st.subheader("📝 Вопрос 1: Теория")
            st.info(st.session_state.theory_q)
            ans = st.text_area("Ваш ответ:", key="ans_theory")
            if st.button("Проверить"):
                with st.spinner("Оцениваю..."):
                    eval_res = asyncio.run(fetch_ai("evaluate", {
                        "context_type": "theory", "question": st.session_state.theory_q,
                        "answer": ans, "direction": direction, "level": level
                    }))
                    st.session_state.theory_eval = eval_res
                    st.session_state.step = "theory_result"
                    st.rerun()

        if st.session_state.step == "theory_result":
            res = st.session_state.theory_eval
            st.success(f"Оценка: {res.get('score')}/10")
            st.write(f"**Фидбек:** {res.get('feedback')}")
            if st.button("Далее к Кодингу 💻"):
                st.session_state.step = "loading_coding"
                st.rerun()

        if st.session_state.step == "loading_coding":
            with st.spinner("Генерирую задачу на кодинг..."):
                res = asyncio.run(
                    fetch_ai("generate-question", {"direction": direction, "level": level, "type": "coding"}))
                st.session_state.coding_q = res.get("question")
                st.session_state.step = "coding_ask"
                st.rerun()

        if st.session_state.step == "coding_ask":
            st.subheader("💻 Вопрос 2: Кодинг")
            st.code(st.session_state.coding_q)
            ans_code = st.text_area("Напишите ваш код здесь:", height=300)
            if st.button("Отправить код"):
                with st.spinner("Тестирую алгоритм..."):
                    eval_res = asyncio.run(fetch_ai("evaluate", {
                        "context_type": "coding", "question": st.session_state.coding_q,
                        "answer": ans_code, "direction": direction, "level": level
                    }))
                    st.session_state.coding_eval = eval_res
                    st.session_state.step = "final"
                    st.rerun()

        if st.session_state.step == "final":
            st.balloons()
            st.title("🏁 Интервью завершено!")
            st.subheader("Результаты кодинга:")
            st.success(f"Оценка: {st.session_state.coding_eval.get('score')}/10")
            st.write(st.session_state.coding_eval.get('feedback'))
            if st.button("В начало"):
                st.session_state.step = "start"
                st.rerun()