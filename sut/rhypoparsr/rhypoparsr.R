sut <- 'rhypoparsr'
dataset <- Sys.getenv('DATASET')
IN_DIR <- paste0('/', dataset, '/csv/')
PARAM_DIR <- paste0('/', dataset, '/parameters/')
OUT_DIR <- paste0('/results/', sut, '/', dataset, '/loading/')
TIME_DIR <- paste0('/results/', sut, '/', dataset, '/')
N_REPETITIONS <- 3

quiet <- function(x) {
  sink(tempfile())
  on.exit(sink())
  invisible(force(x))
}

benchmark_files <- list.files(IN_DIR)

times_dict <- list()
idx <- 0
for (in_filename in benchmark_files) {
  idx <- idx + 1

  in_filepath <- file.path(IN_DIR, in_filename)
  out_filename <- paste0(in_filename, '_converted.csv')
  out_filepath <- file.path(OUT_DIR, out_filename)
  if (file.exists(out_filepath)) {
    next
  }
  print(paste0('Processing file (', idx, '/', length(benchmark_files), ') ', in_filename))

  time_range <- 0:(N_REPETITIONS - 1)
  for (time_rep in time_range) {
    n_rows <- 0
    start_time <- Sys.time()
    tryCatch({
      res <- purrr::quietly(hypoparsr::parse_file)(in_filepath)$result
      end_time <- Sys.time()
      duration <- end_time - start_time
      df <- as.data.frame(res)
      invisible(df)
      n_rows <- nrow(df)
      write.csv(df, out_filepath, row.names = FALSE, na = "")
    }, error = function(e) {
      end_time <- Sys.time()
      duration <- end_time - start_time
      out_file_connection <- file(out_filepath)
      print(paste("Application Error on file", in_filename))
      print(paste(e))
      writeLines(paste0("Application Error\n", e), out_file_connection)
      close(out_file_connection)
    })
    times_dict[[in_filename]] <- c(times_dict[[in_filename]], duration)
  }
}

if (length(times_dict) == 0) {
  quit(save = "no", status = 0, runLast = FALSE)
}
time_filepath <- file.path(TIME_DIR, paste0(sut, '_time.csv'))
time_file_connection <- file(time_filepath)
times_df <- t(data.frame(times_dict))
colnames(times_df) <- c(paste0(sut, '_time_', 0:(N_REPETITIONS - 1)))
times_df <- data.frame("filename" = row.names(times_df), times_df)
write.csv(times_df, time_file_connection, row.names = FALSE, na = "")
