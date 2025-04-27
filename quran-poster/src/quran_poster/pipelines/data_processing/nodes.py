from PIL import Image, ImageFont, ImageDraw
import urllib.request
import sqlite3
import os
import pandas as pd
import numpy as np
import arabic_reshaper
from bidi.algorithm import get_display
import re
import textwrap

def translate_dimensions_to_pixels(poster_width_in: float, poster_height_in: float) -> tuple[int, int]:
    return int(poster_width_in * 300), int(poster_height_in * 300)

def create_blank_canvas(poster_width_px: int, poster_height_px: int) -> Image.Image:
    return Image.new("RGBA", (poster_width_px, poster_height_px), (255, 255, 255, 0))

def add_background_image(blank_canvas: Image.Image, background_image: Image.Image) -> Image.Image:
    #background_image = Image.open(background_image_path)
    background_image = background_image.resize(blank_canvas.size)
    blank_canvas.paste(background_image, (0, 0))
    return blank_canvas

def _get_text(text: dict, lang: str) -> tuple[str]:
    """Look up verses from sqlite database, downloading if needed"""
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

def _clean_text(text: str) -> str:
    while "<sup" in text:
        text = re.sub(r"<sup.*?</sup>", "", text)
    return text


def _add_text(background_image_canvas: Image.Image, text: dict, lang: str, saved_text: list[str]) -> Image.Image:
    font_path = text[f"{lang}_font_path"]
    tl = [float(x.strip()) for x in text[f"{lang}_tl"].replace("(", "").replace(")", "").split(",")]
    br = [float(x.strip()) for x in text[f"{lang}_br"].replace("(", "").replace(")", "").split(",")]
    
    # Calculate bounding box dimensions in pixels
    # https://github.com/python-pillow/Pillow/issues/3081

    w_in, h_in = background_image_canvas.size
    tl_px = (tl[0] * w_in, tl[1] * h_in)
    br_px = (br[0] * w_in, br[1] * h_in)
    
    space_height = br_px[1] - tl_px[1]
    space_width = br_px[0] - tl_px[0]
    font = ImageFont.truetype(font_path, text["font_size"])
    draw = ImageDraw.Draw(background_image_canvas)

    # TODO Redo the line breaks
    new_verses = len(saved_text)
    continuations = 0
    for line in saved_text:
        text_w = draw.textlength(line, font=font)
        continuations += text_w // space_width

    cur_top = tl_px[1]
    for i, line in enumerate(saved_text):
        if lang == "arabic":
            # line = arabic_reshaper.reshape(line)
            # line = get_display(line, base_dir = "R")
            pass
        else:
            line = _clean_text(line)

        # See if we need to wrap the text
        left = tl_px[0]
        right = br_px[0]
        text_w = draw.textlength(line, font=font)

        # Deal with long lines
        if text_w > space_width:
            lines = []
            cur_start = 0 
            words = line.split()
            for j in range(len(words)):
                line_w = draw.textlength(" ".join(words[cur_start:j+1]), font=font)
                if line_w > space_width:
                    lines.append(" ".join(words[cur_start:j]))
                    cur_start = j
            if cur_start < len(words):
                lines.append(" ".join(words[cur_start:]))
        else:
            lines = [line]
        if lang == "arabic":
            pass # lines = lines[::-1]
        for line in lines:
            if lang == "arabic":
                line = arabic_reshaper.reshape(line)
                line = get_display(line, base_dir = "R")
                draw.text((right, cur_top), line, (0,0,0), font=font, anchor="rt")
            else:
                draw.text((left, cur_top), line, (0,0,0), font=font)
            cur_top += text["intraline_spacing"]
        cur_top -= text["intraline_spacing"] # one extra

        # At the end of each verse, newline spacing
        cur_top += text["interline_spacing"]

    return background_image_canvas

def get_arabic_text(text: dict) -> tuple[str]:
    return _get_text(text, "arabic")
def get_english_text(text: dict) -> tuple[str]:
    return _get_text(text, "english")

def add_arabic_text(background_image_canvas: Image.Image, text: dict, saved_text_str: str) -> Image.Image:
    return _add_text(background_image_canvas, text, "arabic", saved_text_str.split("\n"))

def add_english_text(background_image_canvas: Image.Image, text: dict, saved_text_str: str) -> Image.Image:
    return _add_text(background_image_canvas, text, "english", saved_text_str.split("\n"))
