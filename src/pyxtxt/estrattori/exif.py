# pyxtxt/extractors/image_exif.py
from . import register_extractor
from io import BytesIO
import json

try:
    from PIL import Image, ExifTags
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    Image = None
    ExifTags = None
    TAGS = None
    GPSTAGS = None

if Image and ExifTags and TAGS:
    def xtxt_image_exif(file_buffer):
        """
        Extract EXIF metadata from images as human-readable text.
        
        Returns formatted text with:
        - Camera settings (make, model, lens, ISO, aperture, etc.)
        - Shooting parameters (exposure, flash, focal length, etc.) 
        - DateTime information (creation, modification dates)
        - GPS coordinates (if available)
        - Technical metadata (dimensions, orientation, color space, etc.)
        """
        try:
            # Convert buffer to PIL Image
            if hasattr(file_buffer, 'seek'):
                file_buffer.seek(0)
            image_data = file_buffer.read()
            image = Image.open(BytesIO(image_data))
            
            # Get EXIF data
            exif_data = image._getexif()
            
            if not exif_data:
                return "NO_EXIF_DATA_FOUND"
            
            # Extract readable EXIF information
            exif_text_lines = []
            gps_data = {}
            
            # Process main EXIF tags
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, f"UnknownTag_{tag_id}")
                
                # Handle special GPS data
                if tag_name == "GPSInfo" and isinstance(value, dict):
                    gps_data = value
                    continue
                
                # Format common values
                if tag_name in ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]:
                    exif_text_lines.append(f"{tag_name}: {value}")
                elif tag_name in ["Make", "Model", "Software", "Artist", "Copyright"]:
                    exif_text_lines.append(f"{tag_name}: {value}")
                elif tag_name in ["XResolution", "YResolution"]:
                    if isinstance(value, tuple) and len(value) == 2:
                        resolution = value[0] / value[1] if value[1] != 0 else value[0]
                        exif_text_lines.append(f"{tag_name}: {resolution:.1f} dpi")
                    else:
                        exif_text_lines.append(f"{tag_name}: {value}")
                elif tag_name in ["FNumber", "FocalLength", "ExposureTime"]:
                    if isinstance(value, tuple) and len(value) == 2:
                        if value[1] != 0:
                            if tag_name == "FNumber":
                                f_value = value[0] / value[1]
                                exif_text_lines.append(f"Aperture: f/{f_value:.1f}")
                            elif tag_name == "FocalLength":
                                focal_mm = value[0] / value[1]
                                exif_text_lines.append(f"Focal Length: {focal_mm:.0f}mm")
                            elif tag_name == "ExposureTime":
                                if value[0] == 1:
                                    exif_text_lines.append(f"Shutter Speed: 1/{value[1]}s")
                                else:
                                    exp_time = value[0] / value[1]
                                    exif_text_lines.append(f"Shutter Speed: {exp_time:.3f}s")
                        else:
                            exif_text_lines.append(f"{tag_name}: {value}")
                    else:
                        exif_text_lines.append(f"{tag_name}: {value}")
                elif tag_name == "ISOSpeedRatings":
                    exif_text_lines.append(f"ISO: {value}")
                elif tag_name == "Flash":
                    flash_modes = {
                        0: "No Flash",
                        1: "Flash Fired",
                        5: "Flash Fired, Return not detected",
                        7: "Flash Fired, Return detected",
                        9: "Flash Fired, Compulsory",
                        13: "Flash Fired, Compulsory, Return not detected",
                        15: "Flash Fired, Compulsory, Return detected",
                        16: "No Flash, Compulsory",
                        24: "No Flash, Auto",
                        25: "Flash Fired, Auto",
                        29: "Flash Fired, Auto, Return not detected",
                        31: "Flash Fired, Auto, Return detected",
                        32: "No Flash Available"
                    }
                    flash_desc = flash_modes.get(value, f"Flash Mode {value}")
                    exif_text_lines.append(f"Flash: {flash_desc}")
                elif tag_name in ["ExposureMode", "WhiteBalance", "SceneCaptureType", "MeteringMode"]:
                    exif_text_lines.append(f"{tag_name}: {value}")
                elif tag_name == "Orientation":
                    orientations = {
                        1: "Normal", 2: "Mirrored horizontal", 3: "Rotated 180°", 
                        4: "Mirrored vertical", 5: "Mirrored horizontal + rotated 90° CCW",
                        6: "Rotated 90° CW", 7: "Mirrored horizontal + rotated 90° CW",
                        8: "Rotated 90° CCW"
                    }
                    orient_desc = orientations.get(value, f"Orientation {value}")
                    exif_text_lines.append(f"Orientation: {orient_desc}")
                elif isinstance(value, (str, int, float)):
                    # Include other simple values
                    exif_text_lines.append(f"{tag_name}: {value}")
            
            # Process GPS data if available
            if gps_data:
                gps_text_lines = []
                gps_info = {}
                
                # Extract GPS coordinates
                for gps_tag_id, gps_value in gps_data.items():
                    gps_tag_name = GPSTAGS.get(gps_tag_id, f"GPSTag_{gps_tag_id}")
                    gps_info[gps_tag_name] = gps_value
                
                # Format coordinates if available
                if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
                    lat_dms = gps_info['GPSLatitude']
                    lat_ref = gps_info['GPSLatitudeRef']
                    if len(lat_dms) == 3:
                        lat_deg = lat_dms[0] + lat_dms[1]/60 + lat_dms[2]/3600
                        if lat_ref == 'S':
                            lat_deg = -lat_deg
                        gps_text_lines.append(f"GPS Latitude: {lat_deg:.6f}° {lat_ref}")
                
                if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
                    lon_dms = gps_info['GPSLongitude']
                    lon_ref = gps_info['GPSLongitudeRef']
                    if len(lon_dms) == 3:
                        lon_deg = lon_dms[0] + lon_dms[1]/60 + lon_dms[2]/3600
                        if lon_ref == 'W':
                            lon_deg = -lon_deg
                        gps_text_lines.append(f"GPS Longitude: {lon_deg:.6f}° {lon_ref}")
                
                # Add other GPS info
                for tag_name, value in gps_info.items():
                    if tag_name not in ['GPSLatitude', 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef']:
                        if isinstance(value, (str, int, float)):
                            gps_text_lines.append(f"{tag_name}: {value}")
                
                if gps_text_lines:
                    exif_text_lines.extend(["", "=== GPS Information ==="] + gps_text_lines)
            
            # Add image basic info
            basic_info = [
                "",
                "=== Image Information ===",
                f"Format: {image.format}",
                f"Mode: {image.mode}",
                f"Size: {image.width} x {image.height} pixels"
            ]
            
            # Return formatted EXIF data
            if exif_text_lines:
                result = "=== EXIF Metadata ===" + "\n" + "\n".join(exif_text_lines) + "\n" + "\n".join(basic_info)
                return result
            else:
                return "NO_READABLE_EXIF_DATA"
            
        except Exception as e:
            print(f"⚠️ Error extracting EXIF from image: {e}")
            return ""
    
    # Register EXIF extractor for image formats with dedicated MIME types
    # Using EXIF-specific MIME types to avoid conflicts with OCR extractors
    register_extractor("image/jpeg+exif", xtxt_image_exif, name="EXIF")
    register_extractor("image/jpg+exif", xtxt_image_exif, name="EXIF") 
    register_extractor("image/png+exif", xtxt_image_exif, name="EXIF")
    register_extractor("image/tiff+exif", xtxt_image_exif, name="EXIF")
    register_extractor("image/bmp+exif", xtxt_image_exif, name="EXIF")
    register_extractor("image/webp+exif", xtxt_image_exif, name="EXIF")