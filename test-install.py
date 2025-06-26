import os

import openai
import palmerpenguins
import shiny
from chatlas import ChatGithub
from dotenv import load_dotenv

load_dotenv()

chat = ChatGithub(
    model="gpt-4.1",
    system_prompt="You are a terse assistant.",
    api_key=os.getenv("GITHUB_TOKEN"),
)

# Load a shiny app


from palmerpenguins import load_penguins
from plotnine import aes, geom_histogram, ggplot, theme_minimal
from shiny.express import input, render, ui

dat = load_penguins()
species = dat["species"].unique().tolist()

ui.input_radio_buttons("species", "Species", species, inline=True)


@render.plot(height=300)
def plot():
    sel = dat[dat["species"] == input.species()]
    return (
        ggplot(aes(x="bill_length_mm"))
        + geom_histogram(dat, fill="#C2C2C4", binwidth=1)
        + geom_histogram(sel, fill="#447099", binwidth=1)
        + theme_minimal()
    )
