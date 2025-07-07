from shiny import App, ui, render
from palmerpenguins import load_penguins

import module

penguins1 = (
    load_penguins()
    .dropna()
    .loc[:, ["species", "bill_length_mm", "body_mass_g"]]
)

penguins2 = (
    load_penguins()
    .dropna()
    .loc[:, ["island", "sex", "year", "flipper_length_mm"]]
)

app_ui = ui.page_fillable(
    ui.navset_card_tab(
        ui.nav_panel(
            "Penguins 1",
            ui.card(
                ui.layout_sidebar(
                    ui.sidebar(
                        module.filter_ui("module1"),
                    ),
                    ui.output_data_frame("filtered_data1"),
                ),
            ),
        ),
        ui.nav_panel(
            "Penguins 2",
            ui.card(
                ui.layout_sidebar(
                    ui.sidebar(
                        module.filter_ui("module2"),
                    ),
                    ui.output_data_frame("filtered_data2"),
                ),
            ),
        ),
    ),
)


def server(input, output, session):
    # penguins 1 data -----
    filter_module1 = module.filter_server(
        "module1",
        data=penguins1,
        columns=penguins1.columns,
    )

    module_filter_mask1 = filter_module1["mask"]

    @render.data_frame
    def filtered_data1():
        return penguins1.loc[module_filter_mask1()]

    # penguins 2 data -----
    filter_module2 = module.filter_server(
        "module2",
        data=penguins2,
        columns=penguins2.columns,
    )

    module_filter_mask2 = filter_module2["mask"]

    @render.data_frame
    def filtered_data2():
        return penguins2.loc[module_filter_mask2()]


app = App(app_ui, server)
