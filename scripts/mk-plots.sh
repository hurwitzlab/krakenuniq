#!/usr/bin/env bash

OUT_DIR="kraken-plots"
[[ ! -d "$OUT_DIR" ]] && mkdir -p "$OUT_DIR"

#rm -f $OUT_DIR/*

PLOT="./plot.py"
DIRS=$(mktemp)
KRAKEN_OUT="/rsgrps/bhurwitz/hurwitzlab/data/kyclark/krakenuniq-out"
find "$KRAKEN_OUT" -mindepth 1 -maxdepth 1 -type d > "$DIRS"

JOBS=$(mktemp)
for RANK in genus species; do
    for MIN_PCT in 0.00 0.01 0.02; do
        while read -r DIR; do
            DIR_NAME=$(basename "$DIR")
            echo ">>> $DIR_NAME $RANK $MIN_PCT"

            OUT_BASE="$OUT_DIR/$DIR_NAME.$RANK.$MIN_PCT"
            if [[ ! -f "$OUT_BASE.png" ]]; then
                echo "$PLOT -r \"$RANK\" -m \"$MIN_PCT\" -t \"$DIR_NAME\" -o \"$OUT_BASE.png\" -d \"$OUT_BASE.csv\" $DIR/*.report" >> "$JOBS"
            fi
        done < "$DIRS"
    done
done
rm "$DIRS"

echo "Starting jobs"
parallel -j 8 < "$JOBS"
rm "$JOBS"
echo "Done see OUT_DIR \"$OUT_DIR\"."
