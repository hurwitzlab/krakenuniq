#!/usr/bin/env bash

#PBS -q standard
#PBS -l select=1:ncpus=28:mem=168gb:pcmem=6gb
#PBS -N bam2fa
#PBS -W group_list=bhurwitz
#PBS -l place=pack:shared
#PBS -l walltime=12:00:00
#PBS -j oe

set -u

module load samtools

DIR="/rsgrps/bhurwitz/hurwitzlab/data/raw/GWATTS/WGS/NeutropenicFever"
OUT_DIR="/rsgrps/bhurwitz/hurwitzlab/data/kyclark/jet2/np"
BAM2FA="$HOME/work/krakenuniq/scripts/bam2fx.py"

$BAM2FA -f fasta -o "$OUT_DIR" -p 8 $DIR/*.bam

echo "Done."
