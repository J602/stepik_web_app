# encoding=utf-8
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_GET, require_POST

from .models import Question, Answer
from .forms import  AskForm, AnswerForm


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
    context = {'title': 'Questions', 'questions': questions}

    return render(request, 'questions.html', context)


@require_GET
def popular_list(request, *args, **kwargs):

    qe_list = Question.objects.popular()
    questions = paginate(request, qe_list)
    context = {'title': 'Popular', 'questions': questions}

    return render(request, 'questions.html', context)


def question_detail(request, *args, **kwargs):
    question_id = kwargs.get('id', None)
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = AnswerForm(request.POST, initial={'question': question_id})
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.save()
        return redirect('question-detail', id=question_id)
    else:
        answers = Answer.objects.filter(question=question)
        context = {'question': question, 'answers': answers, 'form': AnswerForm}
        return render(request, 'question.html', context)


def ask_question(request, *args, **kwargs):
    if request.method == "GET":
        form = AskForm()
        context = {'form': form, 'title': 'Add new question'}
        return render(request, 'ask.html', context)
    else:
        form = AskForm(request.POST)
        if form.is_valid():
            form.save()
            context = {'id': form.instance.pk}
            return HttpResponseRedirect(reverse('question-detail', kwargs=context))

