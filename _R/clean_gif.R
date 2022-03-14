# Delete plot history and regenerate gif

allf <- list.files("timelapse/frames", pattern = ".png$", full.names = TRUE)

unlink(allf)

# Create gif

source("_R/create_gif.R")

