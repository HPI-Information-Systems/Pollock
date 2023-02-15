FROM r-base:4.2.1

WORKDIR /app
COPY ./sut/rcsv/rcsv.R ./

RUN Rscript -e "install.packages('rjson', repos='https://cran.rstudio.com/')"
CMD ["Rscript", "rcsv.R"]
