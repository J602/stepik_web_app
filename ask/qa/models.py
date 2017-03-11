# encoding=utf-8

from django.db import models
from django.conf import settings


# QuestionManager - менеджер модели Question
class QuestionManager(models.Manager):

    def new(self):                          # new - метод возвращающий последние добавленные вопросы
        return self.all().order_by('-added_at')

    def popular(self):                      # popular - метод возвращающий вопросы отсортированные по рейтингу
        return self.all().order_by('-rating')


# Question - вопрос
class Question(models.Model):
    objects = QuestionManager()
    title = models.CharField(max_length=150)                # title - заголовок вопроса
    text = models.TextField()                               # text - полный текст вопроса
    added_at = models.DateTimeField(auto_now_add=True)      # added_at - дата добавления вопроса
    rating = models.IntegerField(default=0)                          # rating - рейтинг вопроса (число)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='author')                        # author - автор вопроса
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='question_like_users', blank=True)       # likes - список пользователей, поставивших "лайк"

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['-added_at']

    def __str__(self):
        return self.title


# Answer - ответ
class Answer(models.Model):

    text = models.TextField()                               # text - текст ответа
    added_at = models.DateTimeField(auto_now_add=True)      # added_at - дата добавления ответа
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)  # question - вопрос, к которому относится ответ
    author = models.ForeignKey(settings.AUTH_USER_MODEL)                        # author - автор ответа

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        ordering = ['-added_at']

    def __str__(self):
        return self.text
