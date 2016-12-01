from click.testing import CliRunner
from webstore_deployer.deployer import init


def test_init():
    runner = CliRunner()
    result = runner.invoke(init, ['testing_client_ID'])

    assert result.exit_code == 0
    assert result.output.find('testing_client_ID') != -1
    assert result.output.find('testing_client_IDnic') == -1
