
library(gifski)
library(sf)
library(dplyr)
library(readr)
library(tidyr)
library(ggplot2)
library(sysfonts)
library(showtext)


# Import and tidy csv----


db <- read_csv("timelapse/risk_date_countries.csv")
n <- names(db)
n[1] <- "date"
names(db) <- n

# Daily db
daily <- data.frame(date = seq(min(db$date), max(db$date), 1)) %>%
  left_join(db) %>%
  fill(everything())

dates <- daily %>%
  pull(date) %>%
  unique()

# Pivot
daily_long <- daily %>%
  pivot_longer(!date, names_to = "ISO3_CODE")

# Shapes----

shape <- st_read("./assets/geo/country_shapes.geojson", quiet = TRUE) %>%
  st_transform("+proj=robin")

ant <- giscoR::gisco_get_countries(country = "Antarctica") %>%
  st_transform("+proj=robin")

shape <- bind_rows(shape, ant)

deu <- shape %>% filter(ISO3_CODE == "DEU")
world <- shape %>% filter(ISO3_CODE != "DEU")


# Extract background
bck <- st_graticule() %>%
  st_bbox() %>%
  st_as_sfc() %>%
  st_transform(3857) %>%
  st_segmentize(500000) %>%
  st_transform(st_crs(shape))


# Plot loop ----

# Font

font_add("roboto",
  regular = "assets/fonts/Roboto-Regular.ttf",
  bold = "assets/fonts/Roboto-Bold.ttf",
  italic = "assets/fonts/Roboto-Italic.ttf"
)

showtext_auto()


files <- file.path("_R", "timelapse", paste0("D", dates, ".png"))

alldates <- dates

for (i in seq_len(length(alldates))) {
  d <- alldates[i]
  f <- files[i]

  # Optimize
  if (file.exists(f)) next()


  dat <- daily_long %>% filter(date == d)

  shapedat <- world %>% left_join(dat, by = "ISO3_CODE")


  # levels
  low <- shapedat %>% filter(value == 0)
  partial <- shapedat %>% filter(value == 4)
  risk <- shapedat %>% filter(value == 3)
  high <- shapedat %>% filter(value == 2)
  concern <- shapedat %>% filter(value == 1)
  rest <- shapedat %>% filter(!value %in% c(0:4))

  # Mock level for legend
  low$value <- as.factor(low$value)

  levels(low$value) <- c(
    "Not risk area",
    "High risk area",
    "Risk Area (Partial)",
    "Variant of concern",
    "Risk Area",
    "Germany"
  )

  # Base map
  base <- ggplot() +
    geom_sf(data = bck, fill = "lightblue", alpha = 0.4) +
    geom_sf(data = world, fill = "grey70", size = 0.01) +
    theme_minimal() +
    theme(
      plot.background = element_rect(fill = "white", color = NA),
      text = element_text(family = "roboto"),
      plot.title = element_text(hjust = .5, face = "bold", size = 50),
      plot.subtitle = element_text(hjust = .5, size = 20, face = "italic"),
      plot.caption = element_text(size = 12, face = "italic"),
      plot.margin = margin(0, 10, 0, 10),
      legend.text = element_text(size = 15),
      legend.position = "bottom",
      legend.margin = margin(b = 5, 0, 0, 0)
    ) +
    labs(
      title = "Corona Atlas",
      subtitle = as.character(d),
      caption = "Data: Robert Koch Institut   ",
      fill = ""
    ) +
    geom_sf(data = deu, fill = "blue", size = 0.01)


  if (nrow(low) > 1) {
    base <- base +
      geom_sf(data = low, aes(fill = value), size = 0.01) +
      scale_fill_manual(
        values = c(
          "#00FF00",
          "chocolate",
          "yellow",
          "red",
          "orange",
          "blue"
        ),
        drop = FALSE
      ) +
      guides(fill = guide_legend(
        keywidth = 3,
        keyheight = .4,
        label.position = "bottom",
        by_row = FALSE
      ))
  }

  if (nrow(partial) > 1) {
    base <- base +
      geom_sf(data = partial, size = 0.01, fill = "yellow")
  }


  if (nrow(risk) > 1) {
    base <- base +
      geom_sf(data = risk, size = 0.01, fill = "orange")
  }


  if (nrow(high) > 1) {
    base <- base +
      geom_sf(data = high, size = 0.01, fill = "chocolate")
  }



  if (nrow(concern) > 1) {
    base <- base +
      geom_sf(data = concern, size = 0.01, fill = "red")
  }

  if (nrow(rest) > 1) {
    base <- base +
      geom_sf(data = rest, size = 0.01, fill = "grey70")
  }


  # Add back the bk

  base <- base +
    geom_sf(data = bck, fill = NA, alpha = 0.4)


  ggsave(f, base, width = 1000, height = 1000, dpi = 300, units = "px")
}



# Animation----


allf <- list.files("_R/timelapse", pattern = ".png$", full.names = TRUE)

arrange_anim <- c(
  rep(allf[1], 7),
  allf,
  rep(allf[length(allf)], 28)
)



gifski(arrange_anim, "assets/img/corona_atlas_timelapse.gif",
  delay = 1 / 14,
  width = 1000, height = 1000
)


# Old test with magick
# img_arrange <- image_read(arrange_anim)
#
# image_write_gif(img_arrange,
#   "assets/img/corona_atlas_timelapse.gif",
#   loop = TRUE,
#   progress = TRUE,
#   delay = 1 / 14
# )
