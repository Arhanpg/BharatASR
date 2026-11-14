# BharatASR 🇮🇳

**An open-source benchmark for comparing speech-to-text (ASR) models on Indian languages.**

BharatASR runs multiple local/self-hosted ASR systems against the same audio files, stores each model's transcript independently, and produces comparable runtime and (when reference transcripts are provided) accuracy metrics.

> A transcript is not an accuracy score. WER/CER are calculated only when you provide a human-verified reference transcript.

## Model lineup

| Backend | Type | Availability | Notes |
|---|---|---|---|
| faster-whisper (Whisper) | Local | Implemented; reliability fixes added | CUDA/CPU fallback, word timestamps, per-segment diagnostics, and one no-VAD recovery retry when VAD returns no text. Test with and without VAD. |
| Vaani Whisper-Small Hindi | Local | Added as public comparison backend | Hindi-only, Apache-2.0, approximately 967 MB weights. Not a Sanskrit/Prakrit model. |
| SraVaani 1.0 | Local | Access blocked in initial test | Gated Hugging Face checkpoint. The adapter supports cached CLI login or HF_TOKEN; owner approval is still required. |
| AI4Bharat IndicConformer | Local | Implemented | Official NeMo CTC/RNNT checkpoint workflow; download a .nemo model and set its path. |
| Indic-Transcribe Core / Flex | Local | Access blocked in initial test | Official CLI adapter is present, but inference is unverified for this account until Hugging Face grants access. |
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

Every execution gets a unique timestamped run directory. Each model writes to its own folder. The run summary distinguishes completed, completed_needs_review, empty_output, blocked_access, skipped and failed:

```text
outputs/
  20261112_123000_sample/
    input.json
    whisper/
      transcript.txt
      transcript.json
      segments.json
      metrics.json
      quality.json
      transcript.review.md
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


## YouTube video, playlist, and batch file input

VidTrace's YouTube extraction workflow is also carried into BharatASR: yt-dlp downloads **audio only**, FFmpeg converts it to WAV, and each downloaded video is benchmarked independently with the selected backends.

```powershell
pip install -r requirements-youtube.txt
# Install FFmpeg and confirm: ffmpeg -version

# Single video
python -m bharatasr run --youtube-url "https://www.youtube.com/watch?v=VIDEO_ID" --language auto --models whisper,indictranscribe

# Single command running an entire list of URLs or audio files from a text file
python -m bharatasr run --urls-file configs/benchmark_urls.txt --language auto --models whisper

# Or a playlist (each successfully downloaded item gets its own output run)
python -m bharatasr run --youtube-url "https://www.youtube.com/playlist?list=PLAYLIST_ID" --language auto --max-videos 25 --models all
```

Downloaded audio is cached under `.cache/youtube_audio/`, normalized to mono 16 kHz PCM WAV, and accompanied by source metadata. Playlist downloads are limited to 20 videos by default; change the limit explicitly with `--max-videos` (1–100). The downloader is audio-only and does not configure cookies or access-control bypass. Do not publish or commit copyrighted audio or transcripts without the required permissions.

## Sanskrit, Prakrit and mantra preservation

BharatASR includes `configs/sacred_terms.json` as an optional Whisper vocabulary hint file. It contains forms such as OM/ॐ, HRIM/ह्रीं, KLIEM/क्लीं, and selected Jain terminology. These are hints only: transcript text is never rewritten, transliterated or corrected automatically. Each backend saves `transcript.review.md` with manual-review warnings. For Prakrit, use `--language Prakrit`; automatic multilingual recognition is attempted, but no integrated model currently documents a dedicated Prakrit mode. See [the transcription policy](docs/TRANSCRIPTION_POLICY.md) for the review rules.

## Testing and model comparisons

Follow the staged [BharatASR testing protocol](docs/TESTING.md) for unit tests, per-model smoke tests, VAD ablation, multi-model comparisons, human reference preparation, and WER/CER scoring.

Recommended first Hindi comparison on the same WAV:

~~~powershell
python -m bharatasr run --audio data/audio/hi_jain_lecture_01.wav --language hi --models whisper,vaani-whisper-hindi
~~~

Then repeat with --no-whisper-vad to check whether VAD is suppressing quiet speech or chant. Do not change the audio, language or glossary setting between the two passes.

## Accuracy evaluation (WER / CER)

Create a UTF-8 reference transcript at `data/references/sample.txt` or `data/references/<video_id>.txt`. Make sure it is manually verified against the audio.

```powershell
# Evaluate a single run against a specific reference
python -m bharatasr compare --run outputs/20261112_123000_sample --reference data/references/sample.txt

