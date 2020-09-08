from django.contrib import admin
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.safestring import mark_safe

from .models import *


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'news', 'text', 'status')


class NewsAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = News
        fields = '__all__'


class NewsAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    form = NewsAdminForm
    save_on_top = True
    list_display = ('id', 'title', 'category', 'get_photo', 'created_at', 'is_published', 'views')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'content')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'category', 'tags')
    readonly_fields = ('views', 'created_at', 'get_photo')
    fields = (
        'title', 'slug', 'category', 'tags', 'content', 'photo', 'get_photo', 'views', 'created_at', 'is_published')

    def get_photo(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width=100>')
        return '-'

    get_photo.short_description = 'Фото'


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    search_fields = ('title',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug')
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Comment, CommentAdmin)
