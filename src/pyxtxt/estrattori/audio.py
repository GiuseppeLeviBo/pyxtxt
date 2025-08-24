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
        try:
            # Usa un suffixe generico - Whisper + FFmpeg gestiscono il formato
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_buffer.read())
                temp_file.flush()
                
                model = _get_model()
                result = model.transcribe(
                temp_file.name,
                language=None,
                task="transcribe",
                temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                word_timestamps=True
                )
                
                os.unlink(temp_file.name)
                text_with_languages = []
                current_lang = None
            
                for segment in result['segments']:
                # Rileva cambio di lingua (logica semplificata)
                    if 'language' in segment and segment['language'] != current_lang:
                        current_lang = segment['language']
                        text_with_languages.append(f"\n[{current_lang.upper()}]")
                
                    text_with_languages.append(segment['text'])
            
                return " ".join(text_with_languages).strip()
                
        except Exception as e:
            print(f"⚠️ Error while extracting audio with Whisper: {e}")
            return ""
    
    # Registra per tutti i formati audio comuni
    audio_formats = [
        "audio/wav", "audio/wave",
        "audio/mp3", "audio/mpeg",
        "audio/m4a", "audio/mp4",
        "audio/flac",
        "audio/ogg", "audio/ogg-vorbis",
        "audio/opus",
        "audio/aac",
        "audio/wma",
        "audio/webm"
    ]
    
    for format_type in audio_formats:
        register_extractor(format_type, xtxt_audio_whisper, name="Whisper Audio")
# Aggiungi questi formati video al tuo registro
    video_audio_formats = [
        "video/mp4",
        "video/quicktime",  # .mov
        "video/x-msvideo",  # .avi
        "video/webm",
        "video/mkv"
    ]

    for format_type in video_audio_formats:
        register_extractor(format_type, xtxt_audio_whisper, name="Whisper Audio from Video")
