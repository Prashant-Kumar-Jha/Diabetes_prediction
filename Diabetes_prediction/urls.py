from django.contrib import admin
from django.urls import path
from main import views

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
]

