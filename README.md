# PyxTxt

[![PyPI version](https://img.shields.io/pypi/v/pyxtxt.svg)](https://pypi.org/project/pyxtxt/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyxtxt.svg)](https://pypi.org/project/pyxtxt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PyxTxt** is a simple and powerful Python library to extract text from various file formats.  
It supports PDF, DOCX, XLSX, PPTX, ODT, HTML, XML, TXT, legacy XLS files, and more.

---

## ✨ Features

- Extracts text from both file paths and in-memory buffers (`io.BytesIO`).
- Supports multiple formats: PDF, DOCX, PPTX, XLSX, ODT, HTML, XML, TXT, legacy Office files (.xls, .doc, .ppt).
- Automatically detects MIME type using `python-magic`.
- Compatible with modern and legacy formats.
- Can handle streamed content without saving to disk (with some limitations).

---

## 📦 Installation (when will be available now in status PRE-ALPHA)

```bash
pip install pyxtxt
```
## ⚠️ Note: You must have libmagic installed on your system (required by python-magic).

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

##🛠️ Dependencies
- PyMuPDF (fitz)

- beautifulsoup4

- python-docx

- python-pptx

- odfpy

- openpyxl

- lxml

- xlrd (<2.0.0)

- python-magic

Dependencies are automatically installed from pyproject.toml.

##📚 Usage Example
Extract text from a file path:

```python
from pyxtxt import xtxt

text = xtxt("document.pdf")
print(text)
```
Extract text from a file-like buffer:

```python
import io

with open("document.docx", "rb") as f:
    buffer = io.BytesIO(f.read())

from pyxtxt import xtxt
text = xtxt(buffer)
print(text)
```
## ⚠️ Known Limitations
When passing a raw stream (io.BytesIO) without a filename, legacy files (.doc, .xls, .ppt) may not be correctly detected.

This is a limitation of libmagic, not of pyxtxt.

If available, passing the original filename along with the buffer is highly recommended.

##🔒 License
Distributed under the MIT License.

The software is provided "as is" without any warranty of any kind.

Pull requests, issues, and feedback are warmly welcome! 🚀
