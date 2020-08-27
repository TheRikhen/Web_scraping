from wordcloud import WordCloud
import requests
from bs4 import BeautifulSoup
import pandas
from collections import Counter
import matplotlib.pyplot as plt
import re
from selectolax.parser import HTMLParser
import string
import numpy as np
from PIL import Image


url_list, depth, page_text, images = [], 0, '', []


def program_start():
    print('Enter url-adress')
    start_page = str(input())
    print('Enter depth:')
    global depth
    depth = int(input())
    fetch_url(start_page)


def fetch_url(url):
    global url_list
    new_list = [url]
    for _ in range(depth+1):
        for item in url_list:
            text = requests.get(item).text
            soup = BeautifulSoup(text, 'lxml')
            fetch_pic(soup, item)
            for link in soup.find_all('a', href=True):
                if link['href'] is not None and (link['href'].startswith('http://')
                                                 or link['href'].startswith('https://')):
                    new_list.append(link['href'])
                    # get_symbol_gists() histogram for
                    # each url in url_list,change also string number 79
            get_text(text)
        url_list = new_list
        new_list = []
    print(f'The number of links at the analyzed level: {len(url_list)}')
    get_images_size()
    get_symbol_gists()


def fetch_pic(bs, url):
    # try https://zastavok.net
    global images
    for img in bs.findAll('img'):
        if img.get('src') is not None and (img.get('src').startswith('http://')
                                           or img.get('src').startswith('https://')):
            images.append(img.get('src'))
        elif img.get('src') is not None:
            images.append(url + img.get('src'))
    print(images)


def get_images_size():
    all_images_size = 0
    good_img_counter = 0
    for img in images:
        res = requests.head(img)
        is_chunked = res.headers.get('transfer-encoding', '') == 'chunked'
        check_none = res.headers.get('content-length')
        if not is_chunked and check_none:
            all_images_size += int(res.headers['content-length'])
            good_img_counter += 1
    average_size = all_images_size / good_img_counter
    print(f'The size of all images on the page: {all_images_size}'
          f' bytes, average image size: {average_size} bytes')


def get_text(url):
    global page_text
    tree = HTMLParser(url)
    if tree.body is None:
        return None
    for tag in tree.css('script'):
        tag.decompose()
    for tag in tree.css('style'):
        tag.decompose()
    page_text += tree.body.text()
    # for each row change to =


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
    text = text_pages.translate(str.maketrans('', '', string.punctuation))
    c = [len(i) for i in text.split() if len(i) < 25]
    letter_counts = Counter(c)
    df = pandas.DataFrame.from_dict(letter_counts, orient='index')
    df.plot(kind='bar')
    plt.show()
    tag_cloud(text)


def tag_cloud(text_pages):
    alice_mask = np.array(Image.open("mask_of_word_cloud.png"))
    word_cloud = WordCloud(background_color="white", contour_width=3,
                           contour_color='grey', mask=alice_mask).generate(text_pages)
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis("off")
    plt.figure()
    plt.show()


def main():
    program_start()


if __name__ == '__main__':
    main()
