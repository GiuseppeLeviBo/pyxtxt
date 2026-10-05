"""Audio extraction, using a fake `whisper` module so that PyTorch is not needed."""
import subprocess
import sys
import textwrap
import wave

FAKE_WHISPER = '''
import os

class _Model:
    def transcribe(self, path, **kwargs):
        with open(os.environ["SEEN_PATH_FILE"], "w") as f:
            f.write(path)
        if os.environ.get("FAIL_TRANSCRIBE"):
            raise RuntimeError("transcription failed")
        return {"text": " Hello from the fake model. ", "segments": []}

def load_model(name):
    return _Model()
'''


def _write_wav(path):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        wav.writeframes(b"\x00\x00" * 8000)


def _run(tmp_path, fail=False):
    (tmp_path / "whisper.py").write_text(FAKE_WHISPER)
    wav_path = tmp_path / "speech.wav"
    _write_wav(wav_path)
    seen_path_file = tmp_path / "seen.txt"
    code = textwrap.dedent(
        f"""
        import os
        from pyxtxt import xtxt
        from pyxtxt.estrattori import estrattori
        assert "audio/x-wav" in estrattori and "video/x-matroska" in estrattori
        print(repr(xtxt({str(wav_path)!r})))
        """
    )
    env = {
        **__import__("os").environ,
        "PYTHONPATH": str(tmp_path),
        "SEEN_PATH_FILE": str(seen_path_file),
    }
    if fail:
        env["FAIL_TRANSCRIBE"] = "1"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stderr
    return result.stdout, seen_path_file.read_text()


def test_wav_is_transcribed_and_temp_file_removed(tmp_path):
    stdout, temp_path = _run(tmp_path)
    assert "'Hello from the fake model.'" in stdout
    assert not __import__("os").path.exists(temp_path)


def test_temp_file_removed_when_transcription_fails(tmp_path):
    stdout, temp_path = _run(tmp_path, fail=True)
    assert stdout.strip() == "None"  # a failure, not an empty transcription
    assert not __import__("os").path.exists(temp_path)
