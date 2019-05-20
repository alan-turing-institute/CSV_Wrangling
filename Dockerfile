# High version so we get updated version of texlive
FROM ubuntu:19.04

# Install base packages
RUN apt-get update && \
	DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata && \
	apt-get remove -y python && \
	apt-get install -y --no-install-recommends \
		git \
		build-essential \
		r-base \
		latexmk \
		texlive-latex-extra \
		texlive-pictures

# Install R package dependencies that are available on Ubuntu
RUN apt-get install -y --no-install-recommends \
		r-cran-ape r-cran-assertthat r-cran-backports \
		r-cran-base64enc r-cran-bit r-cran-bit64 \
		r-cran-bitops r-cran-blob r-cran-brew \
		r-cran-class r-cran-cli r-cran-codetools \
		r-cran-coin r-cran-colorspace r-cran-crayon \
		r-cran-curl r-cran-data.table r-cran-dbi \
		r-cran-desc r-cran-devtools r-cran-digest \
		r-cran-doparallel r-cran-downloader r-cran-dplyr \
		r-cran-e1071 r-cran-evaluate r-cran-evd \
		r-cran-fastmatch r-cran-foreach r-cran-formula \
		r-cran-ggplot2 r-cran-git2r r-cran-glue \
		r-cran-gridbase r-cran-gridextra r-cran-gtable \
		r-cran-highr r-cran-hms r-cran-htmltools \
		r-cran-htmlwidgets r-cran-httpuv r-cran-httr \
		r-cran-igraph r-cran-ipred r-cran-iterators \
		r-cran-jsonlite r-cran-kernsmooth r-cran-knitr \
		r-cran-labeling r-cran-lattice r-cran-lava \
		r-cran-lazyeval r-cran-magrittr r-cran-markdown \
		r-cran-mass r-cran-matrix r-cran-matrixstats \
		r-cran-memoise r-cran-mgcv r-cran-mime \
		r-cran-mockery r-cran-modeltools r-cran-multcomp \
		r-cran-munsell r-cran-mvtnorm r-cran-nlme \
		r-cran-nnet r-cran-numderiv r-cran-openssl \
		r-cran-pillar r-cran-pkgconfig r-cran-plogr \
		r-cran-plyr r-cran-praise r-cran-prettyunits \
		r-cran-prodlim r-cran-purrr r-cran-r6 \
		r-cran-rcolorbrewer r-cran-rcpp r-cran-rcurl \
		r-cran-readr r-cran-rematch r-cran-reshape2 \
		r-cran-rjson r-cran-rlang r-cran-rpart \
		r-cran-rprojroot r-cran-rsqlite r-cran-rstudioapi \
		r-cran-runit r-cran-sandwich r-cran-scales \
		r-cran-shiny r-cran-sourcetools r-cran-stringi \
		r-cran-stringr r-cran-strucchange r-cran-survival \
		r-cran-testthat r-cran-th.data r-cran-tibble \
		r-cran-tidyr r-cran-tidyselect r-cran-utf8 \
		r-cran-uuid r-cran-viridis r-cran-viridislite \
		r-cran-whisker r-cran-withr r-cran-xml \
		r-cran-xml2 r-cran-xtable r-cran-yaml \
		r-cran-zoo

# Deal with the Python2/3 situation
RUN apt-get install -y --no-install-recommends \
		python3 \
		python3-dev \
		python3-pip && \
	pip3 install --no-cache-dir --upgrade pip setuptools && \
		echo "alias python='python3'" >> /root/.bash_aliases && \
		echo "alias pip='pip3'" >> /root/.bash_aliases && \
		cd /usr/local/bin && ln -s /usr/bin/python3 python

# Clone the repo
RUN git clone https://github.com/alan-turing-institute/CSV_Wrangling

# Install dependencies
RUN pip install -r CSV_Wrangling/requirements.txt
RUN ./CSV_Wrangling/utils/install_R_packages.sh CSV_Wrangling/Rpackages.txt

WORKDIR CSV_Wrangling
