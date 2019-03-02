from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from Service.models import CNUser
import sys, os
sys.path.append(os.pardir)

# Create your models here.


class Meal(models.Model):
    # meal_id = models.AutoField(primary_key=True)
    # 급식 ID - 코멘트 연결할 때 쓰임 -> Django 기본 제공으로 변경

    meal_date = models.DateField()
    # 급식 일자

    meal_txt = models.TextField(null=False)
    # 급식 세부 사항

    meal_time_part = models.IntegerField(default=0)
    # 급식 시간대 0 - 조식, 1 - 중식, 2 - 석식

    def __str__(self):
        return self.meal_txt


class MealComment(models.Model):
    post = models.ForeignKey(Meal, on_delete=models.CASCADE)
    # Comment가 바라보는 Post를 저장

    comment = models.TextField(max_length=1000, null=False)
    # 급식 코멘트

    author = models.ForeignKey(CNUser, related_name='related_author_meal_comment', on_delete=models.CASCADE)
    # 작성자

    created = models.DateTimeField()
    # 작성 일시

    likes = models.ManyToManyField(CNUser, related_name='related_likes_meal_comment', blank=True)
    # 좋아요

    def __str__(self):
        return self.comment

    def save(self, *args, **kwargs):
        self.created = timezone.now() # update timezone every save function
        return super(MealComment, self).save(*args, **kwargs)

    def total_likes(self):
        return int(self.likes.count())
