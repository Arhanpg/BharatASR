# BharatASR — Deep Transcript and Model Benchmark Review (14 November 2026)

**Repository:** https://github.com/Arhanpg/BharatASR  
**Output snapshot:** main at 609c7632ee058d665dec4ef9f8141c5d1760046b (22-video test push)  
**Review scope:** 22 distinct YouTube videos; latest Whisper Small and Vaani Hindi transcript per video; 43 non-empty transcript files; input metadata, run summaries and runtime metrics.  
**Review type:** full-file text statistics + five-position manual transcript inspection + selected phrase-loop inspection. Not source-audio-verified accuracy.

## 1. Executive finding

The new output batch is substantially larger, but transcript quality is uneven. Both models produce coherent Hindi on some shorter explanatory recordings; both also produce serious failures, especially on music/noise-heavy and long-form recordings.

- Whisper returned text for all 22 videos.
- Vaani returned text for 21 videos; its run for 3wlMq29K6TE failed before inference because the feature extractor could not be loaded.
- The corpus is approximately 18.17 hours of normalized mono 16 kHz WAV audio.
- Vaani generates more transcript text: 149,408 content tokens across 21 outputs, compared with 90,064 for Whisper across 22. On the same 21-video subset, Vaani has 1.76× the content-token count.
- That extra text is not evidence of greater correctness. Several Vaani outputs contain long exact phrase loops, including 133 consecutive repetitions of देखने के लिए in one file.
- Whisper has more long identical-token runs overall, and in some files its text is clearly corrupted or incomplete.
- Vaani is slower in the recorded inference runs: the median paired Vaani/Whisper time ratio is about 2.09×.
- Neither model can be ranked by accuracy yet: no human reference transcripts/caption tracks exist in the repo and YouTube source audio could not be retrieved here.

**Current recommendation:** retain Whisper as the multilingual baseline and Vaani as a Hindi-specific challenger. Do not publish an accuracy winner or use either output as a verbatim Jain/Sanskrit/Prakrit transcript without listening and human correction.

## 2. Dataset, outputs and run accounting

| Item | Count |
|---|---:|
| Distinct YouTube video IDs | 22 |
| Summed audio duration from input metadata | 65,415 seconds / 18.17 hours |
| Timestamped run directories in repository | 71 |
| Transcript text files across all reruns | 70 |
| Whisper transcripts across all reruns | 48 |
| Vaani transcripts across all reruns | 22 |
| Latest Whisper outputs for unique IDs | 22/22 |
| Latest Vaani outputs for unique IDs | 21/22 |
| Latest Vaani failure before inference | 1 |
| Latest non-empty texts inspected | 43 |

The 70 transcript files include multiple reruns of the same source videos. This report uses the latest timestamped output folder for each unique video ID. The latest Vaani failure is for 3wlMq29K6TE.

Each latest input record requests Hindi (hi). Some source metadata has a null source-language field, but the language passed to the backend is still hi. The inputs record WAV PCM signed 16-bit, mono, 16 kHz audio.

## 3. Review method and metric definitions

I retrieved the full text of all 43 latest non-empty transcript files. For every output I computed diagnostics over the entire file and manually inspected excerpts around the start, 25%, 50%, 75% and 95% positions. For high-risk outputs I also inspected additional exact repeated-phrase spans.

The per-file calculations use these definitions:

- **Characters:** Unicode code points in the stored transcript.
- **Content tokens:** split on whitespace after Unicode NFC; punctuation-only tokens are removed. This is an approximate text tokenization, not a Hindi morphological tokenizer.
- **Unique-token ratio:** number of unique case-folded content tokens divided by content-token count.
- **U+FFFD:** literal Unicode replacement character (�) count.
- **Longest identical-token run:** longest contiguous run of the same content token after punctuation-only tokens are removed.
- **Phrase loop:** exact, consecutive repetition of a 2–6-token phrase. This is useful for identifying repeated decoder output that a one-token repetition detector misses.

Unique-token ratio is a diagnostic, not accuracy. A mantra, Q&A, song, live audience interaction and a lecture may naturally have different repetition profiles. A repeated mantra must never be deleted automatically; suspicious sequences must be listened to.

## 4. Aggregate statistical comparison

### 4.1 Text quantity and diversity

| Measure | Whisper Small | Vaani Whisper Hindi |
|---|---:|---:|
| Latest non-empty transcripts | 22 | 21 |
| Total content tokens | 90,064 | 149,408 |
| Total characters | 435,857 | 720,414 |
| Matched-video content tokens | 85,096 | 149,408 |
| Median content tokens per video (matched set) | 1,305 | 1,657 |
| Median unique-token ratio | 0.3792 | 0.2985 |
| Total U+FFFD characters | 738 | 319 |
| Files with U+FFFD | 19/22 | 17/21 |
| Files with identical-token run >=10 | 18/22 | 6/21 |

Whisper's matched 21-video U+FFFD count is 670 after removing its transcript for the video where Vaani failed; Vaani has 319 across the same 21 videos. These are text corruption markers, not WER or CER.

Vaani generated approximately 75.6% more content tokens over the matched set. Its median unique-token ratio is lower, however, and its phrase-loop examples are severe. In this batch, token count cannot be used as a proxy for coverage or correctness.

### 4.2 Runtime and text yield

