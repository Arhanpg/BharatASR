# BharatASR — Correct Testing Protocol

This guide separates **software tests**, **model smoke tests**, **controlled ASR comparisons**, and **human transcript verification**. Passing one stage does not mean the next stage passed.

## 0. Prepare a reproducible test set

Do not begin by running every large model on every long YouTube recording. Start with short, representative, locally saved WAV files.

~~~text
data/
  audio/
    hi_clean_01.wav
    hi_jain_lecture_01.wav
    hi_code_mixed_01.wav
    hi_noisy_01.wav
    sa_recitation_01.wav
    prakrit_sample_01.wav
  references/
    hi_clean_01.txt
    hi_jain_lecture_01.txt
    hi_code_mixed_01.txt
    hi_noisy_01.txt
    sa_recitation_01.txt
~~~

For fair model-to-model testing:
- Keep one canonical audio file for each test item. Feed that exact file to every backend.
- Prefer WAV, mono, 16 kHz PCM for the shared local test set. Preserve the original source separately.
- Record source URL, video ID, language, dialect/region, duration, channel count, sample rate and any preprocessing.
- Include clean speech, long lectures, background music/noise, Hindi-English code-switching, names/technical words, Jain terminology and recitation. Add Sanskrit and each known Prakrit variety as separate categories rather than merging them into generic Hindi.
- Prepare UTF-8 reference text by listening to the audio. YouTube auto-caption is another ASR output, not ground truth. Use it as a draft only, then correct it manually.
- Keep a short reference excerpt for rapid iteration and a longer reference for final comparison. Never use a model's own transcript as its reference.

## 1. Run software/unit tests first

From the repository root in your activated virtual environment:

~~~powershell
python -m pip install -e ".[dev]"
python -m compileall -q src
python -m pytest -q
~~~

These tests do not download model weights, require a GPU, or call a hosted API. CI runs the lightweight suite on Python 3.10, 3.11 and 3.12.

## 2. Test faster-whisper by itself

Install the Whisper extra:

~~~powershell
pip install -r requirements-whisper.txt
~~~

Choose a 1–3 minute Hindi WAV with speech from beginning to end. First run the baseline without glossary hints:

~~~powershell
python -m bharatasr run --audio data/audio/hi_jain_lecture_01.wav --language hi --models whisper
~~~

Then run the exact same audio with VAD disabled:

~~~powershell
python -m bharatasr run --audio data/audio/hi_jain_lecture_01.wav --language hi --models whisper --no-whisper-vad
~~~

Compare:
- Did the transcript cover the beginning, middle and end?
- Are timestamps plausible and ordered?
- Are there long repeated words or fragments?
- Did VAD remove quiet chanting or low-volume speech?
- Did the model fall back from CUDA to CPU?
- What changed in runtime and quality warnings?

Do not treat VAD/no-VAD as separate models. This is a configuration ablation. Only change one setting at a time.

**New recovery behavior:** if a VAD-enabled Whisper pass returns no segment text, BharatASR retries once without VAD and records that the recovery was used. Inspect the recovered transcript and timestamps; the non-VAD pass can include silence or non-speech content. This recovery does not apply to every low-quality transcript and is not an accuracy guarantee.

## 3. Compare Hindi-specialized Vaani Whisper with multilingual Whisper

The ARTPARK-IISc checkpoint is Hindi-specific. Its model card describes the Transformers ASR pipeline with 30-second chunking and Hindi decoder prompts. Do not use it as a Sanskrit/Prakrit model.

Install a PyTorch build compatible with the local CUDA/CPU environment from the official PyTorch selector, then:

~~~powershell
pip install -r requirements-vaani-whisper.txt
~~~

Run both backends on identical Hindi audio:

~~~powershell
python -m bharatasr run --audio data/audio/hi_jain_lecture_01.wav --language hi --models whisper,vaani-whisper-hindi
~~~

For the first comparison, keep:
- the exact same WAV,
- the same requested language (hi),
- glossary prompt disabled,
- default Whisper VAD setting,
- separate output folders and all model/device settings recorded.

The Hindi checkpoint does not perform language identification; Hindi is forced. Do not compare its language-detection field with Whisper's automatic language probability.

## 4. Test gated models only after access approval

### SraVaani 1.0

Install requirements, request/accept access on the model page, and authenticate with an approved account:

~~~powershell
pip install -r requirements-sravaani.txt
hf auth login
hf auth whoami
python -m bharatasr run --audio data/audio/hi_jain_lecture_01.wav --language hi --models sravaani
~~~

The adapter defaults to CPU to reduce VRAM pressure. A token does not bypass owner approval.

### Indic-Transcribe Core or Flex

Install runner requirements and verify that the logged-in account has access:

~~~powershell
pip install -r requirements-indictranscribe.txt
hf auth login
hf auth whoami
$env:INDIC_TRANSCRIBE_MODEL = "bodhan-ai/indic-transcribe-core"
python -m bharatasr run --audio data/audio/hi_jain_lecture_01.wav --language hi --models indictranscribe
~~~

Repeat using bodhan-ai/indic-transcribe-flex. Both checkpoints are large; use CPU on a 4 GB GPU laptop unless you have verified sufficient free VRAM. A Hugging Face 403 is blocked_access, not a model accuracy result.

### AI4Bharat IndicConformer

Use the AI4Bharat NeMo environment and a language-matched .nemo checkpoint. For Hindi, for example:

