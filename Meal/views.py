from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import datetime as dt
import json

import requests
from bs4 import BeautifulSoup
import re
from .models import Meal, MealComment
from Service.models import CNUser
# for parser


def index(request):
    url = "http://stu.cne.go.kr/sts_sci_md01_001.do?schulCode=N100002870&schulCrseScCode=4&schulKndScCode=04&schMmealScCode="
    return HttpResponse("Hello")

@csrf_exempt
def add_comment(request):
    if request.method == 'POST':
        postID = request.POST.get('postID')
        comment = request.POST.get('comment')
        student_num = request.POST.get('studentNum') # 유저 학번

        target_author = CNUser.objects.get(student_num=student_num)
        target_meal = Meal.objects.get(id=postID) # 타깃 급식 pk를 반환

        MealComment.objects.create(post=target_meal, comment=comment, author=target_author) # 새로운 코멘트를 추가한다.

        return HttpResponse('CommentSuccess')


def delete_comment(request):
    if request.method == 'POST':
        comment_id = request.POST.get('commentID')
        student_num = request.POST.get('studentNum') # Check Again Is the user is author

        action_author = CNUser.objects.get(student_num=student_num)
        target_comment = MealComment.objects.get(id=comment_id)

        if target_comment.author.id == action_author.id: # same author and deleter
            target_comment.delete()
            return HttpResponse('DeleteSuccess')
        else:
            return HttpResponse('ErrorCode:1112')


def show_meal(request):
    now = dt.datetime.now()
    startDay = now.date() + dt.timedelta(days=-now.weekday()) # select monday
    endDay = now.date() + dt.timedelta(days=6-now.weekday()) # select sunday

    meal_list = list(Meal.objects.filter(meal_date__range=[startDay, endDay]).values())
    response = json.dumps(meal_list, cls=DjangoJSONEncoder, ensure_ascii=False)

    return HttpResponse(response)


def show_meal_comment(request, id):
    target_meal = Meal.objects.get(id=id)

    comment_list = list(MealComment.objects.filter(post=target_meal).order_by('created').values()) # 생성일자 오름차순(날짜 오래된 것 처음) 정렬
    response = json.dumps(comment_list, cls=DjangoJSONEncoder, ensure_ascii=False)

    return HttpResponse(response)


def like_comment(request):
    if request.method == 'POST':
        commentID = request.POST.get('commentID')
        student_num = request.POST.get('student_num')

        try:
            like_User = CNUser.objects.get(student_num=student_num) # Get Liked User
            like_Comment = MealComment.objects.get(id=commentID) # Get Liked Comment
        except:
            return HttpResponse('ErrorCode:1111')

        if like_Comment.likes.filter(id = like_User.id).exists(): # 해당 유저가 이미 좋아요 누르면
            like_Comment.likes.remove(like_User)
            message = 'DislikedSuccess'
        else :
            like_Comment.likes.add(like_User)
            message = 'LikedSuccess'

        content = {'likes_count' : like_Comment.total_likes(), 'message' : message}
        return HttpResponse(json.dumps(content), content_type='application/json') #