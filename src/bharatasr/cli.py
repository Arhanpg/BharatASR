from __future__ import annotations

import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from bharatasr.glossary import build_whisper_prompt, load_glossary
from bharatasr.io import create_run_dir, get_audio_duration, save_result, write_json
from bharatasr.languages import resolve_language
from bharatasr.metrics import compare_run
from bharatasr.model_access import is_huggingface_access_error
from bharatasr.youtube import download_youtube_audio

app = typer.Typer(help="Benchmark ASR models on Indian-language audio.")
console = Console()


def _backend(name: str, whisper_model: str, glossary_prompt: str | None):
    if name == "whisper":
        from bharatasr.backends.whisper import WhisperBackend
        return WhisperBackend(model_id=whisper_model, initial_prompt=glossary_prompt)
    if name == "vaani-whisper-hindi":
        from bharatasr.backends.vaani_whisper_hindi import VaaniWhisperHindiBackend
        return VaaniWhisperHindiBackend()
    if name == "sravaani":
        from bharatasr.backends.sravaani import SraVaaniBackend
        return SraVaaniBackend(device=os.getenv("SRAVAANI_DEVICE", "cpu"))
    if name == "indicconformer":
        from bharatasr.backends.indicconformer import IndicConformerBackend
        return IndicConformerBackend()
    if name == "indictranscribe":
        from bharatasr.backends.indictranscribe import IndicTranscribeBackend
        return IndicTranscribeBackend()
    if name == "sarvam":
        from bharatasr.backends.sarvam import SarvamBackend
        return SarvamBackend()
    raise ValueError(f"Unknown backend: {name}")


def _source_metadata(audio_path: Path, fallback_url: str | None) -> dict[str, Any]:
    metadata_path = audio_path.with_suffix(".source.json")
    if metadata_path.is_file():
        try:
            return json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {"source": "local_audio" if fallback_url is None else "youtube", "webpage_url": fallback_url}


def _run_one_audio(
    audio_path: Path,
    requested_language: str,
    backend_language: str,
    selected: list[str],
    output: Path,
    whisper_model: str,
    glossary_prompt: str | None,
    source_url: str | None = None,
) -> Path:
    run_dir = create_run_dir(audio_path, output)
    duration = get_audio_duration(audio_path)
    source = _source_metadata(audio_path, source_url)
    write_json(run_dir / "input.json", {
        "audio_path": str(audio_path.resolve()),
        "audio_name": audio_path.name,
        "audio_duration_seconds": duration,
        "source_metadata": source,
        "language_requested": requested_language,
        "backend_language_argument": backend_language,
        "selected_models": selected,
        "glossary_prompt_enabled": bool(glossary_prompt),
        "created_at": datetime.now().astimezone().isoformat(),
    })

    rows = []
    for name in selected:
        started = time.perf_counter()
        backend = None
        try:
            if name == "indicconformer" and backend_language in {"auto", "prakrit"}:
                raise RuntimeError(
                    "Skipped: IndicConformer does not auto-detect language or offer a "
                    "dedicated Prakrit mode. Use a language-matched checkpoint and explicit code."
                )
            if name == "indicconformer" and not os.getenv("INDICCONFORMER_LANGUAGE"):
                raise RuntimeError("Skipped: set INDICCONFORMER_LANGUAGE to match the checkpoint.")
            if name == "vaani-whisper-hindi" and backend_language != "hi":
                raise RuntimeError(
                    "Skipped: Vaani Whisper-Small Hindi is monolingual. Specify --language hi."
                )

            backend = _backend(name, whisper_model, glossary_prompt)
            result = backend.transcribe(audio_path, backend_language)
            result.metadata.setdefault("audio_duration_seconds", duration)
            result.metadata["source_metadata"] = source
            result.metadata["language_requested_by_user"] = requested_language
            quality = save_result(run_dir, result, requested_language=requested_language)
            status = "empty_output" if not result.transcript.strip() else "completed"
            row = {
                "backend": name,
                "status": status,
                "transcript_quality": quality["status"],
                "elapsed_seconds": result.elapsed_seconds,
                "model": result.model,
                "language_detected": (
                    result.metadata.get("language_detected")
                    or result.metadata.get("language_detected_initial")
                    or result.metadata.get("language")
                ),
                "quality_flags": quality["flags"],
                "review_required": True,
            }
            rows.append(row)
            if status == "empty_output":
                console.print(f"[red]✗[/red] {audio_path.name} | {name}: empty output")
            elif quality["flags"]:
                console.print(
                    f"[yellow]![/yellow] {audio_path.name} | {name}: completed, "
                    f"{len(quality['flags'])} quality warning(s)"
                )
            else:
                console.print(f"[green]✓[/green] {audio_path.name} | {name}: completed; human review required")
        except Exception as exc:
            if is_huggingface_access_error(exc) or "Hugging Face denied access" in str(exc):
                error_status = "blocked_access"
            elif str(exc).startswith("Skipped:"):
                error_status = "skipped"
            else:
                error_status = "failed"
            error = {
                "backend": name,
                "status": error_status,
                "elapsed_seconds": time.perf_counter() - started,
                "error": f"{type(exc).__name__}: {exc}",
            }
            rows.append(error)
            write_json(run_dir / name / "error.json", error)
            label = "ACCESS NOT APPROVED" if error_status == "blocked_access" else error_status.upper()
            console.print(f"[yellow]![/yellow] {audio_path.name} | {name}: {label} — {exc}")
        finally:
            if backend is not None:
                try:
                    backend.close()
                except Exception:
                    pass

    write_json(run_dir / "run_summary.json", {
        "models": rows,
        "run_dir": str(run_dir),
        "manual_review_required": True,
        "note": (
            "A completed backend is not proof of transcript correctness. Inspect quality.json "
            "and transcript.review.md; calculate WER/CER only with a human-verified reference."
        ),
    })
    console.print(f"Outputs: [bold]{run_dir.resolve()}[/bold]")
    return run_dir