~~~powershell
$env:INDICCONFORMER_CHECKPOINT = "D:\models\indicconformer_hi.nemo"
$env:INDICCONFORMER_LANGUAGE = "hi"
$env:INDICCONFORMER_DEVICE = "cpu"
python -m bharatasr run --audio data/audio/hi_jain_lecture_01.wav --language hi --models indicconformer
~~~

Do not run a Hindi checkpoint against Sanskrit audio and interpret the output as a Sanskrit result.

### Sarvam

Sarvam is a hosted, metered API, not a free local backend. It is optional and excluded from --models all. Do not enable it unless you explicitly accept possible credit consumption and have an API key. The current adapter is for short audio; do not use it for long lectures.

## 5. Run a controlled multi-model test

Once each required model passes its single-model smoke test, run the exact same audio and language:

~~~powershell
python -m bharatasr run --audio data/audio/hi_jain_lecture_01.wav --language hi --models whisper,vaani-whisper-hindi,sravaani,indicconformer,indictranscribe
~~~

Only include models that are installed, available and authorized. Run summary statuses distinguish completed, completed_needs_review, empty_output, blocked_access, skipped and failed. Do not compare an unavailable backend as if it returned a transcript.

For Hindi-only comparisons, Vaani Hindi is eligible. For Sanskrit/Prakrit tests, omit the Hindi-only backend. Use --language auto as a separate language-detection experiment; in a given accuracy comparison, keep language settings constant wherever the models support them.

## 6. Create a human-verified reference and calculate WER/CER

For each audio file, create one UTF-8 reference transcript. Listen to the recording and correct:
- ordinary words and sentence boundaries,
- personal/place names and Jain technical terminology,
- Sanskrit and Prakrit forms,
- mantra syllables such as ॐ, ह्रीं, क्लीं and repeated invocations,
- genuine repetitions versus ASR loops,
- code-switched words and their intended script.

Score every model against the exact same reference:

~~~powershell
python -m bharatasr compare --run outputs\YOUR_RUN_FOLDER --reference data\references\hi_jain_lecture_01.txt
~~~

Lower WER/CER is better. BharatASR normalizes Unicode to NFC and preserves Indic combining marks, vowel signs, viramas and joiners. It removes punctuation for scoring. State this normalization when publishing results.

Important:
- Score the same audio segment and reference for every model.
- YouTube auto-captions are not ground truth.
- Keep empty hypotheses in the report; do not silently exclude them.
- Do not rank models using language-detection probability, token count or heuristic quality warnings.
- WER can be affected by tokenization and script choices; report CER as a complementary metric for Indic scripts.
- For mantra/scripture work, separately verify the exact sacred terms. A low aggregate WER does not prove every mantra is correct.

## 7. Suggested experiment matrix

Run in stages rather than enabling every option at once.

| Experiment | Audio | Models | Question |
|---|---|---|---|
| A — baseline | 1–3 min clean Hindi | Whisper small | Does the basic local pipeline work? |
| B — VAD ablation | Same WAV as A | Whisper with VAD, then no VAD | Does VAD suppress quiet speech/chant? |
| C — language mode | Same Hindi WAV | Whisper hi, then auto | Does automatic detection change the transcript? |
| D — Hindi model | Same Hindi WAV | Whisper small vs Vaani Hindi | Which has lower WER/CER? |
| E — vocabulary hints | Same Jain lecture | Whisper glossary off vs on | Do sacred-term hints help or bias other words? |
| F — noisy audio | Same noisy WAV | Each local multilingual backend | How robust is each model? |
| G — code switching | Same Hindi-English WAV | Multilingual models | How well is mixed speech preserved? |
| H — Sanskrit/Prakrit | Separate verified samples | Supported multilingual models | What works outside Hindi? Verify every sacred term. |
| I — long audio | Same 30–120 min source | Long-form-capable backends | Does quality drift, loop or omit late sections? |

For each experiment, change one variable at a time. Keep an experiment log with command, Git commit, model ID/revision, library versions, device, compute type, VAD/glossary settings, audio SHA-256, reference SHA-256, WER, CER, elapsed time, real-time factor and error/quality flags.

## 8. How to read a BharatASR output

Each run contains:
- input.json: source URL/ID, audio duration, language request, selected backends and settings.
- run_summary.json: per-backend status and aggregate overall_status.
- transcript.txt: exact unmodified model text.
- segments.json: segments and word timestamps when provided.
- metrics.json: runtime, real-time factor, device, precision and model metadata.
- quality.json: heuristic warnings for empty output, repeated tokens, low text yield and Unicode replacement characters.
- transcript.review.md: manual review checklist.
- error.json: access, dependency, configuration or inference error.

completed means text was returned; completed_needs_review means text was returned with diagnostic warnings. Neither certifies correctness. Heuristic warnings do not rewrite text; a genuine mantra repetition must be preserved.

For fair latency comparisons, separate model-loading time from inference time, warm up the model, repeat each test at least three times, and report the median. Label CPU/GPU hardware and do not compare unlike hardware without qualification.

## 9. Recommended order

1. Run unit tests.
2. Run Whisper alone on one clean 1–3 minute Hindi clip.
3. Repeat the same clip with no VAD.
4. Run Whisper small and Vaani Hindi on the same Hindi clip.
5. Select 3–5 representative clips from the current 21-video collection and prepare human-verified references.
6. Score both models with WER/CER.
7. Only then request gated model access or install the larger Indic-Transcribe checkpoints.
8. After the Hindi pipeline is stable, build separate Sanskrit, Prakrit, mantra and code-mixed test sets.

This staged method isolates pipeline problems before downloading large models or processing hours of audio.