| Measure | Whisper Small | Vaani Hindi |
|---|---:|---:|
| Median inference time over 21 matched videos | 156.5 s | 321.4 s |
| Median real-time factor | 0.260 | 0.549 |
| Median content tokens per video-minute | 96.0 | 134.5 |
| Aggregate content tokens per audio minute | 83.4 | 146.4 |

The median paired Vaani/Whisper inference-time ratio is **2.09×**. The timer is the backend's inference timer; model construction/loading occurs before transcription timing. This is the recorded machine's result, not a hardware-independent speed claim.

The saved metrics for representative runs report Whisper on cuda with int8_float16 and Vaani on cuda:0. The repository metadata does not consistently identify the exact GPU SKU, so no GPU-model-specific claim is made.

### 4.3 Run-summary status

| Backend | Latest result | Meaning |
|---|---:|---|
| Whisper Small | 22 non-empty; 1 completed without configured flags; 21 completed_needs_review | Executed on every source; an unflagged output can still contain misspellings |
| Vaani Hindi | 21 non-empty; 4 completed without configured flags; 17 completed_needs_review; 1 failed | Hindi model executed on 21 sources; one feature-extractor failure |
| SraVaani | 0 transcript files; 39 error artifacts in tree | Hugging Face 403/access-denied attempts; no inference result |
| Indic-Transcribe | 0 transcript files; 60 error artifacts in tree | Hugging Face 403/access-denied attempts; no inference result |
| IndicConformer | 0 transcripts and no inference error artifact in this snapshot | No evidence of a completed run |
| Sarvam | No outputs in this batch | Optional metered API, not a local model result |

“Completed” means text was returned without a configured heuristic warning. It does not mean a human checked the transcript or that the words match the audio.

## 5. Phrase-loop evidence

Single-token repetition is not sufficient. The examples below are exact consecutive phrase repeats detected in the saved outputs.

| Video ID | Backend | Repeated phrase/token | Consecutive repeats |
|---|---|---|---:|
| qr8A8HNk9jk | Vaani | बहुत अच्छा | 55 |
| qr8A8HNk9jk | Vaani | देखने में | 42 |
| qr8A8HNk9jk | Vaani | दिखाई दे रहा है | 21 |
| 9jKDDkkg694 | Vaani | जी जी | 54 |
| 053fJPHt4PU | Vaani | देखने के लिए | 133 |
| 053fJPHt4PU | Vaani | ओह | 142-token identical run |
| jDzcOghVQ6Q | Vaani | देखने के लिए | 80 |
| StfeLi9xP0Q | Vaani | देखने के लिए | 40 |
| o1pKnYuV2KY | Vaani | के लिए देखने | 97 |
| o1pKnYuV2KY | Vaani | जी जी | 68 |
| r4hrxMl24B8 | Vaani | ओ ओ | 107 |
| r4hrxMl24B8 | Vaani | हे हे | 90 |
| 1cq_Iwbvpvg | Whisper | ॐ ॐ | 37 |
| 1cq_Iwbvpvg | Whisper | तो तो | 37 |
| Y5S-1N5Yzkk | Whisper | ॐ ॐ | 37 |
| 053fJPHt4PU | Whisper | standalone ौ | 148-token identical run |

The Vaani output for qr8A8HNk9jk has a maximum identical single-token run of just 1, which looks harmless under a single-token detector. The phrase detector exposes the repeated phrase blocks. This is why BharatASR should add n-gram loop diagnostics.

Do not automatically delete these repeats. Some may be a genuine song refrain, audience response or mantra; source audio is needed to distinguish authentic repetition from decoding loops.

## 6. Script and encoding review

### qr8A8HNk9jk — both outputs unusable

Whisper's 330-character transcript has no Devanagari characters in the saved text. It includes 111 Sinhala-script, 73 Georgian-script and 55 Tibetan-script characters, plus the Latin word “Music”. Vaani produces Devanagari but has only 10 unique tokens out of 496 (unique-token ratio 0.0202) and repeats phrases such as बहुत अच्छा and दिखाई दे रहा है. Neither output should be accepted.

### r4hrxMl24B8 — 5.28-hour stress test

Whisper contains 332 U+FFFD characters and script counts include Bengali 1,517, Tamil 517, Telugu 953 and Tibetan 129 characters, plus 16,196 Latin-script characters. Its longest identical-token run is 222 Bengali-script characters.

Vaani produces 50,001 content tokens and 251,791 characters, but its unique-token ratio is 0.180, it contains 158 replacement characters, and has repeated ओ ×214 and हे ×90. This is not a correct transcript merely because it is twice as long as Whisper's.

### General replacement-character finding

U+FFFD means an unrecoverable character appeared in the saved text. It may have been introduced by decoding/serialization or earlier processing; it is not conclusive proof that the acoustic model itself misheard a word. Nevertheless, the stored transcript is corrupted at those positions. Do not guess a Sanskrit or Prakrit replacement.

## 7. Per-video transcript review

The short excerpts below are from the actual saved model outputs, not verified quotations from the speakers. Metrics are full-file calculations.

### 01. [समवसरण के चौंकाने वाले रहस्य | Jainism Explained](https://www.youtube.com/watch?v=R_Dd4slDghA)

**Video ID:** R_Dd4slDghA · **Channel:** Jain sanskar shala · **Upload date:** 2026-06-06 · **Duration:** 7.18 minutes.

