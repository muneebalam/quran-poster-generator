from kedro.pipeline import Pipeline, node, pipeline

from .nodes import create_model_input_table, preprocess_companies, preprocess_shuttles


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=preprocess_companies,
                inputs="companies",
                outputs="preprocessed_companies",
                name="preprocess_companies_node",
            ),
            node(
                func=preprocess_shuttles,
                inputs="shuttles",
                outputs="preprocessed_shuttles",
                name="preprocess_shuttles_node",
            ),
            node(
                func=create_model_input_table,
                inputs=["preprocessed_shuttles", "preprocessed_companies", "reviews"],
                outputs="model_input_table",
                name="create_model_input_table_node",
            ),
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
                inputs = ["blank_canvas", "params:background_image_path"],
                outputs = "background_image_canvas",
            ),
            # add desired user quran text and bounding box into font size
            node(
                func=add_arabic_text,
                inputs = ["background_image_canvas", "params:text"],
                outputs = "arabic_text_canvas",
            ),
            # add arabic
            # repeat for english
            # Add english
            # save
        ]
    )
