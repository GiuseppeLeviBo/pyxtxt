"""The package must import even when optional extractor dependencies are missing."""
import subprocess
import sys
import textwrap

import pytest

ALL_OPTIONAL = [
    "ollama", "PIL", "easyocr", "whisper", "fitz", "pymupdf", "docx", "pptx",
    "openpyxl", "xlrd", "odf", "bs4", "lxml", "markdown", "ebooklib",
    "striprtf", "extract_msg", "pylatexenc", "requests",
]


def _import_with_blocked_modules(blocked):
    """Import pyxtxt in a fresh interpreter where `blocked` modules raise ImportError.

    Warnings are turned into errors, so an extractor module that fails to load
    (and is skipped with a warning) also makes the import fail.
    """
    code = textwrap.dedent(
        f"""
        import importlib.abc, sys, warnings
        BLOCKED = {set(blocked)!r}

        class Blocker(importlib.abc.MetaPathFinder):
            def find_spec(self, name, path, target=None):
                if name.split(".")[0] in BLOCKED:
                    raise ImportError("blocked for test: " + name)
                return None

        sys.meta_path.insert(0, Blocker())
        warnings.simplefilter("error")
        import pyxtxt
        print(pyxtxt.xtxt(b"hello from pyxtxt"))
        """
    )
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)


@pytest.mark.parametrize(
    "blocked",
    [ALL_OPTIONAL, ["ollama"], ["PIL"]],
    ids=["no-optional-deps", "pillow-without-ollama", "ollama-without-pillow"],
)
def test_import_without_optional_dependencies(blocked):
    result = _import_with_blocked_modules(blocked)
    assert result.returncode == 0, result.stderr
    assert "hello from pyxtxt" in result.stdout
