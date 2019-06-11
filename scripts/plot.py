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
from dire import die


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
                        help='Minimum %',
                        metavar='float',
                        type=float,
                        default=0.)

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

    return parser.parse_args()


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()
    rank = args.rank
    min_pct = args.min

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

    if not assigned:
        die('No data!')

    df = pd.DataFrame(assigned)
    plt.scatter(x=df['sample'], y=df['tax_name'], s=df['pct'], alpha=0.5)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=45, ha='right')
    plt.gcf().subplots_adjust(bottom=.4, left=.3)
    plt.ylabel('Organism')
    plt.xlabel('Sample')
    if args.title:
        plt.title(args.title)

    plt.savefig(args.outfile)


# --------------------------------------------------
if __name__ == '__main__':
    main()
