# encoding=utf-8
from django import forms
from django.contrib.auth.forms import UsernameField
from django.contrib.auth.models import User
from .models import Question, Answer



class AskForm(forms.ModelForm):  # AskForm - форма  добавления   вопроса
    class Meta:
        model = Question
        fields = ['title', 'text', ]
        # title - поле   заголовка
        # text - поле   текста    вопроса


class AnswerForm(forms.ModelForm):  # AnswerForm - форма добавления ответа
    class Meta:
        model = Answer
        fields = ['text', 'question']
        # text - поле текста ответа
        # question - поле для связи с вопросом


class NewUserForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=False)

    def clean_username(self):
        try:
            User.objects.get_by_natural_key(self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']

        raise forms.ValidationError(('This user already exist.'), code='invalid')

    def save(self):
        new_user = User.objects.create_user(username=self.cleaned_data['username'],
                                            email=self.cleaned_data['email'],
                                            password=self.cleaned_data['password'])
        new_user.save()
        return new_user


class LoginUserForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
