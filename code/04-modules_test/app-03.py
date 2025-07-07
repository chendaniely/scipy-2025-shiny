# app-03
#
# different input components need different ways to filter the data
# the ui_filters will still have column as key,
# but values will be a dict, containing the input component,
# and label for filter type
#
# problem: lots of code outside the shiny context

from shiny import App, ui, reactive, render
import pandas as pd
from palmerpenguins import load_penguins

penguins = (
    load_penguins()
    .dropna()
    .loc[:, ["species", "bill_length_mm", "body_mass_g"]]
)

ui_filters = {}
for col in penguins.columns:
    if pd.api.types.is_numeric_dtype(penguins[col]):
        min_val = float(penguins[col].min())
        max_val = float(penguins[col].max())
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
        unique = sorted(penguins[col].unique())
        ui_filters[col] = {
            "filter_method": "list_isin",
            "component": ui.input_checkbox_group(
                f"filter_{col}",
                f"Select {col}",
                choices=unique,
                selected=unique,
            ),
        }


app_ui = ui.page_sidebar(
    ui.sidebar(
        *[(ui_filters[col]["component"]) for col in penguins.columns],
    ),
    ui.card(
        ui.card_header("Filtered Penguins Data"),
        ui.output_data_frame("filtered_data"),
    ),
)


# Define the server logic
def server(input, output, session):
    @reactive.calc
    def get_filtered_data():
        mask = pd.Series(True, index=penguins.index)

        for col in penguins.columns:
            if ui_filters[col]["filter_method"] == "sliders2_between":
                min_val, max_val = input[f"filter_{col}"]()
                mask = mask & penguins[col].between(min_val, max_val)
            elif ui_filters[col]["filter_method"] == "list_isin":
                selected_categories = input[f"filter_{col}"]()
                mask = mask & penguins[col].isin(selected_categories)
            else:
                raise ValueError

        return penguins[mask]

    @output
    @render.data_frame
    def filtered_data():
        return get_filtered_data()


# Create and return the app
app = App(app_ui, server)
