# Model integration status

| Model | Adapter | Language behavior | Credentials / setup |
|---|---|---|---|
| faster-whisper | Local, implemented | Automatic initial detection and multilingual per-segment decoding; Sanskrit language token; glossary prompt | Install requirements-whisper.txt |
| Indic-Transcribe Core / Flex | Local, implemented | Core documents automatic language ID, native script, code-mixing, and Sanskrit; 25 language coverage | Hugging Face access/model terms; install requirements-indictranscribe.txt |
| SraVaani 1.0 | Local, implemented | Model card supports 65 Indic languages and dialects including Sanskrit; path-based API | Gated Hugging Face access; HF_TOKEN |
| AI4Bharat IndicConformer | Local, implemented | Checkpoint-specific; no auto language detection in this adapter | AI4Bharat NeMo environment + .nemo checkpoint + INDICCONFORMER_LANGUAGE |
| Sarvam Saaras v4 | Hosted API, optional | Hosted speech-to-text; opt-in only | SARVAM_API_KEY; metered; explicit confirmation flags |

## Sanskrit / Prakrit safety

- Sanskrit is included in Indic-Transcribe Core and SraVaani's documented language coverage.
- The current integrated models do not document a dedicated Prakrit mode. BharatASR's Prakrit setting therefore uses automatic multilingual inference and marks the result for expert review.
- `configs/sacred_terms.json` supplies optional prompt hints. It never changes transcript text.
- Every successful model output includes `transcript.review.md`; do not quote mantras or scriptural passages before checking the audio and an authoritative text.

## Source references

- Whisper / faster-whisper: https://github.com/SYSTRAN/faster-whisper
- SraVaani 1.0: https://huggingface.co/ARTPARK-IISc/SraVaani-1.0
- IndicConformer: https://github.com/AI4Bharat/IndicConformerASR
- Indic-Transcribe Core: https://huggingface.co/bodhan-ai/indic-transcribe-core
- Indic-Transcribe Flex: https://huggingface.co/bodhan-ai/indic-transcribe-flex
- Sarvam STT: https://docs.sarvam.ai/api-reference/speech-to-text/transcribe