**Whisper Small:** 5,319 chars; 1,090 content tokens; 532 unique (48.81%); 0 U+FFFD; longest identical-token run 2 (अपनी); 104.5 s inference; RTF 0.243; 151.9 tokens/min.

**Vaani:** 5,544 chars; 1,154 content tokens; 442 unique (38.30%); 1 U+FFFD; longest run 2 (अपनी); 250.3 s inference; RTF 0.581; 160.8 tokens/min.

**Actual saved-text excerpts:** Whisper: “पिष्वास करेंगे”; Vaani: “पिश्वास करेंगे”.



**Review:** Both openings render a likely ordinary Hindi word (विश्वास) phonetically incorrectly. Vaani's surrounding sentence is more readable, but neither is source-verified.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_000544_316339_R_Dd4slDghA/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_000544_316339_R_Dd4slDghA/vaani-whisper-hindi/transcript.txt).

### 02. [समवसरण के बारे में जानकारी | जैन प्रश्नोत्तरी](https://www.youtube.com/watch?v=1cq_Iwbvpvg)

**Video ID:** 1cq_Iwbvpvg · **Channel:** Jain sangrah · **Upload date:** 2022-09-14 · **Duration:** 3.95 minutes.

**Whisper Small:** 1,805 chars; 459 content tokens; 122 unique (26.58%); 1 U+FFFD; longest identical-token run 74 (ॐ); 78.6 s inference; RTF 0.332; 116.3 tokens/min.

**Vaani:** 2,273 chars; 443 content tokens; 163 unique (36.79%); 0 U+FFFD; longest run 2 (इसके); 96.0 s inference; RTF 0.405; 112.2 tokens/min.

**Actual saved-text excerpts:** Whisper: “ॐ ॐ”; Vaani: “प्रश्न ... उत्तर”.

Whisper bigram loops: ॐ ॐ ×37, तो तो ×37, ौ ौ ×36.

**Review:** Whisper has long contiguous ॐ, तो and standalone ौ blocks (max run 74). Vaani retains the question/answer structure and has no long single-token loop, but still misses specialist spellings.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_001226_483417_1cq_Iwbvpvg/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_001226_483417_1cq_Iwbvpvg/vaani-whisper-hindi/transcript.txt).

### 03. [तीर्थंकर भगवान का समवशरण कहाँ से आता है](https://www.youtube.com/watch?v=zerBj1bH2KY)

**Video ID:** zerBj1bH2KY · **Channel:** अनुप्रेक्षा स्वाध्याय माला · **Upload date:** 2020-11-23 · **Duration:** 6.86 minutes.

**Whisper Small:** 4,183 chars; 911 content tokens; 414 unique (45.44%); 1 U+FFFD; longest identical-token run 74 (तो); 153.6 s inference; RTF 0.373; 132.9 tokens/min.

**Vaani:** 4,833 chars; 1,050 content tokens; 377 unique (35.90%); 0 U+FFFD; longest run 2 (कभी); 243.1 s inference; RTF 0.591; 153.2 tokens/min.

**Actual saved-text excerpts:** Whisper: “तो तो”; Vaani: “समौसरण की रचना”.



**Review:** Whisper repeats तो 74 times consecutively. Vaani is easier to follow in sampled passages and avoids a long single-token run, but technical vocabulary is still phonetically distorted.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_001603_788353_zerBj1bH2KY/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_001603_788353_zerBj1bH2KY/vaani-whisper-hindi/transcript.txt).

### 04. [समवशरण — जैन प्रश्नोत्तरी](https://www.youtube.com/watch?v=qr8A8HNk9jk)

**Video ID:** qr8A8HNk9jk · **Channel:** Jain Gurukul · **Upload date:** 2023-08-01 · **Duration:** 2.86 minutes.

**Whisper Small:** 330 chars; 64 content tokens; 7 unique (10.94%); 3 U+FFFD; longest identical-token run 54 (༽); 35.5 s inference; RTF 0.207; 22.4 tokens/min | non-Devanagari scripts: Sinhala 111, Georgian 73, Tibetan 55.

**Vaani:** 2,495 chars; 496 content tokens; 10 unique (2.02%); 3 U+FFFD; longest run 1 (दिखाई); 146.9 s inference; RTF 0.855; 173.2 tokens/min.

**Actual saved-text excerpts:** Whisper: “Music”; Vaani: “बहुत अच्छा”.

Phrase loop: बहुत अच्छा ×55, देखने में ×42, दिखाई दे रहा है ×21.

**Review:** Both fail. Whisper has no Devanagari and contains Sinhala, Georgian and Tibetan-script fragments. Vaani repeats बहुत अच्छा ×55, देखने में ×42 and दिखाई दे रहा है ×21; its unique-token ratio is only 0.0202.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_002320_537639_qr8A8HNk9jk/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_002320_537639_qr8A8HNk9jk/vaani-whisper-hindi/transcript.txt).

### 05. [what is samavasaran? समवसरण क्या है?](https://www.youtube.com/watch?v=i59O_ajrVig)

**Video ID:** i59O_ajrVig · **Channel:** Jain Pathshala ke sang · **Upload date:** 2021-01-24 · **Duration:** 8.43 minutes.

