from kedro.pipeline import Pipeline, node, pipeline

from .nodes import *


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            # translate desired dimensions into pixels
            node(
                func=translate_dimensions_to_pixels,
                inputs = ["params:poster_width_in", "params:poster_height_in"],
                outputs = ["poster_width_px", "poster_height_px"],
            ),
            # create blank canvas
            node(
                func=create_blank_canvas,
                inputs = ["poster_width_px", "poster_height_px"],
                outputs = "blank_canvas",
            ),
            # add background image
            node(
                func=add_background_image,
                inputs = ["blank_canvas", "background_image"],
                outputs = "background_image_canvas",
            ),
            # add arabic
            node(
                func=get_arabic_text,
                inputs = ["params:text"],
                outputs = "arabic_text",
            ),
            node(
                func=add_arabic_text,
                inputs = ["background_image_canvas", "params:text", "arabic_text"],
                outputs = "arabic_text_canvas",
            ),
            # add english
            node(
                func=get_english_text,
                inputs = ["params:text"],
                outputs = "english_text",
            ),
            node(
                func=add_english_text,
                inputs = ["arabic_text_canvas", "params:text", "english_text"],
                outputs = "arabic_english_text_canvas",
            ),
        ]
    )
