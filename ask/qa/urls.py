# encoding=utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.question_list, name='question-list'),
    url(r'signup/$', views.singup, name='singup'),
    url(r'login/$', views.user_login, name='login'),
    url(r'logout/$', views.user_logout, name='logout'),

    url(r'question/(?P<id>\d+)/$', views.question_detail, name='question-detail'),
    url(r'ask/$', views.ask_question, name='ask-question'),
    url(r'popular/$', views.popular_list, name='popular-list'),
    url(r'new/$', views.test, name='test'),
]
