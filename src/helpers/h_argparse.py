from config import settings

import argparse


def get_args():
    parser = argparse.ArgumentParser(prog=settings.PROJECT_NAME)
    parser.add_argument(
        'vk_id',
        type=str,
        help='String. User VK id (e.g. 45156687 OR alexei.dvorac)',
    )
    parser.add_argument(
        '-s', '--summary',
        action='store_const',
        const=True,
        dest='summary',
        help="This flag triggers summary generation."
    )
    parser.add_argument(
        '-md', '--max-days',
        type=int,
        default=settings.DEFAULT_SUMMARY_PERIOD,
        dest='summary_max_days',
        help="int, max days range for summary. DEFAULT: %(default)s"
    )
    parser.add_argument(
        '-stf', '--summary-to-file',
        type=bool,
        default=True,
        dest='summary_to_file',
        help="if True, summary will be written to file. DEFAULT: %(default)s"
    )
    parser.add_argument(
        '-stc', '--summary-to-console',
        type=bool,
        default=True,
        dest='summary_to_console',
        help="if True, summary will be written to console. DEFAULT: %(default)s"
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s {}'.format(settings.VERSION),
        help="Print program version"
    )
    args = parser.parse_args()
    return args
