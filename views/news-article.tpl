% rebase('base.tpl', title='Vaalibotti Valtteri - Random', **locals())

<div class="section">
  <div class="container">
    <br>
    <br>
    <h1 class="header center blue-text">{{header}}</h1>
    <div class="row flow-text">
      <div id="map-card" class="card">
        <div class="card-content">
          <span class="card-title">{{where}}</span>
            <div style="width:100%; height:400px" id="map"></div>
            <script>
            function constructor(location_lat, location_lng, reference_lat, reference_lng) {
                return function() {
                    // Create map
                    var mapOptions= {
                        center: new google.maps.LatLng(location_lat, location_lng),
                        zoom:6,
                    };
                    var map = new google.maps.Map(document.getElementById('map'), mapOptions);

                    // Add markers
                    var location_marker = new google.maps.Marker({
                        position: mapOptions.center
                    });
                    location_marker.setMap(map);

                    // Set zoom
                    var bounds = new google.maps.LatLngBounds()
                    if (reference_lat == null || reference_lng == null) {
                        bounds.extend(location_marker.position)
                        bounds.extend(new google.maps.LatLng(70.4703, 19.0707))
                        bounds.extend(new google.maps.LatLng(59.4066, 33.3968))
                    } else {
                        bounds.extend(new google.maps.LatLng(location_lat + 0.075, location_lng +0.075))
                        bounds.extend(new google.maps.LatLng(location_lat - 0.075, location_lng - 0.075))
                        bounds.extend(new google.maps.LatLng(reference_lat + 0.075, reference_lng + 0.075))
                        bounds.extend(new google.maps.LatLng(reference_lat - 0.075, reference_lng - 0.075))
                    }
                    map.fitBounds(bounds);
                }
            }
            locator_map_data = {{!locator_map}}
            createMap = constructor(
                locator_map_data.location_lat, 
                locator_map_data.location_lng, 
                locator_map_data.reference_lat, 
                locator_map_data.reference_lng
            )
            </script>
            <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyD7A_wqRiWrVXFAxqyzUY09oDNTxMJl9ZA&callback=createMap"></script>
        </div>
      </div>
      
      {{!body}}
      
      <div id="graph-card" class="card">
        <div class="card-content">
            <canvas id="chart" width="500" height="500"></canvas>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.22.1/moment.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.min.js"></script>
            <script>
                function generate_chart(labels, datasets) {
                    new Chart(document.getElementById('chart'), {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: datasets
                        },
                        options: {
                            title: {
                                display: true,
                                text: 'Rikoksia tuhatta asukasta kohden'
                            }
                        }
                    });
                }
                graph_data = {{!graph}}
                generate_chart(graph_data.labels, graph_data.datasets);
            </script>
        </div>
      </div>
    </div>
  </div>
</div>
