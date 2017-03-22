# encoding=utf-8
from django.conf.urls import url
from . import views
from . import url_ajax

urlpatterns = [

    url(r'^$', views.question_list, name='question-list'),

    url(r'signup/$', views.singup, name='singup'),
    url(r'settings/$', views.user_settings, name='user-settings'),
    url(r'login/$', views.user_login, name='login'),
    url(r'logout/$', views.user_logout, name='logout'),

    url(r'question/(?P<id>\d+)/$', views.question_detail, name='question-detail'),
    url(r'ask/$', views.ask_question, name='ask-question'),
    url(r'popular/$', views.popular_list, name='popular-question-list'),
    url(r'new/$', views.question_list, name='new-question-list'),
    url(r'my_question/$', views.user_question, name='user-question-list'),
    url(r'tag/(?P<id>\d+)/$', views.question_by_tag, name='questions-by-tag'),

    url(r'github/$', views.test, name='my-github'),

    ] + url_ajax.urlpatterns
