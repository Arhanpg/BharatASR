import inspect

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
    assert "urls_file" in parameters


def test_urls_file_processes_batch_entries(tmp_path, monkeypatch):
    audio1 = tmp_path / "audio1.wav"
    audio2 = tmp_path / "audio2.wav"
    audio1.write_bytes(b"data1")
    audio2.write_bytes(b"data2")
    batch_file = tmp_path / "batch.txt"
    batch_file.write_text(f"{audio1}\n{audio2}\n", encoding="utf-8")

    run_dirs_created = []

    def fake_run_one_audio(**kwargs):
        r_dir = tmp_path / f"run_{kwargs['audio_path'].stem}"
        r_dir.mkdir(exist_ok=True)
        (r_dir / "run_summary.json").write_text('{"transcripts_generated": 1}', encoding="utf-8")
        run_dirs_created.append(kwargs["audio_path"])
        return r_dir

    monkeypatch.setattr(cli, "_run_one_audio", fake_run_one_audio)
    result = CliRunner().invoke(
        cli.app,
        [
            "run",
            "--urls-file", str(batch_file),
            "--models", "whisper",
        ],
    )
    assert result.exit_code == 0, result.output
    assert len(run_dirs_created) == 2


def test_compare_cli_command(tmp_path):
    run_dir = tmp_path / "run_sample"
    model_dir = run_dir / "whisper"
    model_dir.mkdir(parents=True)
    (model_dir / "transcript.txt").write_text("नमस्ते भारत", encoding="utf-8")
    ref_file = tmp_path / "ref.txt"
    ref_file.write_text("नमस्ते भारत", encoding="utf-8")

    result = CliRunner().invoke(
        cli.app,
        [
            "compare",
            "--run", str(run_dir),
            "--reference", str(ref_file),
        ],
    )
    assert result.exit_code == 0, result.output
    assert (run_dir / "comparison" / "summary.json").is_file()
    assert (run_dir / "comparison" / "summary.csv").is_file()


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
