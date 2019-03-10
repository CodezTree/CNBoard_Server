from django.urls import path

from . import views

urlpatterns = [
    path('notices/upload/', views.upload_notice, name='upload_notice'),
    path('notices/', views.notice_list, name='notice_list'),
    path('alertNotices/', views.alert_notice_list, name='alert_notice_list'),
    path('alertNotices/delete/<int:pk>', views.delete_alert_notice, name='delete_alert_notice'),
    path('notices/delete/<int:pk>/', views.delete_notice, name='delete_notice'),
    path('class/notices/', views.NoticeListView.as_view(), name='class_notice_list'),
    path('class/notices/upload', views.UploadNoticeView.as_view(), name='class_upload_notice'),
    path('showNotice/', views.show_notice_android, name='show_notice'),
    path('showFilteredNotice/', views.show_filtered_notice, name='show_filtered_notice'),
    path('showAlertNotice/', views.show_alert_notice, name='show_alert_notice'),
    path('deleteAlertNotice/', views.delete_alert_notice_android, name='delete_alert_notice_android'),
    path('uploadAlertNotice/', views.upload_alert_notice, name='upload_alert_notice'),
    path('applyCnboard/', views.apply_cnboard, name='apply_cnboard'),

    path('administrateTools/', views.administrate_tools, name='administrate_tools'),
    path('administrateTools/confirmMealUpdateChange', views.confirm_meal_update_change, name='confirm_meal_update_change'),
    path('administrateTools/updateAppVersion', views.update_app_version, name='update_app_version'),
    path('showAppVersion/', views.show_app_version, name='show_app_version'),

    path('files/', views.file_list, name='file_list'),
    path('files/upload', views.upload_file, name='upload_file'),
    path('files/delete/<int:pk>/', views.delete_file, name='delete_file'),

    path('exams/addExam/', views.add_exam_data, name='add_exam_data'),
    path('showExam/', views.show_exam_data, name='show_exam_data'),
    path('exams/list/', views.exam_data_list, name='exam_data_list'),
    path('exams/list/<int:pk>', views.delete_exam_data, name='delete_exam_data'),
    path('exams/add/', views.add_exam_data, name='add_exam_data'),
    path('exams/serviceAvailCheck/', views.exam_service_avail_check, name='service_avail_check'),
    path('exams/serviceStateChange/', views.exam_service_state_change, name='exam_service_state_change'),
    path('exams/add/Android/', views.add_exam_data_android, name='add_exam_data_android'),

    path('home/', views.Home.as_view(), name='home'),
    path('logout/', views.logout, name='logout'),
    path('', views.admin_login, name='admin_login'),
]
