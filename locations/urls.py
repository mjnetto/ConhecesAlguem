from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('api/cities/<int:province_id>/', views.get_cities, name='get_cities'),
    path('api/neighborhoods/<int:city_id>/', views.get_neighborhoods, name='get_neighborhoods'),
]


