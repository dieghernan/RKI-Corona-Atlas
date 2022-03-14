

message("----Render index_en\n\n")
rmarkdown::render(
  "_R/index_en.Rmd",
  output_dir = "_pages/",
  output_format = "md_document",
  quiet = TRUE
)

message("----Render index\n\n")
rmarkdown::render(
  "_R/index.Rmd",
  output_dir = "_pages/",
  output_format = "md_document",
  quiet = TRUE
)

message("----Render index_es\n\n")
rmarkdown::render(
  "_R/index_es.Rmd",
  output_dir = "_pages/",
  output_format = "md_document",
  quiet = TRUE
)

message("----Render index_fr\n\n")
rmarkdown::render(
 "_R/index_fr.Rmd",
 output_dir = "_pages/",
 output_format = "md_document",
 quiet = TRUE
)

message("----Render index_pl\n\n")
rmarkdown::render(
 "_R/index_pl.Rmd",
 output_dir = "_pages/",
 output_format = "md_document",
 quiet = TRUE
)

message("----Render index_tr\n\n")
rmarkdown::render(
 "_R/index_tr.Rmd",
 output_dir = "_pages/",
 output_format = "md_document",
 quiet = TRUE
)


message("----Render og_image\n\n")
# Dinamic og image
source("_R/og_image.R")


message("----Render gif\n\n")
# Dinamic og image
source("_R/create_gif.R")


# rmarkdown::render("_R/nuts.Rmd", output_dir = "_pages/",
#                   output_format = "md_document", quiet = TRUE)
#
# rmarkdown::render("_R/lau.Rmd", output_dir = "_pages/",
#                   output_format = "md_document", quiet = TRUE)
