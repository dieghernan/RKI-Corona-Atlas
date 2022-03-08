library(giscoR)
library(sf)
library(readr)
library(dplyr)
library(countrycode)
library(tmap)
library(maptiles)
library(rgdal)
library(ragg)
sf::sf_use_s2(FALSE)

data <- readr::read_csv("./assets/data/db_scraped.csv")
rl <- readr::read_csv("./assets/data/risk_level_code.csv")

data_cntries <-
  data %>% filter(ISO3_CODE != "ERROR" & is.na(ERROR)) %>%
  filter(is.na(region)) %>%
  left_join(rl)


cntries_shape <- st_read("./assets/geo/country_shapes.geojson")


cntries_shape_reg2 <- cntries_shape %>%
  select(ISO3_CODE) %>%
  inner_join(data_cntries)

cntries_shape_reg2 <- st_make_valid(cntries_shape_reg2)
crop <- c(-90,-25, 120, 70)
names(crop) <- c("xmin", "ymin", "xmax", "ymax")

cntries_shape_reg <- st_crop(cntries_shape_reg2, crop)

cntries_shape_reg2 <- cntries_shape_reg %>%
  select(ISO3_CODE) %>%
  inner_join(data_cntries)

all_shapes <- st_make_valid(cntries_shape_reg2)

all_shapes <-
  all_shapes %>% select(ISO3_CODE) %>% left_join(data_cntries)


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

og_map <-
  tm_shape(tiles, raster.downsample = FALSE, bbox = all_shapes) +
  tm_rgb() +
  tm_shape(DEU) +
  tm_fill(col = "blue", alpha = .5) +
  tm_layout(frame = FALSE,
            asp = dim(tiles)[2]/dim(tiles)[1])

# Fix #16
if (nrow(level0) > 0) {
  og_map <- og_map +
    tm_shape(level0) +
    tm_fill(col = "#00FF00", alpha = .5)
}
if (nrow(level1) > 0) {
  og_map <- og_map +
    tm_shape(level1) +
    tm_fill(col = "red", alpha = .5)
}

if (nrow(level2) > 0) {
  og_map <- og_map +
    tm_shape(level2) +
    tm_fill(col = "yellow", alpha = .5)
}


# End fix

tmap_save(og_map, "assets/img/og_corona_atlas.png", dpi = 90)

rm(list = ls())
