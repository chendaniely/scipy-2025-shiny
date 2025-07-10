from palmerpenguins import load_penguins
from plotnine import aes, geom_histogram, ggplot, theme_minimal, theme_xkcd

dat = load_penguins()
dat.head()

species = "Gentoo"  # Adelie, Gentoo, Chinstrap
sel = dat.loc[dat.species == species]

(
    ggplot(aes(x="bill_length_mm"))
    + geom_histogram(dat, fill="#C2C2C4", binwidth=1)
    + geom_histogram(sel, fill="#447099", binwidth=1)
    + theme_xkcd()
)
