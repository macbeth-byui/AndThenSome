from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_app, name='login_app'),
    path('home', views.home, name='home'),
    path('category/<int:c_id>', views.category, name="category"),
    path('category', views.category, name="category"),
    path('transact/<int:t_id>', views.transact, name="transact"),    
    path('transact', views.transact, name="transact"),
    path('month', views.month, name="month"),
]