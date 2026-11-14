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
from bharatasr.io import create_run_dir, get_audio_duration, save_result, summarize_run, write_json
from bharatasr.languages import resolve_language
from bharatasr.metrics import compare_run
from bharatasr.model_access import is_huggingface_access_error
from bharatasr.youtube import download_youtube_audio

app = typer.Typer(help="Benchmark ASR models on Indian-language audio.")
console = Console()


def _backend(name: str, whisper_model: str, glossary_prompt: str | None, whisper_vad: bool = True):
    if name == "whisper":
        from bharatasr.backends.whisper import WhisperBackend
        return WhisperBackend(model_id=whisper_model, initial_prompt=glossary_prompt, vad_filter=whisper_vad)
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
    whisper_vad: bool = True,
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
        "whisper_vad_enabled": whisper_vad,
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
                raise RuntimeError("Skipped: Vaani Whisper-Small Hindi is monolingual. Specify --language hi.")

            backend = _backend(name, whisper_model, glossary_prompt, whisper_vad)
            result = backend.transcribe(audio_path, backend_language)
            result.metadata.setdefault("audio_duration_seconds", duration)
            result.metadata["source_metadata"] = source
            result.metadata["language_requested_by_user"] = requested_language

            quality = save_result(run_dir, result, requested_language=requested_language)
            if not result.transcript.strip():
                status = "empty_output"
            elif quality["flags"]:
                status = "completed_needs_review"
            else:
                status = "completed"
            rows.append({
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
            })
            if status == "empty_output":
                console.print(f"[red]✗[/red] {audio_path.name} | {name}: empty output")
            elif status == "completed_needs_review":
                console.print(
                    f"[yellow]![/yellow] {audio_path.name} | {name}: text saved, "
                    f"{len(quality['flags'])} warning(s); review required"
                )
            else:
                console.print(f"[green]✓[/green] {audio_path.name} | {name}: text saved; human verification still required")
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
                "error_type": type(exc).__name__,
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
                except Exception as close_exc:
                    console.print(f"[dim]Cleanup warning for {name}: {close_exc}[/dim]")

    summary = summarize_run(rows, run_dir)
    write_json(run_dir / "run_summary.json", summary)
    console.print(
        f"Run status: [bold]{summary['overall_status']}[/bold] "
        f"({summary['transcripts_generated']}/{summary['backend_count']} non-empty transcripts)"
    )
    console.print(f"Outputs: [bold]{run_dir.resolve()}[/bold]")
    return run_dir


