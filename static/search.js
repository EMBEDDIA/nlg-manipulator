$(document).ready(function() {
    function rec_add(geo_autocomplete, data, str) {
        str = str + " > " + data.name;
        geo_autocomplete.push({
            text: str,
            value: data.type + data.id,
        });
        for (var id in data.children) {
            rec_add(geo_autocomplete, data.children[id], str);
        }
    }

    $.getJSON('api/geodata', function(rawdata) {
        data = rawdata.data;
        geo_autocomplete = [{text:"Suomi", value:"Cfi"}];
        for (var id in data["fi"].children) {
            rec_add(geo_autocomplete, data["fi"].children[id], "Suomi");
        }
        console.log(geo_autocomplete);
        $('#location-search').selectize({
            options: geo_autocomplete,
            items: ['Cfi'],
            closeAfterSelect: true,
        });
    })
});
        