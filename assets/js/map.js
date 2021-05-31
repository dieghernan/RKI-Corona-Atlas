var carto_voyager = L.tileLayer.provider('CartoDB.Voyager');
var stamen_terrain = L.tileLayer.provider('Stamen.TerrainBackground');

var map = new L.Map('leaflet', {
    center: [51.705533, 11.8124408],
    maxBounds: [[-90, -180], [90, 180]],
    zoom: 4,
    minZoom: 1,
    layers: [carto_voyager]
});

var eg_url = "https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units";
L.tileLayer('', {attribution: '&copy; <a href="'+eg_url+'">EuroGeographics</a>' +
        ' for the administrative boundaries'}).addTo(map);

var baseMaps = {
    "Carto Voyager": carto_voyager,
    "Stamen Terrain": stamen_terrain
};

L.easyButton('fa-globe', function(btn, map){
    map.setView([ 51.705533,11.8124408],4);}).addTo(map);

var levels = [
    L.layerGroup(),
    L.layerGroup(),
    L.layerGroup(),
    L.layerGroup(),
    L.layerGroup()
];
var risk_labels = locale["risk_labels"];
var risk_colors = ["#00FF00", "red", "chocolate", "orange", "yellow"];

// loading GeoJSON file
$.getJSON("https://corona-atlas.de/assets/geo/country_shapes.geojson",function(data){
// L.geoJson function is used to parse geojson file and load on to map
    let more_info = locale["more_info"];
    L.geoJson(data,
            {color: "#44444",
            weight: 0.5,
            smoothFactor: .1,
            opacity: 1,
            fillOpacity: 0.5,
            highlightOptions: {
                color: "white",
                weight: 1,
                bringToFront: true,
            },
            onEachFeature: function (feature, layer) {
                let iso3_code = feature.properties.ISO3_CODE;
                let risk_code = risk[iso3_code];
                let risk_level = risk_labels[risk_code];
                if (iso3_code === "DEU") {
                    layer.setStyle({fillColor: "blue"});
                    layer.addTo(map);
                } else{
                    levels[risk_code].addLayer(layer);
                    layer.setStyle({fillColor: risk_colors[risk_code]});
                }
                let info_country = info_rki[feature.properties.ISO3_CODE];
                let country_name = info_country['name'];
                let country_info = info_country["info"];
                let msg = '<strong>'+country_name+'</strong></br>'+risk_level;
                if (country_info.length > 0)
                    msg += '</br></br><strong>'+more_info+'</strong></br>'+country_info;
                layer.bindPopup(msg);
                layer.on("mouseover", function(ev) {
                    ev.target.setStyle({
                        color: "white",
                        weight: 1,
                        bringToFront: true,}); // ev is an event object (MouseEvent in this case)
                });
                layer.on("mouseout", function(ev) {
                    ev.target.setStyle({
                        color: "#44444",
                        weight: 0.5,
                        bringToFront: false,}); // ev is an event object (MouseEvent in this case)
                });
            }
            });
    // .addTo(map);
});
levels.forEach(lv => lv.addTo(map));
var risk_order = [1, 2, 3, 4, 0];

var risk_layers = {};
for (var i = 0; i < risk_order.length; i++){
    var j = risk_order[i];
    risk_layers[risk_labels[j]] = levels[j];
}
L.control.layers(baseMaps, risk_layers).addTo(map);

var legend = L.control({position: 'bottomleft'});
legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend');

    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < risk_order.length; i++) {
        var j = risk_order[i];
        div.innerHTML +=
            '<i style="background:' + risk_colors[j] + '; opacity:0.5;"></i> ' +
            risk_labels[j] + '<br>';
    }

    return div;
};
legend.addTo(map);
$('.leaflet-control-layers-overlays').prepend('<strong>'+locale["risk_level"]+'</strong>');