**Whisper Small:** 4,875 chars; 1,000 content tokens; 457 unique (45.70%); 1 U+FFFD; longest identical-token run 74 (तो); 156.5 s inference; RTF 0.309; 118.6 tokens/min.

**Vaani:** 5,141 chars; 1,030 content tokens; 416 unique (40.39%); 4 U+FFFD; longest run 2 (तीन); 267.7 s inference; RTF 0.529; 122.2 tokens/min.

**Actual saved-text excerpts:** Whisper: “तो तो”; Vaani: “जय जिनेदन दोस्तों”.



**Review:** Vaani is more readable in sampled explanation passages, but replacement characters and term errors remain. Whisper repeats तो 74 times.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_002703_223267_i59O_ajrVig/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_002703_223267_i59O_ajrVig/vaani-whisper-hindi/transcript.txt).

### 06. [samavasarana in Jainism / samosaran ki rachna](https://www.youtube.com/watch?v=KgJJJU_TzUM)

**Video ID:** KgJJJU_TzUM · **Channel:** TIRTHANKAR - AAGAM VAANI · **Upload date:** 2024-08-15 · **Duration:** 4.27 minutes.

**Whisper Small:** 2,101 chars; 450 content tokens; 193 unique (42.89%); 0 U+FFFD; longest identical-token run 73 (ौ); 97.4 s inference; RTF 0.380; 105.4 tokens/min.

**Vaani:** 2,772 chars; 574 content tokens; 236 unique (41.11%); 2 U+FFFD; longest run 2 (पाँच); 145.9 s inference; RTF 0.570; 134.5 tokens/min.

**Actual saved-text excerpts:** Whisper: “ौ ौ”; Vaani: “सम्बसरण कौन रचता”.



**Review:** Whisper has a 73-token standalone-ौ block. Vaani keeps a more readable question/answer sequence and has no long identical-token loop, though spellings remain inaccurate.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_003451_127602_KgJJJU_TzUM/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_003451_127602_KgJJJU_TzUM/vaani-whisper-hindi/transcript.txt).

### 07. [Jain Videos: समवशरण देशना (Samosharan Deshna)](https://www.youtube.com/watch?v=ucxVsyh1T8o)

**Video ID:** ucxVsyh1T8o · **Channel:** Jainism · **Upload date:** 2014-03-06 · **Duration:** 49.58 minutes.

**Whisper Small:** 25,781 chars; 5,143 content tokens; 1,950 unique (37.92%); 5 U+FFFD; longest identical-token run 74 (ॐ); 742.7 s inference; RTF 0.250; 103.7 tokens/min.

**Vaani:** 34,265 chars; 6,587 content tokens; 1,966 unique (29.85%); 10 U+FFFD; longest run 4 (जय); 1769.4 s inference; RTF 0.595; 132.9 tokens/min.

**Actual saved-text excerpts:** Whisper: “नमो अरिहन्तालम”; Vaani: “नमू अरिहंताणम”.



**Review:** Both contain long devotional and Prakrit/Sanskrit passages. The mantra opening differs between models and requires expert review. Whisper has an ॐ/ौ loop; Vaani has 10 replacement characters and lower lexical diversity.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_003950_348812_ucxVsyh1T8o/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_003950_348812_ucxVsyh1T8o/vaani-whisper-hindi/transcript.txt).

### 08. [समवसरण के विविध रहस्य](https://www.youtube.com/watch?v=gKDuNYi5j3c)

**Video ID:** gKDuNYi5j3c · **Channel:** Jain Pathshala ke sang · **Upload date:** 2022-06-12 · **Duration:** 7.17 minutes.

**Whisper Small:** 4,105 chars; 821 content tokens; 415 unique (50.55%); 2 U+FFFD; longest identical-token run 69 (ौ); 134.1 s inference; RTF 0.312; 114.5 tokens/min.

**Vaani:** 4,733 chars; 927 content tokens; 398 unique (42.93%); 1 U+FFFD; longest run 2 (कौन); 233.6 s inference; RTF 0.543; 129.3 tokens/min.

**Actual saved-text excerpts:** Whisper: “ौ ौ”; Vaani: “कुत्रिकापन शब्द”.



**Review:** Vaani is more readable in the sampled passages. Whisper has a 69-token standalone-ौ block; Vaani avoids that loop, but specialist terms remain distorted.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_012227_910030_gKDuNYi5j3c/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_012227_910030_gKDuNYi5j3c/vaani-whisper-hindi/transcript.txt).

### 09. [समवशरण का सम्पूर्ण वर्णन सचित्र परिचय](https://www.youtube.com/watch?v=Y5S-1N5Yzkk)

**Video ID:** Y5S-1N5Yzkk · **Channel:** Acharya Amritansh (Jain darshan + Sarva darshan) · **Upload date:** 2024-06-13 · **Duration:** 27.91 minutes.

**Whisper Small:** 9,957 chars; 2,385 content tokens; 330 unique (13.84%); 30 U+FFFD; longest identical-token run 74 (तो); 496.4 s inference; RTF 0.296; 85.4 tokens/min.

**Vaani:** 25,518 chars; 5,670 content tokens; 872 unique (15.38%); 4 U+FFFD; longest run 3 (देखिये); 1105.0 s inference; RTF 0.660; 203.1 tokens/min.

**Actual saved-text excerpts:** Whisper: “लगे लगे”; Vaani: “बीस हजार सीढ़ियां”.

