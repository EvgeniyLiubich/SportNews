from random import shuffle

from django import template
from news.models import News, Tag

register = template.Library()


@register.inclusion_tag('news/popular_news_tpl.html')
def get_popular(cnt=3):
    news = News.objects.order_by('-views')[:cnt]
    return {'news': news}


@register.inclusion_tag('news/tags_tpl.html')
def get_tags():
    tags = Tag.objects.all()

    return {'tags': tags[:30]}
