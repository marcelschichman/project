from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Test(models.Model):
    teacher = models.ForeignKey(User)
    name = models.CharField(max_length=1000)
    is_active = models.BooleanField(default=False)
    
class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    assignment = models.TextField()
    correct_answer = models.TextField()

class TestProgress(models.Model):
    student = models.ForeignKey(User)
    test = models.ForeignKey(Test)
    time_start = models.DateTimeField(auto_now=True)
    time_end = models.DateTimeField(null=True)

class Answer(models.Model):
    question = models.ForeignKey(Question)
    student = models.ForeignKey(User)
    value = models.TextField()
    correct = models.NullBooleanField()