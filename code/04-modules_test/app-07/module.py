import pandas as pd
from shiny import module, render, ui, reactive

from helper import create_ui_filters


@module.ui
def filter_ui():
    return ui.output_ui("filters")


@module.server
def filter_server(input, output, session, data, columns):
    ui_filters = create_ui_filters(data, columns)

    @render.ui
    def filters():
        return [(ui_filters[col]["component"]) for col in columns]

    @reactive.calc
    def get_filter_mask():
        mask = pd.Series(True, index=data.index)

        for col in columns:
            if ui_filters[col]["filter_method"] == "sliders2_between":
                min_val, max_val = input[f"filter_{col}"]()
                mask = mask & data[col].between(min_val, max_val)
            elif ui_filters[col]["filter_method"] == "list_isin":
                selected_categories = input[f"filter_{col}"]()
                mask = mask & data[col].isin(selected_categories)
            else:
                raise ValueError

        return mask

    return {
        "mask": get_filter_mask,
    }
