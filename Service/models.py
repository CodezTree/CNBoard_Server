from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.


class CNUser(models.Model):
    student_num = models.IntegerField(null=False)
    # 학생 번호 ( 학번 ) -> Teacher = 9999

    student_name = models.CharField(max_length=16, null=False)
    # 학생 이름

    student_grade = models.IntegerField(null=False)
    # 학생 학년 -> Teacher = -1

    def __str__(self):
        return str(self.student_num)


class ExamData(models.Model):
    category = models.CharField(max_length=20, null=False)
    # 과목 카테고리

    exam_code = models.IntegerField(null=False)
    # 과목 코드

    target_grade = models.IntegerField(null=False)
    # 과목 대상 학년

    exam_range = models.TextField(null=False, max_length=1000)
    # 시험 범위

    exam_name = models.CharField(max_length=20, null=False)
    # 시험 과목 이름

    def __str__(self):
        return self.exam_name


class FileData(models.Model):
    file_title = models.CharField(null=False, max_length=30)
    # 파일 제목

    file_description = models.TextField(null=True, blank=True, max_length=500)
    # 파일 설명

    file_document = models.FileField(upload_to='files/', null=False)
    # 파일

    def __str__(self):
        return self.file_title

    def delete(self, *args, **kwargs):
        self.file_document.delete()
        super().delete(*args, **kwargs)


class NoticeData(models.Model):
    notice_date = models.DateField(null=False, auto_now_add=True)
    # 공지 등록 일자

    notice_title = models.CharField(null=False, max_length=30)
    # 공지 제목

    target_grade = models.IntegerField(null=False)
    # 공지 타깃 학년 -> 모든 학년 - 0 / 1학년 - 1 / 2학년 -2 / 3학년 - 3

    notice_image = models.ImageField(upload_to='notice/', null=False)
    # 공지 이미지

    notice_kind = models.IntegerField(null=False, default=0)
    # 공지 종류 -> 0 : 기타,  1 : 일정 , 2 : 대회, 3 : 행사

    def __str__(self):
        return self.notice_title

    def delete(self, *args, **kwargs):
        self.notice_image.delete()
        super().delete(*args, **kwargs) # Call Real Save