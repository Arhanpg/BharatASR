# Model integration status

| Model | Adapter | Where it runs | Credentials / setup |
|---|---|---|---|
| faster-whisper | Implemented | Local CPU or CUDA | Install requirements-whisper.txt |
| SraVaani 1.0 | Implemented using official model-card API | Local CPU (default) or CUDA | Gated Hugging Face access; HF_TOKEN |
| AI4Bharat IndicConformer | Implemented with NeMo CTC workflow | Local CPU or CUDA | AI4Bharat NeMo environment + matching .nemo checkpoint |
| Indic-Transcribe Core / Flex | Implemented by invoking official bundled inference.py | Local | Install requirements-indictranscribe.txt; model downloaded from HF |
| Sarvam Saaras v4 | Implemented optional API adapter | Hosted API | SARVAM_API_KEY; metered; explicit opt-in flags |

## Model source references

- Whisper / faster-whisper: https://github.com/SYSTRAN/faster-whisper
- SraVaani 1.0: https://huggingface.co/ARTPARK-IISc/SraVaani-1.0
- IndicConformer: https://github.com/AI4Bharat/IndicConformerASR
- Indic-Transcribe Core: https://huggingface.co/bodhan-ai/indic-transcribe-core
- Indic-Transcribe Flex: https://huggingface.co/bodhan-ai/indic-transcribe-flex
- Sarvam STT: https://docs.sarvam.ai/api-reference/speech-to-text/transcribe

## Caveats

- The SraVaani model card requires agreement to share contact details and acceptance of gated access conditions, despite the model's MIT license.
- IndicConformer requires the AI4Bharat NeMo fork and the correct monolingual language checkpoint or multilingual checkpoint. The `language_id` must match the model's expected language code.
- Indic-Transcribe delegates preprocessing, chunking and decoding to the official checkpoint's inference script. It preserves stdout/stderr tails in metadata so output-format changes can be diagnosed. The model can consume substantial disk, RAM and GPU memory.
- Sarvam provides a small signup credit according to its current pricing page, but its speech-to-text endpoint is metered. When credits are exhausted, requests fail for insufficient quota until credits are added; this project does not initiate top-ups.
- No benchmark scores are prepopulated. All reported scores must come from a specific run and human-verified reference audio/transcript pair.
