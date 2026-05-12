from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.timeline, name='timeline'),
    path('add/', views.add_entry, name='add_entry'),
    path('ack/<int:entry_id>/', views.toggle_acknowledge, name='toggle_acknowledge'),
    path('edit/<int:entry_id>/', views.edit_entry, name='edit_entry'),
    path('delete/<int:entry_id>/', views.delete_entry, name='delete_entry'),
    path('entry/<int:entry_id>/', views.get_entry, name='get_entry'),
    path('milestones/', views.milestones_list, name='milestones_list'),
]
