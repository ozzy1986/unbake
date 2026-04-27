# Unbake ASR Prototype

Репозиторий с прототипом для тестового задания Unbake: получить текст песни и таймкоды из вокальной дорожки после Demucs v4.

## Что внутри

- `SUBMISSION_DRAFT.txt` - готовый текст ответа для Google Doc.
- `tools/transcribe.py` - распознаёт аудио через `faster-whisper` и сохраняет JSON.
- `tools/align_whisperx.py` - делает второй проход alignment через WhisperX для word-level timestamps.
- `tools/evaluate_text.py` - считает `CER` и `WER` относительно reference lyrics.
- `data/` - аудио, использованное в тестах, и reference lyrics.
- `outputs/` - реальные JSON-результаты наших прогонов.
- `unbake-vocals/` - локальный набор vocal samples, который был использован как тестовый датасет.

## Пайплайн

```text
вокал m4a
  -> распознавание текста
  -> plainLyrics + syncedLyrics + таймкоды слов
  -> опциональный второй проход WhisperX
  -> оценка CER/WER по reference lyrics
```

## Как повторить один прогон

```powershell
py -3.9 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools\transcribe.py "data\unbake-vocals\en\Post Malone & 21 Savage - rockstar.m4a" --output "outputs\rockstar.test.json" --model-size small --device cpu --compute-type int8 --language en
.\.venv\Scripts\python.exe tools\evaluate_text.py --reference "data\references\en\post_malone_rockstar.txt" --hypothesis "outputs\rockstar.test.json"
```

## Что мы измерили

Локальное железо:

- CPU: Intel i5-7300HQ
- RAM: 8 GB
- GPU: GTX 1050 4 GB, но основной baseline запускался на CPU

Результаты `faster-whisper small`:

| Пример | CER | WER | Время |
| --- | ---: | ---: | ---: |
| EN rockstar | 0.250 | 0.345 | 77s / 218s audio |
| ES BELLAKEO | 0.612 | 0.783 | 381s / 197s audio |
| FR Place de la Republique | 0.228 | 0.391 | 62s / 261s audio |
| RU Polkovniku nikto ne pishet | 0.245 | 0.604 | 198s / 243s audio |

## Вывод

Пайплайн работает end-to-end: из вокального `m4a` получается текст, LRCLIB-like `syncedLyrics`, word timestamps и автоматическая оценка качества.

Текущий слабый CPU baseline не даёт production-quality accuracy на грязных vocal stems после Demucs. Для финального качества нужен более сильный ASR на GPU и отдельный alignment-pass для точных таймкодов.
