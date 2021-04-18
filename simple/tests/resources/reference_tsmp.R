# DEPRECATED - use the reference implementation from the original paper
# Reference matrix profile from the latest github release. This is only for the
# self-join, which seem to perform as expected from listening to various
# birdcalls.
library(tsmp)
full <- read.csv("tests/resources/birdcall/full.cens.csv", header=FALSE)
mp <- simple_fast(full, window_size=50)
write.table(
    t(mp$mp), "tests/resources/birdcall/full.cens.mp.csv", 
    row.names=FALSE, col.names=FALSE, sep=","
)
write.table(
    t(mp$pi), "tests/resources/birdcall/full.cens.pi.csv", 
    row.names=FALSE, col.names=FALSE, sep=","
)