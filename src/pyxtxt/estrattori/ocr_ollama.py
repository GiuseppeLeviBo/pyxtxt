# pyxtxt/extractors/image_ocr_ollama.py
from . import register_extractor
from io import BytesIO
import base64

try:
    import ollama
    from PIL import Image
except ImportError:
    ollama = None
    Image = None

# Global configuration for Ollama model and parameters
OLLAMA_MODEL = "gemma3:4b"  # Default multimodal model
OLLAMA_CONFIG = {
    'language': 'auto',  # Language hint for caption generation
    'caption_length': 'medium',  # short, medium, long
    'style': 'descriptive',  # descriptive, technical, simple, detailed
    'temperature': 0.1,  # Response creativity (0.0-1.0)
    'max_tokens': 1500,  # Maximum response length
    'confidence_threshold': 0.7,  # Minimum confidence for text extraction
    'context': 'general',  # Context hint: general, cookbook, document, diagram, medical, xray
    'enhance_image': True,  # Apply image enhancement preprocessing
    'min_size': 800,  # Minimum image size for processing (upscale if smaller)
    'max_size': 2048,   # Maximum image size (downscale if larger)
    'auto_fallback': True,  # Enable automatic model fallback for better results
    'fallback_models': ['gemma3:27b', 'gemma3:12b', 'llava:13b']  # Models to try if primary fails
}

def set_ollama_model(model_name: str):
    """
    Set the Ollama model to use for OCR.
    
    Recommended multimodal models:
    - gemma3:4b (default, balanced speed/quality)
    - gemma3:12b (higher quality, slower)
    - gemma3:27b (best quality, very slow)
    - llava:7b (alternative vision model)
    - llava:13b (higher quality LLAVA)
    """
    global OLLAMA_MODEL
    OLLAMA_MODEL = model_name
    print(f"✅ Ollama OCR model set to: {model_name}")

def get_ollama_model():
    """Get current Ollama model name"""
    return OLLAMA_MODEL

def set_ollama_config(**kwargs):
    """
    Configure Ollama LLM parameters for better caption generation.
    
    Parameters:
    - language: Language hint ('auto', 'italian', 'english', 'spanish', etc.)
    - caption_length: Caption length ('short', 'medium', 'long')
    - style: Caption style ('descriptive', 'technical', 'simple', 'detailed')
    - context: Content context ('general', 'cookbook', 'document', 'handwriting', 'technical', 'medical', 'xray')
    - enhance_image: Apply image enhancement preprocessing (default: True)
    - min_size: Minimum image size for processing - upscale if smaller (default: 800)
    - max_size: Maximum image size - downscale if larger (default: 2048)
    - auto_fallback: Enable automatic model fallback for better results (default: True)
    - fallback_models: List of models to try if primary fails (default: ['gemma3:27b', 'gemma3:12b', 'llava:13b'])
    - temperature: Response creativity 0.0-1.0 (default: 0.1)
    - max_tokens: Maximum response length (default: 1500)
    - confidence_threshold: Text extraction confidence 0.0-1.0 (default: 0.7)
    
    Examples:
        set_ollama_config(language='italian', style='detailed')
        set_ollama_config(context='document', caption_length='long')
        set_ollama_config(context='handwriting', temperature=0.2)
        set_ollama_config(context='medical', enhance_image=True, min_size=1024)
        set_ollama_config(context='xray', style='technical', confidence_threshold=0.8)
        set_ollama_config(auto_fallback=False)  # Disable fallback for faster processing
        set_ollama_config(fallback_models=['llava:13b', 'gemma3:27b'])  # Custom fallback sequence
    """
    global OLLAMA_CONFIG
    for key, value in kwargs.items():
        if key in OLLAMA_CONFIG:
            OLLAMA_CONFIG[key] = value
            print(f"✅ Ollama config updated: {key} = {value}")
        else:
            print(f"⚠️ Unknown config parameter: {key}")

def get_ollama_config():
    """Get current Ollama configuration"""
    return OLLAMA_CONFIG.copy()