# Or evaluate all runs across your entire benchmark in one command:
python -m bharatasr compare --runs-dir outputs --references-dir data/references
```

The comparator calculates:
- **WER** — word error rate (`(substitutions + deletions + insertions) / reference words`).
- **CER** — character error rate (`edit distance / reference characters`).
- Detailed word error breakdown: substitutions (`Sub`), deletions (`Del`), insertions (`Ins`), and correct hits (`Hits`).
- Detailed character error breakdown: character substitutions, deletions, insertions, and hits.
- Hypothesis/reference word and character counts.
- Saves detailed JSON and CSV summaries under `outputs/.../comparison/` (or `outputs/benchmark_summary.csv` for multi-run evaluations).

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

## Latest benchmark review — 14 November 2026

The latest \`main\` snapshot reviewed is \`609c7632ee058d665dec4ef9f8141c5d1760046b\` ("adding the new model test"). The YouTube corpus now contains **22 distinct video IDs**, including the new 5.28-hour recording \`r4hrxMl24B8\`.

### Updated test inventory

| Repository artifact | Count |
|---|---:|
| Distinct YouTube video IDs | 22 |
| Output run directories | 71 |
| Saved \`transcript.txt\` files across repeated runs | 70 |
| Whisper transcript files across all runs | 48 |
| Vaani Hindi transcript files across all runs | 22 |
| Latest videos with a Whisper transcript | 22/22 |
| Latest videos with a Vaani transcript | 21/22 |
| Latest Vaani run failed before inference | 1 |
| SraVaani transcript files | 0 |
| Indic-Transcribe transcript files | 0 |
| IndicConformer transcript files | 0 |

The 70 transcript files include repeated runs; they are not 70 separate videos.

### Actual model-test outcome

The latest per-video run summaries show:
- **Whisper Small:** 22/22 non-empty outputs; 1 run had no configured heuristic flags and 21 were marked for review.
- **Vaani Whisper Hindi:** 21/22 non-empty outputs; 4 had no configured heuristic flags, 17 were marked for review, and the Vaani run for \`3wlMq29K6TE\` failed while loading the feature extractor.
- **SraVaani:** 39 error artifacts and no transcript files. Recorded attempts include Hugging Face 403 gated-model access denials; inference was not reached.
- **Indic-Transcribe:** 60 error artifacts and no transcript files. Recorded attempts include Hugging Face 403 gated-model access denials; inference was not reached.
- **IndicConformer:** no transcript or backend error artifact is present in this snapshot; do not count it as tested.

A \`completed\` status means text was returned without a configured heuristic warning; it does **not** certify correctness. The Whisper transcript for \`R_Dd4slDghA\`, for example, was marked completed even though sampled text contains conspicuous phonetic spelling errors.

### Comparison observations

Vaani is often more readable than Whisper on sampled short and medium Hindi explanations, but it is not consistently clean. Both models still show repeated phrases, corrupted characters, phonetic misspellings, mixed-script fragments and suspiciously short outputs. The new five-hour \`r4hrxMl24B8\` output is especially large and repetitive in both models.

Vaani's median per-video elapsed-time ratio was approximately **2.09×** Whisper's in this batch. On \`r4hrxMl24B8\`, Whisper took about 82 minutes and Vaani about 174 minutes. These timings describe this machine/run set; they do not establish model accuracy.

### Source-audio verification limitation

I inspected the latest saved transcripts at multiple positions and reviewed full-file text diagnostics, but I could not retrieve/play the original YouTube videos from this environment. Watch, mobile, embed, oEmbed and timed-text retrieval attempts failed; direct network DNS resolution for youtube.com also failed. The repository contains no VTT/SRT captions, no human reference transcripts and no WER/CER comparison outputs.

Therefore this is a **text-level transcript review**, not sentence-by-sentence verification against original video audio. No WER, CER or accuracy winner is claimed. YouTube auto-captions, if retrieved locally, must be labelled as machine-generated and human-corrected before accuracy scoring.

**Detailed 22-video review:** [MODEL_BENCHMARK_REVIEW_2026-11-14.md](docs/MODEL_BENCHMARK_REVIEW_2026-11-14.md)  
**Machine-readable statistics:** [MODEL_BENCHMARK_REVIEW_2026-11-14.csv](docs/MODEL_BENCHMARK_REVIEW_2026-11-14.csv)  
**All video inputs:** [youtube_video_urls.txt](docs/youtube_video_urls.txt)  
**Historical report:** [13 November 21-video initial audit](docs/INITIAL_TEST_REPORT.md)

On Windows, check which subtitle tracks YouTube exposes:

~~~powershell
New-Item -ItemType Directory -Force .local-reference\youtube-captions | Out-Null
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "all" --sub-format vtt --ignore-errors -o ".local-reference/youtube-captions/%(id)s.%(language)s.%(ext)s" -a docs/youtube_video_urls.txt
~~~

Creator captions and automatic captions must be labelled separately. WER/CER requires a human-corrected reference transcript from the source audio.


## Current limitations

- Whisper provides word timestamps and multilingual per-segment decoding. The other initial adapters may return utterance-level text only.
- Indic-Transcribe uses its bundled CLI and the adapter records the resulting console output for traceability; if upstream output formatting changes, adjust the parser. Core/Flex checkpoints are ~4.6 GB and should run on CPU by default on a 4 GB GPU laptop.
- IndicConformer does not provide automatic language identification in this adapter; set `INDICCONFORMER_LANGUAGE` to match the checkpoint. It is skipped with a clear message when that value is missing.
- Model-level language support is not identical; a language absent from a model should not be treated as a failed accuracy result.
- A model output is not human-verified and must not be presented as ground truth.

## License

See [LICENSE](LICENSE). Each model/checkpoint and hosted service is also subject to its own license and usage terms.
