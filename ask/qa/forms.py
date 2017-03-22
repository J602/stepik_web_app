# encoding=utf-8
from django import forms
from django.forms import widgets
from django.contrib.auth.models import User
from .models import Question, Answer, Tag


class AskForm(forms.Form):  # AskForm - форма  добавления   вопроса
    title = forms.CharField(widget=widgets.Input(attrs={'class': 'form-control'}), label='Title:')
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'row': 11}, ), label='Text:')
    tags = forms.CharField(max_length=150, strip=True, required=False,
                           widget=widgets.Input(attrs={'class': 'form-control', }), label='Tags:')

    def clean_tags(self):
        raw_tags = self.cleaned_data['tags'].split()

        if len(raw_tags) == 1:
            raw_tags = raw_tags[0].split(',')

        raw_tags = [tag for tag in raw_tags if tag.isalnum() or ',' in tag]
        raw_tags = list(map(lambda x: x.replace(',', ''), raw_tags))
        if len(raw_tags) > Tag.MAX_TAG_COUNT:
            raw_tags = raw_tags[:Tag.MAX_TAG_COUNT]

        self.cleaned_data['tags'] = raw_tags
        return self.cleaned_data['tags']

    def save(self):
        tag_list = []
        for tag in self.cleaned_data['tags']:
            tag_list.append(Tag.objects.get_or_create(name=tag.encode()))

        new_question = Question.objects.create(title=self.cleaned_data['title'],
                                               text=self.cleaned_data['text'])
        for tag in tag_list:
            new_question.tags.add(tag[0])
        new_question.author = self.initial['author']
        new_question.save()
        return new_question


class AnswerForm(forms.ModelForm):  # AnswerForm - форма добавления ответа
    class Meta:
        model = Answer
        fields = ['text', ]
        widgets = {
            'text': widgets.Textarea(attrs={'class': 'form-control', 'rows': 7}),
        }

        labels = {
            'text': ''
        }


class NewUserForm(forms.Form):
    username = forms.EmailField(widget=widgets.Input(attrs={'class': 'form-control'}), label='Login:')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password:')
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Confirm:')
    email = forms.EmailField(required=False, widget=widgets.Input(attrs={'class': 'form-control'}), label='Email:')

    def clean_username(self):
        try:
            User.objects.get_by_natural_key(self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']

        raise forms.ValidationError(('This user already exist.'), code='invalid')

    def clear_password(self):
        passw = self.cleaned_data['password']
        conf_passw = self.cleaned_data['confirm_password']
        if passw and conf_passw:
            if passw == conf_passw and len(passw) >= 8 and not passw.isalpha() and not passw.isnumeric():
                return self.cleaned_data['password']

            raise forms.ValidationError(
                ('Password must be length the 8 symbol, including one letter  and including one numeric character'),
                code='invalid')
        else:
            raise forms.ValidationError(
                ('Password is not equal confirm password'),
                code='invalid')

    def save(self):
        new_user = User.objects.create_user(username=self.cleaned_data['username'],
                                            email=self.cleaned_data['email'],
                                            password=self.cleaned_data['password'])
        new_user.save()
        return new_user


class LoginUserForm(forms.Form):
    username = forms.CharField(widget=widgets.Input(attrs={'class': ''}), label='Login:')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': ''}), label='Password:')
