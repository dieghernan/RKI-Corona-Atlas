---
title: Internationale COVID-19 Risikogebiete
subtitle: ausgewiesen durch das deutsche Auswärtige Amt, BMG und BMI
permalink: /
always_allow_html: yes
output: 
  md_document:
    preserve_yaml: true
---

<!-- Modify _R/index.Rmd file instead -->
<p class="text-right font-weight-bold">
Stand: 24.04.2021
</p>

Risikokarte
-----------

Die folgende interaktive Weltkarte präsentiert die aktuelle
Risikoeinstufung aller Staaten der Welt durch das deutsche Auswärtige
Amt, das Bundesministerium für Gesundheit und das Bundesministerium des
Innern, für Bau und Heimat.

Durch das Anklicken eines beliebigen Landes erfolgt die Anzeige aller
zutreffenden Informationen und ggfs. regionaler Ausnahmen.

<div id="htmlwidget-ebfc517903f14a58203f" style="width:100%;height:75vh;" class="leaflet html-widget"></div>
<script type="application/json" data-for="htmlwidget-ebfc517903f14a58203f">{"x":{"options":{"minZoom":0.5,"crs":{"crsClass":"L.CRS.EPSG3857","code":null,"proj4def":null,"projectedBounds":null,"options":{}}},"calls":[{"method":"setMaxBounds","args":[-90,-180,90,180]},{"method":"addProviderTiles","args":["CartoDB.Voyager",null,"Carto Voyager",{"errorTileUrl":"","noWrap":false,"detectRetina":false}]},{"method":"addProviderTiles","args":["Stamen.TerrainBackground",null,"Stamen Terrain",{"errorTileUrl":"","noWrap":false,"detectRetina":false}]},{"method":"addTiles","args":["",null,null,{"minZoom":0,"maxZoom":18,"tileSize":256,"subdomains":"abc","errorTileUrl":"","tms":false,"noWrap":false,"zoomOffset":0,"zoomReverse":false,"opacity":1,"zIndex":1,"detectRetina":false,"attribution":"&copy; <a href=\"https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units\">EuroGeographics<\/a> for the administrative boundaries"}]},{"method":"addPolygons","args":[[],null,null,{"interactive":true,"className":"","stroke":true,"color":"#44444","weight":0.5,"opacity":1,"fill":true,"fillColor":"blue","fillOpacity":0.5,"smoothFactor":0.1,"noClip":false},[],null,null,{"interactive":false,"permanent":false,"direction":"auto","opacity":1,"offset":[0,0],"textsize":"10px","textOnly":false,"className":"","sticky":true},{"color":"white","weight":1,"bringToFront":true}]},{"method":"addPolygons","args":[[],null,"Kein Risikogebiet",{"interactive":true,"className":"","stroke":true,"color":"#44444","weight":0.5,"opacity":1,"fill":true,"fillColor":"green","fillOpacity":0.5,"smoothFactor":0.1,"noClip":false},[],null,null,{"interactive":false,"permanent":false,"direction":"auto","opacity":1,"offset":[0,0],"textsize":"10px","textOnly":false,"className":"","sticky":true},{"color":"white","weight":1,"bringToFront":true}]},{"method":"addPolygons","args":[[],null,"Virusvarianten-Gebiet",{"interactive":true,"className":"","stroke":true,"color":"#44444","weight":0.5,"opacity":1,"fill":true,"fillColor":"red","fillOpacity":0.5,"smoothFactor":0.1,"noClip":false},[],null,null,{"interactive":false,"permanent":false,"direction":"auto","opacity":1,"offset":[0,0],"textsize":"10px","textOnly":false,"className":"","sticky":true},{"color":"white","weight":1,"bringToFront":true}]},{"method":"addPolygons","args":[[],null,"Hochinzidenzgebiet",{"interactive":true,"className":"","stroke":true,"color":"#44444","weight":0.5,"opacity":1,"fill":true,"fillColor":"orange","fillOpacity":0.5,"smoothFactor":0.1,"noClip":false},[],null,null,{"interactive":false,"permanent":false,"direction":"auto","opacity":1,"offset":[0,0],"textsize":"10px","textOnly":false,"className":"","sticky":true},{"color":"white","weight":1,"bringToFront":true}]},{"method":"addPolygons","args":[[],null,"Risikogebiet",{"interactive":true,"className":"","stroke":true,"color":"#44444","weight":0.5,"opacity":1,"fill":true,"fillColor":"yellow","fillOpacity":0.5,"smoothFactor":0.1,"noClip":false},[],null,null,{"interactive":false,"permanent":false,"direction":"auto","opacity":1,"offset":[0,0],"textsize":"10px","textOnly":false,"className":"","sticky":true},{"color":"white","weight":1,"bringToFront":true}]},{"method":"addPolygons","args":[[],null,"Kein Risikogebiet mehr - seit weniger als 10 Tagen",{"interactive":true,"className":"","stroke":true,"color":"#44444","weight":0.5,"opacity":1,"fill":true,"fillColor":"#00FF00","fillOpacity":0.5,"smoothFactor":0.1,"noClip":false},[],null,null,{"interactive":false,"permanent":false,"direction":"auto","opacity":1,"offset":[0,0],"textsize":"10px","textOnly":false,"className":"","sticky":true},{"color":"white","weight":1,"bringToFront":true}]},{"method":"addEasyButton","args":[{"icon":"fa-globe","title":"","onClick":"function(btn, map){ map.setView([ 51.705533,11.8124408],4); }","position":"topleft"}]},{"method":"addLayersControl","args":[["Carto Voyager","Stamen Terrain"],["Virusvarianten-Gebiet","Hochinzidenzgebiet","Risikogebiet","Kein Risikogebiet mehr - seit weniger als 10 Tagen","Kein Risikogebiet"],{"collapsed":true,"autoZIndex":true,"position":"topright"}]},{"method":"addLegend","args":[{"colors":["red","orange","yellow","#00FF00","green"],"labels":["Virusvarianten-Gebiet","Hochinzidenzgebiet","Risikogebiet","Kein Risikogebiet mehr - seit weniger als 10 Tagen","Kein Risikogebiet"],"na_color":null,"na_label":"NA","opacity":0.5,"position":"bottomleft","type":"unknown","title":null,"extra":null,"layerId":null,"className":"info legend","group":null}]}],"setView":[[51.705533,11.8124408],4,[]],"limits":[]},"evals":["calls.10.args.0.onClick"],"jsHooks":{"render":[{"code":"function(el, x, data) {\n  return (\n        function() {\n            $('.leaflet-control-layers-overlays').prepend('<strong>Risikoeinstufung<\/strong>');\n        }\n    ).call(this.getMap(), el, x, data);\n}","data":null}]}}</script>

