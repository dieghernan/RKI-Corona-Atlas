

library(giscoR)
library(sf)
library(readr)
library(dplyr)
library(countrycode)
library(leaflet)
library(reactable)
library(rmarkdown)
library(jsonlite)
library(leaflet.providers)
library(leaflet.extras)


cntries_shape <-
  gisco_get_countries(
    year = 2020,
    epsg = 4326,
    cache_dir = "./geojson",
    resolution = 20
  )
# Merge overseas and disputed territories to their administrations
overseas <- readr::read_csv("../assets/data/overseas.csv")
overseas_shp <- inner_join(cntries_shape, overseas) %>% select(ISO3_ADMIN) %>%
  mutate(ISO3_CODE = ISO3_ADMIN)

cntries_shape_overseas <- bind_rows(cntries_shape,overseas_shp) %>%
  group_by(ISO3_CODE) %>%
  summarise(n=n())


# Add Kosovo
K <-
  st_read("./geojson/kosovo.geojson", quiet = TRUE) %>% select(ISO3_CODE)

cntries_shape_reg <-
  st_difference(cntries_shape_overseas, st_union(K))

cntries_shape_reg <- bind_rows(cntries_shape_reg, K)




cntries_shape_reg2 <- cntries_shape_reg %>% select(ISO3_CODE)

all_shapes <- st_make_valid(cntries_shape_reg2)

geo_shapes = all_shapes %>% select(ISO3_CODE, geometry)
st_write(geo_shapes, "./geojson/country_shapes.geojson")
