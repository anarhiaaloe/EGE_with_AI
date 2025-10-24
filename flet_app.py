import flet as ft
import psycopg2
import os
import random
from dotenv import load_dotenv
from g4f.client import Client

# --- Загружаем .env ---
load_dotenv()

# --- Подключение к БД ---
def get_connection():
    return psycopg2.connect(
        dbname="EGE",
        user="postgres",
        password=os.getenv('DB_PASS'),
        host="localhost",
        port="5432"
    )

def get_available_task_numbers(subject):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT DISTINCT task_number FROM {subject} ORDER BY task_number;")
    numbers = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return numbers

def get_random_task(subject, task_number):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT question, answer FROM {subject} WHERE task_number = %s ORDER BY RANDOM() LIMIT 1;", (task_number,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row if row else None


# --- Основная функция приложения ---
def main(page: ft.Page):
    page.title = "Тренажёр ЕГЭ"
    page.window_width = 600
    page.window_height = 700
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ADAPTIVE

    # Хранилище состояния
    state = {
        "subject": None,
        "task_number": None,
        "question": None,
        "correct_answer": None,
        "user_answer": None,
        "analysis": None
    }

    # ------------------------- ЭКРАНЫ -------------------------
    def show_main():
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text("Тренажёр ЕГЭ", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Практика ответов и анализ по критериям ЕГЭ.", size=16),
                    ft.ElevatedButton("Начать", on_click=lambda e: show_subjects(), width=200),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    def show_subjects():
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text("Выберите предмет", size=26, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("История", on_click=lambda e: select_subject("historia"), width=250),
                    ft.ElevatedButton("Назад", on_click=lambda e: show_main(), width=150),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    def select_subject(subject):
        state["subject"] = subject
        show_task_numbers()

    def show_task_numbers():
        page.clean()
        task_numbers = get_available_task_numbers(state["subject"])
        buttons = [
            ft.ElevatedButton(
                f"Задание №{num}",
                width=200,
                on_click=lambda e, n=num: select_task(n)
            )
            for num in task_numbers
        ]

        page.add(
            ft.Column(
                [
                    ft.Text("Выберите номер задания", size=24, weight=ft.FontWeight.BOLD),
                    ft.Column(buttons, scroll=ft.ScrollMode.AUTO),
                    ft.ElevatedButton("Назад", on_click=lambda e: show_subjects(), width=150),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    def select_task(task_number):
        state["task_number"] = task_number
        task = get_random_task(state["subject"], task_number)
        if not task:
            page.snack_bar = ft.SnackBar(ft.Text("❌ Нет заданий для этого номера"))
            page.snack_bar.open = True
            page.update()
            return
        state["question"], state["correct_answer"] = task
        show_question()

    def show_question():
        page.clean()
        answer_input = ft.TextField(
            label="Введите ваш ответ...",
            multiline=True,
            min_lines=5,
            max_lines=10,
            width=500
        )

        def on_send(e):
            user_text = answer_input.value.strip()
            if not user_text:
                page.snack_bar = ft.SnackBar(ft.Text("Введите ответ!"))
                page.snack_bar.open = True
                page.update()
                return
            state["user_answer"] = user_text
            show_analysis()

        page.add(
            ft.Column(
                [
                    ft.Text(f"Задание №{state['task_number']}", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(state["question"], size=16),
                    answer_input,
                    ft.Row(
                        [
                            ft.ElevatedButton("Отправить", on_click=on_send, width=150),
                            ft.ElevatedButton("Назад", on_click=lambda e: show_task_numbers(), width=150)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    def show_analysis():
        page.clean()
        progress = ft.ProgressRing()
        loading_text = ft.Text("🤖 Анализ вашего ответа...", size=18)
        page.add(ft.Column([progress, loading_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        page.update()

        # Анализ в фоне
        def analyze():
            try:
                client = Client()
                prompt = f"""
Ты — эксперт ЕГЭ по истории. Проведи оценку ответа ученика на задание №{state['task_number']}.

Задание:
{state['question']}

Ответ ученика:
{state['user_answer']}

Правильный ответ:
{state['correct_answer']}

Требуется:
1. Проанализировать ответ ученика по критериям ЕГЭ.
2. Объяснить, где он прав и где ошибся.
3. Указать, чего не хватает для полного ответа.
4. Дать краткую рекомендацию, как улучшить.
"""
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                )
                state["analysis"] = response.choices[0].message.content.strip()
            except Exception as e:
                state["analysis"] = f"⚠️ Ошибка анализа: {e}"

            page.clean()
            page.add(
                ft.Column(
                    [
                        ft.Text("📊 Разбор вашего ответа", size=22, weight=ft.FontWeight.BOLD),
                        ft.Text(state["analysis"], size=16, selectable=True),
                        ft.Row(
                            [
                                ft.ElevatedButton("Назад", on_click=lambda e: show_question(), width=150),
                                ft.ElevatedButton("На главную", on_click=lambda e: show_main(), width=150)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ],
                    scroll=ft.ScrollMode.ADAPTIVE,
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
            page.update()

        page.run_task(analyze)

    # Показать первый экран
    show_main()

# --- Запуск ---
if __name__ == "__main__":
    ft.app(target=main)
