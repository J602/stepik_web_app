# encoding=utf-8
from django.conf.urls import url, include
from . import views


urlpatterns = [

    url(r'ajax/test', views.test, name='ajax-test'),

    url(r'ajax/question/like/(?P<id>\d+)/$', views.ajax_question_like, name='ajax-question-like'),
    url(r'ajax/question/dislike/(?P<id>\d+)/$', views.ajax_question_dislike, name='ajax-question-dislike'),

    url(r'ajax/answer/like/(?P<id>\d+)/$', views.ajax_answer_like, name='ajax-answer-like'),
    url(r'ajax/answer/dislike/(?P<id>\d+)/$', views.ajax_answer_dislike, name='ajax-answer-dislike'),

    ]
