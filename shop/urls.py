from django.urls import path
from .import views

app_name = 'shop'

urlpatterns = [
    path('', views.all_modules, name='modules'),
    path('<int:module_id>/', views.module_detail, name='module_detail'),
    path('add/<int:module_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:module_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
]
