# Full YouTube Transcript Audit — 21 Distinct Videos

**Audit date:** 13 November 2026  
**Repository snapshot:** main at merge commit 0dc6ef6565e0cf756fc1d1f7ed1a3d0104489dd8  
**Output inventory:** 44 run directories, 22 saved Whisper transcript files, 21 distinct YouTube video IDs  
**Status:** extracted-text audit completed; independent YouTube caption/audio cross-verification is **not completed** in this environment.

## 1. Executive summary

You were right: the earlier report covered only two videos. This expanded audit inventories all YouTube inputs recorded under outputs/ and inspects the saved Whisper transcript for every distinct video ID.

The repository snapshot contains:
- **44** timestamped run folders.
- **22** whisper/transcript.txt files.
- **21 distinct YouTube video IDs**. R_Dd4slDghA appears twice because it was transcribed in two separate runs.
- The remaining run folders are additional backend attempts and do not add more Whisper transcript files.

The saved text is not uniformly usable. Among the 21 distinct videos:
- **1** has an empty saved transcript.
- **2** have extremely low transcript yields relative to the audio duration and need completeness checks.
- **17** have a longest consecutive identical-token run of at least 10 tokens. Many of these runs are 72–74 tokens.
- **19** contain at least one Unicode replacement character (�).
- Whisper initially labelled **20/21** as Hindi; one empty-output run was labelled English with only 0.364 initial probability. The Hindi label itself does not establish word-level correctness.

These are diagnostic signals from the stored files, not WER/CER. Some repetitions can be genuine in a religious recitation (especially ॐ), so a repeated-token flag is a request to listen to the corresponding audio, not proof by itself that the speech was hallucinated.

**Overall finding:** the previous two-video conclusion understated the size of the problem. The artifacts appear across many different videos, not only the two long Samavasaran lectures. Several saved transcripts need rejection or manual correction before they can be treated as usable text.

## 2. What was actually reviewed

For every distinct video, I read the saved UTF-8 transcript.txt and inspected excerpts at five positions: the beginning and approximately 20%, 45%, 70% and 90% through the file. I also examined the full file's text-level statistics:
- Unicode character and whitespace-token counts.
- Unique-token count and unique-token ratio.
- Unicode replacement-character count.
- Longest consecutive run of an identical whitespace token.
- Whisper's stored initial language label and probability.
- Audio duration and inference time from the matching run metadata.

The duplicate R_Dd4slDghA output was inspected as a second run of the same recording, not counted as another unique video.

### Important distinction: this is not yet an audio-to-text verification

The repository contains the YouTube URLs and source metadata in each input.json, but it does **not** contain the original audio/video files or independent YouTube caption tracks (.vtt/.srt). The YouTube watch pages and direct timed-text endpoints could not be retrieved through the available web access (the requests returned cache-miss errors); direct network access from the working container also failed at DNS resolution.

Therefore I cannot honestly state that I manually read YouTube's own captions for all 21 videos or that I verified each Whisper sentence against the spoken audio. The titles and source_language_metadata values in input.json are metadata, not reference transcripts. This audit deliberately does not invent caption matches, quotations, WER or CER.

The per-video table below is a complete **review of the 21 saved Whisper outputs**, with the reference-verification status clearly separated. To finish audio-level verification, independent caption files or the audio need to be made available; instructions are in Section 6.

## 3. Per-video findings

The word counts below are whitespace-token counts, not linguistically normalized word counts. Language probabilities are Whisper's *initial language-identification probabilities*, not transcription-accuracy percentages.

