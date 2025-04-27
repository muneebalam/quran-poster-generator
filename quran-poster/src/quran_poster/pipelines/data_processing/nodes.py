from PIL import Image

def translate_dimensions_to_pixels(poster_width_in: float, poster_height_in: float) -> tuple[int, int]:
    return int(poster_width_in * 300), int(poster_height_in * 300)

def create_blank_canvas(poster_width_px: int, poster_height_px: int) -> Image.Image:
    return Image.new("RGBA", (poster_width_px, poster_height_px), (255, 255, 255, 0))

def add_background_image(background_image_path: str, blank_canvas: Image.Image) -> Image.Image:
    background_image = Image.open(background_image_path)
    background_image = background_image.resize(blank_canvas.size)
    blank_canvas.paste(background_image, (0, 0))
    return blank_canvas

def add_arabic_text(background_image_canvas: Image.Image, text: dict) -> Image.Image:
    arabic_font_path = text["arabic_font_path"]
    english_font_path = text["english_font_path"]
    arabic_tl = text["arabic_tl"]
    arabic_br = text["arabic_br"]
    
    # Calculate bounding box dimensions
