# ensure that we're sourcing relative from the root, or else this whole script
# breaks
source("external/tsmp/simple.R")

# Use birdcall
full <- read.csv("tests/resources/birdcall/full.cens.csv", header=FALSE)
motif <- read.csv("tests/resources/birdcall/motif.cens.0.csv", header=FALSE)
ref_full_mp <- as.vector(t(read.csv("tests/resources/birdcall/full.cens.mp.csv", header=FALSE)))
ref_full_pi <- as.vector(t(read.csv("tests/resources/birdcall/full.cens.pi.csv", header=FALSE)))
ref_motif_mp <- as.vector(t(read.csv("tests/resources/birdcall/motif.cens.0.mp.csv", header=FALSE)))
ref_motif_pi <- as.vector(t(read.csv("tests/resources/birdcall/motif.cens.0.pi.csv", header=FALSE)))


print("test self-join full")
res <- simple_fast(full, window_size=50)
stopifnot(all.equal(as.vector(res$mp), ref_full_mp))
stopifnot(all.equal(as.vector(res$pi), ref_full_pi))

print("test ab-join fill-motif")
res <- simple_fast(full, motif, window_size=10)
# we allow small differences between the joins, but not enough to be noticable
stopifnot(all.equal(as.vector(res$mp), ref_motif_mp, tolerance=0.001))
# there is a difference in the first element...
stopifnot(all.equal(as.vector(res$pi), ref_motif_pi, tolerance=1))
