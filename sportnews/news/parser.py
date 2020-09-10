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
"""Парсер забирает со странички заголовок статьи, картинку, теги, связанные с этой статьей и затем сохраняет в модель новости эти теги, и сам контент"""
"""Для SPORTS.RU"""

start = datetime.now()

url_list = []
qs = Category.objects.all()
for item in qs:
    if item.pars_url_sports:
        url = Category.objects.get(pk=item.pk).pars_url_sports
        cat = Category.objects.get(pk=item.pk)
        url_list.append((url, cat))

data = []
for link in url_list:
    resp = requests.get(link[0], headers[randint(0, 2)])
    if resp.status_code == 200:
        soup = BS(resp.content, 'html.parser')
        items = soup.find_all('article',
                              class_='js-active js-material-list__blogpost material-list__item clearfix piwikTrackContent piwikContentIgnoreInteraction')

    for item in items:
        news = {}
        href = item.find('a')['href']
        photo = item.find('img', class_='material-list__item-img lazyload').get('data-src')
        path = os.path.join(BASE_DIR, 'media') + '\\' + basename(photo)
        with open(path, "wb") as f:
            f.write(requests.get(photo).content)
        news['photo'] = basename(photo)
        news['category'] = link[1]
        resp = requests.get(href, headers[randint(0, 2)])
        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            item = soup.find('div', class_='blog-post')
            if item:
                title = item.find('h1', itemprop="headline").text
                news['title'] = title
                news['slug'] = from_cyrillic_to_eng(title)[:50]
                content = ''
                cont = item.find_all('p')
                for i in cont:
                    if i.text.startswith('Вы подписаны'):
                        pass
                    elif i.text.endswith('Подписаться'):
                        pass
                    else:
                        content += i.text
                news['content'] = content
                taggs = soup.find('div', class_='material-item__tags-line')
                if taggs:
                    news['tags'] = []
                    tag_list = taggs.find_all('a')
                    for item in tag_list:
                        tag = {}
                        tag['title'] = item.text
                        tag['slug'] = from_cyrillic_to_eng(tag['title'])
                        tag_item = Tag(**tag)
                        if Tag.objects.filter(slug=tag_item.slug):
                            pass
                            # print('Tag exist')
                        else:
                            tag_item.save()
                            # print('Tag save')
                        teg_1 = Tag.objects.get(slug=tag_item.slug)
                        news['tags'].append(teg_1.id)

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
    try:
        news2 = News.objects.get(title=news.title)
        for item in tag:
            obj = Tag.objects.get(id=item)
            news2.tags.add(obj)
            news2.save()
            # print('Tag Ok')
    except:
        pass
print(datetime.now() - start)
