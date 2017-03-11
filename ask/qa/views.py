# encoding=utf-8
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_GET, require_POST
from .models import Question


OBJECT_PER_PAGE = 10


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


@require_GET
def question_detail(request, *args, id=None):

    question = get_object_or_404(Question, pk=id)

    context = {'question': question}

    return render(request, 'question.html', context)
