from click.testing import CliRunner
from webstore_manager.manager import main


def test_script():
    """ Check that running a script will not fail on cli. Catches wrong imports etc. """
    runner = CliRunner()
    result = runner.invoke(main, ['script', 'tests/files/script'])

    assert result.exit_code == 0
