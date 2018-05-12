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
            <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"       type="text/javascript"></script>
            <script src="https://code.highcharts.com/highcharts.js"></script>
            <script src="https://code.highcharts.com/modules/exporting.js"></script>
            <script src="https://code.highcharts.com/modules/export-data.js"></script>
            <script>
                  graph_data = {{!graph}}
                  $(function () {
                    var chart = new Highcharts.Chart({
                        chart: {
                        type: 'area',
                        spacingBottom: 40,
                				renderTo:'visualization'
                      },
                      title: {
                        text: 'Rikoksia tuhatta asukasta kohden'
                      },
                      subtitle: {
                        text: 'Rikoksia tuhatta asukasta kohden',
                        floating: true,
                        align: 'right',
                        verticalAlign: 'bottom',
                        y: 15
                      },
                      legend: {
                        layout: 'vertical',
                        align: 'left',
                        verticalAlign: 'top',
                        x: 150,
                        y: 100,
                        floating: true,
                        borderWidth: 2,
                        backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
                      },
                      xAxis: {
                        categories: graph_data.labels//['1M2017', '2M2017', '3M2017', '4M2017', '5M2017', '6M2017', '7M2017', '8M2017']
                      },
                      yAxis: {
                        title: {
                          text: 'Crimes (per 1000 inhabitant)'
                        },
                        labels: {
                          formatter: function () {
                            return this.value;
                          }
                        }
                      },
                        tooltip: {
                            useHTML: true,
                            formatter: function() {
                                setTimeout( function() {
                                    var TooltipChart = new Highcharts.Chart({
                                        chart: {
                                          type: 'column',
                                          height:250,
                                          width:250,
                                  				renderTo:'hc-tooltip'
                                        },
                                        title: {
                                          text: 'crime in month compared to prev yrs'
                                        },
                                        subtitle: {
                                          text: 'subtitle'
                                        },
                                        xAxis: {
                                          categories: [
                                            '2014',
                                            '2015',
                                            '2016',
                                            '2017',
                                            '2018',
                                            '2019 prediction?'
                                          ],
                                          crosshair: true
                                        },
                                        yAxis: {
                                          min: 0,
                                          title: {
                                            text: 'crimes (per 1000 inhabitants)'
                                          }
                                        },
                                        plotOptions: {
                                          column: {
                                            pointPadding: 0.2,
                                            borderWidth: 0
                                          }
                                        },
                                        series: [{
                                          name: 'for month ()',
                                          data: [49, 71, 106, 129, 144, 176]

                                        }]
                                      });
                                    }, 10)

                                return '<div id="hc-tooltip" width="200px" height="200px"></div>';
                            }
                        },
                       plotOptions: {
                      area: {
                        fillOpacity: 0,
                        connectNulls: true,
                      }
                    },
                    credits: {
                      enabled: true
                    },
                    //in case there are missing values we can put null
                    //to add another series add , then provide name and data for the new one
                    series: [{
                      name: graph_data.datasets[0].label,
                      //color: '#003399',
                      data: graph_data.datasets[0].data
                    },{
                      name: graph_data.datasets[1].label,
                      //color: '#3366BB',
                      data: graph_data.datasets[1].data
                    }]
                    });
                });

                //generate_chart(graph_data.labels, graph_data.datasets);
                console.log(graph_data.labels);
                console.log(graph_data.datasets);
            </script>
            <div id="visualization" style="min-width: 310px; height: 600px; margin: 0 auto" class="card"></div>
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