def configure_for_medical_images():
    """
    Quick configuration setup for optimal medical image processing.
    Configures model, enhancement, and context for X-rays and medical scans.
    """
    print("🏥 Configuring for medical image processing...")
    
    # Optimal medical settings  
    global OLLAMA_CONFIG
    OLLAMA_CONFIG.update({
        'context': 'medical',
        'enhance_image': True,
        'min_size': 1024,  # Higher resolution for medical details
        'max_size': 2048,  # Keep high quality
        'style': 'technical',
        'confidence_threshold': 0.8,  # Higher threshold for medical accuracy
        'temperature': 0.05,  # Very low temperature for precision
        'auto_fallback': True,
        'fallback_models': ['gemma3:27b', 'llava:13b', 'gemma3:12b']  # Best models first
    })
    
    # Suggest high-quality model if current is default
    current_model = get_ollama_model()
    if current_model == "gemma3:4b":
        print("💡 Consider upgrading to gemma3:27b for better medical image recognition")
        print("   Run: set_ollama_model('gemma3:27b')")
    
    print("✅ Medical configuration applied:")
    print(f"   - Enhanced image processing: {OLLAMA_CONFIG['enhance_image']}")
    print(f"   - Minimum resolution: {OLLAMA_CONFIG['min_size']}px")
    print(f"   - Confidence threshold: {OLLAMA_CONFIG['confidence_threshold']}")
    print(f"   - Fallback models: {len(OLLAMA_CONFIG['fallback_models'])} configured")

def configure_for_xray_images():
    """
    Specialized configuration for X-ray and radiological image processing.
    Optimized for detecting small text, markers, and technical annotations.
    """
    print("📷 Configuring for X-ray image processing...")
    
    # X-ray specific settings
    global OLLAMA_CONFIG
    OLLAMA_CONFIG.update({
        'context': 'xray',
        'enhance_image': True,
        'min_size': 1200,  # Even higher for X-ray details
        'max_size': 2048,
        'style': 'technical',
        'confidence_threshold': 0.85,  # Very high threshold for X-ray accuracy
        'temperature': 0.02,  # Minimal creativity for technical precision
        'auto_fallback': True,
        'fallback_models': ['gemma3:27b', 'llava:13b']  # Only best models
    })
    
    # Recommend best model for X-rays
    current_model = get_ollama_model()
    if current_model != "gemma3:27b":
        print("🎯 For best X-ray results, use gemma3:27b model")
        print("   Run: set_ollama_model('gemma3:27b')")
    
    print("✅ X-ray configuration applied:")
    print(f"   - Context: Medical X-ray specialization")
    print(f"   - Enhanced processing: Advanced medical filters")
    print(f"   - High precision mode: {OLLAMA_CONFIG['confidence_threshold']} threshold")
    print(f"   - Temperature: {OLLAMA_CONFIG['temperature']} (maximum precision)")

def quick_xray_analysis(image_path: str) -> str:
    """
    Convenient one-function X-ray analysis with optimal settings.
    Automatically configures system for X-ray processing and returns detailed analysis.
    
    Args:
        image_path: Path to X-ray image file
        
    Returns:
        str: Detailed text + description analysis
    """
    # Save current config
    global OLLAMA_CONFIG
    original_config = OLLAMA_CONFIG.copy()
    original_model = get_ollama_model()
    
    try:
        # Apply X-ray configuration  
        configure_for_xray_images()
        set_ollama_model('gemma3:27b')  # Use best model
        
        # Perform analysis
        print("🔍 Analyzing X-ray image...")
        result = xtxt_image_describe(image_path)
        
        return result
        
    finally:
        # Restore original configuration
        OLLAMA_CONFIG = original_config
        set_ollama_model(original_model)
        print("🔄 Configuration restored")

