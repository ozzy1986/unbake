# Unbake ASR Prototype

Prototype for the Unbake test task: accept a vocal stem, recognize lyrics, return LRCLIB-like synced lyrics with word timestamps, and evaluate the result against reference lyrics.

## What Is Included

- `tools/transcribe.py` - runs ASR with `faster-whisper` and writes JSON output.
- `tools/align_whisperx.py` - runs a second WhisperX alignment pass for word-level timestamps.
- `tools/evaluate_text.py` - computes `CER` and `WER` against reference lyrics.
- `data/` - test audio samples and manually collected/reference lyrics used for evaluation.
- `outputs/` - real generated outputs from local experiments.
- `SUBMISSION_DRAFT.txt` - human-readable write-up for the Google Doc answer.

## Pipeline

```text
Vocal m4a
  -> ASR transcription
  -> plainLyrics + syncedLyrics + word timestamps
  -> optional WhisperX alignment
  -> CER/WER evaluation against reference lyrics
```

## Reproduce Locally

```powershell
py -3.9 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools\transcribe.py "data\unbake-vocals\en\Post Malone & 21 Savage - rockstar.m4a" --output "outputs\rockstar.test.json" --model-size small --device cpu --compute-type int8 --language en
.\.venv\Scripts\python.exe tools\evaluate_text.py --reference "data\references\en\post_malone_rockstar.txt" --hypothesis "outputs\rockstar.test.json"
```

## Measured Baseline

Local hardware:

- CPU: Intel i5-7300HQ
- RAM: 8 GB
- GPU: GTX 1050 4 GB, but main baseline was CPU

`faster-whisper small` results:

| Sample | CER | WER | Runtime |
| --- | ---: | ---: | ---: |
| EN rockstar | 0.250 | 0.345 | 77s / 218s audio |
| ES BELLAKEO | 0.612 | 0.783 | 381s / 197s audio |
| FR Place de la Republique | 0.228 | 0.391 | 62s / 261s audio |
| RU Polkovniku nikto ne pishet | 0.245 | 0.604 | 198s / 243s audio |

## Conclusion

The pipeline works end-to-end, including text output, LRCLIB-like line timestamps, word timestamps, and automatic evaluation. The weak local CPU baseline is not accurate enough for production on noisy Demucs vocal stems. Production-quality testing should use a stronger ASR model on GPU and keep WhisperX-style alignment for timing precision.
