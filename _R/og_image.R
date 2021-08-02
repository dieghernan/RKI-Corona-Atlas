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


cntries_shape <-
  gisco_get_countries(
    year = 2020,
    epsg = 4326,
    cache_dir = "./_R/geojson",
    resolution = 3
  )
# Merge overseas and disputed territories to their administrations
overseas <- readr::read_csv("./assets/data/overseas.csv")
overseas_shp <- inner_join(cntries_shape, overseas) %>% select(ISO3_ADMIN) %>%
  mutate(ISO3_CODE = ISO3_ADMIN)

cntries_shape_overseas <- bind_rows(cntries_shape,overseas_shp) %>%
  group_by(ISO3_CODE) %>%
  summarise(n=n())


# Add Kosovo
K <-
  st_read("./_R/geojson/kosovo.geojson", quiet = TRUE) %>% select(ISO3_CODE)

cntries_shape_reg <-
  st_difference(cntries_shape_overseas, st_union(K))

cntries_shape_reg <- bind_rows(cntries_shape_reg, K)




cntries_shape_reg2 <- cntries_shape_reg %>%
  select(ISO3_CODE) %>%
  inner_join(data_cntries)

all_shapes <- st_make_valid(cntries_shape_reg2)
crop <- c(-90,-25, 120, 70)
names(crop) <- c("xmin", "ymin", "xmax", "ymax")



cntries_shape_reg <- st_crop(cntries_shape_reg, crop)


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
  tm_shape(level0) +
  tm_fill(col = "yellow", alpha = .5) +
  tm_shape(level1) +
  tm_fill(col = "red", alpha = .5) +
  tm_shape(level2) +
  tm_fill(col = "chocolate", alpha = .5)


tmap_save(og_map, "assets/img/og_corona_atlas.png", dpi = 90)

rm(list = ls())
