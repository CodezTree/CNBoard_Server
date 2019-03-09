from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
import os
import datetime as dt
import json

import requests
from bs4 import BeautifulSoup
import re
from .FoodParserTest import parse_food_list
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


@csrf_exempt
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

    raw_list = MealComment.objects.filter(post=target_meal).order_by('created')

    comment_list = list(raw_list.values()) # 생성일자 오름차순(날짜 오래된 것 처음) 정렬

    print(comment_list)
    for i, dic in enumerate(comment_list): # 세부 전달 정보 추가
        st = CNUser.objects.get(id=dic['author_id'])
        dic['student_num'] = st.student_num
        dic['student_name'] = st.student_name
        dic['likes_count'] = raw_list[i].total_likes()

    print(comment_list)
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
        return HttpResponse(json.dumps(content), content_type='application/json')


def parse_food_server(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    data = parse_food_list()

    for food in data:
        Meal.objects.create(meal_date=food['meal_date'], meal_txt=food['meal_txt'], meal_time_part=food['meal_time_part'])

    f = open(os.path.join(settings.BASE_DIR, 'Service/ServiceSetting.txt'), 'r+')

    while True:
        line = f.readline()
        if not line:
            break

        sets = line[:-1].split("=")
        print(sets)
        if sets[0] == 'Meal_Updated':
            f.seek(f.tell() - 3, os.SEEK_SET)
            f.write('1')
            break
    f.close()

    return redirect('administrate_tools')