from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='root'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path('home/', views.home, name='home'),
    path('all-donor/', views.new_donor, name='all_donor'),
    path('new-donor/', views.new_donor, name='new_donor'),
    path('update-donor/', views.update_donor, name='update_donor'),
    path('delete-donor/', views.delete_donor, name='delete_donor'),
    path('call-donor/<int:donor_id>/', views.call_donor_action, name='call_donor_action'),

    path('stock/', views.stock, name='stock'),
    path('delete-donor-popup/', views.delete_donor_popup, name='delete_donor_popup'),
]