def reset_ollama_config():
    """Reset Ollama configuration to defaults"""
    global OLLAMA_CONFIG
    OLLAMA_CONFIG = {
        'language': 'auto',
        'caption_length': 'medium', 
        'style': 'descriptive',
        'temperature': 0.1,
        'max_tokens': 1500,
        'confidence_threshold': 0.7,
        'context': 'general',
        'enhance_image': True,
        'min_size': 800,
        'max_size': 2048,
        'auto_fallback': True,
        'fallback_models': ['gemma3:27b', 'gemma3:12b', 'llava:13b']
    }
    print("✅ Ollama configuration reset to defaults")

def _enhance_image(image: Image.Image, context: str, min_size: int, max_size: int) -> Image.Image:
    """
    Apply image enhancement preprocessing for better OCR results.
    
    Args:
        image: PIL Image object
        context: Content context hint (medical, xray, document, etc.)
        min_size: Minimum size threshold for upscaling
        max_size: Maximum size threshold for downscaling
    
    Returns:
        Enhanced PIL Image
    """
    try:
        from PIL import ImageEnhance, ImageFilter, ImageOps
    except ImportError:
        # If PIL enhancements not available, return original
        return image
    
    enhanced = image.copy()
    
    # Get current dimensions
    width, height = enhanced.size
    max_dimension = max(width, height)
    
    # Resize if needed (quality improvement for small images, memory management for large)
    if max_dimension < min_size:
        # Upscale small images for better model processing
        scale_factor = min_size / max_dimension
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor) 
        enhanced = enhanced.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"📈 Image upscaled from {width}x{height} to {new_width}x{new_height}")
    elif max_dimension > max_size:
        # Downscale large images to manageable size
        scale_factor = max_size / max_dimension
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        enhanced = enhanced.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"📉 Image downscaled from {width}x{height} to {new_width}x{new_height}")
    
    # Context-specific enhancements
    if context in ['medical', 'xray']:
        print("🏥 Applying medical image enhancements...")
        # Medical images often benefit from:
        # 1. Contrast enhancement to bring out subtle details
        contrast = ImageEnhance.Contrast(enhanced)
        enhanced = contrast.enhance(1.3)
        
        # 2. Sharpening to improve edge definition 
        enhanced = enhanced.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
        
        # 3. Brightness adjustment for dark X-rays
        brightness = ImageEnhance.Brightness(enhanced)
        enhanced = brightness.enhance(1.1)
        
    elif context in ['document', 'handwriting', 'technical']:
        print("📄 Applying document enhancement...")
        # Documents benefit from:
        # 1. Moderate sharpening for text clarity
        enhanced = enhanced.filter(ImageFilter.UnsharpMask(radius=0.5, percent=150, threshold=3))
        
        # 2. Contrast boost for faded text
        contrast = ImageEnhance.Contrast(enhanced)
        enhanced = contrast.enhance(1.2)
        
    elif context == 'general':
        print("🔧 Applying general enhancements...")
        # General purpose light enhancement
        # 1. Slight contrast improvement
        contrast = ImageEnhance.Contrast(enhanced)
        enhanced = contrast.enhance(1.1)
        
        # 2. Subtle sharpening
        enhanced = enhanced.filter(ImageFilter.UnsharpMask(radius=0.5, percent=110, threshold=3))
    
    return enhanced

def _try_ollama_request(prompt: str, img_base64: str, current_model: str, config: dict) -> tuple:
    """
    Attempt Ollama request with a specific model.
    
    Returns:
        tuple: (success: bool, response: str, confidence: float)
    """
    try:
        print(f"🤖 Trying model: {current_model}")
        
        response = ollama.generate(
            model=current_model,
            prompt=prompt,
            images=[img_base64],
            options={
                'temperature': config['temperature'],
                'top_p': 0.9,
                'num_predict': config['max_tokens']
            }
        )
        
        extracted_content = response.get('response', '').strip()
        
        # Calculate confidence without printing warnings here (let parent handle it)
        confidence_score = _calculate_confidence_score(extracted_content, "ocr" if "Extracted text:" in prompt else "describe")
        
        return True, extracted_content, confidence_score
        
    except Exception as e:
        print(f"❌ Model {current_model} failed: {e}")
        return False, "", 0.0

