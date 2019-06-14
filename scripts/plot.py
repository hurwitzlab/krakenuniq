#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@email.arizona.edu>
Date   : 2019-06-11
Purpose: Plot KrakenUniq out
"""

import argparse
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Plot KrakenUniq out',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('file',
                        metavar='FILE',
                        nargs='+',
                        type=argparse.FileType('r'),
                        help='KrakenUniq output files')

    parser.add_argument(
        '-r',
        '--rank',
        help='Tax rank',
        metavar='str',
        type=str,
        choices=[
            'class', 'family', 'genus', 'infraorder', 'kingdom', 'no rank',
            'order', 'parvorder', 'phylum', 'rank', 'species', 'species group',
            'species subgroup', 'subclass', 'subfamily', 'suborder',
            'subphylum', 'subspecies', 'subtribe', 'superclass', 'superfamily',
            'superkingdom', 'superorder', 'tribe'
        ],
        default='species')

    parser.add_argument('-m',
                        '--min',
                        help='Minimum percent',
                        metavar='float',
                        type=float,
                        default=0.2)

    parser.add_argument('-t',
                        '--title',
                        help='Figure title',
                        metavar='str',
                        type=str,
                        default='')

    parser.add_argument('-o',
                        '--outfile',
                        help='Output file',
                        metavar='str',
                        type=str,
                        default='bubble.png')

    parser.add_argument('-c',
                        '--counts',
                        help='Plot read counts not percent',
                        action='store_true')

    return parser.parse_args()


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()
    rank = args.rank
    min_pct = args.min

    # Kraken out has comment-style "#" lines and blanks before content
    def lines(fh):
        for line in map(lambda s: s.rstrip('\n'), fh):
            if line and not line.startswith('#'):
                yield line

    assigned = []
    for i, fh in enumerate(args.file, start=1):
        basename = os.path.basename(fh.name)
        print('{:3}: {}'.format(i, basename))

        reader = csv.DictReader(lines(fh), delimiter='\t')
        for rec in filter(lambda r: r['rank'] == rank, reader):
            pct = float(rec.get('%'))
            if min_pct and pct < min_pct:
                continue

            assigned.append({
                'sample': basename,
                'tax_id': rec['taxID'],
                'tax_name': rec['taxName'].strip(),
                'pct': pct,
                'reads': int(rec['reads'])
            })

    num_samples = len(args.file)
    num_taxa = len(assigned)
    width = 5 if num_samples < 5 else (3 + (num_samples * .18))
    height = 5 if num_taxa < 5 else num_taxa * .05
    plt.figure(figsize=(width, height))
    df = pd.DataFrame(assigned)
    if args.counts:
        df['reads'] = (df['reads'] / df['reads'].max()) * 100

    plt.scatter(x=df['sample'],
                y=df['tax_name'],
                s=df['reads'] if args.counts else df['pct'],
                alpha=0.5)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=20, ha='right')
    plt.gcf().subplots_adjust(bottom=.4, left=.4)
    plt.ylabel('Organism')
    plt.xlabel('Sample')

    plt.title('{}: Min. {}%'.format(args.title or '{} abundance'.format(rank),
                                    min_pct))

    plt.savefig(args.outfile)
    print('Done plotted {} samples and {} taxa to "{}"'.format(
        num_samples, num_taxa, args.outfile))


# --------------------------------------------------
if __name__ == '__main__':
    main()
