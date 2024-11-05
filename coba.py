import requests

# Replace with your actual API key
API_KEY = 'AIzaSyBm4u5E6WgcIS4E-ES81s6EPa8smPLdtKI'

# Coordinates of the points (latitude,longitude)
point_A = "-6.165456265151834,106.76020926012484"
point_B = "-6.177283555091819,106.76826787671831"
point_C = "-6.179663285810471,106.76107685911676"
point_D = "-6.175299741430307,106.75337053898048"
point_E = "-6.181942351342165,106.7763663594589"

# Function to get distance between two points
def get_distance_and_duration(origin, destination, api_key):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={origin}&destinations={destination}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'OK':
        distance = data['rows'][0]['elements'][0]['distance']['value']  # distance in meters
        duration = data['rows'][0]['elements'][0]['duration']['value']  # duration in seconds
        return distance / 1000, duration / 60  # convert to kilometers
    else:
        return None, None
from itertools import permutations

# Function to calculate total distance and total duration of a path
def calculate_total_distance_and_duration(path):
    total_distance = 0
    total_duration = 0
    for i in range(len(path) - 1):
        distance, duration = get_distance_and_duration(point_E, path[i+1], API_KEY)
        total_distance += distance
        total_duration += duration
    return total_distance, total_duration

# All points except point_E
points = [point_A, point_B, point_C, point_D]

def get_path(points):
    perms = permutations(points)
    min_distance = float('inf')
    efficient_path = []
    for perm in perms:
        perm = [point_E] + list(perm)
        total_distance, total_duration = calculate_total_distance_and_duration(perm)
        if total_distance < min_distance:
            min_distance = total_distance
            efficient_path = perm
    return efficient_path, min_distance, total_distance, total_duration;

efficient_path, min_distance, total_distance, total_duration = get_path(points=points)
print(f"The most efficient path is {efficient_path} with a total distance of {min_distance} km")
print(f"The most efficient path is {efficient_path} with a total distance of {min_distance} km and a total duration of {total_duration} minutes")
# # Print the efficient path
maps = ""
# print("The most efficient path from point E is:")
for i, point in enumerate(efficient_path):
    maps += "/" + point
maps = maps.replace(' ', '')
# # Display in Google Maps
google_maps_url = f"https://www.google.com/maps/dir" + maps

# print(f"Total distance: {total_distance} km")
print(google_maps_url)