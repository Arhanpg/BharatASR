from __future__ import annotations

import csv
import os
import time
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from bharatasr.io import create_run_dir, save_result, write_json
from bharatasr.metrics import compare_run

app = typer.Typer(help="Benchmark ASR models on Indian-language audio.")
console = Console()


def _backend(name: str, whisper_model: str = "small"):
    if name == "whisper":
        from bharatasr.backends.whisper import WhisperBackend
        return WhisperBackend(model_id=whisper_model)
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


@app.command()
def run(
    audio: Path = typer.Option(..., "--audio", exists=True, readable=True),
    language: str = typer.Option("auto", "--language", help="Language code, e.g. hi, mr, kn, ta, auto."),
    models: str = typer.Option("whisper", "--models", help="Comma-separated names or 'all' (local only)."),
    output: Path = typer.Option(Path("outputs"), "--output"),
    whisper_model: str = typer.Option("small", "--whisper-model"),
    sarvam_opt_in: bool = typer.Option(False, "--enable-sarvam", help="Explicitly allow metered Sarvam API usage."),
    confirm_metered_api: bool = typer.Option(False, "--confirm-metered-api", help="Confirm possible consumption of paid credits."),
):
    """Transcribe one audio file with one or more backends; persist outputs independently."""
    local_models = ["whisper", "sravaani", "indicconformer", "indictranscribe"]
    selected = local_models if models.strip().lower() == "all" else [
        item.strip().lower() for item in models.split(",") if item.strip()
    ]
    if "sarvam" in selected:
        if not sarvam_opt_in or not confirm_metered_api:
            raise typer.BadParameter(
                "Sarvam is metered. Pass BOTH --enable-sarvam and --confirm-metered-api to continue."
            )
        if not os.getenv("SARVAM_API_KEY"):
            raise typer.BadParameter("Set SARVAM_API_KEY before enabling Sarvam.")
    if not selected:
        raise typer.BadParameter("Select at least one backend.")

    run_dir = create_run_dir(audio, output)
    write_json(run_dir / "input.json", {
        "audio_path": str(audio.resolve()), "audio_name": audio.name,
        "language_requested": language, "selected_models": selected,
        "created_at": datetime.now().astimezone().isoformat(),
    })
    rows = []
    for name in selected:
        started = time.perf_counter()
        backend = None
        try:
            backend = _backend(name, whisper_model=whisper_model)
            result = backend.transcribe(audio, language)
            save_result(run_dir, result)
            rows.append({
                "backend": name, "status": "success",
                "elapsed_seconds": result.elapsed_seconds, "model": result.model,
            })
            console.print(f"[green]✓[/green] {name}: {result.elapsed_seconds:.2f}s")
        except Exception as exc:
            rows.append({
                "backend": name, "status": "failed",
                "elapsed_seconds": time.perf_counter() - started,
                "error": f"{type(exc).__name__}: {exc}",
            })
            write_json(run_dir / name / "error.json", rows[-1])
            console.print(f"[red]✗[/red] {name}: {exc}")
        finally:
            if backend is not None:
                try:
                    backend.close()
                except Exception:
                    pass

    write_json(run_dir / "run_summary.json", {"models": rows, "run_dir": str(run_dir)})
    console.print(f"\nOutputs: [bold]{run_dir.resolve()}[/bold]")


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
