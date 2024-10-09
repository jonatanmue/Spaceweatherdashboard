import streamlit as st
import polars as pl
import requests
import altair as alt
import pandas as pd
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt

st.markdown("# Startseite")


@st.cache_data
def load_solar_indices():
    response = requests.get(
        "https://kp.gfz-potsdam.de/app/files/Kp_ap_Ap_SN_F107_nowcast.txt"
    )
    return pl.read_csv(skip_rows=40, source=response.content, has_header=False).select(
        (pl.nth(0).str.slice(0, 10).str.to_date("%Y %m %d").alias("Datum")),
        (
            pl.nth(0)
            .str.slice(130, 4)
            .str.strip_chars()
            .alias("Ap")
            .cast(pl.Int32)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(139, 8)
            .str.strip_chars()
            .alias("F10.7")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(135, 3)
            .str.strip_chars()
            .alias("Anzahl Sonnenflecken")
            .cast(pl.Int32)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(33, 6)
            .str.strip_chars()
            .alias("Kp1")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(40, 6)
            .str.strip_chars()
            .alias("Kp2")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(47, 6)
            .str.strip_chars()
            .alias("Kp3")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(54, 6)
            .str.strip_chars()
            .alias("Kp4")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(61, 6)
            .str.strip_chars()
            .alias("Kp5")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(68, 6)
            .str.strip_chars()
            .alias("Kp6")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(75, 6)
            .str.strip_chars()
            .alias("Kp7")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(82, 6)
            .str.strip_chars()
            .alias("Kp8")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
    )


solar_indices = load_solar_indices()

Ap = solar_indices["Ap"].drop_nulls().item(-1)
Ap_chg = Ap - solar_indices["Ap"].drop_nulls().item(-2)

F107 = solar_indices["F10.7"].drop_nulls().item(-1)
F107_chg = F107 - solar_indices["F10.7"].drop_nulls().item(-2)

Kp_indices = solar_indices.select(
    pl.concat_list([f"Kp{i}" for i in range(1, 9)]).alias("Kp").flatten(),
    pl.repeat(list(range(1, 9)), len(solar_indices)).alias("Index").flatten(),
).drop_nulls()
Kp = Kp_indices["Kp"].item(-1)

col1, col2 = st.columns(2)
col1.metric("Ap-Index:", Ap, Ap_chg)
col2.metric("F10.7-Wert:", float(F107), float(F107_chg))

data = pl.DataFrame({"a": ["A"], "b": [float(Kp)]})


def inferno_color(value):
    normalized_value = value / 9.5
    colormap = plt.get_cmap("YlOrRd")
    Farbe = colormap(normalized_value)
    return mp.colors.rgb2hex(Farbe[:3])


st.subheader("Kp-Index:")
chart = (
    alt.Chart(data)
    .mark_bar(color=inferno_color(float(Kp)))
    .encode(
        x=alt.X("a", axis=None),
        y=alt.Y("b", axis=alt.Axis(title=None), scale=alt.Scale(domain=[0, 9.5])),
    )
    .properties(width=150)
    .configure_view(stroke="black", strokeWidth=2)
)
image_url = "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg"

col3, col4 = st.columns(2)
col3.altair_chart(chart)
col4.image(image_url, caption="Das aktuelle Sonnenfoto", width=330)
