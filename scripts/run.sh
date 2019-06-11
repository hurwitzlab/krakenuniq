#!/usr/bin/env bash

#PBS -q standard
#PBS -l select=1:ncpus=24:mem=420gb:pcmem=42gb
#PBS -N krknuniq
#PBS -W group_list=bhurwitz
#PBS -l place=pack:shared
#PBS -l walltime=48:00:00
#PBS -j oe

set -u

DB="/rsgrps/bhurwitz/hurwitzlab/data/kyclark/kraken_db"
KRAKEN_BIN="/rsgrps/bhurwitz/hurwitzlab/src/kraken-1.1.1/bin"
KRAKENUNIQ_BIN="/rsgrps/bhurwitz/hurwitzlab/tools/krakenuniq/bin"
PATH="$KRAKEN_BIN:$KRAKENUNIQ_BIN:$PATH"
THREADS=24
OUT_DIR="/rsgrps/bhurwitz/hurwitzlab/data/kyclark/krakenuniq-out"
IN_DIR="/rsgrps/bhurwitz/hurwitzlab/data/kyclark/jet2/"

if [[ ! -d "$IN_DIR" ]]; then
    echo "IN_DIR \"$IN_DIR\" is not a directory"
    exit 1
fi

[[ ! -d "$OUT_DIR" ]] && mkdir -p "$OUT_DIR"

FILES=$(mktemp)
find "$IN_DIR" -type f > "$FILES"

NUM=$(wc -l "$FILES" | awk '{print $1}')

echo "Found NUM \"$NUM\" files in IN_DIR \"$IN_DIR\""

if [[ $NUM -lt 1 ]]; then
    echo "Nothing to do"
    exit 1
fi

echo "Started $(date)"

i=0
while read -r FILE; do
    BASE=$(basename "$FILE")
    DIR_NAME=$(basename $(dirname "$FILE"))
    DIR_OUT="$OUT_DIR/$DIR_NAME"
    [[ ! -d "$DIR_OUT" ]] && mkdir -p "$DIR_OUT"

    REPORT="$DIR_OUT/$BASE"

    if [[ ! -f "$REPORT" ]]; then
        i=$((i+1))
        printf "%3d: %s %s\n" $i "$DIR_NAME" "$BASE"
        krakenuniq --fasta-input --threads $THREADS --db "$DB" \
            --report-file "$REPORT" --output "$DIR_OUT/$BASE.out" "$FILE"
    fi
done < "$FILES"

rm "$FILES"
echo "Processed $i files"
echo "Ended $(date)"
echo "See OUT_DIR \"$OUT_DIR\""
