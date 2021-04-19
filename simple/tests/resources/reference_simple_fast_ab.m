source("external/simple_fast/SiMPle_Fast.m")
full = csvread("tests/resources/birdcall/full.cens.csv");
motif = csvread("tests/resources/birdcall/motif.cens.0.csv");

[mp, pi] = SiMPle_Fast(full, motif, 10);

csvwrite("tests/resources/birdcall/motif.cens.0.mp.csv", mp)
csvwrite("tests/resources/birdcall/motif.cens.0.pi.csv", pi)

[X, _, sumx2] = fastfindNNPre(full, 10);
size(X)
csvwrite("tests/resources/birdcall/full.cens.fft.csv", real(X))
csvwrite("tests/resources/birdcall/full.cens.sumx2.csv", sumx2)
