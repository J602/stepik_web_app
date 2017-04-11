# encoding=utf-8

import json

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, reverse, redirect, Http404
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST

from .models import Question, Answer, Tag
from .forms import AnswerForm, NewUserForm, LoginUserForm, UserForm, UserProfileForm, AskModelForm

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


def login_required_ajax(view):
    def view2(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view(request, *args, **kwargs)
        elif request.is_ajax():
            return ErrorAjaxHttpResponse(
                code='no_auth',
                message='Not authenticated'
            )
        else:
            redirect('qa:login')
    return view2

@require_GET
def question_list(request, *args, **kwargs):
    q_list = Question.objects.new(request.user)
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

    return render(request, 'qa/questions.html', context)


@require_GET
def popular_list(request, *args, **kwargs):
    q_list = Question.objects.popular(request.user)
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

    return render(request, 'qa/questions.html', context)


@require_GET
def question_by_tag(request, *arg, **kwargs):
    tag_id = kwargs.get('id')
    tag = get_object_or_404(Tag, id=tag_id)
    q_list = Question.objects.by_tag(tag, request.user)
    questions = paginate(request, q_list)
    context = {'questions': questions,
               'title': 'By tag: {}'.format(tag.name.upper()),
               'other_link':
                   [
                       # {'title': 'New Question',
                       #  'url': reverse('qa:new-question-list')},
                       # {'title': 'Hot Question',
                       #  'url': reverse('qa:popular-question-list')},
                       # {'title': 'My Question',
                       #  'url': reverse('qa:user-question-list')}
                   ]
               }

    return render(request, 'qa/questions.html', context)


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

    return render(request, 'qa/questions.html', context)


@require_GET
def question_detail(request, *args, **kwargs):
    question_id = kwargs.get('id', None)
    question = get_object_or_404(Question, pk=question_id)
    context = {'question': question,
               'form': AnswerForm,
               'title': 'Question detail page'}
    return render(request, 'qa/question.html', context)


@require_GET
def answers(request, *args, **kwargs):
    question_id = kwargs.get('id', None)
    question = get_object_or_404(Question, pk=question_id)
    answers = Answer.objects.filter(question=question).order_by('-rating')
    context = {'answers': answers,
               'question': question}
    return render(request, 'qa/answers.html', context)


@login_required
def ask_question(request, *args, **kwargs):
    if request.method == "POST":
        form = AskModelForm(request.POST, initial={'author': request.user})
        if form.is_valid():
            question = form.save()
            return redirect(reverse('qa:question-detail', kwargs={'id': question.pk}))
    else:
        form = AskModelForm()
    context = {'form': form,
               'url': reverse('qa:ask-question'),
               'title': 'New question',
               'button': 'ASK'}
    return render(request, 'qa/ask.html', context)


@login_required
def question_edit(request, *args, **kwargs):
    question_id = kwargs.get('id', None)
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        raise Http404()

    if request.method == 'POST':
        form = AskModelForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect(reverse('qa:question-detail', kwargs={'id': question_id}))
    else:
        form = AskModelForm(instance=question)

    context = {'form': form,
               'url': reverse('qa:question-edit', kwargs={'id': question_id}),
               'title': 'Edit question:',
               'button': 'SAVE'}
    return render(request, 'qa/ask.html', context)


@require_GET
def tags(request, *args, **kwargs):
    context = {'tags': Tag.objects.tags()}
    return render(request, 'core/tags.html', context)


##################################################
#                    LOGIN                       #
##################################################


def singup(request, *args, **kwargs):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, user=new_user)
            return redirect('qa:question-list')
    else:
        form = NewUserForm()

    context = {'form': form, 'title': 'Registration:'}
    return render(request, 'auth/singup.html', context)


@require_GET
def user_logout(request, *args, **kwargs):
    logout(request)
    return redirect('qa:question-list')


def user_login(request, *args, **kwargs):
    if request.method == 'POST':
        next_param = request.GET.get('next')
        form = LoginUserForm(request.POST)
        if form.is_valid():
            if form.user is not None:
                login(request, form.user)
            return redirect(next_param or 'qa:question-list')
    else:
        form = LoginUserForm()

    context = {'form': form, 'title': 'Welcome'}
    return render(request, 'auth/login.html', context)


@login_required
@transaction.atomic
def user_settings(request, *args, **kwargs):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form.save()
            user_profile_form.save()
            # messages.success(request, _('Your profile was successfully updated!'))
            return redirect('qa:user-settings')
        else:
            pass
            # messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        user_profile_form = UserProfileForm(instance=request.user.userprofile)
    context = {
        'user_form': user_form,
        'user_profile_form': user_profile_form
    }
    return render(request, 'auth/settings.html', context)


