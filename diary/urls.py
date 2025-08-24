from django.urls import path
from .import views

app_name = 'diary'

urlpatterns = [
    path('', views.diary_home, name='diary_home'),
    path('add/', views.add_entry, name='add_entry'),
    path('entry/<int:entry_id>/', views.view_entry, name='view_entry'),
    path('entry/<int:entry_id>/edit/', views.edit_entry, name='edit_entry'),
    path(
        'entry/<int:entry_id>/delete/',
        views.delete_entry, name='delete_entry'),
]
