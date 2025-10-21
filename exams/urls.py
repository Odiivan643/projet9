# exams/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Pages protégées - Examens
    path('exams/', views.exam_list, name='exam_list'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exam/<int:exam_id>/start/', views.start_exam, name='start_exam'),
    path('exam/<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('result/<int:session_id>/', views.exam_result, name='exam_result'),
    
    # Dashboard et résultats
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-results/', views.my_results, name='my_results'),
    
    # Démonstration middlewares
    path('middleware-demo/', views.middleware_demo, name='middleware_demo'),
]