# encoding=utf-8
from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'ajax/test', views.test, name='ajax-test'),

    url(r'ajax/question/like/(?P<id>\d+)/$', views.ajax_question_like, name='ajax-question-like'),
    url(r'ajax/question/dislike/(?P<id>\d+)/$', views.ajax_question_dislike, name='ajax-question-dislike'),

    url(r'ajax/answer/like/(?P<id>\d+)/$', views.ajax_answer_like, name='ajax-answer-like'),
    url(r'ajax/answer/dislike/(?P<id>\d+)/$', views.ajax_answer_dislike, name='ajax-answer-dislike'),

    url(r'ajax/answer/correct/(?P<id>\d+)/$', views.ajax_answer_correct, name='ajax-answer-correct'),
    url(r'ajax/answer/add/(?P<id>\d+)/$', views.ajax_add_answer, name='ajax-add-answer'),
    url(r'ajax/answer/edit/$', views.ajax_edit_answer, name='ajax-edit-answer'),
    url(r'ajax/answer/remove/(?P<id>\d+)/$', views.ajax_remove_answer, name='ajax-remove-answer'),

    url(r'github/$', views.ajax_test, name='my-github'),
    ]
