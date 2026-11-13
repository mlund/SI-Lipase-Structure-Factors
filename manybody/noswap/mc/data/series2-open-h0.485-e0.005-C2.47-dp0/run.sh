#!/bin/bash

cargo run --release --features gpu --manifest-path ~/github/pripps/Cargo.toml -- \
-a single_bead.yaml \
-i structure.xyz \
-x traj.xtc \
-s 1 \
--num-molecules 325 \
direct --pmax 100