@app.command()
def run(
    audio: Path | None = typer.Option(None, "--audio", exists=True, readable=True),
    youtube_url: str | None = typer.Option(None, "--youtube-url", help="Public YouTube video or playlist URL; audio only."),
    urls_file: Path | None = typer.Option(None, "--urls-file", help="Path to text file containing audio file paths or YouTube URLs, one per line."),
    language: str = typer.Option("auto", "--language", help="auto or an Indian language/code. Prakrit is experimental and requires manual review."),
    models: str = typer.Option("whisper", "--models", help="Comma-separated backends or 'all' (all local adapters; unavailable ones are reported)."),
    output: Path = typer.Option(Path("outputs"), "--output"),
    whisper_model: str = typer.Option("small", "--whisper-model"),
    whisper_vad: bool = typer.Option(True, "--whisper-vad/--no-whisper-vad", help="Enable/disable Silero VAD; compare both on identical audio."),
    max_videos: int = typer.Option(20, "--max-videos", min=1, max=100, help="Safety cap for a YouTube playlist."),
    glossary: Path = typer.Option(Path("configs/sacred_terms.json"), "--glossary", exists=True, dir_okay=False),
    use_glossary: bool = typer.Option(False, "--use-glossary", help="Pass sacred-term hints to Whisper; this can bias decoding."),
    sarvam_opt_in: bool = typer.Option(False, "--enable-sarvam", help="Explicitly allow metered Sarvam API usage."),
    confirm_metered_api: bool = typer.Option(False, "--confirm-metered-api", help="Confirm possible consumption of paid credits."),
):
    """Transcribe a local audio file, YouTube video/playlist, or a file of URLs."""
    inputs_count = sum(x is not None for x in (audio, youtube_url, urls_file))
    if inputs_count != 1:
        raise typer.BadParameter("Provide exactly one of --audio, --youtube-url, or --urls-file.")
    try:
        language_request = resolve_language(language)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    local_models = ["whisper", "vaani-whisper-hindi", "sravaani", "indicconformer", "indictranscribe"]
    selected = local_models if models.strip().lower() == "all" else [
        item.strip().lower() for item in models.split(",") if item.strip()
    ]
    allowed = set(local_models + ["sarvam"])
    unknown = [item for item in selected if item not in allowed]
    if unknown:
        raise typer.BadParameter(f"Unknown backend(s): {', '.join(unknown)}")
    if len(selected) != len(set(selected)):
        raise typer.BadParameter("Do not specify the same backend more than once.")
    if "sarvam" in selected:
        if not sarvam_opt_in or not confirm_metered_api:
            raise typer.BadParameter("Sarvam is metered. Pass BOTH --enable-sarvam and --confirm-metered-api.")
        if not os.getenv("SARVAM_API_KEY"):
            raise typer.BadParameter("Set SARVAM_API_KEY before enabling Sarvam.")
    if not selected:
        raise typer.BadParameter("Select at least one backend.")

    items_to_run: list[tuple[Path, str | None]] = []
    if audio is not None:
        items_to_run.append((audio, None))
    elif youtube_url is not None:
        downloaded = download_youtube_audio(youtube_url, Path(".cache") / "youtube_audio", max_videos=max_videos)
        for p in downloaded:
            items_to_run.append((p, youtube_url))
    elif urls_file is not None:
        if not urls_file.is_file():
            raise typer.BadParameter(f"URLs file not found: {urls_file}")
        lines = [line.strip() for line in urls_file.read_text(encoding="utf-8").splitlines()]
        targets = [line for line in lines if line and not line.startswith("#")]
        if not targets:
            raise typer.BadParameter(f"No valid URLs or audio paths found in {urls_file}")
        for target in targets:
            if target.startswith(("http://", "https://", "youtu")):
                try:
                    downloaded = download_youtube_audio(target, Path(".cache") / "youtube_audio", max_videos=max_videos)
                    for p in downloaded:
                        items_to_run.append((p, target))
                except Exception as exc:
                    console.print(f"[yellow]Failed to prepare YouTube audio for {target}: {exc}[/yellow]")
            else:
                p = Path(target)
                if not p.is_file():
                    console.print(f"[yellow]Audio file not found, skipping: {target}[/yellow]")
                    continue
                items_to_run.append((p, None))

    if not items_to_run:
        raise typer.BadParameter("No valid audio files were prepared for transcription.")

    glossary_prompt = build_whisper_prompt(load_glossary(glossary)) if use_glossary else None
    original_key = language_request.original.strip().casefold()
    backend_language = language_request.code or (
        "prakrit" if original_key in {"prakrit", "prākrit", "pali-prakrit"} else "auto"
    )
    if language_request.note:
        console.print(f"[yellow]Language note:[/yellow] {language_request.note}")

    run_dirs = []
    for audio_path, src_url in items_to_run:
        run_dirs.append(_run_one_audio(
            audio_path=audio_path,
            requested_language=language_request.original,
            backend_language=backend_language,
            selected=selected,
            output=output,
            whisper_model=whisper_model,
            glossary_prompt=glossary_prompt,
            source_url=src_url,
            whisper_vad=whisper_vad,
        ))

    summaries = []
    for run_dir in run_dirs:
        summary_path = run_dir / "run_summary.json"
        if summary_path.exists():
            summaries.append(json.loads(summary_path.read_text(encoding="utf-8")))
    if summaries and all(summary.get("transcripts_generated", 0) == 0 for summary in summaries):
        console.print("[red]No backend produced a non-empty transcript. Inspect error.json and run_summary.json in the output folders.[/red]")
        raise typer.Exit(code=1)


