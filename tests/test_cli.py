import inspect

from typer.testing import CliRunner

from bharatasr.cli import app


def test_cli_help_lists_run_and_compare():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout
    assert "compare" in result.stdout


def test_run_options_include_playlist_cap_and_glossary_path():
    command = next(item for item in app.registered_commands if item.name == "run")
    parameters = inspect.signature(command.callback).parameters
    assert "max_videos" in parameters
    assert "glossary" in parameters
