import requests
from bs4 import BeautifulSoup
import pandas
from collections import Counter
import matplotlib.pyplot as plt
import re
from selectolax.parser import HTMLParser
import string

# uri = 'https://vk.com'
url_list = []
depth = 0  # 1/2
page_text = ''


def program_start():
    print('Введите url-адресс')
    start_page = str(input())
    print('Введите глубину исследования ссылки:')
    global depth
    depth = int(input())
    fetch_url(start_page)


def fetch_url(url):
    global url_list
    new_list = [url]
    for i in range(depth+1):
        for item in url_list:
            text = requests.get(item).text
            soup = BeautifulSoup(text, 'lxml')
            for link in soup.find_all('a', href=True):
                if link['href'] is not None and (link['href'].startswith('http://') or link['href'].startswith('https://')):
                    new_list.append(link['href'])
                    # get_symbol_gists() histogram for each url in url_list
            get_text(text)
        url_list = new_list
        new_list = []
    print('Количество ссылок на анализируемом уровне:', len(url_list))
    get_symbol_gists()


def get_text(url):
    global page_text
    tree = HTMLParser(url)
    if tree.body is None:
        return None
    for tag in tree.css('script'):
        tag.decompose()
    for tag in tree.css('style'):
        tag.decompose()
    page_text = page_text + tree.body.text()


def get_symbol_gists():
    global page_text
    rus = re.findall('[а-яё]', page_text)
    eng = re.findall('[a-z]', page_text)
    spec = re.findall("[@_!#$%^&*()<>?/|}{~:]", page_text)
    symbol_gist(rus)
    symbol_gist(eng)
    symbol_gist(spec)
    words_symbol_counter_gist(page_text)


def symbol_gist(symbol_type):
    letter_counts = Counter(symbol_type)
    df = pandas.DataFrame.from_dict(letter_counts, orient='index')
    df.plot(kind='bar')
    plt.show()


def words_symbol_counter_gist(text_pages):
    c = []
    text = text_pages.translate(str.maketrans('', '', string.punctuation)).split()
    c = [len(i) for i in text if len(i) < 25]
    letter_counts = Counter(c)
    df = pandas.DataFrame.from_dict(letter_counts, orient='index')
    df.plot(kind='bar')
    plt.show()


def main():
    program_start()


if __name__ == '__main__':
    main()
