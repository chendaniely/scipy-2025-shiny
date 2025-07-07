# in app module

# return a mask, not the dataframe, so the results of the module can be modified

from shiny import App, ui, reactive, render, module
import pandas as pd
from palmerpenguins import load_penguins


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


penguins = (
    load_penguins()
    .dropna()
    .loc[:, ["species", "bill_length_mm", "body_mass_g"]]
)


app_ui = ui.page_sidebar(
    ui.sidebar(
        filter_ui("module"),
    ),
    ui.card(
        ui.card_header("Filtered Penguins Data"),
        ui.output_data_frame("filtered_data"),
    ),
)


# Define the server logic
def server(input, output, session):
    filter_module = filter_server(
        "module",
        data=penguins,
        columns=penguins.columns,
    )

    module_filter_mask = filter_module["mask"]

    @render.data_frame
    def filtered_data():
        return penguins.loc[module_filter_mask()]


# Create and return the app
app = App(app_ui, server)
