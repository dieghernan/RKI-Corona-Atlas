library(giscoR)
library(sf)
library(readr)
library(dplyr)
library(countrycode)
library(ggplot2)
library(tidyterra)
library(maptiles)
library(ragg)
sf::sf_use_s2(FALSE)

data <- readr::read_csv("./assets/data/db_scraped.csv")
rl <- readr::read_csv("./assets/data/risk_level_code.csv")

data_cntries <-
  data %>%
  filter(ISO3_CODE != "ERROR" & is.na(ERROR)) %>%
  filter(is.na(region)) %>%
  left_join(rl)


cntries_shape <- st_read("./assets/geo/country_shapes.geojson")


cntries_shape_reg2 <- cntries_shape %>%
  select(ISO3_CODE) %>%
  inner_join(data_cntries)

cntries_shape_reg2 <- st_make_valid(cntries_shape_reg2)
crop <- c(-90, -25, 120, 70)
names(crop) <- c("xmin", "ymin", "xmax", "ymax")

cntries_shape_reg <- st_crop(cntries_shape_reg2, crop)

cntries_shape_reg2 <- cntries_shape_reg %>%
  select(ISO3_CODE) %>%
  inner_join(data_cntries)

all_shapes <- st_make_valid(cntries_shape_reg2)

all_shapes <-
  all_shapes %>%
  select(ISO3_CODE) %>%
  left_join(data_cntries)


all_shapes <- st_transform(all_shapes, 3857)

tiles <-
  maptiles::get_tiles(all_shapes,
    "CartoDB.Voyager",
    crop = TRUE,
    cachedir = "./_R/geojson/"
  )

tiles <- terra::crop(tiles, all_shapes)



DEU <- all_shapes %>% filter(ISO3_CODE == "DEU")
rest_shapes <- all_shapes %>% filter(ISO3_CODE != "DEU")

rest_shapes$risk_level_code <- factor(rest_shapes$risk_level_code, c(0, 1, 2))

og_map <- ggplot() +
  geom_spatraster_rgb(data = tiles) +
  geom_sf(
    data = rest_shapes, aes(fill = risk_level_code), show.legend = FALSE,
    linewidth = 0.01
  ) +
  geom_sf(data = DEU, fill = "blue", alpha = .5, linewidth = 0.01) +
  scale_fill_manual(values = alpha(c("#00FF00", "#FF0000", "#FFFF00"), 0.5)) +
  coord_sf(expand = FALSE) +
  theme_void()

ggsave("assets/img/og_corona_atlas.png", og_map, dpi = 300)

rm(list = ls())
