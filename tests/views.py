from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.html import escape
from django.shortcuts import get_object_or_404
from .models import *
import json


def login(request):
    return HttpResponse('here will be login page')

@login_required(login_url='/login/')
def lobby(request):    
    if request.user.groups.filter(name='teacher').exists():
        return teacher_lobby(request)
    else:
        return student_lobby(request)


def teacher_lobby(request):
    my_tests = Test.objects.filter(teacher=request.user)
    
    return render(request, 'tests/teacherslobby.html')

def student_lobby(request):
    return  render(request, 'tests/studentslobby.html')

@login_required(login_url='/login/')
def create_test(request, test_id = 0):
    if not is_teacher(request):
        return HttpResponseForbidden()
    if test_id != 0:
        test = get_object_or_404(Test, pk=test_id)
        if request.method == "POST":
            test.question_set.all().delete()
            test.name = request.POST.get('test_name', 'Bez mena')
            test.save()
            test_data = json.loads(request.POST.get('test_data', '[]'));
            for task in test_data:
                question = Question(assignment=json.dumps(task))
                question.test = test
                question.save()
            return redirect('lobby')

        tasks = []
        for question in test.question_set.all():
            tasks.append(question.assignment)
        return render(request, 'tests/createtest.html', {'test_name':test.name, 'test_data': json.dumps(tasks)})
    else:
        if request.method == "POST":
            test = Test(is_active=False)
            test.teacher = request.user
            test.name = request.POST.get('test_name', 'Bez mena')
            test.save()
            test_data = json.loads(request.POST.get('test_data', '[]'))
            for task in test_data:
                question = Question(assignment=json.dumps(task))
                question.test = test
                question.save()
            return redirect('lobby')
        return render(request, 'tests/createtest.html', {'test_name':''})


@login_required(login_url='/login/')
def take_test(request, test_id):
    if not is_student(request):
        return HttpResponseForbidden()

    # try to find test progress
    test = get_object_or_404(Test, pk=test_id)
    progresses = TestProgress.objects.filter(student=request.user, test=test)
    if len(progresses) == 0:
        test_progress = TestProgress(test=test, student=request.user)
        test_progress.save()
    else:
        test_progress = progresses[0]
        # if already submitted
        if not test_progress.time_end is None:
            return HttpResponse('test was submitted, you can check your answers here (maybe)')
        # if this is the submission
        if request.method == 'POST':
            test_data = json.loads(request.POST.get('test_data', '[]'))
            for task_data in test_data:
                question = Question.objects.get(pk=task_data['pk'])
                if question is None or question.test != test:
                    continue
                answer = Answer(question=question, student=request.user, value=task_data['answer'])
                answer.save()

            return redirect('lobby')
    
    tasks = []
    for question in test.question_set.all():
        task = json.loads(question.assignment)
        if 'correct' in task:
            del task['correct']
        task['pk'] = question.pk
        tasks.append(task)
    return render(request, 'tests/take_test.html', {'test_name':test.name, 'test_data': json.dumps(tasks)})

    
def test_results(request, test_progress_id):

    pass

def update_teacher(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    if request.method == 'POST':
        if 'activate' in request.POST:
            test = get_object_or_404(Test, pk=request.POST.get('activate', 0))
            if test.teacher != request.user:
                return HttpResponseForbidden()
            test.is_active = True
            test.save()
        if 'deactivate' in request.POST:
            test = get_object_or_404(Test, pk=request.POST.get('deactivate', 0))
            if test.teacher != request.user:
                return HttpResponseForbidden()
            test.is_active = False
            test.save()

    my_tests = Test.objects.filter(teacher=request.user)
    
    my_tests_render = render_to_string('tests/my_tests.html', {"tests": my_tests})
    return HttpResponse(json.dumps({"my_tests": my_tests_render}))


def update_student(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    
    current_tests = Test.objects.filter(is_active=True)
    current_tests_render = render_to_string('tests/current_tests.html', {"tests": current_tests})
    return HttpResponse(json.dumps({"current_tests": current_tests_render}))

def is_teacher(request):
    return request.user.groups.filter(name='teacher').exists()

def is_student(request):
    return request.user.groups.filter(name='student').exists()