FROM r-base:4.2.1

WORKDIR /app
COPY ./sut/rhypoparsr/rhypoparsr.R ./

RUN R -e "install.packages('remotes')"
RUN R -e "install.packages('purrr')"
CMD ["Rscript", "rhypoparsr.R"]
