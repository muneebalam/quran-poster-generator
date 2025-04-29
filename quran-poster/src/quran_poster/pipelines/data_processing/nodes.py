from PIL import Image, ImageFont, ImageDraw
import urllib.request
import sqlite3
import os
import pandas as pd
import numpy as np
import arabic_reshaper
from arabic_reshaper import ArabicReshaper
from bidi.algorithm import get_display
import re
import textwrap

# Basic utils to start --------------------------------------------------------
def translate_dimensions_to_pixels(poster_width_in: float, poster_height_in: float) -> tuple[int, int]:
    return int(poster_width_in * 300), int(poster_height_in * 300)

def create_blank_canvas(poster_width_px: int, poster_height_px: int) -> Image.Image:
    return Image.new("RGBA", (poster_width_px, poster_height_px), (255, 255, 255, 0))

def add_background_image(blank_canvas: Image.Image, background_image: Image.Image, background_alpha: int) -> Image.Image:
    #background_image = Image.open(background_image_path)
    background_image = background_image.resize(blank_canvas.size)
    blank_canvas.paste(background_image, (0, 0))
    blank_canvas.putalpha(background_alpha)
    return blank_canvas

# Calculate spacing ------------------------------------------------------------
def _clean_pos_tuple(pos_tuple: str) -> tuple[float, float]:
    return tuple([float(x.strip()) for x in pos_tuple.replace("(", "").replace(")", "").split(",")])

def calculate_space_dimensions_px(background_image_canvas: Image.Image, text_params: dict, lang: str) -> tuple[int, int]:
    tl = _clean_pos_tuple(text_params[lang]["tl"])
    br = _clean_pos_tuple(text_params[lang]["br"])
    w_in, h_in = background_image_canvas.size
    tl_px = (tl[0] * w_in, tl[1] * h_in)
    br_px = (br[0] * w_in, br[1] * h_in)
    return br_px[0] - tl_px[0], br_px[1] - tl_px[1]

def _split_single_verse(mytext: str, mywidth: float, lang: str, background_image_canvas: Image.Image,
                        font_path: str, font_size: int):
    if lang == "ar":
        # line = arabic_reshaper.reshape(line)
        # line = get_display(line, base_dir = "R")
        pass
    else:
        mytext = _clean_text(mytext)

    # See if we need to wrap the text
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(background_image_canvas)
    text_w = draw.textlength(mytext, font=font)

    # The end of verse markers showing up as blank - delete
    if lang == "ar":
        mytext = mytext[:-2]

    # Deal with long lines
    if text_w > mywidth:
        lines = []
        cur_start = 0 
        words = mytext.split()
        for j in range(len(words)):
            line_w = draw.textlength(" ".join(words[cur_start:j+1]), font=font)
            if line_w > mywidth:
                lines.append(" ".join(words[cur_start:j]))
                cur_start = j
        if cur_start < len(words):
            lines.append(" ".join(words[cur_start:]))
    else:
        lines = [mytext]
    return lines

def calculate_line_y_positions(ar_text: str, en_text: str, text_params: dict, background_image_canvas: Image.Image) -> tuple[tuple[int]]:
    ar_lines = ar_text.split("\n")
    en_lines = en_text.split("\n")
    ar_font = ImageFont.truetype(text_params["ar"][f"font_path"], text_params["font_size"])
    en_font = ImageFont.truetype(text_params["en"][f"font_path"], text_params["font_size"])
    draw = ImageDraw.Draw(background_image_canvas)

    top_y = _clean_pos_tuple(text_params["en"]["tl"])[1]
    space_width_en, space_height_en = calculate_space_dimensions_px(background_image_canvas, text_params, "en")
    space_width_ar, space_height_ar = calculate_space_dimensions_px(background_image_canvas, text_params, "ar")

    lines_by_verse = []
    for i in range(len(ar_lines)):
        ar_lines_v = _split_single_verse(ar_lines[i], space_width_ar, "ar", background_image_canvas,
                                       text_params["ar"]["font_path"], text_params["font_size"])
        en_lines_v = _split_single_verse(en_lines[i], space_width_en, "en", background_image_canvas,
                                       text_params["en"]["font_path"], text_params["font_size"])
        print(len(en_lines_v), en_lines_v)
        lines_by_verse.append(max(len(ar_lines_v), len(en_lines_v)) + 2) # to be safe

    line_breaks = len(ar_lines) - 1
    continuations = sum(lines_by_verse) - line_breaks
    spacing_param = space_height_en / (3 * line_breaks + 1.3 * continuations)

    line_y_positions = [[top_y * background_image_canvas.size[1]]]
    for i in range(len(ar_lines)):
        line_y_positions.append([line_y_positions[-1][-1] + 3 * spacing_param])
        for j in range(int(lines_by_verse[i])):
            line_y_positions[-1].append(line_y_positions[-1][-1] + 1.3 * spacing_param)
    return (line_y_positions[1:],)
            