Whisper bigram loops include तो तो ×37, ॐ ॐ ×37 and ौ ौ ×36.

**Review:** Both are degraded. Whisper has 30 replacements, repeated-token runs and 13.8% unique tokens. Vaani is longer but still has only 15.4% unique tokens. Extra text does not prove coverage.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_012930_655349_Y5S-1N5Yzkk/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_012930_655349_Y5S-1N5Yzkk/vaani-whisper-hindi/transcript.txt).

### 10. [समवशरण विशेष | Samavsharan Vishesh](https://www.youtube.com/watch?v=rTqsO5M9zbY)

**Video ID:** rTqsO5M9zbY · **Channel:** Jinvani Gyan · **Upload date:** 2019-12-23 · **Duration:** 8.98 minutes.

**Whisper Small:** 4,732 chars; 997 content tokens; 462 unique (46.34%); 2 U+FFFD; longest identical-token run 73 (ौ); 146.3 s inference; RTF 0.272; 111.0 tokens/min.

**Vaani:** 5,419 chars; 1,093 content tokens; 458 unique (41.90%); 1 U+FFFD; longest run 2 (तीन); 319.0 s inference; RTF 0.592; 121.7 tokens/min.

**Actual saved-text excerpts:** Whisper: “ौ ौ”; Vaani: “तीरथंकर भगवान”.



**Review:** Vaani is clearer in sampled sections; Whisper has a 73-token standalone-ौ block. Vaani still has phonetic spelling issues.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_015647_907399_rTqsO5M9zbY/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_015647_907399_rTqsO5M9zbY/vaani-whisper-hindi/transcript.txt).

### 11. [भगवान महावीर का प्रथम समवशरण कहाँ लगा था?](https://www.youtube.com/watch?v=PHyJ0uol4m0)

**Video ID:** PHyJ0uol4m0 · **Channel:** Muni Shri Pranamya Sagar Ji Ke Bhakt · **Upload date:** 2021-01-28 · **Duration:** 16.31 minutes.

**Whisper Small:** 6,981 chars; 1,405 content tokens; 567 unique (40.36%); 25 U+FFFD; longest identical-token run 74 (ता); 223.8 s inference; RTF 0.229; 86.1 tokens/min.

**Vaani:** 9,675 chars; 2,086 content tokens; 544 unique (26.08%); 3 U+FFFD; longest run 2 (अभी); 484.1 s inference; RTF 0.495; 127.9 tokens/min.

**Actual saved-text excerpts:** Whisper: “बबबब”; Vaani: “एक प्रसंग”.



**Review:** Vaani's sampled narrative is substantially more readable. Whisper has 25 replacement characters and a 74-token run; Vaani reduces these symptoms, but references and Jain terminology still need human checking.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_020518_943679_PHyJ0uol4m0/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_020518_943679_PHyJ0uol4m0/vaani-whisper-hindi/transcript.txt).

### 12. [Lockdown Shivir Session on SAMOSARAN](https://www.youtube.com/watch?v=9jKDDkkg694)

**Video ID:** 9jKDDkkg694 · **Channel:** SAMTA YUVA SANGH Kolkata · **Upload date:** 2020-05-10 · **Duration:** 112.74 minutes.

**Whisper Small:** 60,848 chars; 12,236 content tokens; 3,931 unique (32.13%); 36 U+FFFD; longest identical-token run 74 (तो); 2102.9 s inference; RTF 0.311; 108.5 tokens/min.

**Vaani:** 90,062 chars; 19,353 content tokens; 3,276 unique (16.93%); 32 U+FFFD; longest run 109 (जी); 4030.8 s inference; RTF 0.596; 171.7 tokens/min.

**Actual saved-text excerpts:** Whisper: “नमूर्यंतानम नमू सिद्धानम”; Vaani: “जी जी जी”.

Phrase loop: जी जी ×54; the longest identical-token run is जी ×109.

**Review:** Both long outputs are poor. Vaani has जी जी ×54, a 109-token जी run and 16.9% unique tokens. Whisper is more diverse but has its own 74-token तो run and 36 replacement characters.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_021809_644659_9jKDDkkg694/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_021809_644659_9jKDDkkg694/vaani-whisper-hindi/transcript.txt).

### 13. [Samosaran 05 May | Live | पंचकल्याणक एवं प्रतिष्ठा महामहोत्सव](https://www.youtube.com/watch?v=053fJPHt4PU)

**Video ID:** 053fJPHt4PU · **Channel:** Jain Dharam Prabhavna · **Upload date:** 2023-05-06 · **Duration:** 186.53 minutes.

**Whisper Small:** 64,303 chars; 13,439 content tokens; 3,710 unique (27.61%); 131 U+FFFD; longest identical-token run 148 (ौ); 2519.7 s inference; RTF 0.225; 72.0 tokens/min.

**Vaani:** 100,929 chars; 21,640 content tokens; 3,545 unique (16.38%); 40 U+FFFD; longest run 142 (ओह); 4651.0 s inference; RTF 0.416; 116.0 tokens/min.

**Actual saved-text excerpts:** Whisper: “ौ ौ”; Vaani: “देखने के लिए”.

Phrase loop: देखने के लिए ×133; identical-token ओह ×142.

