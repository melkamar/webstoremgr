import click

from . import logging_helper, util
from .chrome_store import commands as chrome_commands
from .firefox_store import commands as firefox_commands
from .script_parser.parser import Parser

logger = logging_helper.get_logger(__file__)


@click.group()
@click.option('-v', '--verbose', count=True,
              help="Much verbosity. May be repeated multiple times. More v's, more info!")
def main(verbose):
    logging_helper.set_level(30 - verbose * 10)

    logger.info("Logging into file: {}".format(logging_helper.log_file))
    logger.debug("Using temporary directory: {}".format(util.build_dir))


@main.command('script')
@click.argument('file', required=True)
def script(file):
    logger.info("Executing script {}".format(file))
    p = Parser(script_fn=file)
    p.execute()


main.add_command(chrome_commands.chrome)
main.add_command(firefox_commands.firefox)
# For any other platforms, add their commands here.

if __name__ == '__main__':
    main()
