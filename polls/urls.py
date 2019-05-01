from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('detail/<int:id>/', views.detail, name='poll'),
    path('create/', views.create, name='create'),
    path('update/<int:id>/', views.update, name='update'),
    path('delete/<int:question_id>/', views.delete_question, name='delete_question'),
    path('<int:question_id>/add-choice/', views.add_choice, name='add_choice'),
    path('login/', views.my_login, name='login'),
    path('logout/', views.my_logout, name='logout'),
    path('api/<int:question_id>/add-choice/', views.add_choice_api, name='add_choice_api'),
]