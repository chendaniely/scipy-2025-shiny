import pandas as pd
from shiny import ui


def create_ui_filters(data, columns):
    ui_filters = {}

    for col in columns:
        if pd.api.types.is_numeric_dtype(data[col]):
            min_val = float(data[col].min())
            max_val = float(data[col].max())
            ui_filters[col] = {
                "filter_method": "sliders2_between",
                "component": ui.input_slider(
                    f"filter_{col}",
                    f"Range for {col}",
                    min=min_val,
                    max=max_val,
                    value=[min_val, max_val],
                    step=1,
                ),
            }

        else:
            unique = sorted(data[col].unique())
            ui_filters[col] = {
                "filter_method": "list_isin",
                "component": ui.input_checkbox_group(
                    f"filter_{col}",
                    f"Select {col}",
                    choices=unique,
                    selected=unique,
                ),
            }

    return ui_filters
