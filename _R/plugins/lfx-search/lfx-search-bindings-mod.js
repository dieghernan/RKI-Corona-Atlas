/* global $, LeafletWidget, L, Shiny, HTMLWidgets, google */

// helper function to conver JS event to Shiny Event
function eventToShiny(e) {
  var shinyEvent = {};
  shinyEvent.latlng = {};
  shinyEvent.latlng.lat = e.latlng.lat;
  shinyEvent.latlng.lng = e.latlng.lng;
  if(!$.isEmptyObject(e.title)) {
    shinyEvent.title = e.title;
  }
  if(!$.isEmptyObject(e.layer)) {
    shinyEvent.layer = e.layer.toGeoJSON();
  }
  return shinyEvent;
}

LeafletWidget.methods.addSearchOSM = function(options) {

  (function(){
    var map = this;

    if(map.searchControlOSM) {
      map.searchControlOSM.removeFrom(map);
      delete map.searchControlOSM;
    }

    options = options || {};
    options.textPlaceholder = 'Search using OSM Geocoder';
    options.url = 'https://nominatim.openstreetmap.org/search?format=json&q={s}';
    options.jsonpParam = 'json_callback';
    options.propertyName = 'display_name';
    options.propertyLoc = ['lat','lon'];

    // https://github.com/stefanocudini/leaflet-search/issues/129
    options.marker = L.circleMarker([0,0],{radius:30});

    if(options.moveToLocation) {
      options.moveToLocation = function(latlng, title, map) {
        var zoom = 6;
        map.setView(latlng, zoom);
      };
    }

    map.searchControlOSM = new L.Control.Search(options);
    map.searchControlOSM.addTo(map);

    map.searchControlOSM.on('search:locationfound', function(e){
      // Shiny stuff
      if (!HTMLWidgets.shinyMode) return;
      Shiny.onInputChange(map.id+'_search_location_found', eventToShiny(e));
    });

  }).call(this);
};
