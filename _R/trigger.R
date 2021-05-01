rmarkdown::render("_R/index_en.Rmd", output_dir = "_pages/",
                  output_format = "md_document", quiet = TRUE)

rmarkdown::render("_R/index.Rmd", output_dir = "_pages/",
                  output_format = "md_document", quiet = TRUE)

rmarkdown::render("_R/labs_heatmap.Rmd", output_dir = "_pages/",
                  output_format = "md_document", quiet = TRUE)

# Dinamic og image
source("_R/og_image.R")

# rmarkdown::render("_R/nuts.Rmd", output_dir = "_pages/",
#                   output_format = "md_document", quiet = TRUE)
#
# rmarkdown::render("_R/lau.Rmd", output_dir = "_pages/",
#                   output_format = "md_document", quiet = TRUE)
