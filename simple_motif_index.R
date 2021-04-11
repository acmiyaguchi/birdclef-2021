#!/usr/bin/Rscript
library(RcppCNPy)
library(tsmp)

args = commandArgs(trailingOnly=TRUE)

if(length(args)!=2) {
    stop("Requires two arguments: PATH and WINDOW_SIZE")
}

mp <- simple_fast(npyLoad(args[1]), window_size=strtoi(args[2]), verbose=1)
min_val <- min_mp_idx(mp)
cat("[", min_val[1], ", ", min_val[2], "]", sep="")
