# CSV Wrangling

[![Build Status](https://travis-ci.org/alan-turing-institute/CSV_Wrangling.svg?branch=master)](https://travis-ci.org/alan-turing-institute/CSV_Wrangling)

This is the repository for reproducing the experiments in the paper:

[**Wrangling Messy CSV files by Detecting Row and Type Patterns**](https://arxiv.org/abs/1811.11242)

by [G.J.J. van den Burg](https://gertjanvandenburg.com), [A. 
Nazabal](https://scholar.google.co.uk/citations?user=IanHvT4AAAAJ&hl=en&oi=ao) 
and [C. Sutton](https://homepages.inf.ed.ac.uk/csutton/).

If you use this paper or this code in your own work, please *cite the paper* 
using the citation information provided below.

The results in the arXiv version of the paper are [fully 
verifiable](https://alan-turing-institute.github.io/CSV_Wrangling/) using this 
repository.

## Introduction

Our experiments are made reproducible through the use of [GNU 
Make](https://www.gnu.org/software/make/). You can either set up your local 
environment with the necessary dependencies, or use the Dockerfile included in 
the repository.

There are two ways to reproduce our results. The first only reproduces the 
figures, tables, and constants in the paper from the raw detection results, 
while the second reruns the detection results as well.

1. You can reproduce the figures, tables, and constants from the raw 
   experimental results included in this repository. This will not re-run all 
   the experiments but will regenerate the output used in the paper. The 
   command for this is:

   ```bash
   $ make results
   ```

2. You can fully reproduce our experiments by downloading the data and 
   rerunning the detection methods on all the files. This might take a while 
   depending on the speed of your machine and the number of cores available. 
   Total wall-clock computation time for a single core is estimated at 11 
   days. The following commands will do all of this.

   ```bash
   $ make clean       # remove existing output files, except human annotated
   $ make data        # download the data
   $ make results     # run all the detectors and generate the result files
   ```

   If you'd like to use multiple cores, you can replace the last command with:

   ```bash
   $ make -j X results
   ```

   where ``X`` is the desired number of cores.


## Data

There are two datasets that are used in the experiments. Because we don't own 
the rights to all these files, we can't package these files and make them 
available in a single download. We can however provide URLs to the files and 
add a download script, which is what we do here. The data can be downloaded 
with:

```bash
$ make data
```

If you wish to change the download location of the data, please edit the 
``DATA_DIR`` variable in the Makefile.

**Note:** We are aware of the fact that some of the files may change or become 
unavailable in the future. This is an unfortunate side-effect of using 
publically available data in this way. The data downloader skips files that 
are unavailable or that have changed.


## Requirements

Below are the requirements for reproducing the experiments, if you're not 
using Docker. Note that at the moment only Linux-based systems are supported. 
MacOS will probably work, but hasn't been tested.

- Python 3.x with the packages in the ``requirements.txt`` file. These can be 
  installed with: ``pip install --user -r requirements.txt``.

- R with the external packages installed through: 
  ``install.packages(c('devtools', 'rjson', 'data.tree', 'RecordLinkage', 
  'readr', 'tibble'))``.

- A working [LaTeX](https://www.latex-project.org/) installation is needed for 
  creating the figures (at least ``texlive-latex-extra`` and 
  ``texlive-pictures``), as well as a working 
  [LaTeXMK](https://mg.readthedocs.io/latexmk.html) installation.


## Instructions

To clone this repository and all its submodules do:

```bash
$ git clone --recurse-submodules https://github.com/alan-turing-institute/CSV_Wrangling
```

Then install the requirements as listed above and run the ``make`` command of 
your choice.

## License

With the exception of the submodule in ``scripts/detection/lib/hypoparsr`` 
this code is licensed under the [MIT 
license](https://en.wikipedia.org/wiki/MIT_License). See the LICENSE file for 
more details.

## Citation

```
@article{van2018wrangling,
  title = {Wrangling Messy {CSV} Files by Detecting Row and Type Patterns},
  author = {{van den Burg}, G. J. J. and Nazabal, A. and Sutton, C.},
  journal = {arXiv preprint arXiv:1811.11242},
  archiveprefix = {arXiv},
  year = {2018},
  eprint = {1811.11242},
  url = {https://arxiv.org/abs/1811.11242},
  primaryclass = {cs.DB},
}
```
