import inspect

from typer.testing import CliRunner

from bharatasr.cli import app, run


def test_cli_help_lists_run_and_compare():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout
    assert "compare" in result.stdout


def test_run_has_vad_control_and_existing_options():
    parameters = inspect.signature(run).parameters
    assert "max_videos" in parameters
    assert "use_glossary" in parameters
    assert "glossary" in parameters
    assert "whisper_vad" in parameters


def test_run_help_exposes_vad_ab_controls():
    result = CliRunner().invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "--whisper-vad" in result.stdout
    assert "--no-whisper-vad" in result.stdout
