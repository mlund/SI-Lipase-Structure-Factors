#!/bin/bash
#SBATCH -A snic2020-5-195
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH --mem-per-cpu=100
#SBATCH -t 168:00:00

#SBATCH -J B2_tll_r
#SBATCH -o out
#SBATCH -e err

module purge
module load GCC
module load CMake
module load pybind11

cd $SLURM_SUBMIT_DIR
OMP_NUM_THREADS=1;/home/marpoli/Work/faunus_parallel/faunus -i input.json --state state.json > out

