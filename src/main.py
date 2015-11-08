from core.vkstalk import VKStalk
from helpers.h_logging import setup_logging
from helpers.h_argparse import get_args
from core.summarizer import write_summary

import sys
import re


if __name__ == "__main__":
    cli_args = vars(get_args())
    setup_logging(cli_args['vk_id'])
    if cli_args['summary']:
        write_summary(cli_args['vk_id'], max_days=cli_args['summary_max_days'],
                      to_file=cli_args['summary_to_file'],
                      to_console=cli_args['summary_to_console'])
        exit()
    vk_object = VKStalk(cli_args['vk_id'])
    vk_object.scrape()
