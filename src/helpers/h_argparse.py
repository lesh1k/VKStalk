from config.settings import PROJECT_NAME

import argparse


def get_args():
    parser = argparse.ArgumentParser(prog=PROJECT_NAME)
    parser.add_argument(
        'vk_id',
        type=str,
        help='String. User VK id (e.g. 45156687 OR alexei.dvorac)',
    )
    # parser.add_argument('-d', '--debug',
    #                     type=bool,
    #                     dest='debug',
    #                     help="Boolean. Enable/disable logging debug messages."
    #                     )
    args = parser.parse_args()
    return args
