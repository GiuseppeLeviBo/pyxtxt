# pyxtxt/extractors/image_exif.py
from io import BytesIO
import logging
import numbers

logger = logging.getLogger(__name__)

try:
    from PIL import Image, ExifTags
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    Image = None
    ExifTags = None
    TAGS = None
    GPSTAGS = None

if Image and ExifTags and TAGS:
    _EXIF_IFD = 0x8769  # ExifOffset: pointer to camera settings (FNumber, ExposureTime, ...)
    _GPS_IFD = 0x8825   # GPSInfo: pointer to GPS data

    def _as_ratio(value):
        """Return (numerator, denominator) for EXIF rationals, or None.

        Older Pillow versions return tuples, newer ones IFDRational objects.
        """
        if isinstance(value, tuple) and len(value) == 2:
            return value
        if isinstance(value, numbers.Rational) or hasattr(value, "denominator"):
            return value.numerator, value.denominator
        return None

    def _collect_exif(image):
        """Return (tags, gps) dictionaries keyed by numeric tag id."""
        exif = image.getexif()
        tags = {tag_id: value for tag_id, value in exif.items() if tag_id not in (_EXIF_IFD, _GPS_IFD)}
        tags.update(exif.get_ifd(_EXIF_IFD))
        return tags, dict(exif.get_ifd(_GPS_IFD))

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
            exif_data, gps_data = _collect_exif(image)
            
            if not exif_data and not gps_data:
                return "NO_EXIF_DATA_FOUND"
            
            # Extract readable EXIF information
            exif_text_lines = []
            
            # Process main EXIF tags
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, f"UnknownTag_{tag_id}")
                if isinstance(value, str):
                    value = value.strip("\x00 ")
                
                # Format common values
                if tag_name in ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]:
                    exif_text_lines.append(f"{tag_name}: {value}")
                elif tag_name in ["Make", "Model", "Software", "Artist", "Copyright"]:
                    exif_text_lines.append(f"{tag_name}: {value}")
                elif tag_name in ["XResolution", "YResolution"]:
                    ratio = _as_ratio(value)
                    if ratio and ratio[1] != 0:
                        exif_text_lines.append(f"{tag_name}: {ratio[0] / ratio[1]:.1f} dpi")
                    else:
                        exif_text_lines.append(f"{tag_name}: {value}")
                elif tag_name in ["FNumber", "FocalLength", "ExposureTime"]:
                    ratio = _as_ratio(value)
                    if ratio and ratio[1] != 0:
                        numerator, denominator = ratio
                        if tag_name == "FNumber":
                            exif_text_lines.append(f"Aperture: f/{numerator / denominator:.1f}")
                        elif tag_name == "FocalLength":
                            exif_text_lines.append(f"Focal Length: {numerator / denominator:.0f}mm")
                        elif numerator == 1:
                            exif_text_lines.append(f"Shutter Speed: 1/{denominator}s")
                        else:
                            exp_time = numerator / denominator
                            if exp_time < 1:
                                exif_text_lines.append(f"Shutter Speed: 1/{round(1 / exp_time)}s")
                            else:
                                exif_text_lines.append(f"Shutter Speed: {exp_time:g}s")
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
                elif isinstance(value, (str, numbers.Number)):
                    # Include other simple values (rationals as decimals)
                    if not isinstance(value, (str, int)):
                        value = round(float(value), 4)
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
                        lat_deg = float(lat_dms[0]) + float(lat_dms[1])/60 + float(lat_dms[2])/3600
                        if lat_ref == 'S':
                            lat_deg = -lat_deg
                        gps_text_lines.append(f"GPS Latitude: {lat_deg:.6f}° {lat_ref}")
                
                if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
                    lon_dms = gps_info['GPSLongitude']
                    lon_ref = gps_info['GPSLongitudeRef']
                    if len(lon_dms) == 3:
                        lon_deg = float(lon_dms[0]) + float(lon_dms[1])/60 + float(lon_dms[2])/3600
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
            logger.warning(f"Error extracting EXIF from image: {e}")
            return ""

    # EXIF metadata is exposed through pyxtxt.xtxt_exif(): xtxt() on an image runs OCR.
