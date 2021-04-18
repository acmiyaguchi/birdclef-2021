source("external/simple_fast/SiMPle_Fast.m")
full = csvread("tests/resources/birdcall/full.cens.csv");
motif = csvread("tests/resources/birdcall/motif.cens.0.csv");

[mp, pi] = SiMPle_Fast(full, motif, 10);

csvwrite("tests/resources/birdcall/motif.cens.0.mp.csv", mp)
csvwrite("tests/resources/birdcall/motif.cens.0.pi.csv", pi)
