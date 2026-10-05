# pyxtxt/extractors/audio_whisper.py
from . import register_extractor
import tempfile
import os

try:
    import whisper
except ImportError:
    whisper = None

if whisper:
    _whisper_model = None

    def _get_model():
        global _whisper_model
        if _whisper_model is None:
            _whisper_model = whisper.load_model("base")
        return _whisper_model

    def xtxt_audio_whisper(file_buffer):
        temp_path = None
        try:
            # Usa un suffisso generico - Whisper + FFmpeg gestiscono il formato
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_buffer.read())
                temp_path = temp_file.name

            model = _get_model()
            result = model.transcribe(
                temp_path,
                language=None,
                task="transcribe",
                temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            )
            return result["text"].strip()

        except Exception as e:
            print(f"⚠️ Error while extracting audio with Whisper: {e}")
            return ""
        finally:
            if temp_path is not None:
                os.unlink(temp_path)

    # Registra per tutti i formati audio comuni.
    # Comprende sia i nomi standard sia quelli restituiti da libmagic (es. audio/x-wav).
    audio_formats = [
        "audio/wav", "audio/wave", "audio/x-wav",
        "audio/mp3", "audio/mpeg",
        "audio/m4a", "audio/x-m4a", "audio/mp4",
        "audio/flac", "audio/x-flac",
        "audio/ogg", "audio/ogg-vorbis",
        "audio/opus",
        "audio/aac", "audio/x-hx-aac-adts",
        "audio/aiff", "audio/x-aiff",
        "audio/wma", "audio/x-ms-wma",
        "audio/webm",
    ]

    for format_type in audio_formats:
        register_extractor(format_type, xtxt_audio_whisper, name="Whisper Audio")

    # Formati video: Whisper estrae la traccia audio tramite FFmpeg
    video_audio_formats = [
        "video/mp4", "video/x-m4v",
        "video/quicktime",  # .mov
        "video/x-msvideo",  # .avi
        "video/webm",
        "video/mkv", "video/x-matroska",
        "video/x-ms-asf",  # .wmv / .wma
        "video/mpeg",
        "video/ogg",
        "video/3gpp",
    ]

    for format_type in video_audio_formats:
        register_extractor(format_type, xtxt_audio_whisper, name="Whisper Audio from Video")
