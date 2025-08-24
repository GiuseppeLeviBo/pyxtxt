#!/usr/bin/env python3
"""
PyxTxt - Usage Examples
=======================

This file shows how to use the PyxTxt library to extract text
from different file types and data streams.
"""

import io
from pyxtxt import xtxt, extxt_available_formats, xtxt_from_url

def example_basic():
    """Example 1: Extraction from local file"""
    print("=== EXAMPLE 1: Local file ====")
    
    # Extract text from a local PDF file
    try:
        text = xtxt("test.pdf")
        if text:
            print(f"Extracted text: {text[:100]}...")
        else:
            print("No text extracted or file not found")
    except Exception as e:
        print(f"Error: {e}")

def example_buffer():
    """Example 2: Extraction from memory buffer"""
    print("\n=== EXAMPLE 2: Memory buffer ====")
    
    # Read file into memory and process
    try:
        with open("test.txt", "rb") as f:
            buffer = io.BytesIO(f.read())
            text = xtxt(buffer)
            print(f"From buffer: {text}")
    except FileNotFoundError:
        print("File test.txt not found - creating example...")
        # Create a sample text buffer
        sample_text = "This is sample text for PyxTxt!"
        buffer = io.BytesIO(sample_text.encode('utf-8'))
        text = xtxt(buffer)
        print(f"From sample buffer: {text}")

def example_bytes():
    """Example 3: Extraction from bytes object (NEW!)"""
    print("\n=== EXAMPLE 3: Bytes object ====")
    
    # Simulate downloaded content
    sample_content = b"This is sample text content downloaded from web"
    text = xtxt(sample_content)
    print(f"From bytes: {text}")
    
    # Example with simulated PDF content (won't work but shows usage)
    try:
        with open("test.pdf", "rb") as f:
            pdf_bytes = f.read()
            text = xtxt(pdf_bytes)
            if text:
                print(f"PDF from bytes: {text[:100]}...")
    except FileNotFoundError:
        print("File test.pdf not found for bytes example")

def example_requests():
    """Example 4: Extraction from requests.Response (NEW!)"""
    print("\n=== EXAMPLE 4: requests.Response ====")
    
    try:
        import requests
        
        # Download a text file
        url = "https://raw.githubusercontent.com/python/cpython/main/README.rst"
        response = requests.get(url)
        
        if response.status_code == 200:
            # Method 1: Pass response object directly
            text1 = xtxt(response)
            if text1:
                print(f"From Response object: {text1[:100]}...")
            
            # Method 2: Pass response.content (bytes)
            text2 = xtxt(response.content) 
            if text2:
                print(f"From response.content: {text2[:100]}...")
        
    except ImportError:
        print("requests not installed. Install with: pip install requests")
    except Exception as e:
        print(f"Download error: {e}")

def example_url_helper():
    """Example 5: URL helper function (NEW!)"""
    print("\n=== EXAMPLE 5: xtxt_from_url helper ====")
    
    # Download directly from URL
    url = "https://raw.githubusercontent.com/python/cpython/main/README.rst"
    text = xtxt_from_url(url)
    
    if text:
        print(f"Downloaded from URL: {text[:100]}...")
    else:
        print("Download or parsing error")
    
    # With additional parameters for requests
    text_with_headers = xtxt_from_url(
        url,
        headers={'User-Agent': 'PyxTxt-Example/1.0'},
        timeout=10
    )
    if text_with_headers:
        print("Download with custom headers successful")

def example_supported_formats():
    """Example 6: Display supported formats"""
    print("\n=== EXAMPLE 6: Supported formats ====")
    
    print("Supported MIME types:")
    formats = extxt_available_formats()
    for fmt in formats:
        print(f"  - {fmt}")
    
    print("\nPretty format names:")
    pretty_formats = extxt_available_formats(pretty=True)
    for fmt in pretty_formats:
        print(f"  - {fmt}")

def example_web_use_cases():
    """Example 7: Common use cases for web content"""
    print("\n=== EXAMPLE 7: Web use cases =====")
    
    # Case 1: API that returns a document
    try:
        import requests
        
        # Simulate API call that returns PDF
        print("Example API call...")
        # api_response = requests.post("https://api.example.com/generate-pdf", 
        #                            json={"type": "report"})
        # text = xtxt(api_response.content)
        
        # Case 2: File download from form upload
        print("Example file upload processing...")
        # uploaded_file_content = request.files['document'].read()  # Flask example
        # text = xtxt(uploaded_file_content)
        
        # Case 3: Email attachments processing
        print("Example email attachment...")
        # attachment_bytes = email_message.get_payload(decode=True)
        # text = xtxt(attachment_bytes)
        
        print("See code comments for detailed examples")
        
    except ImportError:
        print("requests not available - examples commented out")

def main():
    """Run all examples"""
    print("PyxTxt - Usage Examples")
    print("=" * 40)
    
    example_basic()
    example_buffer() 
    example_bytes()
    example_requests()
    example_url_helper()
    example_supported_formats()
    example_web_use_cases()
    
    print("\n" + "=" * 40)
    print("Examples completed!")
    print("\nNew features added:")
    print("✅ bytes object support")
    print("✅ requests.Response support")
    print("✅ xtxt_from_url() helper function")
    print("✅ Better error handling")
    print("✅ Type hints")

if __name__ == "__main__":
    main()