**Review:** Both contain substantial loops. Vaani repeats देखने के लिए 133 times and ओह 142 times; Whisper has standalone-ौ ×148 and 131 replacements. Neither is reliable.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_040112_072243_053fJPHt4PU/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_040112_072243_053fJPHt4PU/vaani-whisper-hindi/transcript.txt).

### 14. [समवशरण सम्पूर्ण जानकारी — देवों और केवलज्ञान के समय अतिशय](https://www.youtube.com/watch?v=6fTqRoPGdzk)

**Video ID:** 6fTqRoPGdzk · **Channel:** Mai Chaitanya Hun · **Upload date:** 2022-02-09 · **Duration:** 8.38 minutes.

**Whisper Small:** 6,739 chars; 1,305 content tokens; 637 unique (48.81%); 2 U+FFFD; longest identical-token run 74 (ॐ); 155.4 s inference; RTF 0.309; 155.7 tokens/min.

**Vaani:** 8,391 chars; 1,657 content tokens; 643 unique (38.81%); 1 U+FFFD; longest run 2 (आदि); 321.4 s inference; RTF 0.639; 197.7 tokens/min.

**Actual saved-text excerpts:** Whisper: “ॐ ॐ”; Vaani: “मानस्तम्भ गंधकुटी”.



**Review:** Vaani is more readable in the inspected passages and avoids long identical-token runs. Whisper has ॐ repeated 74 times. Both still need terminology review.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_060131_632686_6fTqRoPGdzk/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_060131_632686_6fTqRoPGdzk/vaani-whisper-hindi/transcript.txt).

### 15. [Ep25: Samavasaran ka Rahasya | जहाँ शेर और हिरण साथ बैठते हैं](https://www.youtube.com/watch?v=2Y_sQBapWBM)

**Video ID:** 2Y_sQBapWBM · **Channel:** JINVANI SHORTS · **Upload date:** 2025-09-13 · **Duration:** 23.73 minutes.

**Whisper Small:** 16,911 chars; 3,494 content tokens; 1,274 unique (36.46%); 1 U+FFFD; longest identical-token run 2 (टिक); 330.6 s inference; RTF 0.232; 147.2 tokens/min.

**Vaani:** 17,786 chars; 3,773 content tokens; 990 unique (26.24%); 0 U+FFFD; longest run 2 (है); 819.0 s inference; RTF 0.575; 159.0 tokens/min.

**Actual saved-text excerpts:** Whisper: “समववाश्वरन”; Vaani: “हाँ बिल्कुल”.



**Review:** Both have comparatively coherent dialogue structure and no long identical-token run. Vaani is conversational in sampled text, but its unique-token ratio is lower. Neither is reference-scored.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_061025_524898_2Y_sQBapWBM/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_061025_524898_2Y_sQBapWBM/vaani-whisper-hindi/transcript.txt).

### 16. [Samavsharan (Part-10) | 3D Animation](https://www.youtube.com/watch?v=g8BvEaY9LoY)

**Video ID:** g8BvEaY9LoY · **Channel:** Crazy MediaWorks Studios · **Upload date:** 2023-03-30 · **Duration:** 3.41 minutes.

**Whisper Small:** 731 chars; 113 content tokens; 78 unique (69.03%); 1 U+FFFD; longest identical-token run 1 (श्री); 24.9 s inference; RTF 0.122; 33.2 tokens/min | 72 punctuation-only tokens excluded from content-token metric.

**Vaani:** 798 chars; 154 content tokens; 99 unique (64.29%); 0 U+FFFD; longest run 1 (श्रीमंडप); 40.4 s inference; RTF 0.198; 45.2 tokens/min.

**Actual saved-text excerpts:** Whisper: “। ।”; Vaani: “श्रीमंडप भूमि”.



**Review:** Both outputs are unusually short for a 3.4-minute source. Whisper has 72 punctuation-only tokens; after excluding them it has 113 content tokens. Coverage needs audio-boundary inspection.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_063017_708671_g8BvEaY9LoY/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_063017_708671_g8BvEaY9LoY/vaani-whisper-hindi/transcript.txt).

### 17. [कल्पद्रुम यह समवशरण है](https://www.youtube.com/watch?v=x9XAer5p6-k)

**Video ID:** x9XAer5p6-k · **Channel:** Sarvodaya Ahimsa · **Upload date:** 2020-05-22 · **Duration:** 8.50 minutes.

**Whisper Small:** 521 chars; 109 content tokens; 85 unique (77.98%); 0 U+FFFD; longest identical-token run 1 (तीद्खंकर); 9.2 s inference; RTF 0.018; 12.8 tokens/min.

**Vaani:** 3,344 chars; 640 content tokens; 250 unique (39.06%); 3 U+FFFD; longest run 1 (तीरथंकर); 166.2 s inference; RTF 0.326; 75.3 tokens/min.

**Actual saved-text excerpts:** Whisper: “तीद्खंकर देव”; Vaani: “तीरथंकर देव”.



**Review:** Whisper returns only 109 tokens for 8.5 minutes in 9.2 seconds, a serious coverage anomaly. Vaani has far more text, but an apparent devotional/refrain sequence repeats; only audio can determine whether that repetition is genuine.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_063159_665721_x9XAer5p6-k/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_063159_665721_x9XAer5p6-k/vaani-whisper-hindi/transcript.txt).

