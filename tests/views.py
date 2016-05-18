from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.html import escape
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import *
import json
import datetime

def logout_view(request):
    logout(request)
    return redirect('lobby')

def login_view(request):
    if request.user.is_authenticated():
        return redirect('lobby')

    if request.method == "POST":
        if "login-submit" in request.POST:
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('lobby')
            else:
                return render(request, 'tests/login.html', {'login_error': "Nesprávne meno alebo heslo."})
        else:
            signin_errors = []
            username = request.POST.get('username', '')
            email = request.POST.get('email', '')
            password1 = request.POST.get('password', '')
            password2 = request.POST.get('confirm-password', '')
            first_name = request.POST.get('firstname', '')
            last_name = request.POST.get('lastname', '')
            is_teacher = request.POST.get('teacher', False)
            if User.objects.filter(username=username).exists():
                username = ''
                signin_errors.append("Účet s uvedeným prihlasovacím menom už existuje.");
            if User.objects.filter(email=email).exists():
                email = ''
                signin_errors.append("Účet s uvedeným emailom už existuje.");
            if len(password1) < 6:
                signin_errors.append("Príliš krátke heslo.");
            if password1 != password2:
                signin_errors.append("Zadané heslá sa nezhodujú.");
            if not first_name:
                signin_errors.append("Nezadali ste krstné meno.");
            if not last_name:
                signin_errors.append("Nezadali ste priezvisko.");
            if signin_errors:
                return render(request, 'tests/login.html', {
                    'signin_errors': signin_errors, 
                    "username": username,
                    "email": email, 
                    "first_name": first_name, 
                    "last_name": last_name, 
                    "is_teacher": is_teacher
                    })
            else:
                user = User.objects.create_user(username, email, password1)
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                if is_teacher:
                    teachers = Group.objects.get(name='teacher')
                    teachers.user_set.add(user)
                else:
                    students = Group.objects.get(name='student')
                    students.user_set.add(user)
                user = authenticate(username=username, password=password1)
                login(request, user)
                return redirect('lobby')

    return render(request, 'tests/login.html')

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
            test_progress.time_end = datetime.datetime.now()
            test_progress.save()
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
    response_data = {}
    if 'results' in request.POST:
        test = Test.objects.get(pk=request.POST.get('results', 0))
        test_progresses = TestProgress.objects.filter(test=request.POST.get('results', 0))
        result_list = []
        for test_progress in test_progresses:
            row = {
                "pk": test_progress.pk,
                "name": "%s %s" % (test_progress.student.first_name, test_progress.student.last_name),
                "evaluated": test_progress.evaluated,
            }
            if test_progress.evaluated:
                row["total"] = Question.objects.filter(test=test_progress.test).count()
                row["correct"] = Answer.objects.filter(question__test=test_progress.test, student=test_progress.student, correct=True).count()
            result_list.append(row)
        response_data["results"] = render_to_string('tests/results_list.html', {"test_results": result_list, "test_name": test.name})
    
    my_tests_render = render_to_string('tests/my_tests.html', {"tests": my_tests})
    response_data["my_tests"] = my_tests_render
    return HttpResponse(json.dumps(response_data))


def update_student(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    
    current_tests = Test.objects.filter(is_active=True).exclude(pk__in=[progress.test.pk for progress in TestProgress.objects.filter(student__username=request.user, time_end__isnull=False)])
    current_tests_render = render_to_string('tests/current_tests.html', {"tests": current_tests})
    
    response_data = {}
    response_data["current_tests"] = current_tests_render

    
    test_progresses = TestProgress.objects.filter(student=request.user)
    result_list = []
    for test_progress in test_progresses:
        if test_progress.evaluated:
            row = {
                "pk": test_progress.pk,
                "name": test_progress.test.name,
                "total": Question.objects.filter(test=test_progress.test).count(),
                "correct": Answer.objects.filter(question__test=test_progress.test, student=test_progress.student, correct=True).count(),
            }
            result_list.append(row)
    response_data["results"] = render_to_string('tests/my_results.html', {"test_results": result_list})

    return HttpResponse(json.dumps(response_data))


@login_required(login_url='/login/')
def evaluate_test(request, test_progress_id):
    if not is_teacher(request):
        return HttpResponseForbidden()
    test_progress = get_object_or_404(TestProgress, pk=test_progress_id)
    if test_progress.test.teacher != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        test_data = json.loads(request.POST.get('test_data', '[]'))
        for task_data in test_data:
            answer = Answer.objects.get(pk=task_data['pk'])
            if answer is None or answer.question.test.teacher != request.user:
                continue
            answer.correct = task_data["answer_correct"]
            answer.save()
        test_progress.evaluated = True
        test_progress.save()
        return redirect('lobby')

    answers = Answer.objects.filter(student=test_progress.student, question__test=test_progress.test)
    
    tasks = []
    for answer in answers:
        task = json.loads(answer.question.assignment)
        task["pk"] = answer.pk
        task["answer"] = answer.value
        tasks.append(task)
    return render(request, 'tests/evaluatetest.html', {"test_data": json.dumps(tasks)})

def is_teacher(request):
    return request.user.groups.filter(name='teacher').exists()

def is_student(request):
    return request.user.groups.filter(name='student').exists()

