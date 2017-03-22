# encoding=utf-8

from os import path
from django.db import models
from django.conf import settings



class Tag(models.Model):
    MAX_TAG_COUNT = 5

    name = models.CharField(max_length=15, unique=True, blank=False)

    def __str__(self):
        return self.name


# QuestionManager - менеджер модели Question
class QuestionManager(models.Manager):

    def new(self):                          # new - метод возвращающий последние добавленные вопросы
        return self.all().order_by('-added_at')

    def popular(self):                      # popular - метод возвращающий вопросы отсортированные по рейтингу
        return self.all().order_by('-rating')

    def by_tag(self, tag):
        return self.all().filter(tags=tag)

    def user_question(self, user):
        return self.all().filter(author=user)


# Question - вопрос
class Question(models.Model):
    objects = QuestionManager()
    title = models.CharField(max_length=150)                # title - заголовок вопроса
    text = models.TextField()                               # text - полный текст вопроса
    added_at = models.DateTimeField(auto_now_add=True)      # added_at - дата добавления вопроса
    rating = models.IntegerField(default=0)                          # rating - рейтинг вопроса (число)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='author', blank=True, null=True)             # author - автор вопроса
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_question_likes', blank=True)       # likes - список пользователей, поставивших "лайк"
    tags = models.ManyToManyField(Tag)

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
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_answer_likes', blank=True)
    rating = models.IntegerField(default=0)
    correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        ordering = ['-added_at']

    def __str__(self):
        return self.text




def get_image_path(instance, filename):
    return path.join(settings.STATIC_ROOT, 'avatars', str(instance.id), filename)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    name = models.CharField(max_length=75)
    image = models.ImageField(upload_to=get_image_path, blank=True)
    score = models.IntegerField(default=0)

