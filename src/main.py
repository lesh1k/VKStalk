from core.vkstalk import VKStalk
import sys
import re
from helpers.h_logging import setup_logging
from helpers.h_argparse import get_args

if __name__ == "__main__":
    cli_args = vars(get_args())
    setup_logging(cli_args['vk_id'])
    vk_object = VKStalk(cli_args['vk_id'])
    vk_object.scrape()
