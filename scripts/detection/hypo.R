#!/usr/bin/env Rscript
#
# Author: G.J.J. van den Burg
# Copyright (c) 2018 - The Alan Turing Institute
# License: See the LICENSE file.
#

library(devtools)
library(rjson)

# load our local version of hypoparsr
match <- grep("--file=", commandArgs(trailingOnly=F))
this.path <- normalizePath(sub("--file=", "", commandArgs(trailingOnly=F)[match]))
this.dir <- dirname(this.path)
hypoparsr.dir <- paste(this.dir, "/lib/hypoparsr", sep="")
load_all(hypoparsr.dir, export_all=F)

printf <- function(...) invisible(cat(sprintf(...)));
fprintf <- function(file, ...) invisible(cat(sprintf(...), file=file))

#' Replacement for R's ridiculous strsplit that drops empties.
my.strsplit <- function(string, delim) {
  out <- strsplit(string, delim)
  if (substr(string, nchar(string), nchar(string)) == delim)
    out <- c(out, "")
  return(out)
}

real.quotechar <- function(filename, best, delim, rowsep, quote.method)
{
    # Since HypoParsr doesn't reliably return the quote character, we here try
    # to reverse engineer what they do to figure out what the quote character
    # is that they actually use.

    encoding <- strsplit(names(best$confidence[6]), '\n')[[1]][3]
    text <- readr::read_file(filename, locale=readr::locale(encoding=encoding))
    text <- iconv(text)

    if (rowsep == "E")
        regex.rowsep <- "\r\n"
    else if (rowsep == "N")
        regex.rowsep <- "(?<!\r)\n"
    else if (rowsep == "R")
        regex.rowsep <- "\r(?!\n)"
    else
        stop("Unknown rowsep not supported!")

    lines <- unlist(strsplit(text, regex.rowsep, perl=T))

    if (quote.method == "double") {
        escape_double <- T
        escape_backslash <- F
    } else if (quote.method == "escape") {
        escape_double <- F
        escape_backslash <- T
    }

    dim_check <- NULL
    tryCatch({
        dim_check <- suppressWarnings(readr::read_delim(text, delim=delim,
                                                        quote='', col_names=F,
                                                        escape_double=escape_double,
                                                        escape_backslash=escape_backslash,
                                                        n_max=10))
    },
    error=function(e) {
        fprintf(stderr(), "Error occurred in readr::read_delim\n")
        return(NULL)
    }
    )
    if (is.null(dim_check)) {
        fprintf(stderr(), "dim_check is null\n")
        return(NULL)
    }

    coltypes.string <- paste(rep("c", ncol(dim_check)), collapse="")

    # NOTE: We've changed the default ``na`` argument to read_delim because we 
    # don't want to have empty cells interpreted as NA for the purposes of this 
    # function.
    intermediate <- suppressWarnings(readr::read_delim(text, delim=delim, 
                                                       quote='', col_names=F,
                                                       escape_double=escape_double,
                                                       escape_backslash=escape_backslash,
                                                       na=c("NA"),
                                                       col_types=coltypes.string))

    # immediate red flag that parameters aren't correct.
    if (nrow(intermediate) != length(lines)) {
        fprintf(stderr(), "intermediate size doesn't match line size\n")
        return(NULL)
    }

    used.A <- FALSE
    used.Q <- FALSE

    for (qc in c("'", '"')) {
        for (i in 1:length(lines)) {
            cells <- unlist(my.strsplit(lines[i], delim))

            # if this happens, then quote should not have been ignored.
            if (length(cells) != ncol(intermediate)) {
                fprintf(stderr(), "number of cells doesn't match number of cols\n");
                return(NULL)
            }

            for (j in 1:length(cells)) {
                if (!(cells[j] == "NA" && is.na.data.frame(intermediate[i, j]))) {
                    content <- gsub("[\r]", "", cells[j])
                    if (content == '\\' && intermediate[i, j] != '\\') {
                        # Use of the escapechar without (escaped) quotes 
                        # present in the file (otherwise the quotechar in the 
                        # detected dialect shouldn't have been empty)
                        return('')
                    }
                    if (content != intermediate[i, j]) {
                        fprintf(stderr(), "Unequal: %s and %s\n", content, intermediate[i, j])
                        return(NULL)
                    }
                }
                first <- substr(cells[j], 1, 1)
                last <- substr(cells[j], length(cells[j]), length(cells[j]))
                if (first == qc && last == qc) {
                    if (qc == "'")
                        used.A <- TRUE
                    else if (qc == '"')
                        used.Q <- TRUE
                }
            }
        }
    }

    if (used.A && used.Q) {
        return("AMBIGUOUS")
    } else if (used.A) {
        return("'")
    } else if (used.Q) {
        return('"')
    } else {
        return("")
    }
}

