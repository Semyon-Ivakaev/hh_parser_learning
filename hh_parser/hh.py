import requests
from bs4 import BeautifulSoup
import csv
import os

URL = 'https://spb.hh.ru/search/vacancy?clusters=true&area=2&enable_snippets=true&salary=&st=searchVacancy&text=%D0%A2%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D1%89%D0%B8%D0%BA&from=suggest_post'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
           'accept': '*/*'}
FILE = 'vacancy.txt'

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup( html, 'html.parser' )
    pagination = soup.find_all('a', class_='bloko-button HH-Pager-Control')
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='vacancy-serp-item')

    vacancy = []

    for item in items:
        salary = item.find( 'span', class_='bloko-section-header-3 bloko-section-header-3_lite' )
        metro = item.find( 'span', class_='metro-station' )
        if salary:
            salary = salary.get_text()
        else:
            salary = 'Не указано'
        if metro:
            metro = metro.get_text()
        else:
            metro = 'Не указано'
        vacancy.append({
            'title': item.find('span', class_='resume-search-item__name').get_text(),
            'link': item.find( 'a', class_='bloko-link HH-LinkModifier' ).get('href'),
            'company': item.find( 'div', class_='vacancy-serp-item__meta-info' ).get_text(),
            'salary': salary,
            'metro': metro,
        })
    return vacancy


def save_file(items, path):
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';') # delimiter=';' для создания эксельки
        writer.writerow(['Вакансия', 'Ссылка', 'Компания', 'Зарплата', 'Станция метро'])
        for item in items:
            writer.writerow( [item['title'], item['link'], item['company'],
                              item['salary'], item['metro']] )


def parse():

    html = get_html(URL)
    if html.status_code == 200:
        vacancy = []
        pages_count = get_pages_count(html.text)
        for page in range(0, pages_count + 1):
            print(f"Собираем вакансии со страницы {page} из {pages_count}")
            html = get_html(URL, params={'page': page})
            vacancy.extend(get_content(html.text))
        save_file(vacancy, FILE)
        print(f"Найдено {len(vacancy)} вакансий.")
        os.startfile(FILE)
    else:
        print('Error')


parse()