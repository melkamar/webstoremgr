import click
from chrome_store import commands as chrome_commands
from . import logging_helper

logger = logging_helper.get_logger(__file__)


@click.group()
@click.option('-v', '--verbose', count=True,
              help="Much verbosity. May be repeated multiple times. More v's, more info!")
def main(verbose):
    # TODO remove this, let user decide the verbosity level.
    verbose = 2

    logging_helper.set_level(30 - verbose * 10)


main.add_command(chrome_commands.chrome)

if __name__ == '__main__':
    main()
