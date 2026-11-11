from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TranscriptSegment:
    index: int
    start: float | None
    end: float | None
    text: str
    words: list[dict[str, Any]] = field(default_factory=list)
    language: str | None = None


@dataclass
class TranscriptionResult:
    backend: str
    model: str
    transcript: str
    segments: list[TranscriptSegment]
    metadata: dict[str, Any]
    elapsed_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "model": self.model,
            "transcript": self.transcript,
            "segments": [asdict(segment) for segment in self.segments],
            "metadata": self.metadata,
            "elapsed_seconds": self.elapsed_seconds,
        }
