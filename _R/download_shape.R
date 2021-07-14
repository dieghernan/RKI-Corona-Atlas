library(sf)
library(dplyr)


tmp <- tempfile(fileext = ".geojson")
download.file("https://nominatim.openstreetmap.org/search?q=Kosovo&format=geojson&polygon_geojson=1",
              tmp)

r_shp <- st_read(tmp) %>% st_transform(4326)
r_shp <- r_shp[1, ]

df <- data.frame(ISO3_CODE = "XKX",
                 NAME_ENGL = "Kosovo",
                 stringsAsFactors = FALSE)

final_shape <- st_sf(df, geometry=st_geometry(r_shp)) %>% st_make_valid()

plot(st_geometry(final_shape))

st_write(final_shape,"_R/geojson/kosovo.geojson")
rm(list=ls())

b <- st_read("_R/geojson/kosovo.geojson")
plot(st_geometry(b))
