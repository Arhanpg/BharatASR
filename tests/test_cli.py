import inspect

from typer.testing import CliRunner

from bharatasr.cli import app, run


def test_cli_help_lists_run_and_compare():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout
    assert "compare" in result.stdout


def test_run_has_playlist_glossary_options():
    parameters = inspect.signature(run).parameters
    assert "max_videos" in parameters
    assert "use_glossary" in parameters
    assert "glossary" in parameters
