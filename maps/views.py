import os

from django.http import JsonResponse
from django.shortcuts import render
import openrouteservice
# Create your views here
#
.
def directions(request):
    coordinates = coordinates = [[-86.781247, 36.163532], [-80.191850, 25.771645]]
    client = openrouteservice.Client(key=os.environ["MECH"])  # Specify your personal API key
    route = client.directions(coordinates=coordinates,
                              profile='driving-car',
                              format='geojson')
    return JsonResponse({"route":route})