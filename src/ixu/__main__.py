"""
Main module
"""
import argparse
import logging
from .commands import server

from .commands.finder import CommandFinder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M'
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Project to better visualize Gitlab issues statistics")
    parser.add_argument("resource", help="System resource")
    parser.add_argument("action", help="Resource action to be executed")

    try:
        args = parser.parse_args()
        CommandFinder.find(args.resource, args.action)(**(args.__dict__))
    except (KeyError, NotImplementedError) as err:
        parser.print_help()
