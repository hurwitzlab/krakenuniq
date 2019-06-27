#!/usr/bin/env bash

#PBS -q standard
#PBS -l select=1:ncpus=24:mem=420gb:pcmem=42gb
#PBS -N krknuniq
#PBS -W group_list=bhurwitz
#PBS -l place=pack:shared
#PBS -l walltime=48:00:00
#PBS -j oe

set -u

# Optional arg to restrict processed dirs
DB_NAME=${1:-''}

# Options
THREADS=24
PARALLEL_PROCS=1
OUT_DIR="/rsgrps/bhurwitz/hurwitzlab/data/kyclark/krakenuniq-out"
IN_DIR="/rsgrps/bhurwitz/hurwitzlab/data/kyclark/jet2/"
RUN="$HOME/work/krakenuniq/scripts/run_krakenuniq.py"

# Don't change these
KRAKEN_DB="/rsgrps/bhurwitz/hurwitzlab/data/kyclark/kraken_db"
KRAKEN_BIN="/rsgrps/bhurwitz/hurwitzlab/src/kraken-1.1.1/bin"
KRAKENUNIQ_BIN="/rsgrps/bhurwitz/hurwitzlab/tools/krakenuniq/bin"
PATH="$KRAKEN_BIN:$KRAKENUNIQ_BIN:$PATH"

if [[ ! -d "$IN_DIR" ]]; then
    echo "IN_DIR \"$IN_DIR\" is not a directory"
    exit 1
fi

[[ ! -d "$OUT_DIR" ]] && mkdir -p "$OUT_DIR"

DIRS=$(mktemp)
find "$IN_DIR" -maxdepth 1 -mindepth 1 -type d > "$DIRS"

i=0
while read -r DIR; do
    DIR_NAME=$(basename "$DIR")

    [[ -n "$DB_NAME" ]] && [[ $DIR_NAME != $DB_NAME ]] && continue

    DIR_OUT="$OUT_DIR/$DIR_NAME"

    i=$((i+1))
    printf "%3d: %s\n" $i "$DIR_NAME"
    $RUN -q "$DIR" \
        -d "$KRAKEN_DB" \
        -o "$DIR_OUT" \
        -t $THREADS \
        -p $PARALLEL_PROCS \
        -f fasta 
done < "$DIRS"
rm "$DIRS"

echo "Ended $(date)"
echo "Processed $i directories, see OUT_DIR \"$OUT_DIR\""
