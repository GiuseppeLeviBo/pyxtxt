# PyxTxt

[![PyPI version](https://img.shields.io/pypi/v/pyxtxt.svg)](https://pypi.org/project/pyxtxt/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyxtxt.svg)](https://pypi.org/project/pyxtxt/)
[![CI](https://github.com/GiuseppeLeviBo/pyxtxt/actions/workflows/ci.yml/badge.svg)](https://github.com/GiuseppeLeviBo/pyxtxt/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PyxTxt** is a small Python library that extracts plain text from many file formats through a single function, `xtxt()`.
It detects the file type automatically (via `libmagic`) and dispatches to the right extractor. Extractors are optional:
install only the ones you need.

```python
from pyxtxt import xtxt

text = xtxt("report.pdf")
```

---

## ✨ Features

- **One function for everything**: `xtxt()` accepts a file path, an `io.BytesIO` buffer, raw `bytes` or a `requests.Response`
- **Automatic type detection** with `python-magic`, refined by the file extension when libmagic is not specific enough (e.g. Markdown)
- **Modular dependencies**: each format is an optional extra, the core only needs `python-magic`
- **Office, web and document formats**: PDF, DOCX, PPTX, XLSX, XLS, ODT, HTML, XML, SVG, Markdown, EPUB, RTF, EML, MSG, LaTeX, DOC, TXT
- **Audio and video transcription** with OpenAI Whisper
- **OCR from images** with EasyOCR or with a local multimodal LLM through Ollama
- **EXIF metadata** extraction from photos

---

## 📄 Supported formats

| Format | Install extra | Notes |
|---|---|---|
| PDF | `pdf` | PyMuPDF |
| DOCX | `docx` | Paragraph text (tables are not extracted yet) |
| PPTX | `presentation` | Text of all slide shapes |
| XLSX, XLS | `spreadsheet` | Every row of every visible sheet, cells joined with ` \| ` |
| ODT | `odf` | |
| HTML | `html` | |
| XML, SVG | `html` | Both use `lxml`, installed by the `html` extra |
| Markdown | `markdown` | Detected by the `.md` / `.markdown` extension |
| EPUB | `epub` | |
| RTF | `rtf` | |
| EML | `email` | Plain-text and HTML parts |
| MSG (Outlook) | `outlook` | |
| LaTeX | `latex` | |
| DOC (legacy Word) | — | Needs the `antiword` system tool |
| TXT and other `text/*` | — | Always available, decoded as UTF-8 |
| Audio and video | `audio` | Whisper, needs `ffmpeg`; heavy download |
| Images (OCR) | `ocr` or `ocr-ollama` | See [OCR from images](#-ocr-from-images) |

To list what is available in your installation:

```python
from pyxtxt import extxt_available_formats

print(extxt_available_formats())             # MIME types
print(extxt_available_formats(pretty=True))  # Short names
```

---

## 📦 Installation

Install every extractor (this includes the heavy audio and OCR dependencies):

```bash
pip install "pyxtxt[all]"
```

or only the formats you need:

```bash
pip install "pyxtxt[pdf,docx,presentation,spreadsheet,html,markdown,epub,email]"
```

Heavy optional extras:

```bash
pip install "pyxtxt[audio]"       # Whisper transcription (~2 GB with models, pulls in PyTorch)
pip install "pyxtxt[ocr]"         # EasyOCR (~1 GB with models, pulls in PyTorch)
pip install "pyxtxt[ocr-ollama]"  # OCR through a local Ollama server
```

### System dependencies

**libmagic** (required by `python-magic`):

```bash
sudo apt install libmagic1      # Ubuntu / Debian
brew install libmagic           # macOS
```

On Windows the `python-magic-bin` package, which bundles libmagic, is installed automatically.

**antiword** (only for legacy `.doc` files):

```bash
sudo apt install antiword       # Ubuntu / Debian
brew install antiword           # macOS
```

**ffmpeg** (only for audio/video transcription):

```bash
sudo apt install ffmpeg         # Ubuntu / Debian
brew install ffmpeg             # macOS
# Windows: https://ffmpeg.org/download.html
```

---

## 📚 Usage

### Basic usage

```python
import io
from pyxtxt import xtxt

# From a file path
text = xtxt("document.pdf")

# From an in-memory buffer
with open("document.docx", "rb") as f:
    buffer = io.BytesIO(f.read())
text = xtxt(buffer)

# Give the buffer a name to help type detection (useful for Markdown, LaTeX, RTF)
buffer = io.BytesIO(markdown_bytes)
buffer.name = "notes.md"
text = xtxt(buffer)
```

`xtxt()` returns the extracted text as a `str`, or `None` when the file cannot be read or its type is not supported.

### Web content

`xtxt_from_url()` and `requests.Response` support need the `requests` package (`pip install requests`).

```python
import requests
from pyxtxt import xtxt, xtxt_from_url

response = requests.get("https://example.com/document.pdf")
text = xtxt(response.content)   # from bytes
text = xtxt(response)           # from the Response object

text = xtxt_from_url("https://example.com/document.pdf", timeout=10)
```

Extra keyword arguments of `xtxt_from_url()` are passed to `requests.get()`.

Typical uses:

```python
# File uploads (Flask / Django)
text = xtxt(request.files["document"].read())

# Email attachments
text = xtxt(attachment.get_payload(decode=True))
```

### Audio and video transcription

```python
from pyxtxt import xtxt

text = xtxt("meeting_recording.mp3")
text = xtxt("interview.wav")
text = xtxt("presentation.mp4")   # the audio track is extracted automatically
```

The Whisper `base` model is downloaded on first use and cached for the following calls.

### 🖼 OCR from images

Two OCR back-ends are available. If both are installed, **Ollama takes precedence** for `xtxt()` on images.

**EasyOCR** (`pip install "pyxtxt[ocr]"`) runs locally on CPU, recognising Italian and English:

```python
text = xtxt("scanned_document.png")
```

**Ollama** (`pip install "pyxtxt[ocr-ollama]"`) uses a multimodal LLM served by a local
[Ollama](https://ollama.com) instance. Start the server and pull a model first (`ollama pull gemma3:4b`).

```python
from pyxtxt import (
    xtxt, xtxt_image_describe,
    set_ollama_model, set_ollama_config, get_ollama_config, reset_ollama_config,
)

set_ollama_model("gemma3:12b")   # default: gemma3:4b; also llava:7b, llava:13b, gemma3:27b

set_ollama_config(
    language="italian",       # language hint
    caption_length="long",    # short, medium, long
    style="detailed",         # descriptive, technical, simple, detailed
    context="document",       # general, document, handwriting, technical, cookbook, ...
    temperature=0.2,
    max_tokens=2000,
    auto_fallback=False,      # by default other models are tried when the result looks poor
)

text = xtxt("complex_document.png")                   # text only
analysis = xtxt_image_describe("scientific_diagram.png")
# TEXT: ...
# DESCRIPTION: ...

print(get_ollama_config())
reset_ollama_config()
```

#### Confidence score

```python
from pyxtxt import xtxt_image_with_confidence, set_ollama_config

set_ollama_config(confidence_threshold=0.8)
text, confidence = xtxt_image_with_confidence("document.png", mode="ocr")
```

The score is a **heuristic** computed on the model's answer: it rewards structured text (numbers, punctuation) and
penalises vague language and typical hallucination keywords (e.g. "ancient", "papyrus", "painting", "dragon").
It is not a calibrated probability. In OCR mode, results below `confidence_threshold` (default 0.7) are discarded
and an empty string is returned.

### EXIF metadata

Requires Pillow (installed by the `ocr` or `ocr-ollama` extras, or `pip install pillow`).

```python
from pyxtxt import xtxt_exif

print(xtxt_exif("vacation_photo.jpg"))
# Camera make/model, shooting settings, date/time, GPS coordinates, image size...
```

### More examples

An examples script is installed with the package:

```bash
python -m pyxtxt.examples
```

or, to read its source:

```python
from importlib.resources import files
print((files("pyxtxt") / "examples.py").read_text())
```

---

## ⚠️ Known limitations

- **Supported inputs**: file paths, `io.BytesIO`, `bytes` and `requests.Response`. A file object returned by
  `open()` must be read first (`xtxt(f.read())`).
- **Type detection without a file name**: libmagic cannot tell apart some formats from raw bytes (legacy Office files
  share the same signature; Markdown looks like plain text). Pass a file path, or set `buffer.name`, when possible.
- **Legacy PowerPoint (`.ppt`)** is not supported.
- **DOCX**: text inside tables, headers and footers is not extracted yet. **SVG**: text inside `<tspan>` elements is not extracted yet.
- Errors are reported with messages printed to standard output and the functions return `None` or an empty string;
  they do not raise exceptions.

### 🤖 AI-powered features

OCR through Ollama and Whisper transcription rely on machine-learning models and can produce **hallucinations**
(text or content that is not there), misinterpretations and language errors. Results vary between models and versions.

**Do not use them for critical applications** — medical diagnosis or medical image interpretation, legal or financial
documents where errors matter, safety systems — without human verification. Validate the results against the source,
use the confidence score as a hint only, and keep a traditional OCR (EasyOCR) as a cross-check when accuracy matters.

---

## 🛠 Development

```bash
git clone https://github.com/GiuseppeLeviBo/pyxtxt
cd pyxtxt
python -m venv .venv && source .venv/bin/activate
pip install -e ".[pdf,docx,presentation,spreadsheet,odf,html,markdown,epub,rtf,email,latex]" pytest
pytest
```

Tests for formats whose libraries are not installed are skipped. CI runs the test suite on Python 3.10–3.13.

### Releasing

Releases are published to PyPI by GitHub Actions (`.github/workflows/publish.yml`) through
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/), so no API token is needed:

1. Update `version` in `pyproject.toml` and the changelog below; merge to `main`.
2. Tag and push: `git tag v0.3.6 && git push origin v0.3.6`.

The workflow checks that the tag matches the version, builds sdist and wheel, and uploads them.

One-time setup: on PyPI, open the project's *Settings → Publishing* and add a
GitHub publisher with owner `GiuseppeLeviBo`, repository `pyxtxt`, workflow `publish.yml` and environment `pypi`.

---

## 🔒 License

Distributed under the MIT License. See [LICENSE](LICENSE).

## 🤝 Contributing

Pull requests, issues and feedback are welcome.

- **Bug reports**: include a sample file (or how to create one) and the full error message
- **Feature requests**: describe your use case and the expected behaviour
- **Code**: follow the existing patterns and add a test in `tests/`

---

## 📊 Changelog

### v0.3.6
- **FIXED**: `import pyxtxt` crashed with `AttributeError` unless both `ollama` and Pillow were installed (regression in 0.3.4.2 and 0.3.5)
- **FIXED**: Markdown, RTF and LaTeX files were returned as raw source instead of being converted to text
- **FIXED**: a failed extraction (e.g. a corrupted PDF) returned the string `"None"` instead of `None`
- **FIXED**: XLSX and XLS files were silently truncated to 200 and 100 rows per sheet; all rows are now extracted
  (`max_rows_per_sheet` is still available when calling the extractors directly)
- **FIXED**: when both EasyOCR and Ollama were installed, the OCR back-end used for images was random; Ollama now always takes precedence
- **FIXED**: a single extractor failing to load no longer prevents the whole package from importing
- **FIXED**: `BytesIO` buffers keep their `name`, which is now used to refine type detection
- PyMuPDF is imported as `pymupdf`, removing the deprecation warning printed at every import
- Added the missing `LICENSE` file, SPDX license metadata and project URLs
- Removed the obsolete `pyxtxt/pyxtxt.py` module
- Added a test suite and GitHub Actions workflows for CI and PyPI publishing

### v0.3.0 – v0.3.5
- **NEW**: OCR through Ollama multimodal models (`set_ollama_model`, `xtxt_image_describe`) — 0.3.0
- **NEW**: `set_ollama_config()`, `get_ollama_config()`, `reset_ollama_config()` — 0.3.2
- **NEW**: confidence score and hallucination detection (`xtxt_image_with_confidence`) — 0.3.4
- **NEW**: image enhancement before OCR, automatic model fallback, context presets — 0.3.4.2
- **NEW**: EXIF metadata extraction (`xtxt_exif`) — 0.3.5

### v0.2.4
- **NEW**: video transcription support (MP4, MOV, AVI, WebM, MKV) via Whisper

### v0.2.3
- **NEW**: audio transcription (MP3, WAV, M4A, FLAC, ...) with Whisper
- **NEW**: OCR from images (JPEG, PNG, TIFF, BMP, WebP) with EasyOCR
- **NEW**: `audio`, `ocr` and `all` installation extras

### v0.2.0 – v0.2.2
- **NEW**: automatic extractor registration
- **NEW**: Markdown, EPUB, RTF, EML, MSG and LaTeX extractors

### v0.1.24
- **NEW**: support for `bytes` and `requests.Response` inputs, `xtxt_from_url()` helper

### v0.1.0 – v0.1.23
- Initial releases: modular extractors for PDF, DOCX, PPTX, XLSX, ODT, HTML, XML, TXT and legacy Office files,
  MIME detection with python-magic, `BytesIO` support