def _calculate_confidence_score(content: str, mode: str) -> float:
    """
    Calculate confidence score (0.0-1.0) for OCR/caption quality.
    
    Evaluates response based on:
    - Content length and structure
    - Presence of meaningful text patterns
    - Absence of hallucination indicators
    - Appropriate response format
    """
    if not content or len(content.strip()) < 3:
        return 0.0
    
    content_lower = content.lower()
    score = 0.5  # Base score
    
    # Positive indicators (add to confidence)
    positive_patterns = [
        # Structured text indicators
        (r'\b\d+\b', 0.1, "Contains numbers/measurements"),
        (r'[.!?]', 0.1, "Has sentence punctuation"), 
        (r'\b(the|and|of|in|to|for|with|on|at|by)\b', 0.1, "Common words present"),
        (r'\b[A-Z][a-z]+\b', 0.1, "Proper capitalization"),
        (r'[,;:]', 0.05, "Has proper punctuation"),
        
        # Content-specific indicators
        (r'\b(text|document|page|title|heading)\b', 0.1, "Document references"),
        (r'\b(image|photo|picture|shows|contains)\b', 0.1, "Visual descriptions"),
        (r'\b\d+[%$€£¥]\b|\b[%$€£¥]\d+\b', 0.1, "Currency/percentages"),
        (r'\b\d{1,2}[:/]\d{1,2}\b|\b\d{4}\b', 0.05, "Times/years"),
    ]
    
    # Negative indicators (reduce confidence) 
    negative_patterns = [
        # Historical/Archaeological hallucinations (common with X-rays, scans)
        ("ancient", 0.2, "May be hallucinating historical content"),
        ("egypt", 0.15, "Egyptian hallucination"),
        ("hieroglyph", 0.25, "Hieroglyphic hallucination"),
        ("papyrus", 0.2, "Papyrus hallucination"),
        ("scroll", 0.1, "Ancient scroll hallucination"),
        ("medieval", 0.15, "Medieval hallucination"),
        ("manuscript", 0.1, "Manuscript hallucination"),
        ("archaeological", 0.15, "Archaeological hallucination"),
        ("artifact", 0.12, "Artifact hallucination"),
        ("roman", 0.1, "Roman historical hallucination"),
        ("greek", 0.1, "Greek historical hallucination"),
        ("biblical", 0.15, "Religious historical hallucination"),
        ("stone tablet", 0.2, "Stone tablet hallucination"),
        ("carved", 0.1, "Carving hallucination"),
        
        # Art/Cultural hallucinations (common with medical images, diagrams)
        ("painting", 0.1, "Artistic interpretation hallucination"),
        ("artwork", 0.12, "Artwork hallucination"),  
        ("masterpiece", 0.15, "Art masterpiece hallucination"),
        ("renaissance", 0.15, "Renaissance art hallucination"),
        ("portrait", 0.08, "Portrait hallucination"),
        ("landscape", 0.08, "Landscape hallucination"),
        ("abstract art", 0.12, "Abstract art hallucination"),
        
        # Fantasy/Fictional content (can occur with any unclear image)
        ("mystical", 0.15, "Fantasy content hallucination"),
        ("magical", 0.15, "Magical content hallucination"),
        ("mythological", 0.15, "Mythology hallucination"),
        ("fairy tale", 0.15, "Fairy tale hallucination"),
        ("legend", 0.1, "Legend/folklore hallucination"),
        ("dragon", 0.2, "Dragon hallucination"),
        ("wizard", 0.15, "Fantasy character hallucination"),
        
        # Scientific misinterpretations (X-rays as geological, etc.)
        ("fossil", 0.15, "Fossil hallucination"),
        ("geological", 0.1, "Geological misinterpretation"),
        ("mineral", 0.1, "Mineral hallucination"),
        ("crystal", 0.1, "Crystal hallucination"),
        ("rock formation", 0.12, "Rock formation hallucination"),
        ("sediment", 0.1, "Sediment hallucination"),
        
        # Vague/uncertain language
        ("unclear", 0.1, "Uncertainty indicator"),
        ("difficult to read", 0.1, "Reading difficulty"),
        ("appears to be", 0.05, "Tentative language"),
        ("seems to", 0.05, "Uncertain language"),
        ("might be", 0.1, "Possibility language"),
        ("possibly", 0.1, "Uncertain language"),
        ("probably", 0.08, "Probability language"),
        ("looks like", 0.08, "Appearance-based guess"),
        ("reminds me of", 0.1, "Subjective association"),
        ("similar to", 0.05, "Similarity guess"),
        
        # Quality/visibility issues (legitimate but indicate uncertainty)
        ("blurry", 0.05, "Image quality issue"),
        ("faded", 0.05, "Faded content"),
        ("damaged", 0.05, "Damaged content"),
        ("corrupted", 0.1, "Corrupted content"),
        ("low resolution", 0.08, "Resolution issue"),
        ("hard to make out", 0.1, "Visibility issue"),
        
        # Generic/evasive responses
        ("sorry, i cannot", 0.3, "Refusal response"),
        ("cannot determine", 0.2, "Unable to process"),
        ("unable to identify", 0.15, "Identification failure"),
        ("not clear enough", 0.1, "Clarity issue"),
        ("too dark", 0.08, "Darkness issue"),
        ("too bright", 0.08, "Brightness issue"),
        ("no visible text", 0.0, "No text found - appropriate response"),
        
        # Repetitive/nonsensical content (AI breakdown indicators)
        ("lorem ipsum", 0.2, "Placeholder text hallucination"),
        ("test test test", 0.25, "Repetitive test pattern"),
        ("abc abc abc", 0.2, "Repetitive pattern"),
        ("error error", 0.15, "Error message hallucination"),
    ]
    
    import re
    
    # Apply positive pattern scoring
    for pattern, bonus, description in positive_patterns:
        if re.search(pattern, content_lower):
            score += bonus
    
    # Apply negative pattern scoring  
    for pattern, penalty, description in negative_patterns:
        if pattern in content_lower:
            score -= penalty
            print(f"⚠️ Confidence penalty ({penalty}): {description}")
    
    # Length-based adjustments
    if len(content) > 200:  # Substantial content
        score += 0.1
    elif len(content) < 20:  # Very short responses are suspicious
        score -= 0.2
    
    # Mode-specific adjustments
    if mode == "describe":
        # Check for proper formatting in describe mode
        if "TEXT:" in content and "DESCRIPTION:" in content:
            score += 0.1  # Proper format bonus
        elif len(content) > 50:  # Has substantial descriptive content
            score += 0.05
    
    # Context coherence check - very basic
    words = content_lower.split()
    if len(words) > 5:
        # Check for repetitive patterns (hallucination indicator)
        unique_words = set(words)
        repetition_ratio = len(unique_words) / len(words)
        if repetition_ratio < 0.3:  # Too repetitive
            score -= 0.2
    
    # Clamp to valid range
    return max(0.0, min(1.0, score))

