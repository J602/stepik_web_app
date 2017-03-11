# encoding=utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.question_list, name='question-list'),
    url(r'login/$', views.test, name='test'),
    url(r'signup/$', views.test, name='test'),
    url(r'question/(?P<id>\d+)/$', views.question_detail, name='question-detail'),
    url(r'ask/$', views.test, name='test'),
    url(r'popular/$', views.popular_list, name='popular-list'),
    url(r'new/$', views.test, name='test'),
]
