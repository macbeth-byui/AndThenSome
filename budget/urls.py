from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<int:c_id>', views.category, name="category"),
    path('category', views.category, name="category"),
    path('transact/<int:t_id>', views.transact, name="transact"),    
    path('transact', views.transact, name="transact"),
    path('month', views.month, name="month"),
    path('transact_history', views.transact_history, name="transact_history")
]