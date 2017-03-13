# encoding=utf-8
import pprint

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST

from .models import Question, Answer
from .forms import AskForm, AnswerForm, NewUserForm, LoginUserForm

from pprint import pprint

OBJECT_PER_PAGE = 10


@require_GET
def test(request, *args, **kwargs):
    return HttpResponse('OK')


def paginate(request, object_list):
    paginator = Paginator(object_list, OBJECT_PER_PAGE)

    try:
        objects = paginator.page(request.GET.get('page'))
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    return objects


@require_GET
def question_list(request, *args, **kwargs):
    qe_list = Question.objects.new()
    questions = paginate(request, qe_list)
    context = {'questions': questions, 'title': 'New Questions'}

    return render(request, 'questions.html', context)


@require_GET
def popular_list(request, *args, **kwargs):
    qe_list = Question.objects.popular()
    questions = paginate(request, qe_list)
    context = {'questions': questions, 'title': 'Popular question'}

    return render(request, 'questions.html', context)


def question_detail(request, *args, **kwargs):
    question_id = kwargs.get('id', None)
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = AnswerForm(request.POST, initial={'question': question_id})  # для тестов
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()

    answers = Answer.objects.filter(question=question)
    context = {'question': question, 'answers': answers, 'form': AnswerForm, 'title': 'Question detail page'}
    return render(request, 'question.html', context)

@login_required
def ask_question(request, *args, **kwargs):
    if request.method == "GET":
        form = AskForm()
        context = {'form': form, 'title': 'Add new question page'}
        return render(request, 'ask.html', context)
    else:
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            context = {'id': question.pk}
            return redirect(reverse('qa:question-detail', kwargs=context))


##################################################
#                    LOGIN                       #
##################################################


def singup(request, *args, **kwargs):
    if request.method == 'GET':
        form = NewUserForm()
        context = {'form': form, 'title': 'Create new user page'}
        return render(request, 'singup.html', context)
    else:
        form = NewUserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, user=new_user)

        return redirect('qa:question-list')


@require_GET
def user_logout(request):
    logout(request)
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'qa:question-list')


def user_login(request):
    if request.method == 'GET':
        form = LoginUserForm()
        context = {'form': form, 'title': 'Login page'}
        return render(request, 'login.html', context)
    else:
        referer = request.META.get('HTTP_REFERER')
        form = LoginUserForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])

            if user is not None:
                login(request, user)
            else:
                return redirect('qa:login')

            return redirect(referer or 'qa:question-list')
