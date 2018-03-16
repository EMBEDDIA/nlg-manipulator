$(document).ready(function (){
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            $('#geo-icon').addClass('hide');
            $('#geo-wait').removeClass('hide');
            lat = position.coords.latitude;
            lon = position.coords.longitude;
            url = 'https://api.digitransit.fi/geocoding/v1/reverse?point.lat=' + lat + '&point.lon=' + lon + '&size=1'
            $.getJSON(url, function(response) {
                city = response.features[0].properties.localadmin;
                btn = $('#geolocate')
                btn.attr('href', 'city?city=' + city)
                $('#geo-wait').addClass('hide');
                btn.removeClass('disabled');
                $('#geo-icon').removeClass('hide');
            });
        });
    }
});