from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('<slug:slug>/', views.category_detail, name='category_detail'),
    path('<slug:slug>/profissionais/', views.professionals_by_category, name='professionals_by_category'),
]

