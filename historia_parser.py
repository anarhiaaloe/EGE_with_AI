from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from db import create_subject_table, insert_task
import time
import random

# Настройки предмета
subject = "historia"

# Сопоставляем theme_id и номер задания 
themes = {
    137: 1,
    143: 2,
    24: 3,
    149: 4,
    102: 5,
    40: 6,
    110: 6,
    111: 6,
    141: 7,
    34: 13,
    124: 13,
    125: 13,
    35: 14,
    126: 14,
    127: 14






    # 155: 21,
    # 167: 21,
    # 168: 21,
    # 162: 20,
    # 154: 19,
    # 165: 19,
    # 166: 19,
    # 153: 18,
    # 163: 18,
    # 164: 18,
    # 156: 17
}

# Создаём таблицу, если нет
create_subject_table(subject)

# Настройка браузера
options = Options()
options.headless = False
driver = webdriver.Chrome(options=options)

# Проходим по всем темам
for theme_id, task_number in themes.items():
    print(f"\n=== Тема {theme_id} (задание №{task_number}) ===")
    url = f"https://hist-ege.sdamgia.ru/test?theme={theme_id}"
    driver.get(url)

    # Прокрутка страницы до конца
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1.5, 3.5))  # рандомная пауза
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Парсим страницу и собираем ссылки на задания
    soup = BeautifulSoup(driver.page_source, "lxml")
    exercises = []
    for span in soup.find_all("span", class_="prob_nums"):
        a_tag = span.find("a")
        if a_tag and a_tag.get("href"):
            exercises.append("https://hist-ege.sdamgia.ru" + a_tag["href"])

    print(f"Найдено {len(exercises)} заданий по теме {theme_id}")

    # Обрабатываем каждое задание
    for link in exercises:
        driver.get(link)
        time.sleep(random.uniform(1.0, 2.5))  # рандомная пауза после загрузки

        soup = BeautifulSoup(driver.page_source, "lxml")

        # Вопрос
        question_div = soup.find("div", class_="pbody")
        question_blocks = question_div.find_all("p", class_="left_margin") if question_div else []
        question = "\n".join([p.get_text(strip=True) for p in question_blocks]) if question_blocks else "Не найдено"

        # Ответ
        answer_div = soup.find("div", class_="solution")
        answer_blocks = answer_div.find_all("p", class_="left_margin") if answer_div else []
        answer = "\n".join([p.get_text(strip=True) for p in answer_blocks]) if answer_blocks else "Не найдено"

        # Вставка в базу
        insert_task(subject, task_number, link, question, answer)

        time.sleep(random.uniform(0.8, 1.5))  # пауза между заданиями

driver.quit()
print("\n✅ Парсинг завершён.")
