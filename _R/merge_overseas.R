


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

old <- st_read("./_R/geojson/CNTR_RG_03M_2020_4326.geojson")

cntries_shape <-
  gisco_get_countries(
    year = 2020,
    epsg = 4326,
    cache_dir = "_R/geojson",
    resolution = 20
  )

# Merge overseas and disputed territories to their administrations
overseas <- readr::read_csv("./assets/data/overseas.csv")
overseas_shp <- left_join(cntries_shape, overseas) %>%
  mutate(
    OLD_CODE = ISO3_CODE,
    ISO3_CODE = ifelse(is.na(ISO3_ADMIN),
      ISO3_CODE,
      ISO3_ADMIN
    )
  )
# overseas_shp %>% st_drop_geometry() %>% filter(ISO3_CODE != OLD_CODE)


cntries_shape_overseas <- overseas_shp %>%
  group_by(ISO3_CODE) %>%
  summarise(n = n()) %>%
  select(ISO3_CODE)


# Add Kosovo
K <-
  st_read("_R/geojson/kosovo.geojson", quiet = TRUE) %>% select(ISO3_CODE)

cntries_shape_reg <-
  st_difference(cntries_shape_overseas, st_union(K))

cntries_shape_reg <- bind_rows(cntries_shape_reg, K)




cntries_shape_reg2 <- cntries_shape_reg %>% select(ISO3_CODE)

all_shapes <- st_make_valid(cntries_shape_reg2)

geo_shapes <- all_shapes %>% select(ISO3_CODE, geometry)

file.remove("./assets/geo/country_shapes.geojson")

st_write(
  geo_shapes,
  "./assets/geo/country_shapes.geojson"
)

# Check
rki_data <- readr::read_csv("./assets/data/db_scraped.csv")

rki_a <- rki_data %>%
  select(ISO3_CODE) %>%
  unique()

rki_err <- rki_data %>% filter(!ISO3_CODE %in% geo_shapes$ISO3_CODE)

geo_shapes_not_include <- geo_shapes %>%
  st_drop_geometry() %>%
  filter(!ISO3_CODE %in% rki_data$ISO3_CODE)
