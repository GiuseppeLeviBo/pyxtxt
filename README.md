# PyxTxt

[![PyPI version](https://img.shields.io/pypi/v/pyxtxt.svg)](https://pypi.org/project/pyxtxt/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyxtxt.svg)](https://pypi.org/project/pyxtxt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PyxTxt** is a simple and powerful Python library to extract text from various file formats.  
It supports PDF, DOCX, XLSX, PPTX, ODT, HTML, XML, TXT, legacy Office files, **audio/video transcription**, **OCR from images**, and more.

**NEW in v0.2.4**: Added video transcription support! Now supports both audio and video files using Whisper.

---

## ✨ Features

- **Multiple input types**: File paths, `io.BytesIO` buffers, raw `bytes` objects, and `requests.Response` objects
- **Wide format support**: PDF, DOCX, PPTX, XLSX, ODT, HTML, XML, TXT, Markdown, EPUB, RTF, EML, MSG, LaTeX, legacy Office files (.xls, .ppt, .doc)
- **Audio & Video transcription**: MP3, WAV, M4A, FLAC, MP4, MOV, AVI, WebM, MKV and more using OpenAI Whisper
- **OCR from images**: JPEG, PNG, TIFF, BMP using EasyOCR with multilingual support
- **Automatic MIME detection**: Uses `python-magic` for intelligent file type recognition
- **Web-ready**: Direct support for downloading and extracting text from URLs
- **Memory efficient**: Process files without saving to disk
- **Modern Python**: Full type hints and clean API design

---

## 📦 Installation 

The library is modular so you can install all modules:

```bash
pip install pyxtxt[all]
```
or just the modules you need:
```bash
pip install pyxtxt[pdf,docx,presentation,spreadsheet,html,markdown,epub,email]
```

### Audio & OCR (Heavy Dependencies)
```bash
# Audio transcription (~2GB download for Whisper models)
pip install pyxtxt[audio]

# Traditional OCR from images (~1GB download for EasyOCR models)
pip install pyxtxt[ocr]

# AI-powered OCR via Ollama (requires local Ollama + gemma3:4b model)
pip install pyxtxt[ocr-ollama]

# Both audio and traditional OCR
pip install pyxtxt[audio,ocr]
```

Because needed libraries are common, installing the html module will also enable SVG and XML support.
The architecture is designed to grow with new modules for additional formats.
## ⚠️ Note: You must have libmagic installed on your system (required by python-magic).
The pyproject.toml file should select the correct version for your system. But if you have any problem you can install it manually.

**On Ubuntu/Debian:**

```bash
sudo apt install libmagic1
```

**On Mac (Homebrew):**

```bash
brew install libmagic
```
**On Windows:**

Use python-magic-bin instead of python-magic for easier installation.

## 🛠️ Dependencies

### Core Dependencies
- python-magic (automatic file type detection)

### Optional Dependencies by Format
- **PDF**: PyMuPDF
- **Office**: python-docx, python-pptx, openpyxl, xlrd
- **Web/HTML**: beautifulsoup4, lxml
- **OpenDocument**: odfpy
- **Markdown**: markdown
- **EPUB**: ebooklib
- **RTF**: striprtf
- **Email**: extract-msg (for MSG files)
- **LaTeX**: pylatexenc
- **Audio**: openai-whisper (heavy ~2GB models)
- **OCR**: easyocr, pillow (heavy ~1GB models)
- **OCR-Ollama**: ollama, pillow (requires local Ollama server)

Dependencies are automatically installed based on selected optional groups.

### System Dependencies
Some extractors require system-level tools to be installed:

- **Legacy DOC files**: `antiword` - Install via your package manager:
  ```bash
  # Ubuntu/Debian
  sudo apt install antiword
  
  # macOS
  brew install antiword
  
  # CentOS/RHEL
  sudo yum install antiword
  ```

- **Audio/Video transcription**: `ffmpeg` - Required for audio preprocessing:
  ```bash
  # Ubuntu/Debian
  sudo apt install ffmpeg
  
  # macOS
  brew install ffmpeg
  
  # Windows
  # Download from https://ffmpeg.org/download.html
  ```

## 📚 Usage Examples

### Basic Usage
```python
from pyxtxt import xtxt

# Extract from file path
text = xtxt("document.pdf")
print(text)

# Extract from BytesIO buffer
import io
with open("document.docx", "rb") as f:
    buffer = io.BytesIO(f.read())
text = xtxt(buffer)
print(text)
```

### NEW: Web Content Support
```python
import requests
from pyxtxt import xtxt, xtxt_from_url

# Method 1: Direct from bytes
response = requests.get("https://example.com/document.pdf")
text = xtxt(response.content)

# Method 2: Direct from Response object  
text = xtxt(response)

# Method 3: URL helper function
text = xtxt_from_url("https://example.com/document.pdf")
```

### Audio & Video Transcription (NEW)
```python
from pyxtxt import xtxt

# Transcribe audio files
text = xtxt("meeting_recording.mp3")
text = xtxt("interview.wav")
text = xtxt("podcast.m4a")

# Transcribe video files (extracts audio)
text = xtxt("presentation.mp4")
text = xtxt("conference_video.mov")
text = xtxt("webinar.avi")

# From web audio/video
import requests
audio_response = requests.get("https://example.com/audio.mp3")
text = xtxt(audio_response.content)

video_response = requests.get("https://example.com/video.mp4")
text = xtxt(video_response.content)
```

### OCR from Images (NEW)
```python
from pyxtxt import xtxt

# Traditional OCR with EasyOCR (install with: pip install pyxtxt[ocr])
text = xtxt("scanned_document.png")
text = xtxt("screenshot.jpg")
text = xtxt("invoice.tiff")

# Extract EXIF metadata from photos (uses Pillow, already included)
from pyxtxt import xtxt_exif

exif_data = xtxt_exif("vacation_photo.jpg")
print(exif_data)
# Output: Camera make/model, GPS coordinates, shooting settings, datetime, etc.

# AI-powered OCR with Ollama (install with: pip install pyxtxt[ocr-ollama])
# Requires: ollama server running + gemma3:4b model
from pyxtxt import (
    xtxt, xtxt_image_describe, 
    set_ollama_model, set_ollama_config, get_ollama_config
)

# Configure model (optional, default is gemma3:4b)
set_ollama_model("gemma3:12b")  # or llava:7b, llava:13b, gemma3:27b

# Configure LLM parameters for better captions
set_ollama_config(
    language='italian',        # Language hint for captions
    caption_length='long',     # short, medium, long
    style='detailed',          # descriptive, technical, simple, detailed
    temperature=0.2,           # Creativity level (0.0-1.0)
    max_tokens=2000           # Maximum response length
)

# Extract only text (OCR mode) 
text = xtxt("complex_document.png")
print(f"Extracted text: {text}")

# Extract text + detailed caption
full_analysis = xtxt_image_describe("scientific_diagram.png")
print(full_analysis)
# Output example:
# TEXT: Figura 2.1: Struttura molecolare del DNA
# DESCRIPTION: Diagramma scientifico dettagliato che mostra la doppia elica del DNA 
# con nucleotidi colorati, legami idrogeno evidenziati e etichette in italiano per 
# le basi azotate (adenina, timina, citosina, guanina).

# Check current configuration
config = get_ollama_config()
print(f"Current config: {config}")

# Reset to defaults if needed
from pyxtxt import reset_ollama_config
reset_ollama_config()

# From web images
import requests
image_response = requests.get("https://example.com/document.png")
text = xtxt(image_response.content)
```

### AI OCR Confidence Scoring (NEW)

⚠️ **IMPORTANT**: AI-powered OCR is experimental technology that may produce errors, hallucinations, or misinterpretations. Always validate results for critical applications.

The OCR-Ollama system includes confidence scoring to help identify unreliable results:

```python
from pyxtxt import xtxt_image_with_confidence, set_ollama_config

# Configure confidence threshold (0.0-1.0, default: 0.7)
set_ollama_config(confidence_threshold=0.8)  # More restrictive

# Get text with confidence score
text, confidence = xtxt_image_with_confidence("document.png", mode="ocr")
print(f"Confidence: {confidence:.2f} ({confidence*100:.1f}%)")
print(f"Text: {text}")

# Check if reliable
if confidence < 0.7:
    print("⚠️ Low confidence - result may be unreliable")
    print("Consider using traditional OCR or manual verification")
else:
    print("✅ Good confidence - result likely reliable")
```

#### Confidence Scoring Features

- **Hallucination Detection**: Penalizes historical/cultural references that often indicate AI misinterpretation
- **Pattern Recognition**: Rewards structured text (numbers, punctuation, proper formatting)
- **Uncertainty Detection**: Flags vague language ("appears to be", "seems like", etc.)
- **Quality Assessment**: Considers content length, repetition, and coherence

#### Common Hallucination Patterns (Automatically Detected)
- **Historical Content**: "ancient", "medieval", "Egyptian papyrus", "hieroglyphs"
- **Artistic Interpretations**: "painting", "artwork", "masterpiece", "Renaissance"  
- **Fantasy Content**: "mystical", "magical", "dragon", "wizard"
- **Scientific Misinterpretation**: "fossil", "geological formation", "crystal structure"
- **Vague Language**: "unclear", "difficult to read", "appears to be"

### Command-Line OCR Example

A complete example script for command-line usage is available:

```python
# Download and run the example script
import requests

example_url = "https://raw.githubusercontent.com/yourusername/pyxtxt/main/ocr_example.py"
with open("ocr_example.py", "wb") as f:
    f.write(requests.get(example_url).content)

# Usage examples:
# python ocr_example.py document.png
# python ocr_example.py chart.jpg --mode=describe --lang=italian --style=detailed
# python ocr_example.py diagram.png --mode=describe --length=long --temp=0.3

# NEW: Confidence scoring examples
# python ocr_example.py suspicious.png --show-confidence
# python ocr_example.py medical.png --confidence=0.9 --show-confidence
# python ocr_example.py diagram.png --confidence=0.5 --mode=describe --show-confidence
```

The script supports:
- **OCR mode**: Extract only text from images
- **Describe mode**: Extract text + generate detailed captions
- **Language hints**: Specify caption language (italian, english, etc.)
- **Style control**: descriptive, technical, simple, detailed
- **Length control**: short, medium, long captions
- **Temperature**: Adjust LLM creativity (0.0-1.0)
- **Confidence scoring**: Set threshold and display confidence scores
- **Quality filtering**: Automatically reject low-confidence results

### Show Available Formats
```python
from pyxtxt import extxt_available_formats

# List supported MIME types
formats = extxt_available_formats()
print(formats)

# Pretty format names
formats = extxt_available_formats(pretty=True)
print(formats)
```
## 🌐 Common Web Use Cases

```python
# API responses
api_response = requests.post("https://api.example.com/generate-pdf")
text = xtxt(api_response.content)

# File uploads (Flask/Django)
uploaded_bytes = request.files['document'].read()
text = xtxt(uploaded_bytes)

# Audio/video transcription services
audio_response = requests.get("https://api.example.com/recording.mp3")
transcript = xtxt(audio_response.content)

# Video transcription from API
video_response = requests.get("https://api.example.com/meeting.mp4")
transcript = xtxt(video_response.content)

# OCR for uploaded images
image_bytes = request.files['receipt'].read()
text = xtxt(image_bytes)

# Email attachments
attachment_bytes = email_msg.get_payload(decode=True)
text = xtxt(attachment_bytes)
```

## ⚠️ Known Limitations

### General Limitations
- **Legacy file detection**: When using raw streams without filenames, legacy files (.doc, .xls, .ppt) may not be correctly detected due to identical file signatures in libmagic
- **Filename hints recommended**: When available, providing original filenames improves detection accuracy
- **MSWrite .doc files**: Require `antiword` installation:
  ```bash
  sudo apt-get update && sudo apt-get install antiword
  ```

### 🤖 AI-Powered Features - Important Warnings

**⚠️ EXPERIMENTAL TECHNOLOGY**: AI-powered features (OCR-Ollama, audio transcription) are based on machine learning models and may produce:

#### Potential Issues:
- **Hallucinations**: AI may "see" or "hear" content that isn't actually present
- **Misinterpretations**: Complex images may be incorrectly identified (e.g., X-ray images mistaken for historical artifacts)
- **Language Errors**: Transcription accuracy depends on audio quality, accents, and background noise
- **Context Confusion**: AI may apply inappropriate cultural/historical context to technical content
- **Model Dependence**: Results vary significantly between different AI models (gemma3, llava, whisper versions)
- **Bias and Inconsistency**: Models may exhibit cultural, linguistic, or domain-specific biases

#### Critical Applications Warning:
**🚨 DO NOT USE for critical applications** such as:
- Medical diagnosis or medical image interpretation
- Legal document analysis requiring perfect accuracy  
- Financial data extraction where errors have monetary impact
- Security/safety systems where false positives/negatives are dangerous
- Academic research requiring citation-quality accuracy

#### Best Practices:
- **Always validate AI results** against source material when accuracy matters
- **Use confidence scoring** to identify potentially unreliable results
- **Cross-reference** with traditional OCR/transcription tools for important content
- **Human review** recommended for any production use case
- **Test thoroughly** with your specific content types and use cases
- **Fallback options**: Keep traditional OCR (EasyOCR) available as backup

#### Recommended Use Cases:
✅ Content discovery and initial text extraction  
✅ Batch processing of low-stakes content  
✅ Development and prototyping workflows  
✅ Personal document organization  
✅ Educational and learning projects

## 📖 Full Examples

### Accessing Examples After Installation
After installing PyxTxt from PyPI, you can access comprehensive usage examples including local file processing, memory buffer handling, web content extraction, error handling patterns, and all supported formats demonstration:

```python
import pkg_resources

# Get path to examples file
examples_path = pkg_resources.resource_filename('pyxtxt', 'examples.py')
print(f"Examples file location: {examples_path}")

# Run the examples directly
exec(open(examples_path).read())

# Or read the content to view examples
examples_content = pkg_resources.resource_string('pyxtxt', 'examples.py').decode('utf-8')
print(examples_content)
```

## 🔒 License

Distributed under the MIT License. See LICENSE file for details.

The software is provided "as is" without any warranty of any kind.

## 🤝 Contributing

Pull requests, issues, and feedback are warmly welcome! 🚀

- **Bug reports**: Please include file samples and error details
- **Feature requests**: Describe your use case and expected behavior
- **Code contributions**: Follow existing patterns and add tests

## 📊 Changelog

### v0.2.5 (Current Development)
- ✅ **NEW**: AI-powered OCR with Ollama LLM integration
- ✅ **NEW**: Advanced caption generation with configurable parameters
- ✅ **NEW**: `set_ollama_config()` for fine-tuning LLM behavior
- ✅ **NEW**: Language hints, style control (descriptive/technical/simple/detailed)
- ✅ **NEW**: Caption length control (short/medium/long)
- ✅ **NEW**: Temperature and token limit configuration
- ✅ **NEW**: Command-line OCR example script with full parameter support
- ✅ **NEW**: **Confidence Scoring System** - Advanced AI hallucination detection
- ✅ **NEW**: `xtxt_image_with_confidence()` - Returns text + confidence score
- ✅ **NEW**: Automatic rejection of low-confidence results with configurable thresholds
- ✅ **NEW**: 60+ hallucination patterns detected (historical, artistic, fantasy, scientific)
- ✅ **NEW**: `--show-confidence` and `--confidence` CLI parameters
- ✅ **ENHANCED**: OCR-Ollama mode with both text extraction and image description
- ✅ **ENHANCED**: Comprehensive AI safety warnings and best practices documentation
- ✅ Support for gemma3:4b, gemma3:12b, gemma3:27b, llava:7b, llava:13b models

### v0.2.4 
- ✅ **NEW**: Video transcription support (MP4, MOV, AVI, WebM, MKV)
- ✅ **ENHANCED**: Audio transcription now supports video files
- ✅ Whisper automatically extracts audio track from videos
- ✅ Unified interface for both audio and video processing

### v0.2.3
- ✅ **NEW**: Audio transcription support (MP3, WAV, M4A, FLAC, etc.)
- ✅ **NEW**: Traditional OCR from images (JPEG, PNG, TIFF, BMP, WebP) via EasyOCR
- ✅ **NEW**: 6 additional format extractors: Markdown, EPUB, RTF, EML, MSG, LaTeX
- ✅ **NEW**: Modular dependencies with `[audio]`, `[ocr]`, `[all]` installation groups
- ✅ Performance optimizations with model caching for heavy operations
- ✅ Improved multilingual OCR support with automatic language detection

### v0.2.0-0.2.2
- ✅ **MAJOR**: Architectural improvements with automatic extractor registration
- ✅ **NEW**: 6 format extractors added in single session (md, epub, rtf, eml, msg, tex)
- ✅ **FIXED**: Critical memory management issues in MSG extractor
- ✅ **FIXED**: Documentation links and path references
- ✅ **ENHANCED**: Error handling with graceful degradation for missing dependencies
- ✅ Comprehensive testing across all newly supported formats

### v0.1.24
- ✅ **NEW**: Support for raw `bytes` objects (web downloads, API responses)
- ✅ **NEW**: Support for `requests.Response` objects (direct HTTP processing)
- ✅ **NEW**: `xtxt_from_url()` helper function for direct URL processing
- ✅ **ENHANCED**: Web-ready architecture for modern applications
- ✅ **FIXED**: Type hints and Optional[str] return types throughout codebase
- ✅ **FIXED**: Critical bug in xlsx.py:46 (indentation error)
- ✅ **REMOVED**: Debug print statements from production code

### v0.1.0-0.1.23
- ✅ **CORE**: Initial release with modular extractor architecture
- ✅ **CORE**: Support for PDF, DOCX, PPTX, XLSX, ODT, HTML, XML, TXT formats
- ✅ **CORE**: Legacy Office support (.doc, .xls, .ppt) with graceful handling
- ✅ **CORE**: MIME type detection with python-magic
- ✅ **CORE**: BytesIO buffer support for memory-efficient processing
- ✅ **CORE**: Single dispatch pattern for type-based routing
- ✅ **CORE**: Automatic dependency management with optional installs
- ✅ **CORE**: Published to PyPI with proper package structure
