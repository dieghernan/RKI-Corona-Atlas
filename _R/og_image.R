library(giscoR)
library(sf)
library(readr)
library(dplyr)
library(countrycode)
library(tmap)
library(maptiles)
library(rgdal)

data <- readr::read_csv("./assets/data/db_scraped.csv")
rl <- readr::read_csv("./assets/data/risk_level_code.csv")

data_cntries <-
  data %>% filter(ISO3_CODE != "ERROR" & is.na(ERROR)) %>%
  filter(is.na(region)) %>%
  left_join(rl)




cntries_shape_reg <-  st_read("./assets/geo/country_shapes.geojson")

message("Join map and data")
cntries_shape_reg2 <- cntries_shape_reg %>%
  inner_join(data_cntries)



all_shapes <- st_make_valid(cntries_shape_reg2)
crop <- c(-90, -25, 120, 70)
names(crop) <- c("xmin", "ymin", "xmax", "ymax")

message("Crop")
all_shapes <- st_crop(all_shapes, crop)


all_shapes <- st_transform(all_shapes, 3857)

tiles <-
  maptiles::get_tiles(all_shapes,
                      "CartoDB.Voyager",
                      crop = TRUE,
                      cachedir = "./_R/geojson/")

tiles <- terra::crop(tiles, all_shapes)

DEU <- all_shapes %>% filter(ISO3_CODE == "DEU")
level0 <- all_shapes %>% filter(risk_level_code == 0,
                                ISO3_CODE != "DEU")
level1 <- all_shapes %>% filter(risk_level_code == 1)
level2 <- all_shapes %>% filter(risk_level_code == 2)
level3 <- all_shapes %>% filter(risk_level_code == 3)
level4 <- all_shapes %>% filter(risk_level_code == 4)


message("Plot")

og_map <-
  tm_shape(tiles, raster.downsample = FALSE, bbox = all_shapes) +
  tm_rgb() +
  tm_shape(DEU) +
  tm_fill(col = "blue", alpha = .5) +
  tm_shape(level0) +
  tm_fill(col = "#00FF00", alpha = .5) +
  tm_shape(level1) +
  tm_fill(col = "red", alpha = .5) +
  tm_shape(level2) +
  tm_fill(col = "chocolate", alpha = .5) +
  tm_shape(level3) +
  tm_fill(col = "orange", alpha = .5) +
  tm_shape(level4) +
  tm_fill(col = "yellow", alpha = .5) +
  tm_layout(outer.margins = FALSE, frame = FALSE)


tmap_save(og_map, "assets/img/og_corona_atlas.png", dpi = 90)

rm(list = ls())
