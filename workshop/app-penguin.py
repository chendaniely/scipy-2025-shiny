from shiny.express import ui, render, input

from palmerpenguins import load_penguins
from plotnine import aes, geom_histogram, ggplot, theme_minimal

ui.input_radio_buttons(
    id="species",
    label="Species",
    choices=["Adelie", "Gentoo", "Chinstrap"],
    inline=True,
)

dat = load_penguins()


@render.plot #<<
def plot(): #<<
    species = input.species()
    sel = dat.loc[dat.species == species]
    return ( #<<
        ggplot(aes(x="bill_length_mm"))
        + geom_histogram(dat, fill="#C2C2C4", binwidth=1)
        + geom_histogram(sel, fill="#447099", binwidth=1)
        + theme_minimal()
    )
