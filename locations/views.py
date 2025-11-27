from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Province, City, Neighborhood
import json


def get_cities(request, province_id):
    """API endpoint to get cities by province"""
    try:
        province = get_object_or_404(Province, id=province_id)
        cities = City.objects.filter(province=province).order_by('name')
        
        cities_data = [{
            'id': city.id,
            'name': city.name
        } for city in cities]
        
        return JsonResponse({
            'success': True,
            'cities': cities_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def get_neighborhoods(request, city_id):
    """API endpoint to get neighborhoods by city"""
    try:
        city = get_object_or_404(City, id=city_id)
        neighborhoods = Neighborhood.objects.filter(city=city).order_by('name')
        
        neighborhoods_data = [{
            'id': neighborhood.id,
            'name': neighborhood.name
        } for neighborhood in neighborhoods]
        
        return JsonResponse({
            'success': True,
            'neighborhoods': neighborhoods_data,
            'is_luanda': city.name == 'Luanda'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
