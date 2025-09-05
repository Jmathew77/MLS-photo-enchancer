from PIL import Image, ImageEnhance, ImageOps

def enhance_image(img, max_size=2048):
    img = img.convert("RGB")
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Color(img).enhance(1.2)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Sharpness(img).enhance(1.1)
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    return img
