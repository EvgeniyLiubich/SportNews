from datetime import datetime
from os.path import basename
from random import randint, shuffle
import requests
from bs4 import BeautifulSoup as BS

from django.db import DatabaseError

import os, sys

from news.utils import from_cyrillic_to_eng
from sportnews.settings import BASE_DIR

proj = os.path.dirname(os.path.abspath('manage.py'))
# print(proj)
sys.path.append(proj)
os.environ['DJANGO_SETTINGS_MODULE'] = 'sportnews.settings'

import django

django.setup()

from news.models import News, Category, Tag

headers = [{'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:47.0) Gecko/20100101 Firefox/47.0',
            'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8'},
           {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/449.0.2623.112 Safari/537.36',
            'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8'},
           {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8'}
           ]

"""Для TUT.BY"""
start = datetime.now()
url_list = []
qs = Category.objects.all()
for item in qs:
    if item.pars_url_tut:
        url = Category.objects.get(pk=item.pk).pars_url_tut
        cat = Category.objects.get(pk=item.pk)
        url_list.append((url, cat))

data = []
for link in url_list:
    resp = requests.get(link[0], headers[randint(0, 2)])
    if resp.status_code == 200:
        soup = BS(resp.content, 'html.parser')
        items = soup.find_all('div',
                              class_='news-entry big annoticed time ni')

    for item in items:
        news = {}
        href = item.find('a')['href']
        news['category'] = link[1]
        resp = requests.get(href, headers[randint(0, 2)])
        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            item = soup.find('div', class_='col-w')
            if item:
                title = item.find('h1', itemprop="headline")
                # print(title)
                if title:
                    news['title'] = title.text
                    news['slug'] = from_cyrillic_to_eng(title.text)[:50]
                    div_cont = item.find('div', id="article_body")
                    content = ''
                    cont = div_cont.find_all('p')
                    for i in cont:
                        content += i.text
                    news['content'] = content
                    try:
                        photo = div_cont.find('img').get('src')
                        path = os.path.join(BASE_DIR, 'media') + '\\' + basename(photo)
                        with open(path, "wb") as f:
                            f.write(requests.get(photo).content)
                        news['photo'] = basename(photo)
                    except AttributeError:
                        pass
        data.append(news)

shuffle(data)

for news in data:
    if news.get('tags'):
        tag = news.pop('tags')
    news = News(**news)
    if News.objects.filter(title=news.title):
        print('News exist')
    else:
        try:
            news.save()
            print('News save', news.category)
        except DatabaseError:
            print('Error')

print(datetime.now() - start)
