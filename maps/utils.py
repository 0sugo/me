import os
import folium
import openrouteservice
coordinates = coordinates = [[-86.781247, 36.163532], [-80.191850, 25.771645]]
client = openrouteservice.Client(key=os.environ["MECH"]) # Specify your personal API key
route = client.directions(coordinates=coordinates,
                          profile='driving-car',
                          format='geojson')

# map
map_directions = folium.Map(location=[33.77, -84.37], zoom_start=5)

# add geojson to map
folium.GeoJson(route, name='route').add_to(map_directions)

# add layer control to map (allows layer to be turned on or off)
folium.LayerControl().add_to(map_directions)

# display map
map=map_directions.save("index.html")

print(route['features'][0]['properties']['segments'][0]['distance']*0.000621371, 'miles')
print(route['features'][0]['properties']['segments'][0]['duration']*0.000277778, 'hours\n')

# distances are in meters
# timings are in seconds
print('directions')
for index, i in enumerate(route['features'][0]['properties']['segments'][0]['steps']):
    print(index+1, i, '\n')