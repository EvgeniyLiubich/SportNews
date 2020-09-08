from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    """Модель категорий"""
    title = models.CharField(max_length=150, db_index=True, verbose_name='Наименование категории')
    slug = models.SlugField(max_length=150, verbose_name='Url', unique=True)

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug, })

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория(ю)'
        verbose_name_plural = 'Категории'
        ordering = ['-title']


class Tag(models.Model):
    """Модель тегов"""
    title = models.CharField(max_length=50, db_index=True, verbose_name='Тег')
    slug = models.SlugField(max_length=50, verbose_name='Url', unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tag', kwargs={'slug': self.slug, })

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['-title']


class News(models.Model):
    """Модель новостей"""
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, verbose_name='Url', unique=True, blank=True)
    content = models.TextField(blank=True, verbose_name='Контент')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Опубликовано')
    # updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', verbose_name='Фото', blank=True)
    views = models.IntegerField(default=0, verbose_name='Кол-во просмотров')
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name='Категория', related_name='news',
                                 blank=True)
    tags = models.ManyToManyField('Tag', blank=True, verbose_name='Теги', related_name='news', null=True)
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    def get_absolute_url(self):
        return reverse('news', kwargs={'slug': self.slug, })

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']


class Comment(models.Model):
    """Модель комментариев"""
    news = models.ForeignKey(News, on_delete=models.CASCADE, verbose_name='Статья', blank=True, null=True,
                             related_name='comments_news')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    text = models.TextField(verbose_name='Текст комментария')
    status = models.BooleanField(verbose_name='Видимость', default=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']


class Profile(models.Model):
    """Модель данных User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')
    location = models.CharField(max_length=30, blank=True, verbose_name='Местоположение')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