### 18. [Samosaran Se Divya Dhwani](https://www.youtube.com/watch?v=jDzcOghVQ6Q)

**Video ID:** jDzcOghVQ6Q · **Channel:** guruvani · **Upload date:** 2014-04-08 · **Duration:** 72.90 minutes.

**Whisper Small:** 26,808 chars; 5,888 content tokens; 1,662 unique (28.23%); 20 U+FFFD; longest identical-token run 74 (तो); 1043.6 s inference; RTF 0.239; 80.8 tokens/min.

**Vaani:** 42,744 chars; 9,495 content tokens; 1,751 unique (18.44%); 16 U+FFFD; longest run 124 (ए); 2176.6 s inference; RTF 0.498; 130.3 tokens/min.

**Actual saved-text excerpts:** Whisper: “तो तो”; Vaani: “देखने के लिए”.

Phrase loop: देखने के लिए ×80; identical-token ए ×124.

**Review:** Both show major phrase repetition. Vaani contains देखने के लिए ×80 and a 124-token ए run. Whisper's raw output had a 214-token punctuation-only run; after excluding punctuation-only tokens, its largest content run is 74 तो.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_143100_786067_jDzcOghVQ6Q/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_143100_786067_jDzcOghVQ6Q/vaani-whisper-hindi/transcript.txt).

### 19. [Samosaran Se Divya Dhwani 2](https://www.youtube.com/watch?v=StfeLi9xP0Q)

**Video ID:** StfeLi9xP0Q · **Channel:** guruvani · **Upload date:** 2014-04-08 · **Duration:** 72.75 minutes.

**Whisper Small:** 29,584 chars; 6,317 content tokens; 1,804 unique (28.56%); 28 U+FFFD; longest identical-token run 74 (तो); 1242.0 s inference; RTF 0.285; 86.8 tokens/min.

**Vaani:** 51,816 chars; 11,333 content tokens; 1,924 unique (16.98%); 15 U+FFFD; longest run 121 (ए); 2300.6 s inference; RTF 0.527; 155.8 tokens/min.

**Actual saved-text excerpts:** Whisper: “तो तो”; Vaani: “देखने के लिए”.

Phrase loop: देखने के लिए ×40; identical-token ए ×121 (the longest run is a symbol/token diagnostic and needs listening).

**Review:** Vaani has देखने के लिए ×40 and ए repeated 60 times; Whisper has a 74-token तो run and 28 replacement characters. The longer output is not necessarily better.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_152521_877470_StfeLi9xP0Q/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_152521_877470_StfeLi9xP0Q/vaani-whisper-hindi/transcript.txt).

### 20. [समवसरण का थोकडा (ग्यारहवीं) PART 2](https://www.youtube.com/watch?v=o1pKnYuV2KY)

**Video ID:** o1pKnYuV2KY · **Channel:** SHIKSHAN BOARD JODHPUR · **Upload date:** 2021-12-22 · **Duration:** 71.47 minutes.

**Whisper Small:** 19,442 chars; 4,217 content tokens; 641 unique (15.20%); 49 U+FFFD; longest identical-token run 148 (ॐ); 1060.1 s inference; RTF 0.247; 59.0 tokens/min.

**Vaani:** 50,085 chars; 10,252 content tokens; 1,403 unique (13.69%); 25 U+FFFD; longest run 136 (जी); 2338.2 s inference; RTF 0.545; 143.4 tokens/min.

**Actual saved-text excerpts:** Whisper: “ॐ ॐ”; Vaani: “के लिए देखने”.

Phrase loop: के लिए देखने ×97; जी जी ×68.

**Review:** Both are severe failures. Whisper has 15.2% unique tokens, 49 replacements and an ॐ run of 148. Vaani produces 2.4× the tokens but only 13.7% unique tokens; के लिए देखने ×97 and जी जी ×68. Neither is usable verbatim.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_162435_640134_o1pKnYuV2KY/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_162435_640134_o1pKnYuV2KY/vaani-whisper-hindi/transcript.txt).

### 21. [समवसरण का थोकडा (ग्यारहवीं)-PART 1](https://www.youtube.com/watch?v=3wlMq29K6TE)

**Video ID:** 3wlMq29K6TE · **Channel:** SHIKSHAN BOARD JODHPUR · **Upload date:** 2021-12-22 · **Duration:** 69.60 minutes.

**Whisper Small:** 22,158 chars; 4,968 content tokens; 779 unique (15.68%); 68 U+FFFD; longest identical-token run 74 (तो); 1070.9 s inference; RTF 0.256; 71.4 tokens/min.

**Vaani:** no transcript. Model loading failed before inference (feature extractor / preprocessor_config.json).

**Actual saved-text excerpts:** Whisper: “तो तो”; Vaani: “No Vaani transcript”.



**Review:** Whisper has 68 replacements, 15.7% unique tokens and a 74-token तो run. Vaani failed before inference because its feature extractor / preprocessor_config.json could not be loaded.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_172123_917243_3wlMq29K6TE/whisper/transcript.txt) · Vaani output absent; see error.json.

### 22. [17 जून 2023 | श्री समवशरण विधान | आर्यिका रत्न 105 श्री पूर्णमति माताजी](https://www.youtube.com/watch?v=r4hrxMl24B8)

