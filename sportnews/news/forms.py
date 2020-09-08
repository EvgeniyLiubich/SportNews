import re
from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from news.models import News, Comment


class UserRegisterForm(UserCreationForm):
    """Форма регистрации"""
    username = forms.CharField(label='Имя пользоватьеля', help_text='Максимум 150 символов',
                               widget=forms.TextInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(label='Подтверждение пароля',
                                widget=forms.PasswordInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label='Адрес электронной почты', widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        # widgets = {
        #     'username': forms.TextInput(attrs={"class": "form-control"}),
        #     'email': forms.EmailInput(attrs={"class": "form-control"}),
        #     'password1': forms.PasswordInput(attrs={"class": "form-control"}),
        #     'password2': forms.PasswordInput(attrs={"class": "form-control"}),
        # }


class UserLoginForm(AuthenticationForm):
    """Форма входа в систему"""
    username = forms.CharField(label='Имя пользоватьеля',
                               widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={"class": "form-control"}))


class NewsForm(forms.ModelForm):
    """Форма создания новости"""

    class Meta:
        model = News
        fields = ['title', 'slug', 'content', 'photo', 'category']
        widgets = {
            'title': forms.TextInput(attrs={"class": "form-control"}),
            'content': forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            'category': forms.Select(attrs={"class": "form-control"}),
        }

        """Напишем собственный валидатор для title"""

    def clean_title(self):
        """Получим очищеный title"""
        title = self.cleaned_data['title']
        if re.match(r'\d', title):
            raise ValidationError('Название не должно начинаться с цифры')
        return title


class ContactForm(forms.Form):
    """Форма обратной связи"""
    subject = forms.CharField(label='Тема',
                              widget=forms.TextInput(attrs={"class": "form-control"}))
    content = forms.CharField(label='Текст', widget=forms.Textarea(attrs={"class": "form-control",
                                                                          'rows': 5}))
    captcha = CaptchaField()


class CommentForm(forms.ModelForm):
    """Форма комментариев"""

    class Meta:
        model = Comment
        fields = ['text', ]
        widgets = {
            'text': forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }
