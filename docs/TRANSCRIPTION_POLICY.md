# Sanskrit, Prakrit and mantra transcription policy

BharatASR stores model hypotheses exactly as generated. It deliberately does not replace a model's output with glossary spellings or "correct" a mantra by guessing.

## Language identification

- Default to `--language auto`.
- Indic-Transcribe Core documents automatic language identification, native-script output for 25 Indian languages, and code-mixed speech support. Sanskrit is included. Its documented language list does not include a dedicated Prakrit mode.
- faster-whisper uses automatic initial language detection and multilingual per-segment decoding when language is automatic.
- SraVaani supports broad Indic language/dialect coverage, including Sanskrit, and its model card documents a path-based transcribe API. Check the output against the audio.
- IndicConformer is checkpoint-specific in this adapter and is skipped for automatic-language or Prakrit requests.

## Sanskrit and Prakrit

Sanskrit and Prakrit are not interchangeable. A Prakrit word must not be silently rendered as a Sanskrit-looking equivalent. For a recording containing Prakrit:
1. Use `--language Prakrit` to keep the request explicit while allowing multilingual automatic inference.
2. Expect a mandatory review warning.
3. Preserve the complete unmodified model transcript.
4. Verify the precise Prakrit variety and spelling against the original audio and a knowledgeable reviewer.

None of the currently integrated models is documented as a dedicated Prakrit-specialized recognizer.

## Mantra and sacred syllable handling

- `configs/sacred_terms.json` provides optional prompt hints such as OM/ॐ, HRIM/ह्रीं, KLIEM/क्लीं, and selected Jain terms.
- The glossary influences Whisper's decoding context only. It is not a dictionary-based auto-corrector.
- Roman forms such as `HRIM`, `HREEM`, `KLIEM`, and `KLEEM` must not be automatically converted to Devanagari.
- Retain the original punctuation and script emitted by the model in `transcript.txt` and `transcript.json`.
- Review repetitions, visarga, anusvara, chandrabindu, vowel length, conjuncts, and syllable boundaries.

## Provenance and reproducibility

Every YouTube run records video ID, title, webpage URL, channel, upload date, duration and available YouTube language metadata. Audio is converted to mono 16 kHz WAV before model inference so all backends receive the same samples. Playlist runs are bounded by `--max-videos`.

## Manual review is mandatory

An ASR model can omit, repeat or substitute a mantra syllable even when the rest of a lecture is accurate. Each backend output therefore includes `transcript.review.md` and review flags. An ASR confidence score is not a guarantee of mantra correctness.
