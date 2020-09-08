from django.urls import path
from .views import *

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('category/<str:slug>/', NewsByCategory.as_view(), name='category'),
    path('tag/<str:slug>/', NewsByTag.as_view(), name='tag'),
    path('news/<str:slug>/', GetNews.as_view(), name='news'),
    path('search/', Search.as_view(), name='search'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('add_news/', CreateNews.as_view(), name='add_news'),
    path('send_email/', send_email, name='send_email'),
]