detect <- function(filename)
{
    if (!file.exists(filename)) {
        return (list(status="FAIL", status_msg="NONEXISTENT_FILE", 
                     dialect=NULL))
    }

    hypo.res <- hypoparsr::parse_file(filename)

    if (is.null(hypo.res$results))
        return (list(status="FAIL", status_msg="NO_RESULTS", dialect=NULL))

    # Get the delimiter from the result
    best <- hypo.res$results[hypo.res$ranking][[1]]

    # the dialect is at the fifth position in the confidence array
    dialect.idx <- 5
    dialect.string <- names(best$confidence[dialect.idx])
    dialect.list <- strsplit(dialect.string, '\n')
    dialect.array <- dialect.list[[1]]
    delim.quote.string <- dialect.array[3]
    delim.quote.list <- strsplit(delim.quote.string, ' ')
    delim.quote.array <- delim.quote.list[[1]]

    # NOTE: Hypoparsr only returns quotes in this string if they are
    # *functional*, i.e. surrounds a delimiter (and maybe also a row
    # separator?). This leads to problems because they don't report these quote
    # characters in the description, but do end up stripping them from the
    # cells later on. (Actually, the hypothesis with the quote character is
    # created, and gets the same dialect score in this case. Other scores
    # however can cause it not to appear in the best hypothesis).

    delimiter <- delim.quote.array[2]
    quotechar <- delim.quote.array[4]
    rowsep <- delim.quote.array[6]
    quote.method <- delim.quote.array[9]

    used.real.qc <- F
    if (quotechar == "DOUBLEQUOTE") {
        quotechar <- '"'
    } else if (quotechar == "'") {
        quotechar <- "'"
    } else {
        quotechar <- real.quotechar(filename, best, delimiter, rowsep,
                                    quote.method)
        used.real.qc <- T
    }

    if (is.null(quotechar)) {
        quotechar <- ''
    }

    # HypoParsr only considers a single escape character (see 
    # hypoparsr/dialect.R)
    escapechar <- if(quote.method == 'escape') "\\" else ""

    # NOTE: I don't think this case will actually happen, it would occur if 
    # there are mixed quotes in a file, each with no significance.
    if (!is.null(quotechar) && quotechar == "AMBIGUOUS")
        return (list(status="FAIL", status_msg="AMBIGUOUS_QUOTECHAR", 
                     dialect=NULL))

    dialect <- list(delimiter=delimiter, quotechar=quotechar, 
                    escapechar=escapechar)
    if (used.real.qc) {
        out <- list(status="OK", dialect=dialect, note="USED_REAL_QC")
    } else {
        out <- list(status="OK", dialect=dialect)
    }

    return(out)
}

prepare.result <- function(detect.out, filename, runtime)
{
    dialect <- detect.out['dialect']
    names(dialect) <- NULL

    status <- detect.out['status']
    names(status) <- NULL
    status <- status[[1]]
    status.msg <- detect.out['status_msg']

    hostname <- Sys.info()['nodename']
    names(hostname) <- NULL
    res <- list(
                status=status,
                filename=filename,
                detector='hypoparsr',
                runtime=runtime,
                hostname=hostname
                )
    if (!is.null(dialect[[1]]))
        res['dialect'] <- dialect
    if ("status_msg" %in% names(detect.out))
        res['status_msg'] <- detect.out['status_msg']
    if ("note" %in% names(detect.out))
        res['note'] <- detect.out['note']

    as.json <- toJSON(res)
    return(as.json)
}

dump.result <- function(output.file, dialect, filename, duration)
{
    res.json <- prepare.result(dialect, filename, duration)
    write(res.json, output.file, append=T)
}

load.previous <- function(output.file)
{
    previous <- c()
    if (!file.exists(output.file)) {
        printf("Ouput file %s does not exist. No previous results.\n", 
               output.file)
        return(previous)
    }

    lines <- readLines(output.file)
    for (line in lines) {
        record <- fromJSON(line)
        previous = c(previous, record['filename'])
    }
    return(previous)
}

main <- function(path.file, output.file)
{
    files <- readLines(path.file)
    previous <- load.previous(output.file)

    n_files <- length(files)
    n_previous <- length(previous)
    n_todo <- n_files - n_previous
    n_done <- 0

    for (filename in files) {
        if (filename %in% previous)
            next

        printf("[hypoparsr|%i/%i] Analyzing file: %s\n", n_done, n_todo, 
               filename)

        start.time <- Sys.time()
        dialect <- detect(filename)
        end.time <- Sys.time()
        duration <- difftime(end.time, start.time, units="secs")

        dump.result(output.file, dialect, filename, duration)
        n_done <- n_done + 1
    }
}

args <- commandArgs(trailingOnly=T)
if (length(args) == 1) {
    filename <- args[1]
    start.time <- Sys.time()
    dialect <- detect(filename)
    end.time <- Sys.time()
    duration <- difftime(end.time, start.time, units="secs")
    res.json <- prepare.result(dialect, filename, duration)
    printf("%s\n", res.json)
} else if (length(args) == 2) {
    main(args[1], args[2])
} else {
    printf("Usage: hypo.R [path.file output.file | csv.file]\n")
}