# Get text ---------------------------------------------------------------------
def _get_text(text: dict, lang: str) -> tuple[str]:
    """Look up verses from sqlite database, downloading if needed"""
    # Get verses
    include_basmalah = text["include_basmalah"]
    surah = text["quran_surah"]
    verse_start = text["quran_verse_start"]
    verse_end = text["quran_verse_end"]
    source = text[lang][f"source"]
    f_out = f"data/01_raw/{lang}.db"
    
    # Download if needed
    if not os.path.exists(f_out):
        urllib.request.urlretrieve(source, f_out)

    # Look up verses
    conn = sqlite3.connect(f_out)
    if lang == "en":
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
    if include_basmalah:
        basmalah = pd.read_sql(f"SELECT {select_col} FROM {tblname} WHERE {s_col} = 1 AND {a_col} = 1", conn).squeeze()
        verses = [basmalah] + verses
    conn.close()

    return "\n".join(verses)

def _clean_text(text: str) -> str:
    while "<sup" in text:
        text = re.sub(r"<sup.*?</sup>", "", text)
    text = text.replace("\n", "")
    return text

# Add text ---------------------------------------------------------------------
def _add_text(background_image_canvas: Image.Image, text: dict, lang: str, saved_text: list[str], line_y_positions: list[list[float]]) -> Image.Image:
    font_path = text[lang][f"font_path"]
    tl = _clean_pos_tuple(text[lang][f"tl"])
    br = _clean_pos_tuple(text[lang][f"br"])
    font_size = text["font_size"]
    
    # Calculate bounding box dimensions in pixels
    # https://github.com/python-pillow/Pillow/issues/3081

    w_in, h_in = background_image_canvas.size
    tl_px = (tl[0] * w_in, tl[1] * h_in)
    br_px = (br[0] * w_in, br[1] * h_in)
    
    space_height = br_px[1] - tl_px[1]
    space_width = br_px[0] - tl_px[0]
    left = tl_px[0]
    right = br_px[0]
    font = ImageFont.truetype(font_path, text["font_size"])
    draw = ImageDraw.Draw(background_image_canvas)
    
    for i, line in enumerate(saved_text):
        lines = _split_single_verse(line, space_width, lang, background_image_canvas,
                                    font_path, text["font_size"])
        for j, line in enumerate(lines):
            y_needed = line_y_positions[i][j]
            if lang == "ar":
                reshaper = arabic_reshaper.ArabicReshaper(
                    arabic_reshaper.config_for_true_type_font(
                        text["en"]["font_path"],
                        arabic_reshaper.ENABLE_ALL_LIGATURES
                    )
                )
                reshaper = ArabicReshaper(configuration={"delete_harakat": "no",
                                                         "support_ligatures": "yes",
                                                          "RIAL SIGN": "yes"})
                line = reshaper.reshape(line)
                line = get_display(line, base_dir = "R")
                draw.text((right, y_needed), line, font=font, anchor="rt",
                          fill = text["ar"]["color"])

            else:
                draw.text((left, y_needed), line, font=font, fill = text["en"]["color"])

    return background_image_canvas

def get_arabic_text(text: dict) -> tuple[str]:
    return _get_text(text, "ar")
def get_english_text(text: dict) -> tuple[str]:
    return _get_text(text, "en")

def add_arabic_text(background_image_canvas: Image.Image, text: dict, saved_text_str: str, line_y_positions: list[list[float]]) -> Image.Image:
    return _add_text(background_image_canvas, text, "ar", saved_text_str.split("\n"), line_y_positions)

def add_english_text(background_image_canvas: Image.Image, text: dict, saved_text_str: str, line_y_positions: list[list[float]]) -> Image.Image:
    return _add_text(background_image_canvas, text, "en", saved_text_str.split("\n"), line_y_positions)
