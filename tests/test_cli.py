import inspect
from pathlib import Path

from typer.testing import CliRunner

import bharatasr.cli as cli


def test_cli_help_lists_run_and_compare():
    result = CliRunner().invoke(cli.app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout
    assert "compare" in result.stdout


def test_run_has_vad_control_and_existing_options():
    parameters = inspect.signature(cli.run).parameters
    assert "max_videos" in parameters
    assert "use_glossary" in parameters
    assert "glossary" in parameters
    assert "whisper_vad" in parameters


def test_no_whisper_vad_flag_is_passed_to_run(tmp_path, monkeypatch):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"fake audio file")
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    observed = {}

    def fake_run_one_audio(**kwargs):
        observed["whisper_vad"] = kwargs["whisper_vad"]
        return run_dir

    monkeypatch.setattr(cli, "_run_one_audio", fake_run_one_audio)
    result = CliRunner().invoke(
        cli.app,
        [
            "run",
            "--audio", str(audio),
            "--models", "whisper",
            "--no-whisper-vad",
        ],
    )

    assert result.exit_code == 0, result.output
    assert observed["whisper_vad"] is False


def test_whisper_vad_flag_is_passed_to_run(tmp_path, monkeypatch):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"fake audio file")
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    observed = {}

    def fake_run_one_audio(**kwargs):
        observed["whisper_vad"] = kwargs["whisper_vad"]
        return run_dir

    monkeypatch.setattr(cli, "_run_one_audio", fake_run_one_audio)
    result = CliRunner().invoke(
        cli.app,
        [
            "run",
            "--audio", str(audio),
            "--models", "whisper",
            "--whisper-vad",
        ],
    )

    assert result.exit_code == 0, result.output
    assert observed["whisper_vad"] is True