Alle Angaben ohne Gewähr automatisch vom Robert Koch Institut abgerufen.
Für einen aktuellen vollständigen Überblick aller internationalen
Risikogebiete und der geltenden Reisebeschränkungen jeder Risikostufe
empfiehlt sich ein Besuch der
[RKI-Webseite](https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Risikogebiete_neu.html).

Datenbank
---------

Alternativerweise kann man auch die Risikoeinstufung und die
dazugehörigen Informationen jedes Landes direkt auf der Datenbank
nachschlagen.

<script src="https://cdn.jsdelivr.net/gh/dieghernan/RKI-Corona-Atlas/_R/plugins/reactable-binding-0.2.3/reactable.min.js"></script>
<div id="htmlwidget-487801dc3c7c2ffe3fc3" class="reactable html-widget" style="width:auto;height:auto;"></div>
<script type="application/json" data-for="htmlwidget-487801dc3c7c2ffe3fc3">{"x":{"tag":{"name":"Reactable","attribs":{"data":{"Land/Region":[],"Risikoeinstufung":[],"Letzte Änderung am":[],"Details":[]},"columns":[{"accessor":"Land/Region","name":"Land/Region","type":"character"},{"accessor":"Risikoeinstufung","name":"Risikoeinstufung","type":"character"},{"accessor":"Letzte Änderung am","name":"Letzte Änderung am","type":"character"},{"accessor":"Details","name":"Details","type":"character"}],"filterable":true,"searchable":true,"defaultPageSize":10,"showPageSizeOptions":true,"pageSizeOptions":[10,25,50,100],"paginationType":"jump","showPageInfo":true,"minRows":1,"striped":true,"dataKey":"7fe62a26b6836fa56b064475ca882cb3","key":"7fe62a26b6836fa56b064475ca882cb3"},"children":[]},"class":"reactR_markup"},"evals":[],"jsHooks":[]}</script>
<!-- DHH - Maybe style as button -->

[Datenbank herunterladen (CSV-Datei)](assets/data/db_countries.csv)
