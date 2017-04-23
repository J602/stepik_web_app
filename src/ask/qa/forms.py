# encoding=utf-8
import re

from django import forms
from django.forms import widgets
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Question, Answer, Tag, UserProfile


class AskModelForm(forms.ModelForm):

    tags = forms.CharField(max_length=150, strip=True, required=False,
                           widget=widgets.Input(
                               attrs={'class': 'form-control',
                                      'placeholder': 'at least one tag such as (html js),'
                                                     ' max 5 tags, tag characters: [a-z 0-9]'}),
                           label='Tags:')

    class Meta:
        model = Question
        fields = ['title', 'text', 'published']
        widgets = {
            'title': widgets.TextInput(attrs={'class': 'form-control'}),
            'text': widgets.Textarea(attrs={'class': 'form-control',
                                            'rows': 20,
                                            'id': 'ask-textarea',}),
            'published': widgets.CheckboxInput(attrs={}),
        }
        labels = {
            'title': 'Title:',
            'text': 'Text:',
            'published': 'Published:',
        }

    def __init__(self, *args, **kwargs):
        super(AskModelForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags'].initial = ', '.join([str(tag) for tag in self.instance.tags.all()])

    def clean_tags(self):
        max_tag_length = 15
        #  [a-z 0-9 -] characters
        alphabet = '-' + ''.join([chr(i) for i in range(ord('a'), ord('z') + 1)]) + ''.join(
            [chr(i) for i in range(ord('0'), ord('9') + 1)])

        raw_tags = re.split(',|;| ', self.cleaned_data['tags'].lower())
        raw_tags = [tag for tag in raw_tags if tag]
        if len(raw_tags) > Tag.MAX_TAG_COUNT:
            raise forms.ValidationError('Tags maximum is 5 tag.', code='invalid')

        for tag in raw_tags:
            if not all(ch in alphabet for ch in tag):
                raise forms.ValidationError('Tag must contain [a-z 0-9 -] characters.', code='invalid')
            if len(tag) > max_tag_length:
                raise forms.ValidationError('Maximum tag length is 15 characters.', code='invalid')

        self.cleaned_data['tags'] = raw_tags
        return self.cleaned_data['tags']

    def save(self, commit=True, *args, **kwargs):
        instance = super(AskModelForm, self).save(commit=False,  *args, **kwargs)
        if not instance.pk:
            for name, value in self.initial.items():
                if hasattr(instance, name):
                    setattr(instance, name, value)
            instance.save()

        instance.tags.clear()
        for tag in self.cleaned_data['tags']:
            instance.tags.add(Tag.objects.get_or_create(name=tag.encode())[0])

        if commit:
            instance.save()

        return instance


class AnswerForm(forms.ModelForm):  # AnswerForm - форма добавления ответа
    class Meta:
        model = Answer
        fields = ['text', ]
        widgets = {
            'text': widgets.Textarea(attrs={'class': 'form-control',
                                            'rows': 10,
                                            'id': 'answer-textarea',
                                            }),
        }

        labels = {
            'text': ''
        }


class NewUserForm(forms.Form):
    username = forms.EmailField(widget=widgets.Input(attrs={'class': 'form-control',
                                                            'placeholder': 'example@example.com', }), label='Login:')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password:')
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'},), label='Confirm:')
    email = forms.EmailField(required=False,
                             widget=widgets.Input(attrs={'class': 'form-control',
                                                         'placeholder': 'example@example.com', }),
                             label='Email:')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(('This user already exist.'), code='invalid')

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password=password)
        return password

    def clean_confirm_password(self):
        passw = self.cleaned_data.get('password')
        conf_passw = self.cleaned_data.get('confirm_password')
        if passw and conf_passw:
            if passw != conf_passw:
                raise forms.ValidationError(
                    ('Password is not equal confirm password'),
                    code='invalid')
        return conf_passw

    def save(self):
        new_user = User.objects.create_user(username=self.cleaned_data['username'],
                                            email=self.cleaned_data['email'],
                                            password=self.cleaned_data['password'])
        new_user.save()
        return new_user


class LoginUserForm(forms.Form):
    username = forms.CharField(widget=widgets.Input(attrs={'class': 'form-control',
                                                           'placeholder': 'example@example.com', }), label='Login:', )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password:', )

    def __init__(self, *args, **kwargs):
        self.user = None
        super(LoginUserForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError('Invalid login or password.',
                                            code='invalid_login')


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

        widgets = {
            'email': widgets.EmailInput(attrs={'class': 'form-control',
                                               'placeholder': 'example@example.com', }),
            'first_name': widgets.TextInput(attrs={'class': 'form-control', }),
            'last_name': widgets.TextInput(attrs={'class': 'form-control', }),
        }

        labels = {
            'email': 'Email',
            'first_name': 'First name',
            'last_name': 'Last name',
        }


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['name', 'image', 'score', ]

        widgets = {
            'name': widgets.TextInput(attrs={'class': 'form-control'}),
            'image': widgets.FileInput(attrs={'type': 'file', 'accept': 'image/jpeg,image/png, image/svg', }),
            'score': widgets.TextInput(attrs={'class': 'form-control', 'readonly': ''})
        }

        labels = {
            'name': 'Nickname',
            'image': '',
            'score': 'Score',
        }
