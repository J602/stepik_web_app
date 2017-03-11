from django.forms import ModelForm
from .models import Question, Answer


class AskForm(ModelForm):          # AskForm - форма  добавления   вопроса
    class Meta:
        model = Question
        fields = ['title', 'text', ]
    # title - поле   заголовка
    # text - поле   текста    вопроса


class AnswerForm(ModelForm):       # AnswerForm - форма добавления ответа
    class Meta:
        model = Answer
        fields = ['text', 'question']
    # text - поле текста ответа
    # question - поле для связи с вопросом