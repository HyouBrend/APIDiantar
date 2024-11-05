import requests
from itertools import permutations
# Replace with your actual API key
API_KEY = 'AIzaSyA2UR3JwGM74DzzW7nfeaFRE-CsO0nQA7Y'

# Coordinates of the points (latitude,longitude)
point_A = "-6.165456265151834,106.76020926012484"
point_B = "-6.177283555091819,106.76826787671831"
point_C = "-6.179663285810471,106.76107685911676"
point_D = "-6.175299741430307,106.75337053898048"
Toko_Permata = "-6.181942351342165,106.7763663594589"

# Cache untuk menyimpan hasil jarak dan durasi
distance_duration_cache = {}

# Function to get distance between two points
def get_distance_and_duration(origin, destination):
    # Cek cache terlebih dahulu
    cache_key = (origin, destination)
    if cache_key in distance_duration_cache:
        return distance_duration_cache[cache_key]
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={origin}&destinations={destination}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'OK' and 'rows' in data and data['rows']:
        elements = data['rows'][0]['elements'][0]
        if 'distance' in elements and 'duration' in elements:
            distance = elements['distance']['value'] / 1000  # Convert to kilometers
            duration = elements['duration']['value'] / 60  # Convert to minutes
            # Simpan hasil ke cache
            distance_duration_cache[cache_key] = (distance, duration)
            return distance, duration
    # Return None, None if distance or duration is not available
    return None, None

# Function to calculate total distance and total duration of a path
def calculate_total_distance_and_duration(path):
    total_distance = 0
    total_duration = 0
    for i in range(len(path) - 1):
        distance, duration = get_distance_and_duration(path[i], path[i+1])
        total_distance += distance
        total_duration += duration
    return total_distance, total_duration

def get_path(points):
    start_point = Toko_Permata  # Titik awal
    efficient_path = [start_point]
    min_distance = 0
    min_duration = 0

    unvisited = points.copy()

    current_point = start_point
    while unvisited:
        nearest_point = None
        nearest_distance = float('inf')
        nearest_duration = 0  # Inisialisasi nearest_duration
        for point in unvisited:
            distance, duration = get_distance_and_duration(current_point, point)
            # Tambahkan pengecekan jika distance tidak None sebelum membandingkan
            if distance is not None and distance < nearest_distance:
                nearest_distance = distance
                nearest_point = point
                nearest_duration = duration

        # Pastikan nearest_point tidak None sebelum menambahkan ke path dan mengupdate jarak & durasi
        if nearest_point is not None:
            min_distance += nearest_distance
            min_duration += nearest_duration
            efficient_path.append(nearest_point)
            unvisited.remove(nearest_point)
            current_point = nearest_point
        else:
            # Handle kasus dimana tidak ada nearest_point yang valid (misal karena semua distance adalah None)
            break  # Keluar dari loop jika tidak ada point yang bisa dikunjungi selanjutnya

    return efficient_path, min_distance, min_duration

# All points except point_E
# points = [point_A, point_B, point_C, point_D]
# def get_path(points):
#     perms = permutations(points)
#     min_distance = float('inf')
#     efficient_path = []
#     min_duration = 0  # Inisialisasi min_duration

#     for perm in perms:
#         perm = ['point_E'] + list(perm)  # Asumsikan 'point_E' adalah titik awal
#         total_distance, total_duration = calculate_total_distance_and_duration(perm)
#         if total_distance < min_distance:
#             min_distance = total_distance
#             efficient_path = perm
#             min_duration = total_duration  # Update min_duration

#     return efficient_path, min_distance, min_duration

# efficient_path, min_distance, total_distance, total_duration = get_path(points=points)
# print(f"The most efficient path is {efficient_path} with a total distance of {min_distance} km")
# print(f"The most efficient path is {efficient_path} with a total distance of {min_distance} km and a total duration of {total_duration} minutes")
# # Print the efficient path
# maps = ""
# print("The most efficient path from point E is:")
# for i, point in enumerate(efficient_path):
#     maps += "/" + point
# maps = maps.replace(' ', '')
# # Display in Google Maps
# google_maps_url = f"https://www.google.com/maps/dir" + maps

# print(f"Total distance: {total_distance} km")
# print(google_maps_url)