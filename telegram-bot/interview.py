class InterviewManager:
    def __init__(self):
        self.sessions = {}  # user_id -> session_data

    def start_interview(self, user_id: int, direction: str, level: str):
        self.sessions[user_id] = {
            "direction": direction,
            "level": level,
            "theory_answers": [],
            "coding_answers": [],
            "soft_answers": [],
            "current_question_index": 0,
            "questions": self._get_questions(direction, level)
        }

    def _get_questions(self, direction: str, level: str) -> dict:
        questions = {
            "theory": [
                "Что такое ООП? Назови основные принципы.",
                "Чем отличается процесс от потока?",
                "Что такое замыкание в программировании?"
            ],
            "coding": [
                "Напиши функцию, которая проверяет, является ли строка палиндромом.",
                "Напиши функцию для поиска дубликатов в массиве.",
                "Реализуй алгоритм бинарного поиска."
            ],
            "soft": [
                "Расскажи о сложном баге, который ты исправлял.",
                "Как ты действуешь при конфликте в команде?",
                "Почему ты хочешь работать в IT?"
            ]
        }
        return questions

    def get_next_theory_question(self, user_id: int) -> str:
        session = self.sessions.get(user_id)
        if session:
            idx = len(session["theory_answers"])
            questions = session["questions"]["theory"]
            if idx < len(questions):
                return questions[idx]
        return "Вопросы по теории закончились."

    def evaluate_theory_answer(self, user_id: int, answer: str) -> tuple:
        score = 7  # случайная оценка
        feedback = "Хороший ответ, но можно добавить примеров."
        session = self.sessions.get(user_id)
        if session:
            session["theory_answers"].append({"answer": answer, "score": score, "feedback": feedback})
        return score, feedback

    def get_next_coding_question(self, user_id: int) -> str:
        session = self.sessions.get(user_id)
        if session:
            idx = len(session["coding_answers"])
            questions = session["questions"]["coding"]
            if idx < len(questions):
                return questions[idx]
        return None

    def evaluate_code(self, user_id: int, code: str) -> tuple:
        score = 6
        feedback = "Код работает, но можно улучшить читаемость и добавить обработку краевых случаев."
        session = self.sessions.get(user_id)
        if session:
            session["coding_answers"].append({"code": code, "score": score, "feedback": feedback})
        return score, feedback

    def get_next_soft_question(self, user_id: int) -> str:
        session = self.sessions.get(user_id)
        if session:
            idx = len(session["soft_answers"])
            questions = session["questions"]["soft"]
            if idx < len(questions):
                return questions[idx]
        return None

    def evaluate_soft_answer(self, user_id: int, answer: str) -> tuple:
        score = 8
        feedback = "Отличный ответ, хорошая структура по STAR."
        session = self.sessions.get(user_id)
        if session:
            session["soft_answers"].append({"answer": answer, "score": score, "feedback": feedback})
        return score, feedback

    def get_final_report(self, user_id: int) -> str:
        session = self.sessions.get(user_id)
        if not session:
            return "Ошибка: сессия не найдена."

        theory_scores = [a["score"] for a in session["theory_answers"]]
        coding_scores = [a["score"] for a in session["coding_answers"]]
        soft_scores = [a["score"] for a in session["soft_answers"]]

        avg_theory = sum(theory_scores) / len(theory_scores) if theory_scores else 0
        avg_coding = sum(coding_scores) / len(coding_scores) if coding_scores else 0
        avg_soft = sum(soft_scores) / len(soft_scores) if soft_scores else 0
        total = (avg_theory + avg_coding + avg_soft) / 3

        report = f"""
📊 Результаты собеседования
━━━━━━━━━━━━━━━━━━
🎯 Направление: {session['direction']}
📌 Уровень: {session['level']}

📖 Теория: {avg_theory:.1f}/10
💻 Алгоритмы: {avg_coding:.1f}/10
🗣 Soft skills: {avg_soft:.1f}/10

🏆 ИТОГОВЫЙ БАЛЛ: {total:.1f}/10

Рекомендации:
• Повтори тему многопоточности
• Добавляй комментарии к сложным участкам кода
• Продолжай развивать навыки коммуникации
"""
        return report