from . import register_extractor
import os
import shutil
import subprocess
import tempfile


def xtxt_doc(file_buffer):
    if shutil.which("antiword") is None:
        raise RuntimeError("'antiword' is not installed or is not in the system PATH")

    file_buffer.seek(0)
    with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as temp_file:
        temp_file.write(file_buffer.read())
        temp_path = temp_file.name

    try:
        result = subprocess.run(["antiword", temp_path], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"antiword failed: {result.stderr.strip()}")
        return result.stdout.strip()
    finally:
        os.unlink(temp_path)


register_extractor("application/msword", xtxt_doc, name="DOC")
