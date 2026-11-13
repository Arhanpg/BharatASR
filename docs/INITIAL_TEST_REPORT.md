# Initial BharatASR Model Test Report

**Report date:** 13 November 2026  
**Test output commit:** user-pushed commit \`61edb98\`  
**Test type:** initial integration smoke test, not a controlled accuracy benchmark

## Executive summary

The committed run metadata proves that YouTube audio preparation and faster-whisper completed for two long Hindi lecture recordings. It does **not** prove that Whisper transcribed them accurately.

SraVaani 1.0 and Indic-Transcribe Core/Flex did not reach inference. Their saved error files show Hugging Face HTTP 403 responses stating that the account was not on the model's authorized list. Those attempts are access-blocked, not model-quality measurements.

Manual inspection of the saved Whisper text found serious visible artifacts: long repeated token runs, malformed Devanagari fragments and Unicode replacement characters. Hindi language classification was confident, but language identification and transcript correctness are separate measurements.

**Initial conclusion:** Whisper ran but these saved transcripts are not acceptable as verified lecture/mantra transcripts. SraVaani and Indic-Transcribe remain untested for inference until access is granted. No WER/CER score is available because no human-verified reference transcript was supplied.

## Test environment and input

The committed metadata records:
- Windows PowerShell and a Python virtual environment with BharatASR installed editable.
- YouTube audio normalized to mono, 16 kHz, 16-bit PCM WAV.
- Whisper model \`small\`.
- CUDA device with \`int8_float16\`.
- Automatic language selection; VAD and word timestamps enabled.
- Sacred-term glossary prompt enabled in the recorded runs.

The run metadata does not identify the exact GPU model or VRAM, so this report does not attribute results to a specific GPU.

## Run 1 — Samavasaran lecture, Part 2

| Field | Recorded value |
|---|---|
| Video | [समवसरण का थोकडा (ग्यारहवीं) PART 2](https://www.youtube.com/watch?v=o1pKnYuV2KY) |
| Channel | SHIKSHAN BOARD JODHPUR |
| Audio duration | 4,288.25 s (71.47 min) |
| Requested language | Auto |
| Whisper model | faster-whisper \`small\` |
| Detected language | Hindi (\`hi\`) |
| Initial language probability | 0.9106 |
| Inference elapsed | 1,273.81 s (21.23 min) |
| Real-time factor | 0.297 |
| Device / precision | CUDA, \`int8_float16\` |

### Saved-transcript inspection

The inspected saved text has approximately 19,111 characters and 3,734 whitespace tokens. It contains 617 unique whitespace tokens (unique-token ratio 0.165), 47 Unicode replacement characters (�), and a maximum consecutive identical-token run of 74 occurrences of \`तो\`.

Sampled offsets near the beginning, 20%, 45%, 70% and 90% showed very long repetitions, repeated fragments, malformed Devanagari and non-lexical fragments. The transcript should not be treated as a clean record.

## Run 2 — Samavasaran lecture, Part 1

| Field | Recorded value |
|---|---|
| Video | [समवसरण का थोकडा (ग्यारहवीं)-PART 1](https://www.youtube.com/watch?v=3wlMq29K6TE) |
| Channel | SHIKSHAN BOARD JODHPUR |
| Audio duration | 4,175.74 s (69.60 min) |
| Requested language | Auto |
| Whisper model | faster-whisper \`small\` |
| Detected language | Hindi (\`hi\`) |
| Initial language probability | 0.9346 |
| Inference elapsed | 1,249.60 s (20.83 min) |
| Real-time factor | 0.299 |
| Device / precision | CUDA, \`int8_float16\` |

### Saved-transcript inspection

The inspected saved text has approximately 21,986 characters and 4,530 whitespace tokens. It contains 835 unique whitespace tokens (unique-token ratio 0.184), 72 Unicode replacement characters (�), and a maximum consecutive repeated-token run of 74 occurrences of \`ौ\`.

Sampled offsets showed repeated \`अगर\`, \`अपने\`, \`तो\`, long runs of partial Devanagari characters and replacement symbols. This transcript is also not acceptable as verified lecture text.

## Other backend outcomes

| Backend | Recorded outcome | Interpretation |
|---|---|---|
| SraVaani 1.0 | HTTP 403 while downloading \`ARTPARK-IISc/SraVaani-1.0\`; account not on authorized list | Model did not reach inference |
| Indic-Transcribe Core | Gated-repository HTTP 403 while fetching repository files | Model did not reach inference |
| Indic-Transcribe Flex | Gated-repository HTTP 403 while fetching repository files | Model did not reach inference |
| Indic-Transcribe retry | A separate \`Cannot send a request, as the client has been closed\` error | Transient client issue; no transcript produced |

These are access/setup failures, not model-quality results. The initial CLI retried gated downloads for multiple videos. Updated adapters now use cached Hugging Face credentials when available and report a distinct \`blocked_access\` state. Model-owner approval is still mandatory.

## Manual Whisper review — verdict

**Verdict: NOT ACCEPTABLE as a verified transcript in these two runs.**

What was checked:
- The committed UTF-8 \`transcript.txt\` files were inspected directly.
- Beginning, roughly 20%, 45%, 70% and 90% offsets were sampled for each transcript.
- Repetition runs, token diversity and replacement-character counts were measured.
- Findings were cross-checked against matching \`input.json\`, \`run_summary.json\` and \`metrics.json\`.

What this does and does not claim:
- The saved text visibly contains serious transcription artifacts.
- Without the original audio alongside the transcript, I cannot verify exact spoken words or identify which passages are correct.
- Repetition can be genuine in recitation, but the scale of repetition plus malformed fragments makes these outputs unsuitable as verified transcripts.
- The 91.06% and 93.46% values are initial language-classification probabilities, not word-accuracy scores.
- No ground truth was committed, so WER/CER is not available.

## Corrective changes in this update

1. Added public ARTPARK-IISc Whisper-Small Vaani Hindi as a separate local Hindi comparison model. Its model card documents a 718-hour Hindi fine-tune, Apache-2.0 licensing and a 30-second Transformers pipeline.
2. Gated adapters now use \`HF_TOKEN\` or the token stored by the Hugging Face CLI.
3. HTTP 403/gated errors are reported as \`blocked_access\`, with instructions to request access and authenticate after approval.
4. Added transcript diagnostics for empty output, repeated tokens, token diversity, dominant tokens and Unicode replacement characters.
5. Every successful backend writes \`quality.json\` alongside the transcript and review report.
6. The CLI distinguishes completed inference from empty output, blocked access and other failures.
7. Added regression tests for quality diagnostics, access errors, Hindi-only checkpoint constraints and CLI options.

Diagnostics are review warnings only. They do not edit transcript text, determine semantic correctness or replace WER/CER.

## Recommended next experiment

For the same Hindi Samavasaran lectures, run the baseline and public Vaani-Hindi model on identical audio:

\`\`\`powershell
# Install PyTorch for your CPU/CUDA environment from pytorch.org first.
pip install -r requirements-vaani-whisper.txt

python -m bharatasr run --youtube-url "https://www.youtube.com/watch?v=o1pKnYuV2KY" --language hi --models whisper,vaani-whisper-hindi
\`\`\`

Repeat with the Part 1 URL. Compare against a human-verified reference transcript. Do not rank SraVaani or Indic-Transcribe until access is approved and each produces a real transcript.

Do not use the Hindi-only Vaani Whisper checkpoint for Sanskrit or Prakrit. For those recordings use multilingual backends and verify the output against the recording and an authoritative text.

## Model references

- [Vaani Whisper-Small Hindi model card](https://huggingface.co/ARTPARK-IISc/whisper-small-vaani-hindi)
- [SraVaani 1.0 model card and access conditions](https://huggingface.co/ARTPARK-IISc/SraVaani-1.0)
- [Indic-Transcribe Core](https://huggingface.co/bodhan-ai/indic-transcribe-core)
- [Indic-Transcribe Flex](https://huggingface.co/bodhan-ai/indic-transcribe-flex)
