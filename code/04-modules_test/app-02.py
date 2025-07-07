# app-02
#
# Starting to refactor repetitive code a bit
# using a for loop for the UI elements
#
# fix: add for loops to reduce repeating code for common input types
#
# problem: we are very tied to a strict set of components to the data type
# would be good to track the input type,
# so we can use it as a placeholder to manually override in the future

from shiny import App, ui, reactive, render
import pandas as pd
from palmerpenguins import load_penguins

penguins = (
    load_penguins()
    .dropna()
    .loc[:, ["species", "bill_length_mm", "body_mass_g"]]
)

# use a loop instead of listing individual components
ui_filters = {}
for col in penguins.columns:
    # numeric columns have a 2 way slider
    if pd.api.types.is_numeric_dtype(penguins[col]):
        ui_filters[col] = ui.input_slider(
            id=f"filter_{col}",
            label=f"Range for {col}",
            min=float(penguins[col].min()),
            max=float(penguins[col].max()),
            value=[
                float(penguins[col].min()),
                float(penguins[col].max()),
            ],
            step=1,
        )
    else:
        # categorical columns get a checkbox
        ui_filters[col] = ui.input_checkbox_group(
            id=f"filter_{col}",
            label=f"Select {col}",
            choices=sorted(penguins[col].unique()),
            selected=sorted(penguins[col].unique()),
        )

app_ui = ui.page_sidebar(
    ui.sidebar(
        # add the components
        # yuck
        *[(ui_filters[col]) for col in penguins.columns],
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
        # Start with all rows
        mask = pd.Series(True, index=penguins.index)

        for col in penguins.columns:
            if pd.api.types.is_numeric_dtype(penguins[col]):
                min_val, max_val = input[f"filter_{col}"]()
                mask = (
                    mask
                    & (penguins[col] >= min_val)
                    & (penguins[col] <= max_val)
                )
            else:
                selected_categories = input[f"filter_{col}"]()
                mask = mask & penguins[col].isin(selected_categories)

        return penguins[mask]

    @output
    @render.data_frame
    def filtered_data():
        return get_filtered_data()


# Create and return the app
app = App(app_ui, server)
