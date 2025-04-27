# PyxTxt

[![PyPI version](https://img.shields.io/pypi/v/pyxtxt.svg)](https://pypi.org/project/pyxtxt/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyxtxt.svg)](https://pypi.org/project/pyxtxt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PyxTxt** is a simple and powerful Python library to extract text from various file formats.  
It supports PDF, DOCX, XLSX, PPTX, ODT, HTML, XML, TXT, legacy XLS files, and more.

---

## ✨ Features

- Extracts text from both file paths and in-memory buffers (`io.BytesIO`).
- Supports multiple formats: PDF, DOCX, PPTX, XLSX, ODT, HTML, XML, TXT, legacy Office files (.xls,.ppt).
- Automatically detects MIME type using `python-magic`.
- Compatible with modern and legacy formats.
- Can handle streamed content without saving to disk (with some limitations).

---

## 📦 Installation 

The library i modular so you can install all modules:

```bash
pip install pyxtxt[all]
```
or just the modules you need:
```bash
pip install pyxtxt[pdf,odf,docx,presentation,spreadsheet,html]
```
Beause needed libraries are common installing the html module will enable also SVG and XML.
The architecture is designed to be able to grow with new modules to work with other formats as well.
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

## 📚 Usage Example
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
Show available formats:
from pyxtxt import extxt_available_formats
```python
from pyxtxt import extxt_available_formats
text = extxt_available_formats()
print(text)
# For a pretty printing
text = extxt_available_formats(True)
print(text)
```
## ⚠️ Known Limitations
When passing a raw stream (io.BytesIO) without a filename, legacy files (.doc, .xls, .ppt) may not be correctly detected.

This is a limitation of libmagic beacuse the signature byte sequence at the start of doc/xls/ppt is exactly the same (b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'),
not of pyxtxt.

If available, using the original filename is highly recommended.

To extract text from documents in MSWrite's old .doc format, it is necessary to install antiword.

```bash
sudo apt-get update
sudo apt-get -y install antiword
```

## 🔒 License
Distributed under the MIT License.

The software is provided "as is" without any warranty of any kind.

Pull requests, issues, and feedback are warmly welcome! 🚀
