from django.contrib import admin
from .models import NoticeData, FileData, CNUser, ExamData

# Register your models here.
admin.site.register(NoticeData)
admin.site.register(FileData)
admin.site.register(CNUser)
admin.site.register(ExamData)