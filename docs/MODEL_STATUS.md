# Model integration status

| Model | Adapter | Test evidence | Access |
|---|---|---|---|
| faster-whisper | Local | Ran on two Hindi lectures; language ID succeeded, but inspected transcripts showed serious repetition and replacement characters | Public weights |
| ARTPARK Vaani Whisper-Small Hindi | Local | Added as a public Hindi-only comparison backend; not yet run on the user's test videos | Public, Apache-2.0 |
| SraVaani 1.0 | Local | No inference; user's runs received HTTP 403 | Gated; owner approval and accepted conditions required |
| Indic-Transcribe Core / Flex | Local | No inference; user's runs received gated HTTP 403 | Gated; owner approval and accepted conditions required |
| AI4Bharat IndicConformer | Local | Not part of the observed successful test runs | AI4Bharat NeMo environment and checkpoint required |
| Sarvam Saaras | Hosted API | Not part of the initial test | Optional, metered, explicit opt-in |

See [INITIAL_TEST_REPORT.md](INITIAL_TEST_REPORT.md) for evidence and limitations.
