# BharatASR 🇮🇳

**An open-source benchmark for evaluating speech-to-text (ASR) systems on Indian-language audio, with special attention to Hindi Jain, Sanskrit and Prakrit religious discourse.**

[![Repository](https://img.shields.io/badge/GitHub-BharatASR-black?logo=github)](https://github.com/Arhanpg/BharatASR)

## 🏆 Current recommendation (evidence status: provisional)

> **Best practical choice from the models actually tested in this repository: Vaani Whisper-Small Hindi for short/medium Hindi explanatory speech, with mandatory human review.** This is a text-quality/diagnostic preference, **not a proven accuracy winner**. The saved experiments contain no human-verified reference transcripts and no completed source-audio alignment, so WER/CER cannot be reported.

> **For long religious recordings, mantras, Sanskrit or Prakrit: there is currently no validated winner. Do not publish or rely on either transcript without listening and expert correction.** The current results show severe repetition loops, incomplete outputs and Unicode replacement characters in both Whisper Small and Vaani.

**Next model to test:** [SraVaani 1.0](https://vaani.iisc.ac.in/models/sravaani) is the highest-priority additional local candidate: a 430M FastConformer trained for Indian speech, with broad Indian-language/dialect coverage and published benchmark results. Its model access is gated, and it has not completed inference in this repository yet. **It is a candidate, not the current winner.**

**Other candidates:** [AI4Bharat IndicConformer](https://ai4bharat.iitm.ac.in/areas/model/ASR/IndicConformer/) (local multilingual baseline) and [Sarvam Saaras v4](https://docs.sarvam.ai/api/api-guides-tutorials/models/saaras) (hosted API; separate paid/API track).

### At-a-glance: latest 14 November 2026 test batch

| Diagnostic (latest unique-video outputs) | Whisper Small | Vaani Whisper-Small Hindi |
|---|---:|---:|
| Non-empty transcripts | 22 | 21 |
| Content tokens | 90,064 | 149,408 |
| Median unique-token ratio | 0.3792 | 0.2985 |
| Files containing U+FFFD replacement characters | 19/22 | 17/21 |
| Files with a consecutive identical-token run ≥10 | 18/22 | 6/21 |
| Median inference time on 21 matched videos | 156.5 s | 321.4 s |
| Median real-time factor (21-video matched set) | 0.260 | 0.549 |

**How to read this:** Vaani generated more text and had fewer long single-token runs in this batch, but it was about 2.09× slower by median paired inference time. Its outputs also contain phrase-loop examples (for example, *देखने के लिए* repeated 133 times). Token quantity and heuristic cleanliness are not accuracy. A repeated ॐ/mantra may be genuine; every suspicious span needs audio review.

**Benchmark status:** a substantial *output-quality audit*, not a ground-truth accuracy benchmark. Do not interpret the table as WER, CER, word accuracy, or verified coverage.

---

## Executive conclusion

BharatASR has so far evaluated 22 distinct YouTube recordings (about 18.17 hours of normalized audio) using Whisper Small and the Hindi-specific Vaani Whisper-Small model. The latest audit inspected 43 non-empty transcript outputs, with full-file text diagnostics and excerpts at multiple positions.

- **Vaani is the provisional practical preference** for short/medium Hindi explanation-style clips among the two tested models: several inspected passages were more readable and the batch had fewer long identical-token runs. However, Vaani is slower, has low lexical diversity on many long recordings, and exhibits serious repeated-phrase loops.
- **Whisper Small remains the multilingual baseline**, not the quality winner. Some short clips are readable, but the batch shows repeated fragments, script contamination, replacement characters and very low-yield/empty outputs.
- **Neither model is dependable for verbatim Jain/Sanskrit/Prakrit content yet.** Sacred terms, mantra syllables, vowel length, anusvara/visarga, conjuncts and Prakrit forms need domain-expert review.
- **No accuracy ranking is possible yet.** The repository has no independent human-verified reference transcript. YouTube auto-captions, when available, are another ASR system's output and must not be treated as ground truth.

### Important failure cases to inspect first

| Video ID | Observed issue | Interpretation |
|---|---|---|
| [qr8A8HNk9jk](https://www.youtube.com/watch?v=qr8A8HNk9jk) | Whisper output is empty/foreign-script; Vaani repeats phrases such as *बहुत अच्छा* and *देखने में* | Both hypotheses are unusable without re-run and source listening |
| [g8BvEaY9LoY](https://www.youtube.com/watch?v=g8BvEaY9LoY) | Only about 112–154 content tokens for a 3.4-minute video | Possible partial output or low speech coverage |
| [x9XAer5p6-k](https://www.youtube.com/watch?v=x9XAer5p6-k) | Whisper has about 109 tokens for an 8.5-minute video; Vaani has repeated devotional/refrain-like output | Coverage and genuine refrain must be checked against audio |
| [053fJPHt4PU](https://www.youtube.com/watch?v=053fJPHt4PU) | Whisper has 131 replacement characters; Vaani has phrase repetition such as *देखने के लिए* ×133 | Neither can be accepted verbatim |
| [r4hrxMl24B8](https://www.youtube.com/watch?v=r4hrxMl24B8) | 5.28-hour stress test; both outputs have mixed-script/repetition and replacement-character issues | Long-form decoding needs chunk-boundary and coverage validation |

See the [full 14 November review](docs/MODEL_BENCHMARK_REVIEW_2026-11-14.md) and [per-video CSV](docs/MODEL_BENCHMARK_REVIEW_2026-11-14.csv) for the complete table and methodology.

## What “best model” means in this repository

We distinguish three different questions:

1. **Accuracy:** how closely the transcript matches verified spoken words (WER/CER against a human-corrected reference).
2. **Operational performance:** latency, real-time factor, model loading time, RAM/VRAM and hardware.
3. **Output quality diagnostics:** empty output, incomplete coverage, repeated-token/phrase loops, unexpected scripts and Unicode replacement characters.

Only the third category, plus recorded runtime, is available for the current 22-video comparison. These diagnostics are useful for rejecting suspicious outputs, but they cannot substitute for reference-based accuracy.

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

## Detailed transcript audit — 14 November 2026

The latest output batch contains **22 unique YouTube videos**, approximately **18.17 hours** of normalized Hindi audio and **43 latest non-empty transcript outputs**: 22 Whisper Small and 21 Vaani Hindi. Vaani failed to load its feature extractor on 3wlMq29K6TE.

### Full-file statistics

| Measure | Whisper Small | Vaani Hindi |
|---|---:|---:|
| Latest transcripts | 22 | 21 |
| Content tokens | 90,064 | 149,408 |
| Median unique-token ratio | 0.3719 | 0.2985 |
| U+FFFD replacement characters | 738 | 319 |
| Files with U+FFFD | 19/22 | 17/21 |
| Files with a repeated identical-token run of 10+ | 18/22 | 6/21 |

On the matched 21 videos, Vaani produces approximately **1.76× more content tokens**, but it also has long multiword loops. Examples include बहुत अच्छा ×55, देखने के लिए ×133, जी जी ×54 and ओ ओ ×107. The extra output must not be interpreted as better coverage.

### Runtime comparison

| Measure | Whisper | Vaani |
|---|---:|---:|
| Median inference time over matched videos | 156.5 s | 321.4 s |
| Median real-time factor | 0.260 | 0.549 |
| Median paired Vaani/Whisper inference-time ratio | — | 2.09× slower |

### Per-video comparison

| Video ID | Duration | Whisper tokens / unique ratio / U+FFFD | Vaani tokens / unique ratio / U+FFFD | Main text finding |
|---|---:|---:|---:|---|
| [R_Dd4slDghA](https://www.youtube.com/watch?v=R_Dd4slDghA) | 7.2m | 1,090 / 0.488 / 0 | 1,154 / 0.383 / 1 | Both openings render a likely ordinary Hindi word (विश्वास) phonetically incorrectly. Vaani's surrounding sentence is more readable, but neither is source-verified. |
| [1cq_Iwbvpvg](https://www.youtube.com/watch?v=1cq_Iwbvpvg) | 3.9m | 459 / 0.266 / 1 | 443 / 0.368 / 0 | Whisper has long contiguous ॐ, तो and standalone ौ blocks (max run 74). Vaani retains the question/answer structure and has no long single-token loop, but still misses specialist spellings. |
| [zerBj1bH2KY](https://www.youtube.com/watch?v=zerBj1bH2KY) | 6.9m | 911 / 0.454 / 1 | 1,050 / 0.359 / 0 | Whisper repeats तो 74 times consecutively. Vaani is easier to follow in sampled passages and avoids a long single-token run, but technical vocabulary is still phonetically distorted. |
| [qr8A8HNk9jk](https://www.youtube.com/watch?v=qr8A8HNk9jk) | 2.9m | 64 / 0.109 / 3 | 496 / 0.020 / 3 | Both fail. Whisper has no Devanagari and contains Sinhala, Georgian and Tibetan-script fragments. Vaani repeats बहुत अच्छा ×55, देखने में ×42 and दिखाई दे रहा है ×21; its unique-token ratio is only 0.0202. |
| [i59O_ajrVig](https://www.youtube.com/watch?v=i59O_ajrVig) | 8.4m | 1,000 / 0.457 / 1 | 1,030 / 0.404 / 4 | Vaani is more readable in sampled explanation passages, but replacement characters and term errors remain. Whisper repeats तो 74 times. |
| [KgJJJU_TzUM](https://www.youtube.com/watch?v=KgJJJU_TzUM) | 4.3m | 450 / 0.429 / 0 | 574 / 0.411 / 2 | Whisper has a 73-token standalone-ौ block. Vaani keeps a more readable question/answer sequence and has no long identical-token loop, though spellings remain inaccurate. |
| [ucxVsyh1T8o](https://www.youtube.com/watch?v=ucxVsyh1T8o) | 49.6m | 5,143 / 0.379 / 5 | 6,587 / 0.298 / 10 | Both contain long devotional and Prakrit/Sanskrit passages. The mantra opening differs between models and requires expert review. Whisper has an ॐ/ौ loop; Vaani has 10 replacement characters and lower lexical diversity. |
| [gKDuNYi5j3c](https://www.youtube.com/watch?v=gKDuNYi5j3c) | 7.2m | 821 / 0.505 / 2 | 927 / 0.429 / 1 | Vaani is more readable in the sampled passages. Whisper has a 69-token standalone-ौ block; Vaani avoids that loop, but specialist terms remain distorted. |
| [Y5S-1N5Yzkk](https://www.youtube.com/watch?v=Y5S-1N5Yzkk) | 27.9m | 2,385 / 0.138 / 30 | 5,670 / 0.154 / 4 | Both are degraded. Whisper has 30 replacements, repeated-token runs and 13.8% unique tokens. Vaani is longer but still has only 15.4% unique tokens. Extra text does not prove coverage. |
| [rTqsO5M9zbY](https://www.youtube.com/watch?v=rTqsO5M9zbY) | 9.0m | 997 / 0.463 / 2 | 1,093 / 0.419 / 1 | Vaani is clearer in sampled sections; Whisper has a 73-token standalone-ौ block. Vaani still has phonetic spelling issues. |
| [PHyJ0uol4m0](https://www.youtube.com/watch?v=PHyJ0uol4m0) | 16.3m | 1,405 / 0.404 / 25 | 2,086 / 0.261 / 3 | Vaani's sampled narrative is substantially more readable. Whisper has 25 replacement characters and a 74-token run; Vaani reduces these symptoms, but references and Jain terminology still need human checking. |
| [9jKDDkkg694](https://www.youtube.com/watch?v=9jKDDkkg694) | 112.7m | 12,236 / 0.321 / 36 | 19,353 / 0.169 / 32 | Both long outputs are poor. Vaani has जी जी ×54, a 109-token जी run and 16.9% unique tokens. Whisper is more diverse but has its own 74-token तो run and 36 replacement characters. |
| [053fJPHt4PU](https://www.youtube.com/watch?v=053fJPHt4PU) | 186.5m | 13,439 / 0.276 / 131 | 21,640 / 0.164 / 40 | Both contain substantial loops. Vaani repeats देखने के लिए 133 times and ओह 142 times; Whisper has standalone-ौ ×148 and 131 replacements. Neither is reliable. |
| [6fTqRoPGdzk](https://www.youtube.com/watch?v=6fTqRoPGdzk) | 8.4m | 1,305 / 0.488 / 2 | 1,657 / 0.388 / 1 | Vaani is more readable in the inspected passages and avoids long identical-token runs. Whisper has ॐ repeated 74 times. Both still need terminology review. |
| [2Y_sQBapWBM](https://www.youtube.com/watch?v=2Y_sQBapWBM) | 23.7m | 3,494 / 0.365 / 1 | 3,773 / 0.262 / 0 | Both have comparatively coherent dialogue structure and no long identical-token run. Vaani is conversational in sampled text, but its unique-token ratio is lower. Neither is reference-scored. |
| [g8BvEaY9LoY](https://www.youtube.com/watch?v=g8BvEaY9LoY) | 3.4m | 113 / 0.690 / 1 | 154 / 0.643 / 0 | Both outputs are unusually short for a 3.4-minute source. Whisper has 72 punctuation-only tokens; after excluding them it has 113 content tokens. Coverage needs audio-boundary inspection. |
| [x9XAer5p6-k](https://www.youtube.com/watch?v=x9XAer5p6-k) | 8.5m | 109 / 0.780 / 0 | 640 / 0.391 / 3 | Whisper returns only 109 tokens for 8.5 minutes in 9.2 seconds, a serious coverage anomaly. Vaani has far more text, but an apparent devotional/refrain sequence repeats; only audio can determine whether that repetition is genuine. |
| [jDzcOghVQ6Q](https://www.youtube.com/watch?v=jDzcOghVQ6Q) | 72.9m | 5,888 / 0.282 / 20 | 9,495 / 0.184 / 16 | Both show major phrase repetition. Vaani contains देखने के लिए ×80 and a 124-token ए run. Whisper's raw output had a 214-token punctuation-only run; after excluding punctuation-only tokens, its largest content run is 74 तो. |
| [StfeLi9xP0Q](https://www.youtube.com/watch?v=StfeLi9xP0Q) | 72.7m | 6,317 / 0.286 / 28 | 11,333 / 0.170 / 15 | Vaani has देखने के लिए ×40 and ए repeated 60 times; Whisper has a 74-token तो run and 28 replacement characters. The longer output is not necessarily better. |
| [o1pKnYuV2KY](https://www.youtube.com/watch?v=o1pKnYuV2KY) | 71.5m | 4,217 / 0.152 / 49 | 10,252 / 0.137 / 25 | Both are severe failures. Whisper has 15.2% unique tokens, 49 replacements and an ॐ run of 148. Vaani produces 2.4× the tokens but only 13.7% unique tokens; के लिए देखने ×97 and जी जी ×68. Neither is usable verbatim. |
| [3wlMq29K6TE](https://www.youtube.com/watch?v=3wlMq29K6TE) | 69.6m | 4,968 / 0.157 / 68 | failed before inference | Whisper has 68 replacements, 15.7% unique tokens and a 74-token तो run. Vaani failed before inference because its feature extractor / preprocessor_config.json could not be loaded. |
| [r4hrxMl24B8](https://www.youtube.com/watch?v=r4hrxMl24B8) | 316.8m | 23,253 / 0.255 / 332 | 50,001 / 0.180 / 158 | 5.28-hour stress test. Whisper has 332 replacements and mixed-script contamination (Bengali 1,517; Tamil 517; Telugu 953; Tibetan 129; Latin 16,196 characters); Bengali-script র repeats 222 times. Vaani is twice as long but has 18% unique tokens, 158 replacements, ओ ×214 and हे ×90. |

### What this means

Vaani often looks more readable on short and medium Hindi explanations, but long-form phrase loops and low token diversity undermine that advantage. Whisper produces more single-token loops and severe script anomalies in selected files. Neither model is ready for unreviewed sacred-text transcription.

**Detailed report:** [MODEL_BENCHMARK_REVIEW_2026-11-14.md](docs/MODEL_BENCHMARK_REVIEW_2026-11-14.md)  
**Per-video/per-model statistics:** [MODEL_BENCHMARK_REVIEW_2026-11-14.csv](docs/MODEL_BENCHMARK_REVIEW_2026-11-14.csv)

**Verification boundary:** this is a full-file text-statistics audit with multi-position manual inspection. The original YouTube audio and captions were inaccessible from this environment, and the repository contains no human references. Therefore no sentence-by-sentence source verification, WER/CER or accuracy winner is claimed. See the detailed report for the source-access attempts and local reference-building procedure.

SraVaani and Indic-Transcribe have no transcript outputs in this snapshot because recorded attempts were blocked by Hugging Face access errors. IndicConformer also has no completed inference output here.


## Current limitations

- Whisper provides word timestamps and multilingual per-segment decoding. The other initial adapters may return utterance-level text only.
- Indic-Transcribe uses its bundled CLI and the adapter records the resulting console output for traceability; if upstream output formatting changes, adjust the parser. Core/Flex checkpoints are ~4.6 GB and should run on CPU by default on a 4 GB GPU laptop.
- IndicConformer does not provide automatic language identification in this adapter; set `INDICCONFORMER_LANGUAGE` to match the checkpoint. It is skipped with a clear message when that value is missing.
- Model-level language support is not identical; a language absent from a model should not be treated as a failed accuracy result.
- A model output is not human-verified and must not be presented as ground truth.

## Recommended next experiments

The next comparison should test these candidates on the **same byte-identical audio segments and same human-verified references**:

| Priority | Candidate | Why test it | Status in this repository |
|---|---|---|---|
| 1 | [SraVaani 1.0](https://huggingface.co/ARTPARK-IISc/SraVaani-1.0) | Indian-speech FastConformer; broad language/dialect coverage; published evaluation across multiple Indian datasets | Adapter exists; prior access attempts were blocked; no transcript result |
| 2 | [Vaani Whisper-Small Hindi](https://huggingface.co/ARTPARK-IISc/whisper-small-vaani-hindi) | Hindi-specific fine-tune of Whisper Small; useful direct challenger | Inference completed on 21/22 latest videos |
| 3 | [AI4Bharat IndicConformer](https://github.com/AI4Bharat/IndicConformerASR) | Open multilingual CTC/RNNT Indian-language baseline | Adapter exists; no completed result in current test batch |
| 4 | [Sarvam Saaras v4](https://docs.sarvam.ai/api/api-guides-tutorials/models/saaras) | Strong hosted candidate with verbatim mode and keyterm prompting; test domain vocabulary and long-form batch support | Optional metered API; not evaluated |
| 5 | Whisper Small / Medium / Large-v3 or Turbo | Establish whether larger multilingual Whisper checkpoints improve specialist Hindi speech | Small is the current measured baseline; larger variants need controlled runs |

### Published model-card context (not BharatASR test results)

- The official [SraVaani 1.0 benchmark page](https://vaani.iisc.ac.in/models/sravaani) reports Hindi average WER of **12.4** across its listed evaluation sets and **10.9** on its FLEURS set.
- The [Vaani Whisper-Small Hindi model card](https://huggingface.co/ARTPARK-IISc/whisper-small-vaani-hindi) reports **19.08 WER** on its FLEURS evaluation and results on several other Hindi speech datasets.
- These published figures are useful reasons to prioritize SraVaani for a controlled trial, but they are **not a valid head-to-head result**: test-set versions, segmentation, normalization and evaluation implementations may differ. Only BharatASR runs over the same reference audio can decide which performs better on this Jain-domain corpus.

Published benchmarks are **not directly comparable across datasets**. For context only, the SraVaani model page publishes Hindi WER values on FLEURS and other test sets; Vaani's Hindi Whisper model card also publishes WER on several corpora. Those numbers must not be placed in the same leaderboard as BharatASR results unless audio, references, normalization and evaluation split are identical.

### Religious-domain evaluation protocol

1. Select representative 30–60 second clips from short explanations, long lectures, recitation/mantra, Q&A, music/noisy recordings and Sanskrit/Prakrit-heavy passages.
2. Create a human-verified Devanagari reference by listening to the exact clip. Have specialist terminology and sacred syllables reviewed by a knowledgeable speaker.
3. Store provenance, timestamp ranges, language variety, speaker/recording conditions, and annotator/reviewer notes. Keep copyrighted audio and captions out of Git unless redistribution is permitted.
4. Run every model with identical audio, sample rate, channel count, chunking policy and decoding settings. Record exact model revision, library versions, hardware, precision, cold-start and warm inference times.
5. Report normalized WER and CER, substitutions/deletions/insertions, plus domain-term accuracy as a separate metric. Publish raw and normalized scores; do not silently normalize away meaningful diacritics or sacred syllable differences.
6. Manually inspect missing spans, repeated spans and chunk boundaries. Do not automatically remove repetitions: they may be real chants or audience responses.
7. Keep local open-weight models and hosted API models in separate tables. Report API cost and network latency separately.

### Suggested acceptance criteria before declaring an accuracy winner

- At least 30 minutes of human-verified evaluation audio for the initial Hindi domain set, with coverage across multiple recordings and content types.
- Identical test segments and a single reference per segment shared across every candidate.
- Publish aggregate WER/CER and per-video scores, not only a few attractive examples.
- Include confidence intervals or bootstrap intervals over segments when sample size permits.
- Report model failures and unsupported cases; do not omit them from the accounting.
- Have a second reviewer audit a subset, especially Sanskrit/Prakrit and mantra segments.

## Current project status

**Completed:** multi-backend framework, YouTube audio ingestion, timestamped model outputs, diagnostics, transcript review artifacts, 22-video Whisper/Vaani text-quality audit.

**Not completed:** source-audio verification of every transcript, human-reference WER/CER, SraVaani/IndicConformer/Sarvam measured results, and a statistically defensible best-model claim.

The project is therefore **not a concluded accuracy benchmark yet**. The defensible conclusion today is: *Vaani is the provisional text-readability choice for shorter Hindi explanatory audio among the two tested models; Whisper is the multilingual baseline; neither is validated for verbatim religious transcription.* Further experiments should target SraVaani first, then IndicConformer and a separate Sarvam Saaras v4 API track.

## License

See [LICENSE](LICENSE). Each model/checkpoint and hosted service is also subject to its own license and usage terms.

