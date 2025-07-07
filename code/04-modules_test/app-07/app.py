from shiny import App, ui, render
from palmerpenguins import load_penguins

import module

penguins = (
    load_penguins()
    .dropna()
    .loc[:, ["species", "bill_length_mm", "body_mass_g"]]
)

app_ui = ui.page_sidebar(
    ui.sidebar(
        module.filter_ui("module"),
    ),
    ui.card(
        ui.card_header("Filtered Penguins Data"),
        ui.output_data_frame("filtered_data"),
    ),
)


def server(input, output, session):
    filter_module = module.filter_server(
        "module",
        data=penguins,
        columns=penguins.columns,
    )

    module_filter_mask = filter_module["mask"]

    @render.data_frame
    def filtered_data():
        return penguins.loc[module_filter_mask()]


app = App(app_ui, server)
