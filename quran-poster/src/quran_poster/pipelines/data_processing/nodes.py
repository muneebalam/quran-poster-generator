from PIL import Image
import urllib.request
import sqlite3
import os
import pandas as pd


def translate_dimensions_to_pixels(poster_width_in: float, poster_height_in: float) -> tuple[int, int]:
    return int(poster_width_in * 300), int(poster_height_in * 300)

def create_blank_canvas(poster_width_px: int, poster_height_px: int) -> Image.Image:
    return Image.new("RGBA", (poster_width_px, poster_height_px), (255, 255, 255, 0))

def add_background_image(blank_canvas: Image.Image, background_image_path: str) -> Image.Image:
    background_image = Image.open(background_image_path)
    background_image = background_image.resize(blank_canvas.size)
    blank_canvas.paste(background_image, (0, 0))
    return blank_canvas

def _get_text(text: dict, lang: str) -> tuple[str]:
    # Get verses
    include_basmalah = text["include_basmalah"]
    surah = text["quran_surah"]
    verse_start = text["quran_verse_start"]
    verse_end = text["quran_verse_end"]
    source = text[f"{lang}_source"]
    f_out = f"data/01_raw/{lang}.db"
    
    # Download if needed
    if not os.path.exists(f_out):
        urllib.request.urlretrieve(source, f_out)

    # Look up verses
    conn = sqlite3.connect(f_out)
    if lang == "english":
        # English
        tblname = "content"
        s_col = "sura"
        a_col = "aya"
        select_col = "text"
    else:
        # Arabic
        tblname = "verses_v1"
        s_col = "sura_no"
        a_col = "aya_no"
        select_col = "aya_text"
    
    verses = pd.read_sql(f"SELECT {select_col} FROM {tblname} WHERE {s_col} = {surah} AND {a_col} BETWEEN {verse_start} AND {verse_end}", conn).squeeze().to_list()
    print(verses)
    if include_basmalah and verse_start != 1:
        basmalah = pd.read_sql(f"SELECT * FROM {tblname} WHERE {s_col} = 1 AND {a_col} = 1", conn).squeeze().to_list()
        verses = basmalah + verses
    conn.close()

    return "\n".join(verses)

def _add_text(background_image_canvas: Image.Image, text: dict, lang: str, saved_text: list[str]) -> Image.Image:
    font_path = text[f"{lang}_font_path"]
    tl = text[f"{lang}_tl"].replace("(", "").replace(")", "").split(",")
    br = text[f"{lang}_br"].replace("(", "").replace(")", "").split(",")
    
    # Calculate bounding box dimensions
    # width = int(br[0]) - int(tl[0])
    # height = int(br[1]) - int(tl[1])

    
    return background_image_canvas

def get_arabic_text(text: dict) -> tuple[str]:
    return _get_text(text, "arabic")
def get_english_text(text: dict) -> tuple[str]:
    return _get_text(text, "english")

def add_arabic_text(background_image_canvas: Image.Image, text: dict, saved_text_str: str) -> Image.Image:
    return _add_text(background_image_canvas, text, "arabic", saved_text_str.split(","))

def add_english_text(background_image_canvas: Image.Image, text: dict, saved_text_str: str) -> Image.Image:
    return _add_text(background_image_canvas, text, "english", saved_text_str.split(","))
    
    return background_image_canvas

def save_poster(arabic_text_canvas: Image.Image, output_path: str) -> None:
    arabic_text_canvas.save(output_path)
    print(f"Poster saved to {output_path}")