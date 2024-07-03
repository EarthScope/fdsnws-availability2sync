#!/usr/bin/env python3

from datetime import datetime, timezone
import argparse
import textwrap
import os.path
import sys
import re

__version__ = '0.1.0'


def read_input(input):
    timespans = []
    delimiter = None

    for line in input:
        if line.startswith('#'):
            # Extract delimiter from header (e.g. GeoCSV format)
            if line.startswith('#delimiter:'):
                delimiter = re.findall(r'#delimiter:\s*([^\s]+)\s*', line.strip())[0]

            # Skip all header lines
            continue

        if line.startswith('Network'):
            # Skip field description header line
            continue

        # Split on delimter, expecting 8 fields: network, station, location, channel, quality, samplerate, start, end
        if delimiter is None:
            values = line.strip().split()
        else:
            values = line.strip().split(delimiter)

        timespans.append(values)

    return timespans


def print_sync(dccid, timespans):

    # Print SYNC header line
    year_day = datetime.now(tz=timezone.utc).strftime('%Y,%j')
    print(f'{dccid}|{year_day}')

    for timespan in timespans:
        (network, station, location, channel, quality, samplerate, start, end) = timespan

        # Convert start and end times to SEED ordinate date format
        seed_start = seed_datetime(start)
        seed_end = seed_datetime(end)

        # Print SYNC timespan line
        print(f'{network}|{station}|{location}|{channel}|{seed_start}|{seed_end}||{samplerate}||||{quality}||||')


def seed_datetime(dtstr):
    (datestr, timestr) = dtstr.split('T')

    dt = datetime.fromisoformat(datestr)

    return datetime.strftime(dt, '%Y,%j') + ',' + timestr.strip('Z')


def main():
    parser = argparse.ArgumentParser(description='Convert fdsnws-availability output to legacy SYNC format',
                                     prog=os.path.basename(sys.argv[0]),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(f"""
                                     Convert output from an fdsnws-availability request to the legacy SYNC format.
                                     The fdnsws-availability output is defined in the web service specification:
                                     https://fdsn.org/webservices/

                                     The output fdsnws-availability should be the full granularity of the selected
                                     data, i.e. using the "query" method.  Output from the "extent" method does not
                                     contain gaps or overlaps and is not suitable for most uses of SYNC output.
                                     """))

    parser.add_argument('--version', '-V', action='version', version=f'%(prog)s v{__version__}')
    parser.add_argument('--dccid', default='DCC',
                        help='DCC ID to use in SYNC header (default: DCC)')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help='Input fdsnws-availability result file (default: stdin)')

    args = parser.parse_args()

    timespans = read_input(args.infile)

    print_sync(args.dccid, timespans)


if __name__ == '__main__':
    sys.exit(main())
