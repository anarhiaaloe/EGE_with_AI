from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

driver.get('https://hist-ege.sdamgia.ru/test?theme=168')
time.sleep(5)  # ждём, пока JS подгрузит задания

soup = BeautifulSoup(driver.page_source, 'lxml')
data = soup.find_all('span', class_='prob_nums')

exercises = []
for span in data:
    a_tag = span.find('a')
    if a_tag and a_tag.get('href'):
        exercises.append('https://hist-ege.sdamgia.ru' + a_tag.get('href'))

driver.quit()

print(f"Найдено {len(exercises)} заданий:")
for link in exercises:
    print(link)
