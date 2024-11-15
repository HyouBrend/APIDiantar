from jinja2 import Template

# Data titik koordinat
points = {
    "A": {"lat": -6.233889, "lng": 106.772944},  # Jakarta
    "B": {"lat": -6.181556, "lng": 106.757694},  # Bandung
    "C": {"lat": -6.150222, "lng": 106.791111},  # Surabaya
}

# API Key Google Maps
API_KEY = 'API_KEY'

# Template HTML
html_template = """
<!DOCTYPE html>
<html>
  <head>
    <title>Google Maps dengan Marker dan Polyline</title>
    <script src="https://maps.googleapis.com/maps/api/js?key={{ api_key }}"></script>
    <script>
      function initMap() {
        var mapOptions = {
          zoom: 7,
          center: {lat: -6.233889, lng: 106.772944}
        };
        var map = new google.maps.Map(document.getElementById('map'), mapOptions);

        // Marker
        var markerA = new google.maps.Marker({position: {lat: {{ points.A.lat }}, lng: {{ points.A.lng }}}, map: map, title: 'Point A'});
        var markerB = new google.maps.Marker({position: {lat: {{ points.B.lat }}, lng: {{ points.B.lng }}}, map: map, title: 'Point B'});
        var markerC = new google.maps.Marker({position: {lat: {{ points.C.lat }}, lng: {{ points.C.lng }}}, map: map, title: 'Point C'});

        // Polyline
        var flightPlanCoordinates = [
          {lat: {{ points.A.lat }}, lng: {{ points.A.lng }}},
          {lat: {{ points.B.lat }}, lng: {{ points.B.lng }}},
          {lat: {{ points.C.lat }}, lng: {{ points.C.lng }}}
        ];
        var flightPath = new google.maps.Polyline({
          path: flightPlanCoordinates,
          geodesic: true,
          strokeColor: '#FF0000',
          strokeOpacity: 1.0,
          strokeWeight: 2
        });

        flightPath.setMap(map);
      }
    </script>
  </head>
  <body onload="initMap()">
    <div id="map" style="height: 500px; width: 100%;"></div>
  </body>
</html>
"""

# Buat template dengan Jinja2
template = Template(html_template)

# Render template dengan data
rendered_html = template.render(api_key=API_KEY, points=points)

# Simpan file HTML
with open('map_with_markers_and_polyline.html', 'w') as file:
    file.write(rendered_html)

print("File HTML berhasil dibuat: map_with_markers_and_polyline.html")
