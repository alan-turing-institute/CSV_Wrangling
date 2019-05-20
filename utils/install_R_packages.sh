#!/bin/bash
#
# Install R packages from a file
#
# Author: G.J.J. van den Burg
# Date: 2019-05-16
#
if [ $# -ne 1 ]
then
	echo "Usage: $0 packages.txt"
	exit 1
fi

if [ ! -s "$1" ]
then
	echo "Provided package file $1 has no packages. Skipping"
	exit 0
fi

while read -r pkg
do
	Rscript -e "install.packages('${pkg}', repos=c('https://cloud.r-project.org'))"
done < "$1"
