from django.contrib import admin
from django.urls import path
from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('history/', views.history, name='history'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # ✅ Updated path to match history.html
    path('submit-feedback/<int:result_id>/', views.submit_feedback, name='submit_feedback'),
    path('admin-portal/', views.admin_portal, name='admin_portal'),
    path('adminportal/users/', views.admin_user_management, name='admin_user_management'),
    path('adminportal/delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('history/download_excel/', views.download_excel, name='download_excel'),
    path('history/download_pdf/', views.download_pdf, name='download_pdf'),
    path('delete/<int:record_id>/', views.delete_record, name='delete_record'),
    path('bmi/', views.bmi_calculator, name='bmi_calculator'),
]




