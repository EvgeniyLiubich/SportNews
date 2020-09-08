from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login, logout
from django.db import transaction
from django.db.models import F
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.generic.edit import FormMixin

from news.forms import UserLoginForm, UserRegisterForm, NewsForm, ContactForm, CommentForm, UserForm, ProfileForm
from news.models import News, Category, Tag


class Home(ListView):
    """Домашняя страница"""
    model = News
    template_name = 'news/index.html'
    context_object_name = 'news'
    paginate_by = 4

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sports news'
        return context


class NewsByCategory(ListView):
    """Новости по категориям"""
    template_name = 'news/index.html'
    context_object_name = 'news'
    paginate_by = 4
    allow_empty = False

    def get_queryset(self):
        return News.objects.filter(category__slug=self.kwargs['slug'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = Category.objects.get(slug=self.kwargs['slug'])
        return context


class NewsByTag(ListView):
    """Новости по тегам"""
    template_name = 'news/index.html'
    context_object_name = 'news'
    paginate_by = 4
    allow_empty = False

    def get_queryset(self):
        return News.objects.filter(tags__slug=self.kwargs['slug'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Записи по тегу: ' + str(Tag.objects.get(slug=self.kwargs['slug']))
        return context


class GetNews(FormMixin, DetailView):
    """Просмотр одной новости"""
    model = News
    template_name = 'news/single.html'
    context_object_name = 'news'
    form_class = CommentForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object.views = F('views') + 1
        self.object.save()
        self.object.refresh_from_db()
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('news', kwargs={'slug': self.get_object().slug})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.news = self.get_object()
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)


class Search(ListView):
    """Реализация поиска"""
    template_name = 'news/search.html'
    context_object_name = 'news'
    paginate_by = 4

    def get_queryset(self):
        return News.objects.filter(title__icontains=self.request.GET.get('s'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['s'] = f"s={self.request.GET.get('s')}&"
        return context


# def register(request):
#     """Регистрация нового пользователя"""
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, 'Вы успешно зарегистрированы')
#             return redirect('home')
#         else:
#             messages.error(request, 'Ошибка регистрации')
#     else:
#         form = UserCreationForm()
#     return render(request, 'news/register.html', {'form': form})


# def user_login(request):
#     """Функция для авторизации"""
#     if request.method == 'POST':
#         form = AuthenticationForm(data=request.POST)
#         # form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             messages.success(request, 'Привет ' + user.username)
#             return redirect('home')
#     else:
#         # form = UserLoginForm()
#         form = AuthenticationForm()
#     return render(request, 'news/login.html', {'form': form})


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрированы')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = UserRegisterForm()
    return render(request, 'news/register.html', {'form': form})


def user_login(request):
    """Функция для авторизации"""
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Привет ' + user.username)
            return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'news/login.html', {'form': form})


def user_logout(request):
    """Выход, logout"""
    logout(request)
    return redirect('login')


class CreateNews(CreateView):
    """Добавление новости"""
    form_class = NewsForm
    template_name = 'news/add_news.html'


def send_email(request):
    """Отправка сообщений"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            mail = send_mail(form.cleaned_data['subject'], form.cleaned_data['content'],
                             'allenwalkertest2007@gmail.com',
                             ['lyubitch89@yandex.by'],
                             fail_silently=False)
            if mail:
                messages.success(request, 'Письмо отправлено')
                return redirect('home')
            else:
                messages.error(request, 'Ошибка отправки')
        else:
            messages.error(request, 'Ошибка валидации')
    else:
        form = ContactForm()
    return render(request, 'news/send_email.html', {'form': form})


@login_required
@transaction.atomic
def update_profile(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль отредактирован')
            return redirect('home')
        else:
            messages.error(request, 'Исправьте ошибку')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'news/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })