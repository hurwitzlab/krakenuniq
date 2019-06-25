#!/usr/bin/env python3
"""
Author : kyclark
Date   : 2019-06-25
Purpose: Run KrakenUniq
"""

import argparse
import logging
import os
import parallelprocs
import re
import sys
from pprint import pformat as pf
from collections import defaultdict


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Run KrakenUniq',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-q',
                        '--query',
                        metavar='str',
                        help='Input file/directory',
                        nargs='+',
                        required=True)

    parser.add_argument('-d',
                        '--kraken_db',
                        help='Kraken DB directory',
                        metavar='DIR',
                        type=str,
                        required=True)

    parser.add_argument('-o',
                        '--outdir',
                        metavar='DIR',
                        default='krakenuniq-out',
                        help='Output directory')

    parser.add_argument('-f',
                        '--input_format',
                        help='Input file format',
                        metavar='str',
                        type=str,
                        choices=['fasta', 'fastq'],
                        default='fasta')

    parser.add_argument('-t',
                        '--threads',
                        help='Number of threads',
                        metavar='int',
                        type=int,
                        default=24)

    parser.add_argument('-p',
                        '--num_procs',
                        help='Number of concurrent processes',
                        metavar='int',
                        type=int,
                        default=1)

    parser.add_argument('-O',
                        '--overwrite',
                        help='Overwrite existing reports',
                        action='store_true')

    parser.add_argument('-D',
                        '--debug',
                        help='Debug to ".log"',
                        action='store_true')

    parser.add_argument('--dry_run',
                        help='Dry run',
                        action='store_true')


    args = parser.parse_args()

    for q in args.query:
        if not any([os.path.isdir(q), os.path.isfile(q)]):
            parser.error('--query "{}" neither file nor directory'.format(q))

    return args


# --------------------------------------------------
def unique_extensions(files):
    exts = set()
    for file in files:
        _, ext = os.path.splitext(file)
        exts.add(ext[1:])  # skip leading "."

    return exts


# --------------------------------------------------
def find_input_files(query):
    """Find input files from list of files/dirs"""

    files = []
    for qry in query:
        if os.path.isdir(qry):
            for filename in os.scandir(qry):
                if filename.is_file():
                    files.append(filename.path)
        elif os.path.isfile(qry):
            files.append(qry)
        else:
            raise Exception(
                'query "{}" neither file nor directory'.format(qry))

    extensions = unique_extensions(files)
    paired_re = re.compile('(.+)[_-][Rr]?[12](?:_\d+)?\.(?:' +
                           '|'.join(extensions) + ')$')

    unpaired = []
    paired = defaultdict(list)
    for fname in files:
        basename = os.path.basename(fname)
        paired_match = paired_re.search(basename)

        if paired_match:
            sample_name = paired_match.group(1)
            paired[sample_name].append(fname)
        else:
            unpaired.append(fname)

    return {'paired': paired, 'unpaired': unpaired}


# --------------------------------------------------
def make_jobs(**args):
    """Run KrakenUniq"""

    files = args['files']

    if not isinstance(files, dict):
        raise Exception('Expected a dict')

    tmpl = ('krakenuniq --{input_format}-input --threads {threads} '
            '--db {db} --report-file {report} --output {out_file} {file}')

    if not 'unpaired' in files:
        files['unpaired'] = []

    file_args = []
    if 'paired' in files:
        for sample_name, pairs in files['paired'].items():
            if len(pairs) == 2:
                file_args.append(
                    (sample_name, '--paired {}'.format(' '.join(pairs))))
            else:
                files['unpaired'].extend(pairs)

    for file in files['unpaired']:
        file_args.append((os.path.basename(file), file))

    jobs = []
    for sample_name, file_arg in file_args:
        out_base = os.path.join(args['out_dir'], sample_name)
        report = out_base + '.report'

        if not os.path.isfile(report) or args.overwrite:
            jobs.append(
                tmpl.format(threads=args['threads'],
                            db=args['kraken_db'],
                            report=report,
                            input_format=args['input_format'],
                            out_file=out_base + '.out',
                            file=file_arg))

    return jobs


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    logging.basicConfig(
        filename='.log',
        filemode='w',
        level=logging.DEBUG if args.debug else logging.CRITICAL)

    files = find_input_files(args.query)
    logging.debug('found files =\n{}'.format(pf(files)))

    jobs = make_jobs(files=files,
                     out_dir=args.outdir,
                     file_format=args.input_format,
                     threads=args.threads,
                     input_format=args.input_format,
                     kraken_db=args.kraken_db)
    logging.debug('jobs =\n{}'.format('\n'.join(jobs)))

    if args.dry_run:
        print('Would run {} jobs'.format(len(jobs)))
    else:
        parallelprocs.run(jobs,
                          msg='Running KrakenUniq',
                          num_procs=args.num_procs,
                          verbose=True,
                          halt=1)

    print('Done.')


# --------------------------------------------------
if __name__ == '__main__':
    main()
