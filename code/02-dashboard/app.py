
import plotly.express as px
from ridgeplot import ridgeplot
import seaborn as sns
from shiny.express import input, ui, render
from shiny import reactive
from shinywidgets import render_plotly, render_widget

tips = sns.load_dataset("tips")

# title
ui.page_opts(title="Restaurant tipping", fillable=True)

# sidebar
with ui.sidebar(open="desktop"):
    ui.input_slider(
        id="slider",
        label="Bill amount",
        min=tips.total_bill.min(),
        max=tips.total_bill.max(),
        value=[tips.total_bill.min(), tips.total_bill.max()])
    ui.input_checkbox_group(
        id="checkbox_group",
        label="Food service",
        choices={
            "Lunch": "Lunch",
            "Dinner": "Dinner",
        },
        selected=[
            "Lunch",
            "Dinner",
        ],
    )
    ui.input_action_button("action_button", "Reset filter")

@reactive.calc
def filtered_data():
    idx1 = tips.total_bill.between(
                left=input.slider()[0],
                right=input.slider()[1],
                inclusive="both",
            )
    idx2 = tips.time.isin(input.checkbox_group())
    tips_filtered = tips[idx1 & idx2]
    return tips_filtered


# body of application
# first row of value boxes
with ui.layout_columns(fill=False):
    with ui.value_box():
        "Total tippers"
        @render.text
        def total_tippers():
            return filtered_data().shape[0]


    with ui.value_box():
        "Average tip"
        @render.text
        def average_tip():
            perc = filtered_data().tip / filtered_data().total_bill
            return f"{perc.mean():.1%}"

    with ui.value_box():
        "Average bill"
        @render.text
        def average_bill():
            bill = filtered_data().total_bill.mean()
            return f"${bill:.2f}"

# second row of cards
with ui.layout_columns(col_widths=[6, 6]):
    with ui.card(full_screen=True):
        ui.card_header("Tips data")
        @render.data_frame
        def tips_data():
            return filtered_data()

    with ui.card(full_screen=True):
        ui.card_header("Total bill vs tip")
        @render_plotly
        def scatterplot():
            return px.scatter(
                filtered_data(),
                x="total_bill",
                y="tip",
                trendline="lowess"
            )


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Tip percentages")
        @render_widget
        def ridge():
            filtered_data()["percent"] = filtered_data().tip / filtered_data().total_bill

            uvals = filtered_data().day.unique()
            samples = [[filtered_data().percent[filtered_data().day == val]] for val in uvals]

            plt = ridgeplot(
                samples=samples,
                labels=uvals,
                bandwidth=0.01,
                colorscale="viridis",
                colormode="row-index"
            )

            plt.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                )
            )

            return plt
