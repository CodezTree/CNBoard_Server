from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

import os
import json

from .forms import NoticeForm, FileForm, LoginForm, ExamForm, AlertNoticeForm, PasswordCheckForm, VersionUpdateForm
from .models import NoticeData, FileData, ExamData, AlertNoticeData, CNBoardApply

# Create your views here.


class Home(TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        if request.session['login_session'] != '$%@#@asf22qwr12t':
            return redirect('admin_login') # 로그인 안되어 있을경우

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


# --------------------- EXAM -----------------------

def add_exam_data(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('exam_data_list')
    else:
        form = ExamForm()
    return render(request, 'add_exam_data.html', {
        'form': form
    })


def exam_service_avail_check(request):
    f = open(os.path.join(settings.BASE_DIR, 'Service/ServiceSetting.txt'), 'r')
    avail = '0'

    while True:
        line = f.readline()
        if not line:
            break

        sets = line.split("=")
        if sets[0] == 'Exam_Service_Available':
            avail = sets[1]
            break

    f.close()

    return HttpResponse(avail)  # 0 - Not Available  1 - Available


def exam_service_state_change(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    f = open(os.path.join(settings.BASE_DIR, 'Service/ServiceSetting.txt'), 'r+')
    avail = '0'

    while True:
        line = f.readline()
        if not line:
            break

        sets = line[:-1].split("=")
        print(sets)
        if sets[0] == 'Exam_Service_Available':
            avail = sets[1]
            if avail == '0':
                print(f.tell())
                f.seek(f.tell() - 3, os.SEEK_SET)
                f.write('1')
            else:
                f.seek(f.tell() - 3, os.SEEK_SET)
                f.write('0')
            break
    f.close()

    return redirect('exam_data_list')


@csrf_exempt
def add_exam_data_android(request):
    if request.method == 'POST':
        exam_data = json.load(request.POST.get('examData')) # examData 는 dictionary

        #for i, _exam in enumerate(exam_data):
        # try:
        #     tempExam = ExamData.objects.get(exam_code=int(exam_data.get('exam_code')), exam_name=exam_data.get('exam_name'))
        #     if tempExam:
        #         tempExam.exam
        #
        # except ObjectDoesNotExist:
        #
        ExamData.objects.create(category=exam_data.get('category'), exam_code=int(exam_data.get('exam_code')),
                                    target_grade=int(exam_data.get('target_grade')),
                                    exam_range=exam_data.get('exam_range'), exam_name=exam_data.get('exam_name'))
        # Create Exam Data Files

        return HttpResponse('DataAddSuccess')


def exam_data_list(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    exam_all = ExamData.objects.all()
    f = open(os.path.join(settings.BASE_DIR, 'Service/ServiceSetting.txt'), 'r')

    exam_available = 0
    while True:
        line = f.readline()
        if not line:
            break # No readable line

        sets = line.split('=')
        if sets[0] == 'Exam_Service_Available': # found params
            exam_available = int(sets[1])
            break

    f.close()
    return render(request, 'exam_list.html', {
        'exams' : exam_all, 'exam_available': exam_available
    })


def show_exam_data(request):

    exam_list = list(ExamData.objects.all().values())

    json_data = json.dumps(exam_list, cls=DjangoJSONEncoder, ensure_ascii=False)

    return HttpResponse(json_data)


def delete_exam_data(request, pk):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    if request.method == 'POST':
        exam = ExamData.objects.get(pk=pk)
        exam.delete()

        return redirect('exam_data_list')


# --------------------- EXAM END -----------------------


# -------------- NOTICE ----------------

def show_notice_android(request):
    # notices = NoticeData.objects.all()
    # serialized_query = serializers.serialize('json', notices)
    notices = list(NoticeData.objects.all().order_by('notice_date').values())
    # response = serializers.serialize('json', notices)
    response = json.dumps(notices, cls=DjangoJSONEncoder, ensure_ascii=False)

    return HttpResponse(response)


def notice_list(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    notices = NoticeData.objects.all()
    return render(request, 'notice_list.html', {
        'notices': notices
    })


def upload_notice(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('notice_list')
    else:
        form = NoticeForm()
    return render(request, 'upload_notice.html', {
        'form': form
    })


def delete_notice(request, pk):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    if request.method == 'POST':
        notice = NoticeData.objects.get(pk=pk)
        notice.delete()
    return redirect('notice_list')


@csrf_exempt
def show_filtered_notice(request):
    if request.method == 'POST':
        notice_kind = request.POST.get('notice_kind')
        target_grade = request.POST.get('target_grade')

        if not notice_kind or not target_grade:
            return HttpResponse('ErrorCode:1113')

        notice_kind = int(notice_kind)
        target_grade = int(target_grade)

        if notice_kind == 0:
            if target_grade == 0:
                return redirect('show_notice') # 전체공지 보여주기
            else:
                notice_return = list(NoticeData.objects.filter(target_grade=target_grade).values())
        else:
            if not target_grade:
                notice_return = list(NoticeData.objects.filter(notice_kind=notice_kind).values())
            else:
                notice_return = list(
                    NoticeData.objects.filter(notice_kind=notice_kind, target_grade=target_grade).values())

        response = json.dumps(notice_return, cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(response)

    return HttpResponse('')


def show_alert_notice(request): # 긴급공지 리스트

    alert_notice_list = list(AlertNoticeData.objects.all().values())

    response = json.dumps(alert_notice_list, cls=DjangoJSONEncoder, ensure_ascii=False)

    return HttpResponse(response)


def delete_alert_notice(request, pk):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    if request.method == 'POST':
        data = AlertNoticeData.objects.get(pk=pk)
        data.delete()

        return redirect('alert_notice_list')


@csrf_exempt
def delete_alert_notice_android(request): # 누구나 시간대 확인해서 다르면 삭제 가능
    if request.method == 'POST':
        notice_id = request.POST.get('noticeID')

        notice = AlertNoticeData.objects.get(id=notice_id)
        notice.delete()

    return HttpResponse('')


def upload_alert_notice(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    if request.method == 'POST':
        form = AlertNoticeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('alert_notice_list')
    else:
        form = AlertNoticeForm()
    return render(request, 'upload_alert_notice.html', {
        'form': form
    })


def alert_notice_list(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    notices = AlertNoticeData.objects.all()
    return render(request, 'alert_notice_list.html', {
        'notices': notices
    })


# ---------------- NOTICE END ----------------


# ---------------- FILE -------------------

def upload_file(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('file_list')
    else:
        form = FileForm()
    return render(request, 'upload_file.html', {
        'form': form
    })


def delete_file(request, pk):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    if request.method == 'POST':
        file = FileData.objects.get(pk=pk)
        file.delete()
    return redirect('file_list')


def file_list(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    files = FileData.objects.all()
    return render(request, 'file_list.html', {
        'files': files
    })


# ------------------- FILE END --------------------

# ------------------- APPLY -----------------------

@csrf_exempt
def apply_cnboard(request):
    if request.method == 'POST':
        student_number = request.POST.get('student_number')
        apply_target = request.POST.get('apply_target')
        apply_content = request.POST.get('apply_content')

        CNBoardApply.objects.create(student_number=student_number, apply_target=apply_target, apply_content=apply_content)

        return HttpResponse('')


# ----------------- AUTHENTICATION -----------------

def admin_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(data)
            if data.get('ID') == 'admin' and data.get('Pass') == 'cnboard1234!':
                request.session['login_session'] = '$%@#@asf22qwr12t'
                return redirect('home')
            else :
                return HttpResponseForbidden()  # 접근 제한
    else:
        form = LoginForm()
        request.session['login_session'] = ''
    return render(request, 'login.html', {
        'form': form
    })


def logout(request):
    if request.session['login_session'] == '$%@#@asf22qwr12t':
        request.session['login_session'] = ''

    return redirect('admin_login')

# ----------------- AUTHENTICATION -----------------


# --------------- ADMINISTRATE TOOLS ---------------


def administrate_tools(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    f = open(os.path.join(settings.BASE_DIR, 'Service/ServiceSetting.txt'), 'r+')
    ret = 0
    app_version = ''

    while True:
        line = f.readline()
        if not line:
            break

        sets = line[:-1].split("=")

        if sets[0] == 'Meal_Updated':
            avail = sets[1]
            print(avail)
            if avail == '0':
                ret = 0
            else:
                ret = 1

        if sets[0] == 'App_Lastest_Version':
            app_version = sets[1]
    f.close()

    return render(request, 'administrate_tools.html', {
        'meal_setting': ret,
        'app_version': app_version
    })


def confirm_meal_update_change(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    if request.method == 'POST':
        form = PasswordCheckForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data.get('Pass') == 'cnboard1234!':
                f = open(os.path.join(settings.BASE_DIR, 'Service/ServiceSetting.txt'), 'r+')
                avail = '0'

                while True:
                    line = f.readline()
                    if not line:
                        break

                    sets = line[:-1].split("=")
                    print(sets)
                    if sets[0] == 'Meal_Updated':
                        avail = sets[1]
                        if avail == '1':
                            f.seek(f.tell() - 3, os.SEEK_SET)
                            f.write('0')
                        break
                f.close()

                return redirect('administrate_tools')
    else:
        form = PasswordCheckForm()

    return render(request, 'login.html', {
        'form': form
    })


def update_app_version(request):
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    if request.method == 'POST':
        form = VersionUpdateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data.get('Pass') == 'cnboard1234!':
                f = open(os.path.join(settings.BASE_DIR, 'Service/ServiceSetting.txt'), 'r+')

                while True:
                    line = f.readline()
                    if not line:
                        break

                    sets = line[:-1].split("=")
                    print(sets)
                    if sets[0] == 'App_Lastest_Version':
                        f.seek(f.tell() - 6, os.SEEK_SET) # 4 칸 뒤로 가서 버전코드는 0000 0001 4글자
                        f.write(data.get('Version'))
                        break
                f.close()

                return redirect('administrate_tools')
    else:
        form = VersionUpdateForm()

    return render(request, 'login.html', {
        'form': form
    })


def show_app_version(request):
    f = open(os.path.join(settings.BASE_DIR, 'Service/ServiceSetting.txt'), 'r+')

    while True:
        line = f.readline()
        if not line:
            break

        sets = line[:-1].split("=")
        print(sets)
        if sets[0] == 'App_Lastest_Version':
            f.close()
            return HttpResponse(set[1])

# --------------------------------------------------


def upload(request):
    context = {}
    if request.session['login_session'] != '$%@#@asf22qwr12t':
        return redirect('admin_login')  # 로그인 안되어 있을경우

    if request.method == 'POST':
        uploaded_file = request.FILES['notice_doc']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['saved_url'] = fs.url(name)
    return render(request, 'upload.html', context)


class NoticeListView(ListView):
    model = NoticeData
    template_name = 'class_notice_list.html'
    context_object_name = 'notices'


class UploadNoticeView(CreateView):
    model = NoticeData
    form_class = NoticeForm
    success_url = reverse_lazy('class_notice_list')
    template_name = 'upload_notice.html'
