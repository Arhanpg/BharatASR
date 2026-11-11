# BharatASR 🇮🇳

**An open-source benchmark for comparing speech-to-text (ASR) models on Indian languages.**

BharatASR runs multiple local/self-hosted ASR systems against the same audio files, stores each model's transcript independently, and produces comparable runtime and (when reference transcripts are provided) accuracy metrics.

> A transcript is not an accuracy score. WER/CER are calculated only when you provide a human-verified reference transcript.

## Model lineup

| Backend | Type | Availability | Notes |
|---|---|---|---|
| faster-whisper (Whisper) | Local | Implemented | Adapted from VidTrace: VAD, word timestamps, CUDA detection and CPU fallback. |
| SraVaani 1.0 | Local | Implemented | Project Vaani FastConformer; model card reports 65 Indian languages/dialects. Gated Hugging Face access; accept conditions and set `HF_TOKEN`. |
| AI4Bharat IndicConformer | Local | Implemented | Official NeMo CTC/RNNT checkpoint workflow; download a .nemo model and set its path. |
| Indic-Transcribe Core / Flex | Local | Implemented | Runs the official model-packaged `inference.py` script; choose Core or Flex with `INDIC_TRANSCRIBE_MODEL`. |
| Sarvam Saaras v4 | Hosted API | Optional / disabled | Signup includes ₹100 credits; usage is metered. It is excluded from `all` and needs two explicit CLI confirmations. No payment method is needed for local backends. |

## Quick start — Windows PowerShell

Python 3.10+ is required. Python 3.11 is recommended.

```powershell
git clone https://github.com/Arhanpg/BharatASR.git
cd BharatASR
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
pip install -r requirements-whisper.txt
```

Install FFmpeg and ensure `ffmpeg -version` works in a new terminal. For current YouTube extraction, also install a supported JavaScript runtime (Deno is recommended by yt-dlp): `winget install -e --id DenoLand.Deno`, then verify `deno --version`. Place an audio file in `data/audio/`.

## First run — Whisper

```powershell
python -m bharatasr run --audio data/audio/sample.wav --language hi --models whisper
```

Whisper defaults to the `small` checkpoint to be friendlier to GPUs with 4 GB VRAM. Change it when needed:

```powershell
python -m bharatasr run --audio data/audio/sample.wav --language hi --models whisper --whisper-model medium
```

## Run multiple open models

Install optional backends separately, then run:

```powershell
python -m bharatasr run --audio data/audio/sample.wav --language hi --models whisper,sravaani,indicconformer,indictranscribe
```

Or use `--models all` to run all local backends. It never enables Sarvam. A backend that is not installed, has no checkpoint, or is gated will create an `error.json` in its own output folder without stopping other backends.

Use `--language auto` by default. You may also specify a language name or code such as `hi`, `mr`, `kn`, `ta`, `te`, `bn`, `gu`, `ml`, `pa`, `or`, `as`, or `sa`. `--language Prakrit` is an experimental review-only mode: it keeps automatic multilingual inference and never pretends Prakrit is a supported dedicated model language.

## Optional local model setup

### 1. SraVaani 1.0 (Project Vaani)

The model card reports a ~430M parameter FastConformer, ~900 MB FP16 checkpoint and 65 Indian languages/dialects. Access is gated: sign in to Hugging Face, accept the model conditions, and create a read token.

```powershell
$env:HF_TOKEN = "hf_your_token"
pip install -r requirements-sravaani.txt
python -m bharatasr run --audio data/audio/sample.wav --language hi --models sravaani
```

This adapter uses CPU by default to avoid VRAM pressure on 4 GB GPUs. Set `SRAVAANI_DEVICE=cuda` only when you have sufficient free VRAM.

Model card: https://huggingface.co/ARTPARK-IISc/SraVaani-1.0

### 2. AI4Bharat IndicConformer

