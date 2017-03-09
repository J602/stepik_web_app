from django.db import models
from django.contrib.auth.models import User


# QuestionManager - менеджер модели Question
from pygments.styles import default


class QuestionManager(models.Manager):

    def new(self):                          # new - метод возвращающий последние добавленные вопросы
        return self.all().order_by('added_at')

    def popular(self):                      # popular - метод возвращающий вопросы отсортированные по рейтингу
        return self.all().order_by('rating')


# Question - вопрос
class Question(models.Model):

    objects = QuestionManager()

    title = models.CharField(max_length=150)                # title - заголовок вопроса
    text = models.TextField()                               # text - полный текст вопроса
    added_at = models.DateTimeField(auto_now_add=True)      # added_at - дата добавления вопроса
    rating = models.IntegerField(default=0)                          # rating - рейтинг вопроса (число)
    author = models.ForeignKey(User, related_name='author')                        # author - автор вопроса
    likes = models.ManyToManyField(User, related_name='question_like_users', blank=True)       # likes - список пользователей, поставивших "лайк"


# Answer - ответ
class Answer(models.Model):

    text = models.TextField()                               # text - текст ответа
    added_at = models.DateTimeField(auto_now_add=True)      # added_at - дата добавления ответа
    question = models.ForeignKey(Question)                  # question - вопрос, к которому относится ответ
    author = models.ForeignKey(User)                        # author - автор ответа




