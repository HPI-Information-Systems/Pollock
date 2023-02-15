FROM r-base:4.2.2

WORKDIR /app
COPY ./sut/rhypoparsr/rhypoparsr.R ./
RUN apt-get update
RUN apt install -y r-cran-utf8 r-cran-fansi r-cran-cpp11 r-cran-pillar \
    r-cran-prettyunits r-cran-pkgconfig r-cran-ellipsis r-cran-bit \
    r-cran-progress r-cran-withr r-cran-tzdb r-cran-tidyselect r-cran-tibble \
    r-cran-hms r-cran-crayon r-cran-bit64  r-cran-parallelly r-cran-listenv \
    r-cran-digest r-cran-globals r-cran-future r-cran-progressr r-cran-future.apply \
    r-cran-lava  r-cran-rcpp r-cran-prodlim r-cran-proxy r-cran-fastmap r-cran-cachem \
    r-cran-plogr r-cran-memoise r-cran-dbi r-cran-blob  r-cran-vroom r-cran-clipr r-cran-xtable \
    r-cran-data.table r-cran-evd r-cran-ipred r-cran-e1071  r-cran-ff r-cran-rsqlite \
    r-cran-stringi r-cran-readr r-cran-remotes r-cran-purrr


RUN R -e "install.packages(c('vroom', 'ada', 'RecordLinkage', 'data.tree'))"
RUN R -e "remotes::install_github('tdoehmen/hypoparsr', quiet = 1)"
CMD ["Rscript", "rhypoparsr.R"]
