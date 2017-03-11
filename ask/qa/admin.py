# encoding=utf-8
from django.contrib import admin
from .models import Question, Answer


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author']
    list_display_links = ['title']
    search_fields = ['title', 'text']
    list_per_page = 10

admin.site.register(Question, QuestionAdmin)


class AnswerAdmin(admin.ModelAdmin):
    ordering = ['question']
    list_display = ['question', 'author']
    list_display_links = ['question']
    search_fields = ['question', 'text']

    list_per_page = 25

admin.site.register(Answer, AnswerAdmin)
