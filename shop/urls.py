from django.urls import path
from .import views

app_name = 'shop'

urlpatterns = [
    path('', views.all_modules, name='modules'),
    path('<int:module_id>/', views.module_detail, name='module_detail'),
]