def _compare_one_run(run: Path, reference: Path) -> list[dict]:
    rows = compare_run(run, reference)
    if not rows:
        raise typer.BadParameter("No model transcript.txt files found in this run directory. Run ASR first.")
    comparison_dir = run / "comparison"
    comparison_dir.mkdir(parents=True, exist_ok=True)
    write_json(comparison_dir / "summary.json", rows)
    csv_path = comparison_dir / "summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    table = Table(title="BharatASR model comparison (lower WER/CER is better)")
    for heading in ("Backend", "WER", "CER", "Ref words", "Hyp words", "Sub", "Del", "Ins", "Hits"):
        table.add_column(heading)
    for row in rows:
        table.add_row(
            row["backend"], f"{row['wer']:.4f}", f"{row['cer']:.4f}",
            str(row["reference_words"]), str(row["hypothesis_words"]),
            str(row.get("substitutions", 0)), str(row.get("deletions", 0)),
            str(row.get("insertions", 0)), str(row.get("hits", 0)),
        )
    console.print(table)
    console.print(f"Saved comparison: {comparison_dir.resolve()}")
    return rows


@app.command()
def compare(
    run: Path | None = typer.Option(None, "--run", help="Single run directory to evaluate."),
    reference: Path | None = typer.Option(None, "--reference", help="Reference transcript file for a single run."),
    runs_dir: Path | None = typer.Option(None, "--runs-dir", help="Directory of runs (e.g. outputs) to compare."),
    references_dir: Path = typer.Option(Path("data/references"), "--references-dir", help="Directory of reference transcripts (<video_id>.txt)."),
):
    """Calculate WER/CER against a human-verified reference transcript."""
    if run is not None:
        if reference is None:
            raise typer.BadParameter("Provide --reference when using --run.")
        _compare_one_run(run, reference)
    elif runs_dir is not None:
        if not runs_dir.is_dir():
            raise typer.BadParameter(f"Runs directory not found: {runs_dir}")
        run_folders = sorted(p for p in runs_dir.iterdir() if p.is_dir() and (p / "input.json").is_file())
        if not run_folders:
            raise typer.BadParameter(f"No run folders with input.json found in {runs_dir}")

        all_comparison_rows = []
        matched_runs = 0
        for r_dir in run_folders:
            input_meta = {}
            try:
                input_meta = json.loads((r_dir / "input.json").read_text(encoding="utf-8"))
            except Exception:
                pass
            video_id = (
                input_meta.get("source_metadata", {}).get("video_id")
                or Path(input_meta.get("audio_path", "")).stem
                or r_dir.name.split("_")[-1]
            )
            candidate_refs = [
                references_dir / f"{video_id}.txt",
                references_dir / f"{r_dir.name}.txt",
            ]
            ref_file = next((f for f in candidate_refs if f.is_file()), None)
            if ref_file is None:
                continue

            matched_runs += 1
            console.print(f"[bold]Evaluating {r_dir.name} against {ref_file.name}...[/bold]")
            run_rows = _compare_one_run(r_dir, ref_file)
            for row in run_rows:
                all_comparison_rows.append({"run": r_dir.name, "video_id": video_id, **row})

        if not matched_runs:
            console.print(f"[yellow]No matching reference transcripts found in {references_dir} for runs in {runs_dir}.[/yellow]")
            return

        summary_json = runs_dir / "benchmark_summary.json"
        summary_csv = runs_dir / "benchmark_summary.csv"
        write_json(summary_json, all_comparison_rows)
        with summary_csv.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(all_comparison_rows[0]))
            writer.writeheader()
            writer.writerows(all_comparison_rows)
        console.print(f"[green]Saved overall benchmark summary across {matched_runs} run(s):[/green] {summary_csv}")
    else:
        raise typer.BadParameter("Provide either --run with --reference, or --runs-dir.")


if __name__ == "__main__":
    app()
