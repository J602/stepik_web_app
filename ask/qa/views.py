# encoding=utf-8

import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST

from .models import Question, Answer, Tag
from .forms import AskForm, AnswerForm, NewUserForm, LoginUserForm

OBJECT_PER_PAGE = 10


class AjaxHttpResponse(HttpResponse):
    def __init__(self, status='ok', **kwargs):
        kwargs['status'] = status
        super(AjaxHttpResponse, self).__init__(
            content=json.dumps(kwargs),
            content_type='application/json; charset=utf-8',)


class ErrorAjaxHttpResponse(AjaxHttpResponse):
    def __init__(self, code, message):
        super(ErrorAjaxHttpResponse, self).__init__(status='error',
                                                    code=code, message=message)


def test(request, *args, **kwargs):
    return HttpResponse('OK')


def ajax_test(request, *args, **kwargs):
    return AjaxHttpResponse()


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
    q_list = Question.objects.new()
    questions = paginate(request, q_list)
    context = {'questions': questions,
               'title': 'New Questions',
               'other_link':
                   [
                       {'title': 'Hot Question',
                        'url': reverse('qa:popular-question-list')},
                       {'title': 'My Question',
                        'url': reverse('qa:user-question-list')}
                   ]
               }

    return render(request, 'questions.html', context)


@require_GET
def popular_list(request, *args, **kwargs):
    q_list = Question.objects.popular()
    questions = paginate(request, q_list)
    context = {'questions': questions,
               'title': 'Hot Question',
               'other_link':
                   [
                       {'title': 'New Question',
                        'url': reverse('qa:new-question-list')},
                       {'title': 'My Question',
                        'url': reverse('qa:user-question-list')}
                   ]
               }

    return render(request, 'questions.html', context)


@require_GET
def question_by_tag(request, *arg, **kwargs):
    tag_id = kwargs.get('id')
    tag = get_object_or_404(Tag, id=tag_id)
    q_list = Question.objects.by_tag(tag)
    questions = paginate(request, q_list)
    context = {'questions': questions,
               'title': 'By tag: {}'.format(tag.name.upper()),
               'other_link':
                   [
                       {'title': 'New Question',
                        'url': reverse('qa:new-question-list')},
                       {'title': 'Hot Question',
                        'url': reverse('qa:popular-question-list')},
                       {'title': 'My Question',
                        'url': reverse('qa:user-question-list')}
                   ]
               }

    return render(request, 'questions.html', context)


@require_GET
@login_required
def user_question(request, *arg, **kwargs):
    q_list = Question.objects.user_question(request.user)
    questions = paginate(request, q_list)
    context = {'questions': questions,
               'title': 'My question',
               'other_link':
                   [
                       {'title': 'New Question',
                        'url': reverse('qa:new-question-list')},
                       {'title': 'Hot Question',
                        'url': reverse('qa:popular-question-list')},
                   ]
               }

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
        context = {'form': form, 'title': 'New question'}
        return render(request, 'ask.html', context)
    else:
        form = AskForm(request.POST, initial={'author': request.user})
        if form.is_valid():
            question = form.save()
            context = {'id': question.pk}
            return redirect(reverse('qa:question-detail', kwargs=context))


##################################################
#                    LOGIN                       #
##################################################


def singup(request, *args, **kwargs):
    if request.method == 'GET':
        form = NewUserForm()
        context = {'form': form, 'title': 'New user'}
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
        context = {'form': form, 'title': ''}
        return render(request, 'login.html', context)
    else:
        form = LoginUserForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])

            if user is not None:
                login(request, user)
            else:
                return redirect('qa:login')

            return redirect('qa:question-list')


def user_settings(request, *args, **kwargs):
    return HttpResponse('OK')


@require_POST
@login_required
def ajax_question_like(request, *args, **kwargs):
    q_id = kwargs.get('id')
    try:
        question = Question.objects.get(pk=q_id)
    except Question.DoesNotExist:
        return ErrorAjaxHttpResponse(code=404, message='Question not found.')

    if request.user not in question.likes.all():
        question.likes.add(request.user)
        question.rating = len(question.likes.all())
        question.save()
        return AjaxHttpResponse(code=200, id=question.id, rating=question.rating, message='New like added.')
    else:
        return ErrorAjaxHttpResponse(code=200, message='Like already exist.')


@require_POST
@login_required
def ajax_question_dislike(request, *args, **kwargs):
    q_id = kwargs.get('id')
    try:
        question = Question.objects.get(pk=q_id)
    except Question.DoesNotExist:
        return ErrorAjaxHttpResponse(code=404, message='Question not found.')

    if request.user in question.likes.all():
        question.likes.remove(request.user)
        question.rating = len(question.likes.all())
        question.save()
        return AjaxHttpResponse(code=200, id=question.id, rating=question.rating, message='Like removed.')
    else:
        return ErrorAjaxHttpResponse(code=418, message='You don`t like this.')


@require_POST
@login_required
def ajax_answer_like(request, *args, **kwargs):
    a_id = kwargs.get('id')
    try:
        answer = Answer.objects.get(pk=a_id)
    except Answer.DoesNotExist:
        return ErrorAjaxHttpResponse(code=404, message='Answer not found.')

    if request.user not in answer.likes.all():
        answer.likes.add(request.user)
        answer.rating = len(answer.likes.all())
        answer.save()
        return AjaxHttpResponse(code=200, id=answer.id, rating=answer.rating, message='New like added.')
    else:
        return ErrorAjaxHttpResponse(code=418, message='Like already exist.')


@require_POST
@login_required
def ajax_answer_dislike(request, *args, **kwargs):
    a_id = kwargs.get('id')
    try:
        answer = Answer.objects.get(pk=a_id)
    except Answer.DoesNotExist:
        return ErrorAjaxHttpResponse(code=404, message='Answer not found.')

    if request.user in answer.likes.all():
        answer.likes.remove(request.user)
        answer.rating = len(answer.likes.all())
        answer.save()
        return AjaxHttpResponse(code=200, id=answer.id, rating=answer.rating, message='Like removed.')
    else:
        return ErrorAjaxHttpResponse(code=200, message='You don`t like this.')