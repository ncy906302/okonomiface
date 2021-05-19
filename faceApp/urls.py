from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('reset/', views.RemoveAllPhoto, name='reset'),
    path('result/', views.result, name='result'),
    path('ajax/', views.ajax, name='ajax'),
]