| YouTube video | Duration | Whisper language / probability | Saved words | Replacement characters | Longest repeated-token run | Text-only review |
|---|---:|---:|---:|---:|---|---|
| [R_Dd4slDghA — समवसरण के चौंकाने वाले रहस्य](https://www.youtube.com/watch?v=R_Dd4slDghA) | 7.18 min | hi / 0.713 | 1,000 and 1,075 (two runs) | 2 and 1 | अगर ×44 | Several readable Hindi passages, but pervasive phonetic misspellings and a long repeated-word run. Not verified. |
| [1cq_Iwbvpvg — समवसरण के बारे में जानकारी](https://www.youtube.com/watch?v=1cq_Iwbvpvg) | 3.95 min | hi / 0.977 | 434 | 2 | । ×74 (ौ occurs 145 times) | Severe non-lexical/repeated fragments and malformed Devanagari. Not reliable. |
| [zerBj1bH2KY — तीर्थंकर भगवान का समवशरण कहाँ से आता है](https://www.youtube.com/watch?v=zerBj1bH2KY) | 6.86 min | hi / 0.951 | 786 | 3 | तो ×72 | Repeated-word loop, malformed phrases and replacement characters. Not reliable. |
| [qr8A8HNk9jk — समवशरण।।जैन प्रश्नोत्तरी](https://www.youtube.com/watch?v=qr8A8HNk9jk) | 2.86 min | en / 0.364 | 0 | 0 | — | **Empty transcript.** The old run summary nevertheless said Whisper succeeded; this is an output/status failure, not a successful transcript. |
| [i59O_ajrVig — what is samavasaran?](https://www.youtube.com/watch?v=i59O_ajrVig) | 8.43 min | hi / 0.996 | 964 | 3 | तो / ॐ ×74 | Repeated fragments and spelling corruption; requires audio review. |
| [KgJJJU_TzUM — samavasarana in Jainism](https://www.youtube.com/watch?v=KgJJJU_TzUM) | 4.27 min | hi / 0.993 | 414 | 1 | ॐ ×74 | Some readable content, but repeated mantra/token fragments and garbled words. |
| [ucxVsyh1T8o — Jain Videos: समवशरण देशना](https://www.youtube.com/watch?v=ucxVsyh1T8o) | 49.58 min | hi / 0.949 | 5,482 | 21 | র ×74 | Mixed Latin/Devanagari output, replacement characters and suspicious repeated non-Devanagari token. Requires specialist review. |
| [gKDuNYi5j3c — समवसरण के विविध रहस्य](https://www.youtube.com/watch?v=gKDuNYi5j3c) | 7.17 min | hi / 0.965 | 828 | 1 | कुन ×2 | The most readable-looking sample among several files, but still contains substantial phonetic spelling errors and a replacement character. Not accuracy-verified. |
| [Y5S-1N5Yzkk — समवशरण का सम्पूर्ण वर्णन](https://www.youtube.com/watch?v=Y5S-1N5Yzkk) | 27.91 min | hi / 0.906 | 2,217 | 24 | ौ ×74 (तो occurs 455 times overall) | Severe repetition, low vocabulary diversity and malformed fragments. Not reliable. |
| [rTqsO5M9zbY — समवशरण विशेष](https://www.youtube.com/watch?v=rTqsO5M9zbY) | 8.98 min | hi / 0.997 | 1,011 | 2 | ौ / ॐ ×74 | Repeated mantra/fragment sequences and a repeated-token run near the end. Requires audio review. |
| [PHyJ0uol4m0 — भगवान महावीर का प्रथम समवशरण](https://www.youtube.com/watch?v=PHyJ0uol4m0) | 16.31 min | hi / 0.979 | 1,489 | 3 | तो ×74 | Repeated-word run and substantial phonetic corruption. Not reliable as a verbatim transcript. |
| [9jKDDkkg694 — Lockdown Shivir Session on SAMOSARAN](https://www.youtube.com/watch?v=9jKDDkkg694) | 112.74 min | hi / 0.658 | 12,311 | 70 | ौ ×73 | Long transcript with many replacement characters and malformed fragments. Hindi detection probability is also relatively low. Requires extensive review. |
| [053fJPHt4PU — Samosaran 05 May live](https://www.youtube.com/watch?v=053fJPHt4PU) | 186.53 min | hi / 0.817 | 13,499 | 246 | तो ×74 | Very large number of replacement characters, repeated fragments and spelling corruption. Not reliable. |
| [6fTqRoPGdzk — समवशरण सम्पूर्ण जानकारी](https://www.youtube.com/watch?v=6fTqRoPGdzk) | 8.38 min | hi / 0.968 | 1,177 | 3 | ौ ×73 | Non-lexical repeated fragments and malformed text. Not reliable without correction. |
| [2Y_sQBapWBM — Ep25: Samavasaran ka Rahasya](https://www.youtube.com/watch?v=2Y_sQBapWBM) | 23.73 min | hi / 0.998 | 3,365 | 1 | ॐ ×74 | Several passages are readable, but there are phonetic spelling errors and a long repeated mantra token. Needs audio verification. |
| [g8BvEaY9LoY — Samavsharan (Part-10) 3D Animation](https://www.youtube.com/watch?v=g8BvEaY9LoY) | 3.41 min | hi / 0.984 | 112 | 1 | 1 | **Very low transcript yield** for a 3.4-minute recording. The saved text may be partial; coverage must be checked against the audio. |
| [x9XAer5p6-k — कल्पद्रुम यह समवशरण है](https://www.youtube.com/watch?v=x9XAer5p6-k) | 8.50 min | hi / 0.919 | 60 | 0 | 1 | **Extremely low transcript yield** (60 tokens for an 8.5-minute recording); inference took about 6.3 seconds. Strong incomplete-output suspicion. |
| [jDzcOghVQ6Q — Samosaran Se Divya Dhwani](https://www.youtube.com/watch?v=jDzcOghVQ6Q) | 72.90 min | hi / 0.487 | 6,278 | 50 | ॐ ×74 | Low initial language probability, 50 replacement characters, code-mixed/garbled passages and repeated tokens. Not reliable as-is. |
| [StfeLi9xP0Q — Samosaran Se Divya Dhwani 2](https://www.youtube.com/watch?v=StfeLi9xP0Q) | 72.75 min | hi / 0.815 | 6,459 | 47 | तो ×74 | Repeated-word runs, replacement characters and malformed fragments. Not reliable as-is. |
| [o1pKnYuV2KY — समवसरण का थोकडा (ग्यारहवीं) PART 2](https://www.youtube.com/watch?v=o1pKnYuV2KY) | 71.47 min | hi / 0.911 | 3,734 | 47 | तो ×74 | Very low unique-token ratio (0.165), replacement characters and long repeated runs. Not reliable. |
| [3wlMq29K6TE — समवसरण का थोकडा (ग्यारहवीं)-PART 1](https://www.youtube.com/watch?v=3wlMq29K6TE) | 69.60 min | hi / 0.935 | 4,530 | 72 | ौ ×74 | Very low unique-token ratio (0.184), replacement characters and long repeated fragments. Not reliable. |

### Interpreting the flags correctly

- A repeated ॐ token may reflect a real chant. It should not be deleted or corrected without listening.
- A long run of fragments such as ौ, ।, or a repeated ordinary word such as तो is suspicious, but still requires audio confirmation.
- The � symbol is a Unicode replacement character present in the saved transcript file. It is not a valid spelling of a Sanskrit/Prakrit syllable.
- A high language probability only describes the initial language classifier. It does not certify word accuracy.
- A short transcript may mean no speech, silence, or a failed/partial decode. The audio is needed to distinguish these cases.

## 4. Overall findings

| Finding | Count |
|---|---:|
| Distinct YouTube videos represented in the test outputs | 21 |
| Saved Whisper transcript files | 22 |
| Videos with an empty transcript | 1 |
| Videos with very low transcript yield requiring coverage verification | 2 |
| Videos with a 10+ identical-token consecutive run | 17 |
| Videos containing at least one Unicode replacement character | 19 |
| Videos initially labelled Hindi | 20 |
| Videos with a non-Hindi initial label | 1 (English, 0.364 probability) |
| Videos with no independent YouTube-caption/reference transcript in the repository | 21 |

The duplicate R_Dd4slDghA run had 1,000 words in one transcript and 1,075 in the other; both had a 44-token consecutive run of अगर. The two runs should not be counted as separate videos.

## 5. What can be concluded now

1. Whisper inference completed for most selected videos, but the saved output quality is inconsistent and frequently visibly degraded.
2. The older CLI could label the empty qr8A8HNk9jk output as success. This demonstrates why an inference call returning without raising an exception is not enough to mark a transcript as successful. The updated CLI distinguishes empty output from completed text output.
3. The two low-yield transcripts (g8BvEaY9LoY and x9XAer5p6-k) must be checked for missing content before any comparison.
4. No reliable winner or accuracy ranking can be declared. There is no human reference transcript, no WER/CER, and no verified caption-to-Whisper alignment.
5. These recordings are mostly Samavasaran/Jain educational material; they do not form a balanced Indian-language benchmark. They are a useful initial domain test set, not evidence of broad Indian-language performance.

## 6. How to complete YouTube-caption cross-verification locally

The 21 URLs are listed in youtube_video_urls.txt. The YouTube video pages and timed-text endpoints could not be retrieved in this environment, so use your local Windows machine (where you already downloaded the audio) to check whether each video exposes manual or automatic subtitle tracks.

~~~powershell
pip install -r requirements-youtube.txt
New-Item -ItemType Directory -Force data/references/youtube-captions | Out-Null
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "all" --sub-format vtt --ignore-errors -o "data/references/youtube-captions/%(id)s.%(language)s.%(ext)s" -a docs/youtube_video_urls.txt
~~~

Then inspect the downloaded VTT for every video ID:
- Record whether it is a creator-provided subtitle or an auto-generated caption.
- Align the VTT timestamps with the same sections of the Whisper transcript.
- Manually listen to sections with mismatched words, mantra syllables, Sanskrit/Prakrit terms, and any � or repeated-token flags.
- Create a human-corrected reference transcript for any clip used in WER/CER. YouTube auto-captions are another ASR output, not ground truth.

Do not publish or commit caption files or transcripts unless their redistribution is permitted. If you add the locally retrieved VTT files to your working environment, BharatASR can make a follow-up report that records the exact caption availability and compares each transcript against those tracks.

## 7. Recommended next steps

1. Fix the empty and low-yield Whisper cases first: qr8A8HNk9jk, g8BvEaY9LoY, and x9XAer5p6-k.
2. Re-run the 21 videos with the updated quality diagnostics; keep raw output and quality warnings separately.
3. Download any available YouTube subtitle tracks locally and establish which are manual and which are automatic.
4. Prepare human-verified reference text for a representative 30–60 second segment from each video before calculating WER/CER.
5. Only after the Whisper baseline is stable, compare another ASR backend on identical audio and the same reference.
