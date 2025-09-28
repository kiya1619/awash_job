from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('hr_dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('post_job/', views.post_job, name='post_job'),
    path('all_jobs/', views.all_jobs, name='all_jobs'),
    path('my_applications/', views.my_applications, name='my_applications'),
    path('applicants/', views.applicants_list, name='applicants'),
    path('view_detail/<int:id>', views.view_detail, name='view_detail'),
    path('delete_job/<int:id>', views.delete_job, name='delete_job'),
    path('edit_job/<int:id>', views.edit_job, name='edit_job'),
    path('view_applicants_per_job/<int:id>', views.view_applicants_per_job, name='view_applicants_per_job'),
    path('apply/<int:id>', views.apply, name='apply'),
    path("get-employee/", views.get_employee, name="get_employee"),  # new

]