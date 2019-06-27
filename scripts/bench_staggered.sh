#!/usr/bin/env bash

#PBS -q standard
#PBS -l select=1:ncpus=24:mem=420gb:pcmem=42gb
#PBS -N bnchkruniq
#PBS -W group_list=bhurwitz
#PBS -l place=pack:shared
#PBS -l walltime=12:00:00
#PBS -j oe

set -u

# Options
THREADS=24
PARALLEL_PROCS=1
OUT_DIR="/rsgrps/bhurwitz/hurwitzlab/data/kyclark/bench/krakenuniq-out"
RUN="$HOME//work/krakenuniq/scripts/run_krakenuniq.py"

# Don't change these
KRAKEN_DB="/rsgrps/bhurwitz/hurwitzlab/data/kyclark/kraken_db"
KRAKEN_BIN="/rsgrps/bhurwitz/hurwitzlab/src/kraken-1.1.1/bin"
KRAKENUNIQ_BIN="/rsgrps/bhurwitz/hurwitzlab/tools/krakenuniq/bin"
PATH="$KRAKEN_BIN:$KRAKENUNIQ_BIN:$PATH"

FILE="/rsgrps/bhurwitz/hurwitzlab/data/kyclark/jet2/mock/IonXpress_029_MockCommunity_staggered.fa"

echo "Started $(date)"
$RUN -q "$FILE" \
    -d "$KRAKEN_DB" \
    -o "$OUT_DIR" \
    -t $THREADS \
    -p $PARALLEL_PROCS \
    -f fasta 
echo "Ended $(date)"