**Video ID:** r4hrxMl24B8 · **Channel:** ShriVani - श्री वाणी · **Upload date:** 2023-06-17 · **Duration:** 316.77 minutes.

**Whisper Small:** 117,643 chars; 23,253 content tokens; 5,930 unique (25.50%); 332 U+FFFD; longest identical-token run 222 (র); 4933.6 s inference; RTF 0.260; 73.4 tokens/min | Latin 16,196; Bengali 1,517; Tamil 517; Telugu 953; Tibetan 129.

**Vaani:** 251,791 chars; 50,001 content tokens; 8,998 unique (18.00%); 158 U+FFFD; longest run 214 (ओ); 10437.2 s inference; RTF 0.549; 157.8 tokens/min.

**Actual saved-text excerpts:** Whisper: “Alept Jal Mekamalasamme”; Vaani: “ओ ओ ओ”.

Phrase loop: ओ ओ ×107; हे हे ×90.

**Review:** 5.28-hour stress test. Whisper has 332 replacements and mixed-script contamination (Bengali 1,517; Tamil 517; Telugu 953; Tibetan 129; Latin 16,196 characters); Bengali-script র repeats 222 times. Vaani is twice as long but has 18% unique tokens, 158 replacements, ओ ×214 and हे ×90.

**Files:** [Whisper transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_173922_416511_r4hrxMl24B8/whisper/transcript.txt) · [Vaani transcript](https://github.com/Arhanpg/BharatASR/blob/main/outputs/20261114_173922_416511_r4hrxMl24B8/vaani-whisper-hindi/transcript.txt).


## 8. Domain terminology sanity check

The transcripts contain Jain terms and passages such as समवसरण, तीर्थंकर, केवलज्ञान, देशना, गंधकुटी, मानस्तम्भ, गणधर and Namokar mantra forms. Models differ in the spelling and segmentation of these expressions. A human reviewer with Jain/Sanskrit/Prakrit knowledge must approve them.

For terminology background, Jain Education International's “The First Step of Jainism” describes Samavasaran as the assembly hall where Tirthankaras preach after attaining Keval-jnan and outlines its enclosures and attendees. Ramanlal C. Shah's Samavasaran text is also available through Jain Quantum. These are background references only; they do not verify what a speaker said in any of these 22 videos.

- Jain Education International: https://jcgb.org/wp-content/uploads/2025/09/jes203_first_step_of_jainism_000125_data.pdf
- Ramanlal C. Shah, Samavasaran: https://jainqq.org/booktext/Samavasaran/249488

## 9. YouTube source verification — explicit limitation

I attempted direct retrieval of representative YouTube watch pages, exact-ID searches and the timed-text route. Retrieval returned inaccessible/cache-miss failures in this environment; direct network resolution for youtube.com also failed. The repository contains no original WAV/MP4 files, VTT/SRT subtitles or human reference transcripts. data/references contains only its placeholder.

Therefore, **I cannot honestly claim sentence-by-sentence verification against the source audio**. This report is a full-file text-statistics audit and multi-position manual text review. I did not listen to the 22 videos here, and I did not calculate WER/CER or invent accuracy percentages.

To finish source verification, retrieve available creator subtitles and auto-captions locally, label their provenance, then listen to fixed windows and create human-corrected references. Creator captions and auto-captions are not interchangeable; auto-captions are not ground truth.

PowerShell subtitle discovery command:

~~~powershell
New-Item -ItemType Directory -Force .local-reference\youtube-captions | Out-Null
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "all" --sub-format vtt --ignore-errors -o ".local-reference/youtube-captions/%(id)s.%(language)s.%(ext)s" -a docs/youtube_video_urls.txt
~~~

For each video, select beginning/middle/end windows and add windows around suspicious loops. Create a UTF-8 human reference by listening; preserve genuine mantra repetitions exactly. Score both models against the same exact reference. Do not use one ASR model's transcript as another model's ground truth. Do not redistribute copyrighted media/captions without permission.

## 10. Recommended benchmark conclusion and next engineering step

1. Keep Whisper Small as the multilingual baseline.
2. Keep Vaani Hindi as a promising Hindi-specific comparison backend; it often appears more readable on short/medium Hindi explanations, but long-form phrase-loop failures make it unsuitable as an automatic winner.
3. Do not publish a model accuracy ranking until human references are available.
4. Prioritize a phrase-level loop detector, script-consistency diagnostic and speech-coverage check in the quality pipeline. Preserve the exact original output; diagnostics should flag, never auto-correct.
5. First manually reference 3–5 representative clips: a clean short Hindi explanation, a medium lecture, a long lecture, a chanting/mantra segment and the music-heavy qr8A8HNk9jk failure.
6. Then benchmark more models. SraVaani and Indic-Transcribe must first pass gated access and actual inference; IndicConformer needs an output artifact before it can be called tested.

## 11. Related files

- [Main README](../README.md)
- [Per-video/per-model statistics CSV](MODEL_BENCHMARK_REVIEW_2026-11-14.csv)
- [YouTube source URL list](youtube_video_urls.txt)
- [Historical 21-video initial audit](INITIAL_TEST_REPORT.md)
- [Staged testing protocol](TESTING.md)

**Final status:** 43 latest non-empty model outputs were reviewed at multiple transcript positions and with full-file statistics. Source-audio verification remains pending. This is a detailed output-quality review, not a ground-truth accuracy benchmark.
