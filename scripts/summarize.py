#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@email.arizona.edu>
Date   : 2019-06-11
Purpose: Summarize KrakenUniq out
"""

import argparse
import csv
import os
import pandas as pd
import re


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

    parser.add_argument('-o',
                        '--outfile',
                        help='Output file',
                        metavar='str',
                        type=str,
                        default='summary.csv')

    return parser.parse_args()


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()
    rank = args.rank
    min_pct = args.min
    out_file = args.outfile

    def lines(fh):
        for line in map(lambda s: s.rstrip('\n'), fh):
            if line and not line.startswith('#'):
                yield line

    data = []
    for i, fh in enumerate(args.file, start=1):
        basename = os.path.basename(fh.name)
        print('{:3}: {}'.format(i, basename))

        reader = csv.DictReader(lines(fh), delimiter='\t')
        for rec in filter(lambda r: r['rank'] == rank, reader):

            pct = float(rec.get('%'))
            if min_pct and pct < min_pct:
                continue

            data.append({
                'sample': basename,
                'tax_id': rec['taxID'],
                'tax_name': rec['taxName'].strip(),
                'pct': pct,
                'reads': int(rec['reads']),
            })

    if data:
        df = pd.DataFrame(data)
        df.to_csv(out_file, index=False)
        print('Done, at min {} exported {} to "{}"'.format(min_pct, len(data), out_file))
    else:
        print('No data!')


# --------------------------------------------------
if __name__ == '__main__':
    main()
