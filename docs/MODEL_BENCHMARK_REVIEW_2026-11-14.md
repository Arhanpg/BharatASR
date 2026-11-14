# BharatASR — Model Benchmark and Transcript Review (14 November 2026)

**Repository snapshot:** \`main\` at \`609c7632ee058d665dec4ef9f8141c5d1760046b\`  
**Review scope:** all 22 distinct YouTube IDs in the updated URL list; latest available Whisper and Vaani Hindi outputs; run summaries, model metrics, access errors and transcript text.  
**Review classification:** text-level review and artifact audit. **Not an audio-verified accuracy benchmark.**

## 1. Executive summary

The latest push expands the collection to **22 distinct videos**, including the new five-hour recording \`r4hrxMl24B8\`.

| Repository artifact | Count |
|---|---:|
| Distinct YouTube video IDs | 22 |
| Output run directories | 71 |
| Saved \`transcript.txt\` files across repeated runs | 70 |
| Whisper transcript files across all runs | 48 |
| Vaani Hindi transcript files across all runs | 22 |
| Videos with a latest Whisper transcript | 22/22 |
| Videos with a Vaani transcript | 21/22 |
| Vaani latest run failed before inference | 1 |
| SraVaani transcript files | 0 |
| Indic-Transcribe transcript files | 0 |
| IndicConformer transcript files | 0 |

The 70 transcript files are not 70 distinct recordings: several videos were processed more than once. The 22 source recordings represent approximately **18.17 hours** of audio.

### Main conclusions

1. The two backends that actually produced this batch's comparison transcripts are **faster-whisper Small** and **ARTPARK/IISc Vaani Whisper-Small Hindi**.
2. Vaani is often more readable than Whisper in sampled short/medium Hindi explanations, but it is not consistently clean and is not proven more accurate.
3. Both backends still show repeated phrases, repeated syllables, phonetic misspellings, corrupted characters, mixed-script fragments and suspiciously short outputs.
4. Long recordings are particularly problematic. More text is not evidence of better coverage: some long Vaani outputs contain extensive phrase repetition and very low vocabulary diversity.
5. SraVaani and Indic-Transcribe did not reach inference in the recorded attempts. The repository contains access-denied errors, not transcripts, so their accuracy is unmeasured.
6. There are no human reference transcripts, caption files or WER/CER comparison outputs in the repository. **No numerical accuracy ranking is justified.**

## 2. Inspection method and verification boundary

For every latest transcript available, I inspected text excerpts near the beginning, 25%, 50%, 75% and 95% positions and reviewed full-file diagnostics: character count, whitespace-token count, unique-token ratio, Unicode replacement-character count and longest identical whitespace-token run. I also inspected source metadata, run summaries and elapsed-time records.

This is a multi-position manual review plus full-file text diagnostics. It is **not a word-by-word human correction of every token**.

### Original YouTube audio/caption verification was not possible here

I attempted the supplied YouTube watch pages and alternate mobile, embed, oEmbed and timed-text endpoints. Retrieval failed with cache-miss/inaccessible-page errors; exact-ID searches returned no indexed results; direct network access from the working container failed because DNS could not resolve youtube.com.

The repository contains no original audio/video files, no VTT/SRT caption tracks and no human references: \`data/references\` contains only its placeholder. Therefore I could not play the source videos or verify sentences against the spoken audio.

The comments below describe saved ASR text only. They are not quotations confirmed against a speaker, and are not WER/CER or accuracy claims. YouTube auto-captions, if downloaded later, are another machine-generated hypothesis, not human ground truth.

## 3. Model execution status

The latest per-video run summaries show:

| Backend | Latest runs | Text generated | Completed (no configured flags) | Completed, needs review | Failed |
|---|---:|---:|---:|---:|---:|
| Whisper Small | 22 | 22 | 1 | 21 | 0 |
| Vaani Whisper Hindi | 22 | 21 | 4 | 17 | 1 |

A \`completed\` status means text was returned without a configured heuristic warning; it does **not** mean a person verified correctness. The Whisper result for \`R_Dd4slDghA\`, for example, was marked completed while its sampled Hindi still contains conspicuous phonetic spelling errors.

The Vaani failure is for \`3wlMq29K6TE\`: it stopped with an \`OSError\` loading the feature extractor for \`ARTPARK-IISc/whisper-small-vaani-hindi\` (the expected \`preprocessor_config.json\` could not be loaded). This is a model-loading/setup failure, not an accuracy result.

### Other model attempts

| Backend | Error artifacts | Transcript files | Assessment |
|---|---:|---:|---|
| SraVaani | 39 | 0 | Recorded errors include Hugging Face 403 gated-repository/authorization denials; inference was not reached. |
| Indic-Transcribe | 60 | 0 | Recorded errors include Hugging Face 403 gated-repository/authorization denials; inference was not reached. |
| IndicConformer | 0 | 0 | No transcript or backend error artifact in this snapshot; do not count it as tested. |
| Sarvam | 0 | 0 | No output in this batch; hosted API is optional and metered. |

Error artifact counts include repeated attempts. A 403 is **blocked access**, not a model-quality failure.

## 4. Runtime comparison

Elapsed times are from the latest per-video run summaries. They depend on model-loading/cache/device conditions and are not accuracy measurements.

- Whisper Small median elapsed time: approximately **224 seconds**.
- Vaani Hindi median elapsed time: approximately **321 seconds** across its successful video outputs.
- Median of per-video Vaani/Whisper elapsed-time ratios across matched successes: approximately **2.09×**.
- On the new 5.28-hour \`r4hrxMl24B8\` recording: Whisper took about **4,934 seconds (82 minutes)**; Vaani took about **10,437 seconds (174 minutes)**.

Vaani was slower on this run set. This is specific to the recorded environment, not a hardware-independent speed guarantee.

A special warning is \`x9XAer5p6-k\`: Whisper returned only 109 whitespace tokens for an 8.5-minute source in about 9 seconds. Vaani took about 166 seconds and returned 640 tokens. Vaani's longer output does not prove correctness, but the Whisper output requires an urgent audio-coverage check.

## 5. Per-video text comparison

The counts are raw text diagnostics. The unique-token ratio is unique whitespace tokens divided by all whitespace tokens; it is not a language-quality score. The longest run can include punctuation/symbol-only tokens, noted where relevant. A repeated \`ॐ\` may be genuine chanting; listen before treating it as an error.

| YouTube video | Duration | Whisper: chars / tokens / unique ratio / � / max run | Vaani: chars / tokens / unique ratio / � / max run | Text-only finding |
|---|---:|---|---|---|
| [R_Dd4slDghA](https://www.youtube.com/watch?v=R_Dd4slDghA) | 7.18m | 5,319 / 1,090 / .510 / 0 / 2 | 5,544 / 1,154 / .383 / 1 / 2 | Vaani is more naturally readable in samples; both contain phonetic spelling errors. Whisper's "completed" status does not make its text correct. |
| [1cq_Iwbvpvg](https://www.youtube.com/watch?v=1cq_Iwbvpvg) | 3.95m | 1,805 / 459 / .270 / 1 / 74 (\`ॐ\`) | 2,273 / 443 / .370 / 0 / 2 | Vaani keeps the question/answer sequence more coherently. Whisper has a long \`ॐ\`/\`ौ\` fragment run. |
| [zerBj1bH2KY](https://www.youtube.com/watch?v=zerBj1bH2KY) | 6.86m | 4,183 / 911 / .471 / 1 / 74 (\`तो\`) | 4,833 / 1,050 / .359 / 0 / 2 | Vaani is more readable in the sampled passages; both still misrender terminology and phonetic words. |
| [qr8A8HNk9jk](https://www.youtube.com/watch?v=qr8A8HNk9jk) | 2.86m | 330 / 64 / .125 / 3 / 54 | 2,495 / 496 / .020 / 3 / 1 | **Both unusable.** Whisper emits \`Music\` with unrelated-looking scripts/symbols; Vaani repeats short phrases extensively. More text is not better here. |
| [i59O_ajrVig](https://www.youtube.com/watch?v=i59O_ajrVig) | 8.43m | 4,875 / 1,000 / .477 / 1 / 74 (\`तो\`) | 5,141 / 1,030 / .404 / 4 / 2 | Vaani is more readable, but has corrupt characters and errors in names/terms. Whisper has a long repeated-word run. |
| [KgJJJU_TzUM](https://www.youtube.com/watch?v=KgJJJU_TzUM) | 4.27m | 2,101 / 450 / .438 / 0 / 73 (\`ौ\`) | 2,772 / 574 / .413 / 2 / 2 | Vaani's sampled text is more coherent; Whisper has a non-lexical \`ौ\` block. |
| [ucxVsyh1T8o](https://www.youtube.com/watch?v=ucxVsyh1T8o) | 49.58m | 25,781 / 5,217 / .386 / 5 / 74 (\`ॐ\`) | 34,265 / 6,587 / .299 / 10 / 4 | Vaani preserves more readable devotional/verse passages, but both need specialist review for Sanskrit/Jain terms and mantra text. |
| [gKDuNYi5j3c](https://www.youtube.com/watch?v=gKDuNYi5j3c) | 7.17m | 4,105 / 821 / .516 / 2 / 69 (\`ौ\`) | 4,733 / 927 / .429 / 1 / 2 | Vaani is more readable; Whisper has a long repeated fragment sequence. |
| [Y5S-1N5Yzkk](https://www.youtube.com/watch?v=Y5S-1N5Yzkk) | 27.91m | 9,957 / 2,386 / .143 / 30 / 74 | 25,518 / 5,670 / .155 / 4 / 3 | Both heavily degraded. Vaani returns more text, but its vocabulary diversity is still very low and sections repeat. Not a reliable Vaani win. |
| [rTqsO5M9zbY](https://www.youtube.com/watch?v=rTqsO5M9zbY) | 8.98m | 4,732 / 997 / .481 / 2 / 73 (\`ौ\`) | 5,419 / 1,093 / .421 / 1 / 2 | Vaani is clearer in the sampled sections; Whisper has a repeated \`ौ\` block. |
| [PHyJ0uol4m0](https://www.youtube.com/watch?v=PHyJ0uol4m0) | 16.31m | 6,981 / 1,405 / .423 / 25 / 74 | 9,675 / 2,086 / .261 / 3 / 2 | Vaani is substantially more readable in samples; doctrinal terms, names and locations still need correction. |
| [9jKDDkkg694](https://www.youtube.com/watch?v=9jKDDkkg694) | 112.74m | 60,848 / 12,236 / .339 / 36 / 74 | 90,062 / 19,353 / .170 / 32 / 109 (\`जी\`) | Both long-form outputs are problematic. Vaani is longer but repeats \`जी\` heavily and has low vocabulary diversity. |
| [053fJPHt4PU](https://www.youtube.com/watch?v=053fJPHt4PU) | 186.53m | 64,303 / 13,446 / .294 / 131 / 148 (\`ौ\`) | 100,929 / 21,640 / .164 / 40 / 142 (\`ओह\`) | Vaani's sample is more sentence-like and has fewer replacements, but both have huge repeated blocks and severe corruption. |
| [6fTqRoPGdzk](https://www.youtube.com/watch?v=6fTqRoPGdzk) | 8.38m | 6,739 / 1,305 / .510 / 2 / 74 (\`ॐ\`) | 8,391 / 1,657 / .388 / 1 / 2 | Vaani is more readable in samples; Whisper has a long repeated \`ॐ\` block. |
| [2Y_sQBapWBM](https://www.youtube.com/watch?v=2Y_sQBapWBM) | 23.73m | 16,911 / 3,494 / .394 / 1 / 2 | 17,786 / 3,773 / .263 / 0 / 2 | Both have a more coherent dialogue structure; Vaani is somewhat cleaner in samples. |
| [g8BvEaY9LoY](https://www.youtube.com/watch?v=g8BvEaY9LoY) | 3.41m | 731 / 185 / .438 / 1 / 72 (punctuation) | 798 / 154 / .643 / 0 / 1 | Both files are unusually short and begin mid-topic. Coverage is uncertain; inspect the source boundaries. |
| [x9XAer5p6-k](https://www.youtube.com/watch?v=x9XAer5p6-k) | 8.50m | 521 / 109 / .826 / 0 / 1 | 3,344 / 640 / .391 / 3 / 1 | Vaani returns much more text; Whisper's output and ~9-second runtime are suspiciously low. Vaani still needs audio coverage checks. |
| [jDzcOghVQ6Q](https://www.youtube.com/watch?v=jDzcOghVQ6Q) | 72.90m | 26,808 / 6,106 / .289 / 20 / 214 (comma token) | 42,744 / 9,495 / .186 / 16 / 124 (\`ए\`) | Both are noisy/repetitive. Whisper's longest run is punctuation-only, not 214 spoken words. Vaani is longer but low-diversity. |
| [StfeLi9xP0Q](https://www.youtube.com/watch?v=StfeLi9xP0Q) | 72.75m | 29,584 / 6,317 / .298 / 28 / 74 (\`तो\`) | 51,816 / 11,333 / .171 / 15 / 121 (\`ए\`) | Vaani is longer but contains long repeated blocks and lower vocabulary diversity. Neither is reliable as-is. |
| [o1pKnYuV2KY](https://www.youtube.com/watch?v=o1pKnYuV2KY) | 71.47m | 19,442 / 4,217 / .157 / 49 / 148 (\`ॐ\`) | 50,085 / 10,252 / .137 / 25 / 136 (\`जी\`) | Both have severe repetition and low diversity. Vaani's larger output does not establish better transcript fidelity. |
| [3wlMq29K6TE](https://www.youtube.com/watch?v=3wlMq29K6TE) | 69.60m | 22,158 / 4,968 / .163 / 68 / 74 (\`तो\`) | **No transcript** | Whisper is degraded; Vaani failed while loading its feature extractor before inference. |
| [r4hrxMl24B8](https://www.youtube.com/watch?v=r4hrxMl24B8) | 316.77m | 117,643 / 23,768 / .258 / 332 / 222 (Bengali-script \`র\`) | 251,791 / 50,001 / .181 / 158 / 214 (\`ओ\`) | New 5.28-hour stress case. Both outputs contain severe repetition and script/encoding anomalies. Vaani is longer but took ~174 minutes versus Whisper ~82 minutes. Neither is validated. |

### Reading the table correctly

- \`�\` counts are U+FFFD replacement characters present in the saved text.
- Unique-token ratio is a crude diagnostic. Low values may indicate loops or legitimate repetition; it is not a correctness metric.
- A repeated \`ॐ\` or other mantra may be authentic. No repetition should be deleted automatically.
- The punctuation-only maximum run for \`jDzcOghVQ6Q\` is not a lexical repeat; it is shown to preserve the raw diagnostic.
- "More tokens" and "more characters" do not mean "more correct".

## 6. Cross-model conclusion

### Where Vaani appears better in text-level inspection

The strongest readability differences are in \`1cq_Iwbvpvg\`, \`zerBj1bH2KY\`, \`i59O_ajrVig\`, \`KgJJJU_TzUM\`, \`rTqsO5M9zbY\`, \`PHyJ0uol4m0\` and \`6fTqRoPGdzk\`. Vaani's sampled Hindi sentences are generally more coherent there.

This is not proof that Vaani matches the speakers better. Without a reference transcript, a fluent sentence could still be a fluent hallucination.

### Where both fail

- \`qr8A8HNk9jk\`: both outputs appear dominated by non-speech/noisy or repetitive content.
- \`Y5S-1N5Yzkk\`, \`9jKDDkkg694\`, \`053fJPHt4PU\`, \`jDzcOghVQ6Q\`, \`StfeLi9xP0Q\`, \`o1pKnYuV2KY\`, \`3wlMq29K6TE\` and \`r4hrxMl24B8\`: long recordings show extensive repetitions, script artefacts or low diversity.
- \`g8BvEaY9LoY\` and \`x9XAer5p6-k\`: coverage/length needs checking against the full source audio.
- Both models make errors in Jain terminology and sacred-word spellings. Neither should be trusted to spell mantras or Prakrit/Sanskrit terms without human review.

**Recommendation:** retain Vaani as a Hindi-specialist comparison candidate and Whisper as a multilingual baseline. Do not name an accuracy winner yet.

## 7. Why WER/CER is not reported

The tree contains no human reference transcript files beyond \`data/references/.gitkeep\`, no VTT/SRT caption tracks and no model comparison outputs. WER/CER require a human-verified reference for the exact audio segment. Scoring Vaani against Whisper (or vice versa) would measure disagreement, not accuracy.

## 8. Next validation work

1. On the Windows machine where the source audio is cached, use yt-dlp to check for manual and auto-caption tracks for the 22 source URLs. Keep creator captions and auto-captions labelled separately.
2. Select fixed windows near the beginning, middle and end of every source; add targeted windows around repeated loops and suspected omissions.
3. Listen and prepare a human-corrected UTF-8 reference for each selected window. Preserve genuine mantra repetitions exactly.
4. Run Whisper and Vaani on byte-identical clips with the same language hint and preprocessing.
5. Calculate WER/CER against those human references; include empty and failed outputs rather than silently dropping them.
6. Score sacred-term fidelity separately (OM/ॐ, HRIM/ह्रीं, KLIEM/क्लीं, Jain technical terms). Aggregate WER is not enough for scripture/recitation use.
7. For long recordings, compare segment timestamps and VAD/chunk coverage against the source audio.

Local caption-discovery command (run from the repository root on Windows):

~~~powershell
New-Item -ItemType Directory -Force .local-reference\youtube-captions | Out-Null
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "all" --sub-format vtt --ignore-errors -o ".local-reference/youtube-captions/%(id)s.%(language)s.%(ext)s" -a docs/youtube_video_urls.txt
~~~

Do not commit copyrighted captions, audio or transcripts unless redistribution is permitted. Use human-reviewed references for benchmark scores.

## 9. Related files

- [Main README](../README.md)
- [All YouTube input URLs](youtube_video_urls.txt)
- [Historical 21-video report (13 November)](INITIAL_TEST_REPORT.md)
- [Machine-readable per-video statistics](MODEL_BENCHMARK_REVIEW_2026-11-14.csv)
- [Testing protocol](TESTING.md)

**Final status:** the latest saved model outputs have been reviewed at multiple points and compared textually. **Sentence-by-sentence verification against original YouTube audio is still pending because the source media/captions were inaccessible in this environment.** These results must not be presented as ground-truth accuracy measurements.
