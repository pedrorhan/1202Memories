import io
from PIL import Image, UnidentifiedImageError
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

def process_and_convert_image_to_webp(uploaded_file):
    """
    Takes an uploaded image file, verifies it, converts it to WEBP, 
    and returns a new InMemoryUploadedFile.
    Returns None if the file is not a valid image.
    """
    try:
        # Pillow will automatically verify the file headers, preventing malicious files
        img = Image.open(uploaded_file)
        
        # Convert to RGB if necessary (e.g. RGBA for PNGs)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        output = io.BytesIO()
        # Save as WEBP with 80% quality
        img.save(output, format='WEBP', quality=80)
        output.seek(0)
        
        # Determine the new filename
        original_name = uploaded_file.name
        name_without_ext = original_name.rsplit('.', 1)[0]
        new_filename = f"{name_without_ext}.webp"
        
        # Create a new Django InMemoryUploadedFile
        webp_file = InMemoryUploadedFile(
            file=output,
            field_name=uploaded_file.field_name,
            name=new_filename,
            content_type='image/webp',
            size=sys.getsizeof(output),
            charset=None
        )
        return webp_file
    except UnidentifiedImageError:
        # Not a valid image file
        return None
    except Exception as e:
        return None
