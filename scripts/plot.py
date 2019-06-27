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
                        help='Minimum percent',
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

    parser.add_argument('-d',
                        '--dataout',
                        help='Output data file',
                        metavar='str',
                        type=str,
                        default='')

    parser.add_argument('-O',
                        '--open_image',
                        help='Open the image when done',
                        action='store_true')

    return parser.parse_args()


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()
    rank_wanted = args.rank
    min_pct = args.min

    def lines(fh):
        for line in map(lambda s: s.rstrip('\n'), fh):
            if line and not line.startswith('#'):
                yield line

    num_root, num_unclassified = 0, 0
    assigned = []
    for i, fh in enumerate(args.file, start=1):
        basename = os.path.basename(fh.name)
        print('{:3}: {}'.format(i, basename))

        reader = csv.DictReader(lines(fh), delimiter='\t')
        for rec in reader:
            try:
                reads = int(rec['reads'])
            except:
                continue

            tax_name = rec['taxName'].strip()
            if tax_name == 'root':
                num_root = reads
                continue
            elif tax_name == 'unclassified':
                num_unclassified = reads
                continue
            elif rec['rank'] == rank_wanted:
                continue

            total_reads = num_root + num_unclassified
            if total_reads == 0:
                die('Failed to find root/unclassified')

            pct = reads / total_reads
            if min_pct and pct < min_pct:
                continue

            assigned.append({
                'sample': basename,
                'tax_id': rec['taxID'],
                'tax_name': tax_name,
                'pct': pct,
                'reads': reads
            })

    if not assigned:
        die('No data!')

    df = pd.DataFrame(assigned)
    if args.dataout:
        df.to_csv(args.dataout, index=False)

    num_found = len(assigned)
    print('At a {}% found {} {}'.format(min_pct, num_found, rank_wanted))
    if num_found > 1000:
        die('Too many to plot')

    x = df['sample']
    y = df['tax_name']
    plt.figure(figsize=(5 + len(x.unique()) / 5, len(y.unique()) / 3))
    plt.scatter(x, y, s=df['pct'], alpha=0.5)
    plt.xticks(rotation=45, ha='right')
    plt.gcf().subplots_adjust(bottom=.4, left=.4)
    plt.ylabel('Organism')
    plt.xlabel('Sample')
    if args.title:
        plt.title(args.title)

    plt.savefig(args.outfile)

    print('Done, see outfile "{}"'.format(args.outfile))

    if args.open_image:
        plt.show()

# --------------------------------------------------
if __name__ == '__main__':
    main()