AI4Bharat provides a multilingual 600M checkpoint and language-specific NeMo checkpoints. The model is a hybrid RNNT/CTC system. Follow the official AI4Bharat NeMo fork installation instructions in a dedicated Linux/WSL environment, then download the checkpoint for your language.

First install the AI4Bharat NeMo fork in a dedicated Linux/WSL environment, exactly as required by the model authors:

```bash
git clone https://github.com/AI4Bharat/NeMo.git
cd NeMo
git checkout nemo-v2
bash reinstall.sh
```

Then, from the Python environment where that fork is installed, run BharatASR:

```bash
export INDICCONFORMER_CHECKPOINT="$HOME/models/indicconformer_hi.nemo"
export INDICCONFORMER_LANGUAGE=hi
export INDICCONFORMER_DEVICE=cpu
python -m bharatasr run --audio data/audio/sample.wav --language hi --models indicconformer
```

The adapter uses NeMo's generic `ASRModel.restore_from` loader so the checkpoint's hybrid RNNT/CTC model class is restored from its own metadata. CPU is the default; use `INDICCONFORMER_DEVICE=cuda` only when enough VRAM is available. The checkpoint and language code must match. For model downloads, install steps and the language list, see https://github.com/AI4Bharat/IndicConformerASR.

### 3. AI4Bharat / Bodhan Indic-Transcribe Core or Flex

Install the model runner dependencies:

```powershell
pip install -r requirements-indictranscribe.txt
```

