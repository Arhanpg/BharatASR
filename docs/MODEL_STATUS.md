# Model integration and evaluation status

**Updated:** 20 November 2026  
**Evaluation snapshot:** latest 14 November 2026 YouTube batch (22 distinct recordings; approximately 18.17 hours).

| Model | Adapter | Actual repository evidence | Access / next action |
|---|---|---|---|
| faster-whisper / Whisper Small | Local | 22/22 latest unique-video outputs are non-empty, but 21 carry heuristic review warnings. Output audit finds repetition, replacement characters, script contamination and low-yield cases. | Public weights. Keep as the multilingual baseline; do not call it accurate without reference scoring. |
| ARTPARK Vaani Whisper-Small Hindi | Local | 21/22 latest unique-video outputs completed; one run failed before inference because the feature extractor / `preprocessor_config.json` could not be loaded. Many shorter explanatory excerpts look more readable than Whisper, but long-form phrase loops and low lexical diversity occur. Median matched-video inference time is about 2.09x Whisper in the recorded run set. | Public model card, Apache-2.0. Retain as provisional readability preference for short/medium Hindi explanation audio, with human review. Not a verified accuracy winner. |
| SraVaani 1.0 | Local | No transcript output in the current benchmark. Previous attempts recorded HTTP 403/access restrictions. | Hugging Face access is gated by acceptance/contact requirements. Highest-priority additional local model to evaluate; model page reports 430M FastConformer and published benchmark results. |
| AI4Bharat IndicConformer | Local | Adapter is implemented, but no completed inference result is present in the current successful test batch. | Requires the AI4Bharat NeMo environment and matching checkpoint. Run as a multilingual Indian-language baseline. |
| Indic-Transcribe Core / Flex | Local | No transcript output in the current benchmark; previous attempts recorded gated-access HTTP 403. | Requires access approval and acceptance of model terms. Large (~4.6 GB) checkpoint; CPU path is recommended for 4 GB VRAM hardware. Re-test after access is granted. |
| Sarvam Saaras v4 | Hosted API | No result in the current benchmark. | Optional metered API; evaluate separately from local inference. Use `verbatim` mode for word-preserving religious-domain trials and batch API for long recordings, subject to current provider limits/pricing. |

## Current conclusion

There is **no defensible accuracy winner** yet. The repository has not produced a set of human-verified reference transcripts aligned to the source audio, so no BharatASR WER/CER ranking can be calculated.

Among the two models with usable transcript outputs, Vaani Whisper-Small Hindi is the provisional text-readability preference for shorter/medium Hindi explanatory clips. Whisper Small remains the multilingual baseline. Neither is validated for verbatim Jain, Sanskrit or Prakrit discourse. All sacred terminology and mantra repetitions require listening and knowledgeable human review.

See [README.md](../README.md) for the headline recommendation and [MODEL_BENCHMARK_REVIEW_2026-11-14.md](MODEL_BENCHMARK_REVIEW_2026-11-14.md) for the full 22-video text-quality audit.
