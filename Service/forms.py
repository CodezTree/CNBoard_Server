from django import forms

from .models import NoticeData, FileData, ExamData, AlertNoticeData


class NoticeForm(forms.ModelForm):
    class Meta:
        model = NoticeData
        fields = ('notice_title', 'target_grade', 'notice_kind', 'notice_image')


class FileForm(forms.ModelForm):
    class Meta:
        model = FileData
        fields = ('file_title', 'file_description', 'file_document')


class LoginForm(forms.Form):
    ID = forms.CharField(max_length=16)
    Pass = forms.CharField(max_length=20, widget=forms.PasswordInput())


class ExamForm(forms.ModelForm):
    class Meta:
        model = ExamData
        fields = ('category', 'exam_code', 'target_grade', 'exam_name', 'exam_range')


class AlertNoticeForm(forms.ModelForm):
    class Meta:
        model = AlertNoticeData
        fields = ('notice_title', 'notice_content', 'target_grade', 'notice_due_date', 'notice_image', 'notice_file')