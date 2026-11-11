from typer.testing import CliRunner

from bharatasr.cli import app


def test_cli_help_lists_run_and_compare():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout
    assert "compare" in result.stdout


def test_run_help_exposes_playlist_safety_cap():
    result = CliRunner().invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "--max-videos" in result.stdout
    assert "--glossary" in result.stdout
