from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

import os
import json

from .forms import NoticeForm, FileForm, LoginForm, ExamForm
from .models import NoticeData, FileData, ExamData

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


def add_exam_data_android(request):
    if request.method == 'POST':
        exam_data = json.load(request.POST.get('examData')) # examData 는 dictionary

        #for i, _exam in enumerate(exam_data):
        ExamData.objects.create(category=exam_data.get('category'), exam_code=int(exam_data.get('exam_code')), target_grade=int(exam_data.get('target_grade')), exam_range=exam_data.get('exam_range'), exam_name=exam_data.get('exam_name'))
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
    notices = list(NoticeData.objects.all().values())
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
    else :
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
