

message("----Render index_fr\n\n")
rmarkdown::render(
 "_R/index_fr.Rmd",
 output_dir = "_pages/",
 output_format = "md_document",
 quiet = TRUE
)
