IN_DIR <- './results/polluted_files_csv/'
OUT_DIR <- './results/loading/rcsv/'

parse_utf <- function(filename, pollution) {
  last_enc <- substring(filename, nchar(pollution) + 1, nchar(filename) - 4)
  hex_arr <- strsplit(last_enc, "_")
  s <- ""
  for (d in hex_arr) {
    for (e in d) {
      s <- paste0(s, rawToChar(as.raw(strtoi(e))))
    }
  }
  return(s)
}

process_file <- function(in_filename, idx, total, header, separator, quote) {
  print(paste0('Processing file (', idx, '/', total, ') ', in_filename))

  in_filepath <- file.path(IN_DIR, in_filename)

  out_filename <- paste0(in_filename, '_converted.csv')
  out_filepath <- file.path(OUT_DIR, out_filename)

  tryCatch({
    data <- read.csv(in_filepath, header = header, sep = separator, quote = quote) # TODO parse header, separator, quote
    write.csv(data, out_filepath,row.names = FALSE)

  }, error = function(e) {
    out_file_connection <- file(out_filepath)
    print(paste("Application Error on file", in_filename))
    print(paste(e))
    writeLines(paste0("Application Error\n", e), out_file_connection)
    close(out_file_connection)
  })

}

benchmark_files <- list.files(IN_DIR)


c <- 0
for (f in benchmark_files) {
  c <- c + 1
  header <- TRUE
  quotation_char <- '\"'
  separator <- ','

  out_filename <- paste0(f, '_converted.csv')
  out_filepath <- file.path(OUT_DIR, out_filename)
  if (file.exists(out_filepath)) {
      next
  }
  val <- grepl(f, "file_field_delimiter")

  if (grepl("no_header", f)) {
    header <- FALSE
  } else if (grepl("file_field_delimiter", f)) {
    separator <- parse_utf(f, "file_field_delimiter_")
  }else if (grepl("file_quotation_char", f)) {
    quotation_char <- parse_utf(f, "file_quotation_char_")
  }

  process_file(f, c, length(benchmark_files), header, separator, quotation_char)
}