The backend downloads the official Hugging Face model repository on first use and invokes its bundled `inference.py`. Both checkpoints require agreeing to their gated Hugging Face terms and using the Indic Open Model License (plus the base model's terms); these are not MIT/Apache-licensed checkpoints. Core is the default; set Flex to compare the flexible checkpoint:

```powershell
$env:INDIC_TRANSCRIBE_MODEL = "bodhan-ai/indic-transcribe-flex"
python -m bharatasr run --audio data/audio/sample.wav --language hi --models indictranscribe
```

Use `bodhan-ai/indic-transcribe-core` for the default Core model. Both Core and Flex are about 4.6 GB on disk and use a 1.2B-parameter architecture, so neither is a sensible GPU choice for your 4 GB RTX 3050. The runner forces CPU by default (`INDIC_TRANSCRIBE_DEVICE=cpu`). Only set `$env:INDIC_TRANSCRIBE_DEVICE = "cuda"` to explicitly try GPU inference on a machine with enough VRAM. The model script performs its own long-audio chunking. First download can be large and inference may be slow on CPU. Model card and usage: https://huggingface.co/bodhan-ai/indic-transcribe-core and https://huggingface.co/bodhan-ai/indic-transcribe-flex.

### 4. Sarvam Saaras v4 — optional hosted API

Sarvam is **not required**. Official documentation currently describes ₹100 signup credits; requests are metered, and when credits are exhausted the API returns an insufficient-quota error until credits are added. The project never calls Sarvam unless you explicitly pass both flags below.

```powershell
pip install sarvamai
$env:SARVAM_API_KEY = "your_api_key"
python -m bharatasr run --audio data/audio/sample.wav --language hi --models sarvam --enable-sarvam --confirm-metered-api
```

The synchronous Sarvam REST endpoint supports audio up to 30 seconds; longer recordings need its separate batch endpoint, which is not yet wired into this initial adapter. Try it only on short clips. This confirmation does not add a payment method or top up credits. Do not run the Sarvam backend if you want strictly local inference. Pricing and API docs: https://docs.sarvam.ai/api/getting-started/pricing and https://docs.sarvam.ai/api-reference/speech-to-text/transcribe.

## Output structure

Every execution gets a unique timestamped run directory. Each model writes to its own folder:

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
      segments.json
      metrics.json
    indicconformer/
      ...
    indictranscribe/
      ...
    comparison/
      summary.json
      summary.csv
```

The Sarvam folder appears only when you explicitly enable it. Failed backends receive an `error.json`; successful results remain intact.


## YouTube video and playlist input

VidTrace's YouTube extraction workflow is also carried into BharatASR: yt-dlp downloads **audio only**, FFmpeg converts it to WAV, and each downloaded video is benchmarked independently with the selected backends.

```powershell
pip install -r requirements-youtube.txt
# Install FFmpeg and confirm: ffmpeg -version

python -m bharatasr run --youtube-url "https://www.youtube.com/watch?v=VIDEO_ID" --language auto --models whisper,indictranscribe

# Or a playlist (each successfully downloaded item gets its own output run)
python -m bharatasr run --youtube-url "https://www.youtube.com/playlist?list=PLAYLIST_ID" --language auto --max-videos 20 --models all
```

Downloaded audio is cached under `.cache/youtube_audio/`, normalized to mono 16 kHz PCM WAV, and accompanied by source metadata. Playlist downloads are limited to 20 videos by default; change the limit explicitly with `--max-videos` (1–100). The downloader is audio-only and does not configure cookies or access-control bypass. Do not publish or commit copyrighted audio or transcripts without the required permissions.

## Sanskrit, Prakrit and mantra preservation

BharatASR includes `configs/sacred_terms.json` as an optional Whisper vocabulary hint file. It contains forms such as OM/ॐ, HRIM/ह्रीं, KLIEM/क्लीं, and selected Jain terminology. These are hints only: transcript text is never rewritten, transliterated or corrected automatically. Each backend saves `transcript.review.md` with manual-review warnings. For Prakrit, use `--language Prakrit`; automatic multilingual recognition is attempted, but no integrated model currently documents a dedicated Prakrit mode. See [the transcription policy](docs/TRANSCRIPTION_POLICY.md) for the review rules.

## Accuracy evaluation (WER / CER)

Create a UTF-8 reference transcript at `data/references/sample.txt`. Make sure it is manually verified against the audio.

```powershell
python -m bharatasr compare --run outputs/20261112_123000_sample --reference data/references/sample.txt
```

The comparator calculates:
- **WER** — word error rate (substitutions + deletions + insertions divided by reference words).
- **CER** — character error rate (edit distance divided by reference characters).
- Hypothesis/reference word counts.

Normalization applies Unicode NFC, case-folding, punctuation removal and whitespace collapsing. For Indic scripts, CER can be a more stable complementary metric. Before publishing, state the normalization rules, ensure one reference per audio, and use the same reference for every model. WER can be script/tokenization-sensitive, especially for code-mixed speech.

Runtime, audio duration, device, precision and model metadata are saved separately per backend. Do not compare raw latency across different hardware or cold/warm model conditions without reporting them.

## Fair benchmarking protocol

1. Feed byte-identical audio to each model.
2. Use a human-verified reference transcript; never use another model's output as ground truth.
3. Record language, dialect/region, duration, sample rate, channels, noise and recording conditions.
4. Keep inference settings, checkpoint revisions and library versions.
5. Separate model loading time from inference time when collecting repeated latency results.
6. Report CPU/GPU, RAM/VRAM, precision, and whether the model fell back to CPU.
7. Report model failures and unsupported languages instead of silently dropping them.
8. Respect dataset licenses, privacy, consent and redistribution permissions.

## Current limitations

- Whisper provides word timestamps and multilingual per-segment decoding. The other initial adapters may return utterance-level text only.
- Indic-Transcribe uses its bundled CLI and the adapter records the resulting console output for traceability; if upstream output formatting changes, adjust the parser. Core/Flex checkpoints are ~4.6 GB and should run on CPU by default on a 4 GB GPU laptop.
- IndicConformer does not provide automatic language identification in this adapter; set `INDICCONFORMER_LANGUAGE` to match the checkpoint. It is skipped with a clear message when that value is missing.
- Model-level language support is not identical; a language absent from a model should not be treated as a failed accuracy result.
- A model output is not human-verified and must not be presented as ground truth.

## License

See [LICENSE](LICENSE). Each model/checkpoint and hosted service is also subject to its own license and usage terms.
