from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from organizations.models import Organization
User = get_user_model()

LEVEL_CHOICES = [
        (1, 'A1'),
        (2, 'A2'),
        (3, 'B1'),
        (4, 'B2'),
        (5, 'C1'),
        (6, 'C2'),
    ]


class Exam(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    level = models.IntegerField('Уровень',
                             choices=LEVEL_CHOICES,
                             validators=[
                                 MinValueValidator(1),
                                 MaxValueValidator(6)
                             ],
                             null=False, blank=False, default='1')
    author = models.ForeignKey(Organization, related_name='exams', on_delete=models.CASCADE, verbose_name='Автор теста')
    @property
    def total_points(self):
        return sum(question.point for question in self.questions.all())
    



class Question(models.Model):
    exam = models.ForeignKey(Exam, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    number = models.IntegerField('Номер вопроса', default=1, help_text='Порядковый номер вопроса в тесте')
    point = models.IntegerField('Баллы за вопрос', default=1, help_text='Количество баллов за правильный ответ на вопрос',
                                validators=[MinValueValidator(1), MaxValueValidator(10)])

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=128)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'

    def __str__(self):
        return self.text

class Result(models.Model):
    user = models.ForeignKey(User, related_name='results', on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, related_name='results', on_delete=models.CASCADE)
    score = models.IntegerField('Баллы', default=0, help_text='Количество баллов, набранных в тесте', validators=
                                [MinValueValidator(0), 
                                 MaxValueValidator(100)])
    completed_at = models.DateTimeField(auto_now_add=True)