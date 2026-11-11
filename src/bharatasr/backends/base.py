from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from bharatasr.types import TranscriptionResult


class ASRBackend(ABC):
    name: str
    model_id: str

    @abstractmethod
    def transcribe(self, audio_path: Path, language: str = "auto") -> TranscriptionResult:
        raise NotImplementedError

    def close(self) -> None:
        """Release model resources when supported."""
