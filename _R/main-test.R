library(giscoR)
library(sf)
library(readr)
library(dplyr)
library(countrycode)
library(leaflet)
library(rmarkdown)

data <- readr::read_csv("assets/data/db_countries.csv")

cntries_shape <-
  gisco_get_countries(
    year = 2020,
    epsg = 4326,
    cache_dir = "assets/data/geojson",
    resolution = 10
  )

# Get NUTS units
data_units <- data %>% filter(region == TRUE & !is.na(NUTS_CODE))


nuts_shape <- gisco_get_nuts(
  year = 2021,
  epsg = 4326,
  cache_dir = "assets/data/geojson",
  resolution = 10,
  nuts_id = data_units$NUTS_CODE
)

# Get LAU
data_lau <- data_units %>% filter(!NUTS_CODE %in% nuts_shape$NUTS_ID)

lau_shape <- gisco_get_lau(
  year = 2019,
  epsg = 4326,
  cache_dir = "assets/data/geojson",
  gisco_id = data_lau$NUTS_CODE
)


# Put all units together
nuts_shape_end <- nuts_shape %>%
  mutate(NUTS_CODE = NUTS_ID, name.en = NAME_LATN) %>%
  select(NUTS_CODE, name.en)

lau_shape_end <- lau_shape %>%
  mutate(NUTS_CODE = GISCO_ID, name.en = LAU_NAME, name.de = LAU_NAME) %>%
  select(NUTS_CODE, name.en)

regions_end <- bind_rows(nuts_shape_end, lau_shape_end) %>%
  inner_join(data) %>%
  select(NUTS_CODE, name.en, risk_level_code)


# Substract regions from countries

cntries_shape_reg <- st_difference(cntries_shape, st_union(regions_end))

cntries_shape_reg <- cntries_shape_reg %>%
  left_join(data) %>%
  filter(region != "TRUE") %>%
  mutate(
    name.en = NAME_ENGL,
    name.de = countrycode(ISO3_CODE, "iso3c", "cldr.name.de")
  ) %>%
  select(ISO3_CODE, name.en, name.de, risk_level_code)

all_shapes <- bind_rows(cntries_shape_reg, regions_end)

#------




leaflet(all_shapes) %>%
  setView(lat = 51.705533, lng = 11.8124408, zoom = 4) %>%
  addPolygons(data = filter(all_shapes, risk_level_code == "3"),
              stroke = FALSE,
              smoothFactor = 0.3,
              fillColor = "green")


