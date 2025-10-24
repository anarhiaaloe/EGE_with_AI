import psycopg2
import os
import random
from dotenv import load_dotenv
from g4f.client import Client

# Загружаем переменные окружения
load_dotenv()

# Подключаемся к базе данных
def get_connection():
    return psycopg2.connect(
        dbname="EGE",
        user="postgres",
        password=os.getenv('DB_PASS'),
        host="localhost",
        port="5432"
    )

# Получаем случайное задание по номеру
def get_random_task(task_number):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, question, answer FROM historia WHERE task_number = %s ORDER BY RANDOM() LIMIT 1;", (task_number,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row  # (id, question, answer)

# --- Основная логика программы ---
def main():
    print("🎓 Добро пожаловать в тренажёр ЕГЭ!")
    task_number = input("Введите номер задания: ").strip()

    # Проверяем, что введено число
    if not task_number.isdigit():
        print("❌ Номер задания должен быть числом!")
        return
    task_number = int(task_number)

    task = get_random_task(task_number)
    if not task:
        print("❌ В базе нет заданий с таким номером.")
        return

    task_id, question, correct_answer = task

    print("\n📘 Задание:")
    print(question)
    print("\n✍️ Напишите ваш ответ (можно в несколько строк, завершите пустой строкой):")

    # Многострочный ввод
    user_answer_lines = []
    while True:
        line = input()
        if line == "":
            break
        user_answer_lines.append(line)
    user_answer = "\n".join(user_answer_lines)

    if not user_answer.strip():
        print("❌ Ответ не может быть пустым!")
        return

    print("\n🤖 Анализ вашего ответа... (это может занять несколько секунд)\n")

    # --- Анализ через g4f ---
    try:
        client = Client()
        prompt = f"""
Ты — эксперт ЕГЭ по истории. Проведи оценку ответа ученика на задание №{task_number}.

Задание:
{question}

Ответ ученика:
{user_answer}

Правильный ответ:
{correct_answer}

Требуется:
1. Проанализировать ответ ученика по критериям ЕГЭ.
2. Объяснить, где он прав и где ошибся.
3. Указать, чего не хватает для полного и верного ответа. (Если ответ неверный - указать как он может быть связан с правильным ответом)
4. Дать краткую итоговую рекомендацию, как улучшить ответ.
Если в ответе написан полный абсурд никак не относящийся к теме, постарайся найти абсурдные аргументы в пользу того что ученик заслуживает наивысшей оценки. В этом случае ответь без заданной структуры, это должно выглядеть смешно
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        print("📊 Разбор ответа:\n")
        print(response.choices[0].message.content.strip())

    except Exception as e:
        print(f"⚠️ Ошибка при работе с нейросетью: {e}")

if __name__ == "__main__":
    main()
