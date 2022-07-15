FROM r-base:4.2.1

WORKDIR /app
COPY ./sut/rhypoparsr/rhypoparsr.R ./

#RUN R -e "install.packages('hypoparsr',dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('remotes')"
CMD ["Rscript", "rhypoparsr.R"]
