# BharatASR 🇮🇳

**An open-source benchmark for comparing speech-to-text (ASR) models on Indian languages.**

BharatASR runs multiple local/self-hosted ASR systems against the same audio files, stores each model's transcript independently, and produces comparable runtime and (when reference transcripts are provided) accuracy metrics.

> **Important:** No benchmark results are included until you run the models on your own audio and reference transcripts. A transcript by itself is not an accuracy score.

## What is included

| Backend | Type | Default availability | Notes |
|---|---|---|---|
| faster-whisper (Whisper) | Local | Enabled | Adapted from the working VidTrace implementation: VAD, word timestamps, CUDA detection and CPU fallback. |
| SraVaani 1.0 | Local | Optional | Project Vaani FastConformer model for Indian languages. Hugging Face access is gated; accept its model conditions and provide `HF_TOKEN`. |
| IndicConformer | Local | Optional / advanced | AI4Bharat NeMo checkpoint workflow. Requires a separately downloaded checkpoint and NeMo-compatible environment. |
| Indic-Transcribe Core / Flex | Local | Planned adapter | Newer AI4Bharat/Bodhan ASR family. Model loading interface and license conditions should be verified against its current model card before enabling. |
| Sarvam Saaras | Hosted API | Disabled | Optional only. API is metered; signup credits are limited and requests can incur charges after exhaustion. Not required for this project. |

The default setup does **not** require a Sarvam account, API key, payment method, or billing setup.

## Quick start (Windows PowerShell)

Python 3.10+ is required. Python 3.11 is a good starting point.

```powershell
git clone https://github.com/Arhanpg/BharatASR.git
cd BharatASR

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install FFmpeg and make sure `ffmpeg -version` works in a new terminal. Then install the local Whisper backend:

```powershell
pip install -r requirements-whisper.txt
```

Place audio in `data/audio/`. Supported input formats depend on FFmpeg/decoder support (WAV, MP3, M4A, FLAC and common formats).

## Run Whisper first

```powershell
python -m bharatasr run --audio data/audio/sample.wav --language hi --models whisper
```

Run all currently available local backends:

```powershell
python -m bharatasr run --audio data/audio/sample.wav --language hi --models all
```

Use `--language auto` for automatic language detection where supported. Model availability and language coverage differ; inspect the backend notes before comparing.

## Output layout

Every run receives its own timestamped directory. Each model writes into a separate folder:

```text
outputs/
  20261112_123000_sample/
    input.json
    whisper/
      transcript.txt
      transcript.json
      segments.json
      metrics.json
    sravaani/
      transcript.txt
      transcript.json
      metrics.json
    indicconformer/
      ...
    sarvam/
      ... (only when explicitly enabled)
    comparison/
      summary.json
      summary.csv
```

A failed/locked/unavailable model is recorded as a failure and does not erase successful outputs from other models.

## Compare accuracy (WER / CER)

Create a UTF-8 reference transcript at `data/references/sample.txt`, then run:

```powershell
python -m bharatasr compare --run outputs/20261112_123000_sample --reference data/references/sample.txt
```

The comparison calculates:
- **WER** (word error rate): word-level substitutions, deletions and insertions divided by reference word count.
- **CER** (character error rate): character-level edit distance divided by reference character count.
- **Runtime** and **real-time factor** when audio duration can be read.
- **Output availability** and backend error status.

Use the same normalization policy and the same reference text for every model. For research-quality results, document whether punctuation, case, numerals, Unicode normalization, and script variants are normalized. Do not compare WER across different normalization policies.

## Optional backends

### SraVaani 1.0

1. Request/accept access on the [SraVaani Hugging Face model page](https://huggingface.co/ARTPARK-IISc/SraVaani-1.0).
2. Create a Hugging Face read token and set it in your shell:

```powershell
$env:HF_TOKEN = "hf_your_token"
pip install -r requirements-sravaani.txt
python -m bharatasr run --audio data/audio/sample.wav --language hi --models sravaani
```

The checkpoint is roughly 900 MB and model inference requires PyTorch. On a 4 GB GPU, use CPU or expect memory pressure; this adapter chooses CPU by default unless configured otherwise.

### AI4Bharat IndicConformer

This backend requires NeMo and a compatible downloaded `.nemo` checkpoint. Follow the official [IndicConformerASR repository](https://github.com/AI4Bharat/IndicConformerASR) and AI4Bharat documentation for checkpoint setup. Set `INDICCONFORMER_CHECKPOINT` to the local checkpoint path and install the backend's dedicated dependencies. It is intentionally kept out of the base install because NeMo has a large and environment-sensitive dependency stack.

### Sarvam (optional; paid after free credits)

Sarvam provides a signup credit, but speech-to-text is usage-metered. This project therefore **does not call Sarvam unless you explicitly pass `--enable-sarvam`** and set `SARVAM_API_KEY`. The CLI also requires a second explicit confirmation flag `--confirm-metered-api` to prevent accidental requests.

No billing configuration is needed for the local models. Do not add a payment method just to run the default benchmark.

## Fair benchmarking protocol

1. Use identical audio bytes for every backend.
2. Keep reference transcripts human-verified and separate from model output.
3. Record language, dialect/region, duration, sample rate, channel count and noise conditions.
4. Run each backend more than once when measuring latency; report warm-up separately.
5. Report CPU/GPU, RAM/VRAM, precision, model/checkpoint revision and package versions.
6. Do not treat a model's language-detection output as ground truth.
7. Report unavailable languages and model errors rather than silently excluding them.
8. Publish dataset provenance and permissions. Do not commit private or copyrighted recordings without permission.

## Current status

This is the initial benchmark scaffold. Whisper is the first implemented backend. SraVaani is an optional gated local backend. IndicConformer is documented as an advanced/manual checkpoint setup. Sarvam is disabled by default and requires explicit opt-in. Actual model accuracy must be established by running the benchmark with references.

## References

- [VidTrace](https://github.com/Arhanpg/VidTrace) — source of the faster-whisper implementation adapted here.
- [Project Vaani — SraVaani 1.0](https://vaani.iisc.ac.in/models/sravaani)
- [SraVaani 1.0 model card](https://huggingface.co/ARTPARK-IISc/SraVaani-1.0)
- [AI4Bharat IndicConformer](https://github.com/AI4Bharat/IndicConformerASR)
- [Bodhan AI / AI4Bharat Indic-Transcribe](https://ai4bharat.iitm.ac.in/blog/bodhan-asr/)
- [Sarvam pricing](https://docs.sarvam.ai/api/getting-started/pricing)

## License

See [LICENSE](LICENSE). Each model and service remains subject to its own license and terms.