@app.command()
def run(
    audio: Path | None = typer.Option(None, "--audio", exists=True, readable=True),
    youtube_url: str | None = typer.Option(None, "--youtube-url", help="Public YouTube video or playlist URL; audio only."),
    language: str = typer.Option("auto", "--language", help="auto, Sanskrit, Prakrit (experimental/review-only), or an Indian language/code."),
    models: str = typer.Option("whisper", "--models", help="Comma-separated backends or 'all' (local only)."),
    output: Path = typer.Option(Path("outputs"), "--output"),
    whisper_model: str = typer.Option("small", "--whisper-model"),
    max_videos: int = typer.Option(20, "--max-videos", min=1, max=100, help="Safety cap for a YouTube playlist."),
    glossary: Path = typer.Option(Path("configs/sacred_terms.json"), "--glossary", exists=True, dir_okay=False),
    use_glossary: bool = typer.Option(False, "--use-glossary", help="Pass sacred-term hints to Whisper; this can bias decoding."),
    sarvam_opt_in: bool = typer.Option(False, "--enable-sarvam", help="Explicitly allow metered Sarvam API usage."),
    confirm_metered_api: bool = typer.Option(False, "--confirm-metered-api", help="Confirm possible consumption of paid credits."),
):
    """Transcribe a local audio file or a bounded YouTube video/playlist."""
    if (audio is None) == (youtube_url is None):
        raise typer.BadParameter("Provide exactly one of --audio or --youtube-url.")
    try:
        language_request = resolve_language(language)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    local_models = [
        "whisper", "vaani-whisper-hindi", "sravaani", "indicconformer", "indictranscribe"
    ]
    selected = local_models if models.strip().lower() == "all" else [
        item.strip().lower() for item in models.split(",") if item.strip()
    ]
    allowed = set(local_models + ["sarvam"])
    unknown = [item for item in selected if item not in allowed]
    if unknown:
        raise typer.BadParameter(f"Unknown backend(s): {', '.join(unknown)}")
    if "sarvam" in selected:
        if not sarvam_opt_in or not confirm_metered_api:
            raise typer.BadParameter("Sarvam is metered. Pass BOTH --enable-sarvam and --confirm-metered-api.")
        if not os.getenv("SARVAM_API_KEY"):
            raise typer.BadParameter("Set SARVAM_API_KEY before enabling Sarvam.")
    if not selected:
        raise typer.BadParameter("Select at least one backend.")

    audio_paths = (
        [audio] if audio is not None
        else download_youtube_audio(
            youtube_url or "", Path(".cache") / "youtube_audio", max_videos=max_videos
        )
    )
    glossary_prompt = build_whisper_prompt(load_glossary(glossary)) if use_glossary else None
    original_key = language_request.original.strip().casefold()
    backend_language = language_request.code or (
        "prakrit" if original_key in {"prakrit", "prākrit", "pali-prakrit"} else "auto"
    )
    if language_request.note:
        console.print(f"[yellow]Language note:[/yellow] {language_request.note}")

    for audio_path in audio_paths:
        _run_one_audio(
            audio_path=audio_path,
            requested_language=language_request.original,
            backend_language=backend_language,
            selected=selected,
            output=output,
            whisper_model=whisper_model,
            glossary_prompt=glossary_prompt,
            source_url=youtube_url,
        )


@app.command()
def compare(
    run: Path = typer.Option(..., "--run", exists=True, file_okay=False),
    reference: Path = typer.Option(..., "--reference", exists=True, dir_okay=False),
):
    """Calculate WER/CER against a human-verified reference transcript."""
    rows = compare_run(run, reference)
    comparison_dir = run / "comparison"
    comparison_dir.mkdir(parents=True, exist_ok=True)
    write_json(comparison_dir / "summary.json", rows)
    csv_path = comparison_dir / "summary.csv"
    if rows:
        with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    table = Table(title="BharatASR model comparison")
    for heading in ("Backend", "WER", "CER"):
        table.add_column(heading)
    for row in rows:
        table.add_row(row["backend"], f"{row['wer']:.4f}", f"{row['cer']:.4f}")
    console.print(table)
    console.print(f"Saved comparison: {comparison_dir.resolve()}")


if __name__ == "__main__":
    app()
