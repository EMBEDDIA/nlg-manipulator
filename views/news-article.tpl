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
      <style>
      .highcharts-container, svg:not(:root) {
          overflow: visible !important;
      }
      </style>
      <div id="graph-card" class="card" >
        <div id="visualization" class="card-content"></div></div>
            <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"       type="text/javascript"></script>
            <script src="https://code.highcharts.com/highcharts.js"></script>
            <script src="https://code.highcharts.com/modules/exporting.js"></script>
            <script src="https://code.highcharts.com/modules/export-data.js"></script>
            <script>
                  //months enum
                  const MonthsEnumEn = {"01":"January", "02":"February", "03":"March", "04":"April", "05":"May", "06":"June", "07":"July", "08":"August", "09":"September", "10":"October", "11":"November", "12":"December"};
                  const MonthsEnumFi = {"01":"tammikuu", "02":"helmikuu", "03":"maaliskuu", "04":"huhtikuu", "05":"toukokuu", "06":"kesäkuu", "07":"heinäkuu", "08":"elokuu", "09":"syyskuu", "10":"lokakuu", "11":"marraskuu", "12":"joulukuu"};
                  graph_data = {{!graph}}
                  var language = '{{!language}}';
                  var yAxisTitle = '';
                  var tooltipTitle = '';
                  var title2 = '';
                  var title3 = '';
                  switch(language) {
                    case "en":
                        yAxisTitle = 'per 1000 inhabitant';
                        tooltipTitle = 'compared to previous years';
                        title2 = 'average of other municipalities';
                        title3 = 'average of similar municipalities';

                        break;
                    case "fi":
                        yAxisTitle = 'tuhatta asukasta kohden';
                        tooltipTitle = 'edellisiin vuosiin verrattuna';
                        title2 = 'Muiden kuntien keskiarvo ';
                        title3 = 'Samanlaisten kuntien keskiarvo ';
                        break;
                  }
                  $(function () {
                    var chart = new Highcharts.Chart({
                        chart: {
                        type: 'area',
                        spacingBottom: 40,
                				renderTo:'visualization'
                      },
                      title: {
                        text: graph_data.title,
                      },
                      subtitle: {
                        text: '',
                        floating: true,
                        align: 'right',
                        verticalAlign: 'bottom',
                        y: 15
                      },
                      legend: {
                        layout: 'horizontal',
                        align: 'left',
                        verticalAlign: 'top',
                        x: 150,
                        y: 20,
                        floating: true,
                        borderWidth: 2,
                        backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
                      },
                      xAxis: {
                        categories: graph_data.labels//['1M2017', '2M2017', '3M2017', '4M2017', '5M2017', '6M2017', '7M2017', '8M2017']
                      },
                      yAxis: {
                        title: {
                          text: yAxisTitle
                        },
                        labels: {
                          formatter: function () {
                            return this.value;
                          }
                        }
                      },
                      tooltip: {
                          borderColor: '#000000',
                          borderWidth: 2,
                          useHTML: true,
                          formatter: function() {
                              var currentSelection = this.x;
                              var currentSeries = this.series.name;
                              var currentDataSet = 0
                              switch(currentSeries) {
                                  case graph_data.datasets[0].label:
                                      currentDataSet = 0;
                                      break;
                                  case graph_data.datasets[1].label:
                                      currentDataSet = 1;
                                      break;
                              }
                              month = currentSelection.slice(-2);

                              switch(language) {
                                case "en":
                                    SelectedMonth = MonthsEnumEn[month];
                                    break;
                                case "fi":
                                    SelectedMonth = MonthsEnumFi[month];
                                    break;
                              }

                              setTimeout( function() {
                                  var TooltipChart = new Highcharts.Chart({
                                      chart: {
                                        type: 'column',
                                        height:250,
                                        width:250,
                                        renderTo:'hc-tooltip'
                                      },
                                      title: {
                                        text: tooltipTitle
                                      },
                                      subtitle: {
                                        text: ''
                                      },
                                      xAxis: {
                                        categories: graph_data.datasets[currentDataSet].subgraph_labels,
                                        crosshair: true
                                      },
                                      yAxis: {
                                        min: 0,
                                        title: {
                                          text: yAxisTitle
                                        }
                                      },
                                      plotOptions: {
                                        column: {
                                          pointPadding: 0.2,
                                          borderWidth: 0
                                        }
                                      },
                                      series: [{
                                        name: SelectedMonth,
                                        data: graph_data.datasets[currentDataSet].subgraph_data[month.toString()]

                                      }]
                                    });
                                  }, 10)

                              return '<div id="hc-tooltip" width="300px" height="200px"></div>';
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
                      data: graph_data.datasets[0].data
                    },{
                      name: title2, //graph_data.datasets[1].label,
                      data: graph_data.datasets[1].data
                    },{
                      name: title3, //graph_data.datasets[2].label,
                      data: graph_data.datasets[2].data
                    }]
                    });
                });
            </script>
        </div>
      </div>
    </div>
  </div>
</div>
