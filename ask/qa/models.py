# encoding=utf-8

from os import path
from os import remove, rmdir

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models import Count, Q
from django.db.models.signals import post_save, pre_save, pre_delete


class TagManager(models.Manager):

    def tags(self):
        return self.all().filter(question__published=True).annotate(count=Count('question'))


class Tag(models.Model):
    objects = TagManager()
    MAX_TAG_COUNT = 5
    name = models.CharField(max_length=15, unique=True, blank=False)

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):

    def user_or_published(self, user):
        if user.is_authenticated:
            return self.all().filter(Q(published=True) | Q(author=user))
        else:
            return self.all().filter(published=True)

    def new(self, user):
        return self.user_or_published(user).order_by('-added_at')

    def popular(self, user):
        return self.user_or_published(user).order_by('-rating')

    def by_tag(self, tag, user):
        return self.user_or_published(user).filter(tags=tag)

    def user_question(self, user):
        return self.all().filter(author=user)


class Question(models.Model):
    objects = QuestionManager()
    title = models.CharField(max_length=150)
    text = models.TextField()
    added_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='author', blank=True, null=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_question_likes', blank=True)
    tags = models.ManyToManyField(Tag)
    published = models.BooleanField(default=False)

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
    return path.join('avatars', str(instance.id), filename)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=15, blank=True)
    image = models.ImageField(upload_to=get_image_path, blank=True)
    score = models.IntegerField(default=0)

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def save_user_profile(sender, instance, **kwargs):
        instance.userprofile.save()

    def save(self, *args, **kwargs):
        if not self.name:
            index = self.user.username.find('@')
            if index != -1:
                self.name = self.user.username[:index]
            else:
                self.name = self.user.username
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


@receiver(pre_save, sender=UserProfile)
def auto_delete_image_on_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_image = UserProfile.objects.get(pk=instance.pk).image
        except UserProfile.DoesNotExist:
            return False
        if old_image:
            if old_image != instance.image:
                if path.isfile(old_image.path):
                    remove(old_image.path)


@receiver(pre_delete, sender=UserProfile)
def auto_delete_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        if path.isfile(instance.image.path):
            image_dir = path.dirname(instance.image.path)
            remove(instance.image.path)
            rmdir(image_dir)