##################################################
#                     AJAX                       #
##################################################


@require_POST
@login_required_ajax
def ajax_add_answer(request, *args, **kwargs):
    q_id = kwargs.get('id', None)
    try:
        question = Question.objects.get(pk=q_id)
    except Question.DoesNotExist:
        return ErrorAjaxHttpResponse(code='not_found', message='Question not found.')
    data = json.loads(request.body.decode('utf-8'))
    form = AnswerForm(data, initial={'question': q_id})
    if form.is_valid():
        answer = form.save(commit=False)
        answer.question = question
        answer.author = request.user
        answer.save()
        return AjaxHttpResponse(message='Answer added.')
    return ErrorAjaxHttpResponse(code='invalid', message='Error.')                # it's almost impossible


@require_POST
@login_required_ajax
def ajax_question_like(request, *args, **kwargs):
    q_id = kwargs.get('id')
    try:
        question = Question.objects.get(pk=q_id)
    except Question.DoesNotExist:
        return ErrorAjaxHttpResponse(code='not_found', message='Question not found.')

    if request.user not in question.likes.all():
        question.likes.add(request.user)
        question.rating = len(question.likes.all())
        question.save()
        return AjaxHttpResponse(id=question.id, rating=question.rating, message='New like added.')
    else:
        return ErrorAjaxHttpResponse(code='exist', message='Like already exist.')


@require_POST
@login_required_ajax
def ajax_question_dislike(request, *args, **kwargs):
    q_id = kwargs.get('id')
    try:
        question = Question.objects.get(pk=q_id)
    except Question.DoesNotExist:
        return ErrorAjaxHttpResponse(code='not_found', message='Question not found.')

    if request.user in question.likes.all():
        question.likes.remove(request.user)
        question.rating = len(question.likes.all())
        question.save()
        return AjaxHttpResponse(id=question.id, rating=question.rating, message='Like removed.')
    else:
        return ErrorAjaxHttpResponse(code='not_exist', message='You don`t like this.')


@require_POST
@login_required_ajax
def ajax_answer_like(request, *args, **kwargs):
    a_id = kwargs.get('id')
    try:
        answer = Answer.objects.get(pk=a_id)
    except Answer.DoesNotExist:
        return ErrorAjaxHttpResponse(code='not_found', message='Answer not found.')

    if request.user not in answer.likes.all():
        answer.likes.add(request.user)
        answer.rating = len(answer.likes.all())
        answer.save()
        return AjaxHttpResponse(id=answer.id, rating=answer.rating, message='New like added.')
    else:
        return ErrorAjaxHttpResponse(code='exist', message='Like already exist.')


@require_POST
@login_required_ajax
def ajax_answer_dislike(request, *args, **kwargs):
    a_id = kwargs.get('id')
    try:
        answer = Answer.objects.get(pk=a_id)
    except Answer.DoesNotExist:
        return ErrorAjaxHttpResponse(code='not_found', message='Answer not found.')

    if request.user in answer.likes.all():
        answer.likes.remove(request.user)
        answer.rating = len(answer.likes.all())
        answer.save()
        return AjaxHttpResponse(id=answer.id, rating=answer.rating, message='Like removed.')
    else:
        return ErrorAjaxHttpResponse(code='not_exist', message='You don`t like this.')


@require_POST
@login_required_ajax
def ajax_answer_correct(request, *args, **kwargs):
    a_id = kwargs.get('id')
    try:
        answer = Answer.objects.get(pk=a_id)
    except Answer.DoesNotExist:
        return ErrorAjaxHttpResponse(code='not_found', message='Answer not found.')

    if answer.question.author != request.user:
        return ErrorAjaxHttpResponse(code='other_owner', message="It's other author question")

    answer.correct = not answer.correct
    answer.save()
    msg = 'Correct' if answer.correct else 'Incorrect'
    return AjaxHttpResponse(id=answer.id, correct=answer.correct, message=msg)


def search(request, *args, **kwargs):
    context = {'title': 'Search', }
    if request.method == "POST":
        search_param = json.loads(request.body.decode('utf-8')).get('search_text')
        if search_param:
            q = Question.objects.user_or_published(request.user).filter(
                Q(title__contains=search_param) |
                Q(text__contains=search_param) |
                Q(answers__text__contains=search_param)
            ).values('id', 'title').distinct()
            q = list(q)
            [elem.update({'url': reverse('qa:question-detail', kwargs={'id': elem.get('id')})}) for elem in q]
            return AjaxHttpResponse(questions=q)

    return render(request, 'qa/search.html', context)


##################################################
#                    ERROR                       #
##################################################


def error404(request, *args, **kwargs):
    return render(request, 'error/404.html')


def error500(request, *args, **kwargs):
    return render(request, 'error/500.html')
