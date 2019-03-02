from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('showMeal/', views.show_meal, name='show_meal'),
    path('showMeal/comment/<int:id>', views.show_meal_comment, name='show_meal_comment'),
    path('likeComment/', views.like_comment, name='like_comment'),
    path('addComment/', views.add_comment, name='add_comment'),
]
