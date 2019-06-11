#!/usr/bin/env bash

#PBS -q standard
#PBS -l select=1:ncpus=10:mem=420gb:pcmem=42gb
#PBS -N krknbld
#PBS -W group_list=bhurwitz
#PBS -l place=pack:shared
#PBS -l walltime=48:00:00
#PBS -j oe


KRAKEN_BIN="/rsgrps/bhurwitz/hurwitzlab/src/kraken-1.1.1/bin"
DB="/rsgrps/bhurwitz/hurwitzlab/data/kyclark/kraken_db"

PATH="$KRAKEN_BIN:$PATH"

set -u

echo "Started $(date)"
echo ">> Downloading taxonomy to \"$DB\""
kraken-build --download-taxonomy --db "$DB"

for LIB in bacteria archaea plasmid viral human; do
    echo ">> Building lib \"$LIB\""
    kraken-build --download-library "$LIB" --db "$DB"
done

echo ">> Building db"
kraken-build --db "$DB" --build --jellyfish-hash-size 100M --threads 40

echo "Ended $(date)"
