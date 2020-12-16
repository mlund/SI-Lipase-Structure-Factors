#!/bin/bash
#SBATCH -A lu2020-2-5
#SBATCH -N 1
#SBATCH --tasks-per-node=3
#SBATCH --mem-per-cpu=100
#SBATCH -t 168:00:00
#SBATCH -J TLL_run_3
#SBATCH --partition=lu

module purge
module load GCC
module load CMake
module load pybind11

cd SLURM_SUBMIT_DIR

OMP_NUM_THREADS=3;/home/marpoli/Work/faunus_parallel/faunus -i tll.json -o tll.out --state state.json
