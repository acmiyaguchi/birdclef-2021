source("external/simple_fast/SiMPle_SelfFast.m")
full = csvread("tests/resources/birdcall/full.cens.csv");

[mp, pi] = SiMPle_SelfFast(full, 50);

csvwrite("tests/resources/birdcall/full.cens.mp.csv", mp)
csvwrite("tests/resources/birdcall/full.cens.pi.csv", pi)