if ollama and Image:
    def xtxt_image_ocr_ollama(file_buffer, mode="ocr", model=None):
        """
        Extract text from images using Ollama with multimodal models.
        
        Args:
            file_buffer: Image file buffer
            mode: "ocr" (text only) or "describe" (text + description)  
            model: Override default model (optional)
        """
        try:
            # Use specified model or global default
            current_model = model or OLLAMA_MODEL
            
            # Convert buffer to PIL Image
            # Reset buffer position if it has read method
            if hasattr(file_buffer, 'seek'):
                file_buffer.seek(0)
            image_data = file_buffer.read()
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get current configuration
            config = OLLAMA_CONFIG
            
            # Apply image enhancement if enabled
            if config.get('enhance_image', True):
                print("⚡ Enhancing image for better OCR...")
                image = _enhance_image(image, config['context'], config['min_size'], config['max_size'])
            
            # Convert image to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Build language hint
            lang_hint = ""
            if config['language'] != 'auto':
                lang_hint = f"Text language: {config['language']}. "
            
            # Different prompts based on mode
            if mode == "ocr":
                # Context-specific OCR prompts
                if config.get('context') == 'xray':
                    prompt = f"""This is a medical X-ray or radiological image. Look carefully and extract ALL visible text, including:
- Patient identification numbers, names, or codes
- Date and time stamps (exam dates, birth dates)
- Anatomical position markers (L/R, LEFT/RIGHT, AP, LAT)
- Measurement scales, rulers, or calibration marks
- Technical annotations or radiologist markings
- Equipment identifiers or hospital names
- Any small text on borders or corners

IMPORTANT:
- Medical images often have small text around borders - examine carefully
- {lang_hint}Look for technical markings that might be faint or small
- Include any numbers that might be measurements or identifiers
- If absolutely no readable text is visible, respond with 'NO_TEXT_FOUND'

Extracted text:"""
                elif config.get('context') == 'medical':
                    prompt = f"""This appears to be a medical document or image. Look carefully and extract ALL text, including:
- Patient information (names, IDs, dates of birth)
- Medical terminology and diagnostic information
- Dates, times, and timestamps
- Measurements, values, and test results
- Doctor names, hospital information, department names
- Small print and technical annotations

IMPORTANT:
- Medical documents often contain critical small text - examine thoroughly
- {lang_hint}Include all numerical values as they may be measurements
- Preserve formatting for medical data accuracy
- If no readable text is found, respond with 'NO_TEXT_FOUND'

Extracted text:"""
                else:
                    # General OCR prompt
                    prompt = f"""Look carefully at this image and extract ALL text that you can see, including:
- Titles, headings, and main text content  
- Small print, captions, labels, and annotations
- Numbers, measurements, quantities, and symbols
- Menu items, ingredient lists, cooking instructions
- Any text in boxes, speech bubbles, or decorative elements

IMPORTANT: 
- Read carefully and include even small or partially visible text
- Preserve the original formatting and line breaks where possible
- {lang_hint}Process the text from left to right, top to bottom
- If you cannot find any readable text at all, respond with 'NO_TEXT_FOUND'

Extracted text:"""
            
            else:  # mode == "describe"
                # Build style-specific prompts
                style_prompts = {
                    'descriptive': "Provide a clear, descriptive explanation",
                    'technical': "Use technical terminology and precise descriptions", 
                    'simple': "Use simple, easy-to-understand language",
                    'detailed': "Provide comprehensive details about all visual elements"
                }
                
                length_hints = {
                    'short': "Keep descriptions brief (1-2 sentences)",
                    'medium': "Provide moderate detail (2-4 sentences)",
                    'long': "Give comprehensive descriptions (4-8 sentences)"
                }
                
                style_instruction = style_prompts.get(config['style'], style_prompts['descriptive'])
                length_instruction = length_hints.get(config['caption_length'], length_hints['medium'])
                
                # Context-specific hints (only when explicitly set)
                context_hint = ""
                context = config.get('context', 'general').lower()
                if context == 'cookbook' or context == 'recipe':
                    context_hint = """
   - If this appears to be a recipe/cookbook page, include: ingredients, cooking steps, quantities, cooking times
   - Mention any photos of prepared dishes or cooking techniques shown
   - Note any special formatting like ingredient lists, step numbers, or cooking tips"""
                elif context == 'document':
                    context_hint = """
   - Focus on document structure: headers, paragraphs, sections, page numbers
   - Note any official formatting, letterheads, signatures, or stamps"""
                elif context == 'handwriting' or context == 'notes':
                    context_hint = """
   - Pay special attention to handwritten text which may be harder to read
   - Note any sketches, diagrams, or informal formatting typical of personal notes"""
                elif context == 'technical' or context == 'diagram':
                    context_hint = """
   - Focus on technical elements: labels, measurements, specifications, diagrams
   - Include any mathematical formulas, technical symbols, or engineering notations"""
                elif context == 'medical':
                    context_hint = """
   - Focus on medical content: patient data, measurements, anatomical labels, medical terminology
   - Look for dates, patient IDs, measurement values, diagnostic information
   - Note any visible text on medical equipment or instrumentation"""
                elif context == 'xray':
                    context_hint = """
   - This appears to be a medical X-ray or radiological image
   - Look for: anatomical markers, measurement scales, patient information, timestamps
   - Focus on any visible text annotations, labels, or technical markings
   - Note positioning indicators (L/R, anterior/posterior) or measurement rulers"""

                prompt = f"""Analyze this image and provide:
1. All visible text exactly as written (preserve formatting, line breaks, bullet points)
2. Image description following these guidelines:
   - {style_instruction}
   - {length_instruction}
   - {lang_hint}Focus on key visual elements, layout, and context{context_hint}

Format:
TEXT: [all visible text here, or NO_TEXT_FOUND if none]
DESCRIPTION: [image description following the guidelines above]"""
            
            # Try primary model first
            success, extracted_content, confidence_score = _try_ollama_request(prompt, img_base64, current_model, config)
            
            # If primary model failed or confidence is very low, try fallback models
            if config.get('auto_fallback', True) and (not success or confidence_score < 0.3):
                print("🔄 Primary model result unsatisfactory, trying fallback models...")
                
                fallback_models = config.get('fallback_models', [])
                best_result = (extracted_content, confidence_score) if success else ("", 0.0)
                
                for fallback_model in fallback_models:
                    if fallback_model == current_model:
                        continue  # Skip if same as primary
                    
                    success, fallback_content, fallback_confidence = _try_ollama_request(prompt, img_base64, fallback_model, config)
                    
                    if success and fallback_confidence > best_result[1]:
                        print(f"✨ Better result from {fallback_model} (confidence: {fallback_confidence:.2f} vs {best_result[1]:.2f})")
                        best_result = (fallback_content, fallback_confidence)
                        
                        # Stop if we found a good enough result
                        if fallback_confidence >= config['confidence_threshold']:
                            break
                
                extracted_content, confidence_score = best_result
            
            # Check confidence threshold
            if confidence_score < config['confidence_threshold']:
                print(f"⚠️ Low confidence ({confidence_score:.2f} < {config['confidence_threshold']}): {extracted_content[:100]}...")
                if mode == "ocr":
                    return ""  # Return empty for OCR if below threshold
                else:
                    # For describe mode, add warning prefix
                    extracted_content = f"[LOW_CONFIDENCE_{confidence_score:.2f}] {extracted_content}"
            else:
                print(f"✅ Good confidence ({confidence_score:.2f}): Processing successful")
            
            # Handle no-text case for OCR mode
            if mode == "ocr" and ('NO_TEXT_FOUND' in extracted_content or len(extracted_content) < 3):
                return ""
            
            return extracted_content
            
        except Exception as e:
            print(f"⚠️ Error extracting from image with Ollama {current_model}: {e}")
            return ""
    
    def xtxt_image_ocr_ollama_with_confidence(file_buffer, mode="ocr", model=None):
        """
        Version of OCR-Ollama that returns both text and confidence score.
        
        Returns:
            tuple: (extracted_text, confidence_score)
        """
        try:
            # Use specified model or global default
            current_model = model or OLLAMA_MODEL
            
            # Convert buffer to PIL Image
            if hasattr(file_buffer, 'seek'):
                file_buffer.seek(0)
            image_data = file_buffer.read()
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get current configuration
            config = OLLAMA_CONFIG
            
            # Apply image enhancement if enabled
            if config.get('enhance_image', True):
                print("⚡ Enhancing image for better OCR...")
                image = _enhance_image(image, config['context'], config['min_size'], config['max_size'])
            
            # Convert image to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Build prompts (same logic as main function)
            lang_hint = ""
            if config['language'] != 'auto':
                lang_hint = f"Text language: {config['language']}. "
            
            if mode == "ocr":
                prompt = f"""Look carefully at this image and extract ALL text that you can see, including:
- Titles, headings, and main text content  
- Small print, captions, labels, and annotations
- Numbers, measurements, quantities, and symbols
- Menu items, ingredient lists, cooking instructions
- Any text in boxes, speech bubbles, or decorative elements

IMPORTANT: 
- Read carefully and include even small or partially visible text
- Preserve the original formatting and line breaks where possible
- {lang_hint}Process the text from left to right, top to bottom
- If you cannot find any readable text at all, respond with 'NO_TEXT_FOUND'

Extracted text:"""
            else:  # describe mode
                style_prompts = {
                    'descriptive': "Provide a clear, descriptive explanation",
                    'technical': "Use technical terminology and precise descriptions", 
                    'simple': "Use simple, easy-to-understand language",
                    'detailed': "Provide comprehensive details about all visual elements"
                }
                
                length_hints = {
                    'short': "Keep descriptions brief (1-2 sentences)",
                    'medium': "Provide moderate detail (2-4 sentences)",
                    'long': "Give comprehensive descriptions (4-8 sentences)"
                }
                
                style_instruction = style_prompts.get(config['style'], style_prompts['descriptive'])
                length_instruction = length_hints.get(config['caption_length'], length_hints['medium'])
                
                prompt = f"""Analyze this image and provide:
1. All visible text exactly as written (preserve formatting, line breaks, bullet points)
2. Image description following these guidelines:
   - {style_instruction}
   - {length_instruction}
   - {lang_hint}Focus on key visual elements, layout, and context

Format:
TEXT: [all visible text here, or NO_TEXT_FOUND if none]
DESCRIPTION: [image description following the guidelines above]"""
            
            # Try primary model first
            success, extracted_content, confidence_score = _try_ollama_request(prompt, img_base64, current_model, config)
            
            # Try fallback if enabled and primary result is poor
            if config.get('auto_fallback', True) and (not success or confidence_score < 0.3):
                fallback_models = config.get('fallback_models', [])
                best_result = (extracted_content, confidence_score) if success else ("", 0.0)
                
                for fallback_model in fallback_models:
                    if fallback_model == current_model:
                        continue
                    
                    success, fallback_content, fallback_confidence = _try_ollama_request(prompt, img_base64, fallback_model, config)
                    
                    if success and fallback_confidence > best_result[1]:
                        best_result = (fallback_content, fallback_confidence)
                        if fallback_confidence >= config['confidence_threshold']:
                            break
                
                extracted_content, confidence_score = best_result
            
            # Return both text and confidence
            return extracted_content, confidence_score
            
        except Exception as e:
            print(f"⚠️ Error extracting from image with Ollama {current_model}: {e}")
            return "", 0.0

    # Wrapper functions for each mode
    def xtxt_image_ocr_only(file_input):
        """Traditional OCR: extract only visible text using Ollama"""
        # Handle both file paths and buffers
        if isinstance(file_input, str):
            with open(file_input, 'rb') as f:
                return xtxt_image_ocr_ollama(f, mode="ocr")
        else:
            return xtxt_image_ocr_ollama(file_input, mode="ocr")
    
    def xtxt_image_describe(file_input):
        """OCR + Description: text + image context using Ollama"""
        # Handle both file paths and buffers  
        if isinstance(file_input, str):
            with open(file_input, 'rb') as f:
                return xtxt_image_ocr_ollama(f, mode="describe")
        else:
            return xtxt_image_ocr_ollama(file_input, mode="describe")

    def xtxt_image_with_confidence(file_input, mode="ocr"):
        """Get both text and confidence score from image OCR"""
        if isinstance(file_input, str):
            with open(file_input, 'rb') as f:
                return xtxt_image_ocr_ollama_with_confidence(f, mode=mode)
        else:
            return xtxt_image_ocr_ollama_with_confidence(file_input, mode=mode)
    
    # Register OCR-only version as default
    # Note: Will override traditional EasyOCR if both modules are loaded
    image_formats = [
        "image/jpeg", "image/jpg", "image/png", 
        "image/bmp", "image/tiff", "image/webp"
    ]
    
    for format_type in image_formats:
        register_extractor(format_type, xtxt_image_ocr_only, name="OCR-Ollama")